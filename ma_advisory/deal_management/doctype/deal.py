"""Deal DocType controller"""

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, flt, add_days, get_datetime
from frappe import _

class Deal(Document):
    """Deal document class for M&A transactions"""
    
    def autoname(self):
        """Auto-generate name based on deal type and year"""
        abbr = {
            "Acquisition": "ACQ",
            "Fusion": "FUS",
            "Cession": "CES",
            "Levée de Fonds": "LDF",
            "MBO/MBI": "MBO",
            "Recapitalisation": "REC"
        }.get(self.deal_type, "DEL")
        
        from datetime import datetime
        year = datetime.now().year
        
        # Get next sequence number
        last_deal = frappe.db.sql("""
            SELECT name FROM `tabDeal`
            WHERE name LIKE %(pattern)s
            ORDER BY name DESC LIMIT 1
        """, {"pattern": f"{abbr}-{year}-%"})
        
        if last_deal:
            last_num = int(last_deal[0][0].split("-")[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        self.name = f"{abbr}-{year}-{next_num:04d}"
    
    def before_insert(self):
        """Called before inserting new record"""
        if not self.created_date:
            self.created_date = nowdate()
        
        # Set default currency if not set
        if not self.currency:
            self.currency = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_currency") or "EUR"
    
    def validate(self):
        """Validate deal before saving"""
        self.validate_dates()
        self.calculate_probability()
        self.validate_value()
        self.set_title()
        self.update_team_details()
    
    def validate_dates(self):
        """Ensure dates are logical"""
        if self.expected_close_date and self.created_date:
            if getdate(self.expected_close_date) < getdate(self.created_date):
                frappe.throw(_("La date de clôture prévue ne peut pas être antérieure à la date de création"))
        
        if self.closing_date and self.created_date:
            if getdate(self.closing_date) < getdate(self.created_date):
                frappe.throw(_("La date de clôture ne peut pas être antérieure à la date de création"))
        
        # Auto-set closing date when status is Terminé
        if self.status == "Terminé" and not self.closing_date:
            self.closing_date = nowdate()
    
    def validate_value(self):
        """Validate deal value"""
        if self.value and self.value < 0:
            frappe.throw(_("La valeur de la transaction ne peut pas être négative"))
    
    def calculate_probability(self):
        """Auto-calculate probability based on stage"""
        stage_probability = {
            "Origination": 10,
            "Mandat Signé": 20,
            "Teaser Envoyé": 30,
            "NDA Signés": 40,
            "CIM Distribué": 50,
            "Offres Indicatives": 60,
            "Due Diligence": 70,
            "Offres Finales": 80,
            "Négociation": 85,
            "Signing": 95,
            "Closing": 100
        }
        
        # Only auto-calculate if not manually set
        if self.stage and (not self.probability or self.has_value_changed("stage")):
            self.probability = stage_probability.get(self.stage, 50)
    
    def set_title(self):
        """Set display title"""
        if not self.deal_name:
            self.deal_name = f"{self.deal_type} - {self.target_company or 'TBD'}"
    
    def update_team_details(self):
        """Update team member details from User"""
        if self.advisor_team:
            for team_member in self.advisor_team:
                if team_member.user and not team_member.full_name:
                    user_doc = frappe.get_doc("User", team_member.user)
                    team_member.full_name = user_doc.full_name
                    team_member.email = user_doc.email
    
    def on_update(self):
        """Called when deal is updated"""
        self.update_valuation_status()
        self.update_linked_project()
        self.notify_stage_change()
        self.create_timeline_entry()
    
    def after_insert(self):
        """Called after creating new deal"""
        self.create_linked_project()
        self.create_initial_dd_items()
        self.send_notification()
    
    def update_valuation_status(self):
        """Update status on related valuation documents"""
        if self.status == "Terminé":
            valuations = frappe.get_all(
                "Valuation",
                filters={"deal": self.name}
            )
            for val in valuations:
                val_doc = frappe.get_doc("Valuation", val.name)
                if val_doc.status != "Archivé":
                    val_doc.status = "Archivé"
                    val_doc.save(ignore_permissions=True)
    
    def create_linked_project(self):
        """Create ERPNext Project linked to this deal"""
        if self.status == "Terminé" or self.status == "Annulé":
            return
        
        # Check if project already exists
        existing_project = frappe.db.get_value("Project", {"deal": self.name})
        if existing_project:
            return
        
        # Create new project
        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": self.deal_name,
            "status": "Open",
            "expected_start_date": self.created_date,
            "expected_end_date": self.expected_close_date,
            "customer": self.client,
            "deal": self.name,
            "project_type": "Internal"
        })
        
        try:
            project.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to create project for deal {self.name}: {str(e)}")
    
    def update_linked_project(self):
        """Update linked ERPNext Project"""
        project_name = frappe.db.get_value("Project", {"deal": self.name})
        if not project_name:
            return
        
        try:
            project = frappe.get_doc("Project", project_name)
            project.project_name = self.deal_name
            project.expected_end_date = self.expected_close_date
            project.customer = self.client
            
            if self.status == "Terminé":
                project.status = "Completed"
            elif self.status == "Annulé":
                project.status = "Cancelled"
            
            project.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to update project for deal {self.name}: {str(e)}")
    
    def create_initial_dd_items(self):
        """Create initial due diligence checklist"""
        if frappe.db.exists("Due Diligence Item", {"deal": self.name}):
            return
        
        # Standard DD categories with items
        dd_template = {
            "Financière": [
                "États financiers 3 dernières années",
                "Liasse fiscale",
                "Budget et prévisions",
                "Dette et engagements financiers",
                "Analyse du BFR"
            ],
            "Juridique": [
                "Statuts et K-bis",
                "Pacte d'actionnaires",
                "Contrats principaux",
                "Litiges en cours",
                "Propriété intellectuelle"
            ],
            "Commerciale": [
                "Liste des clients principaux",
                "Contrats commerciaux",
                "Pipeline commercial",
                "Analyse de la concurrence"
            ]
        }
        
        for category, items in dd_template.items():
            for item_name in items:
                try:
                    dd_item = frappe.get_doc({
                        "doctype": "Due Diligence Item",
                        "deal": self.name,
                        "category": category,
                        "item_name": item_name,
                        "status": "À Faire",
                        "priority": "Moyenne"
                    })
                    dd_item.insert(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Failed to create DD item {item_name}: {str(e)}")
        
        frappe.db.commit()
    
    def notify_stage_change(self):
        """Notify team when stage changes"""
        if not self.has_value_changed("stage"):
            return
        
        # Get all team members
        team_emails = []
        if self.lead_advisor:
            team_emails.append(self.lead_advisor)
        
        for member in self.advisor_team:
            if member.email:
                team_emails.append(member.email)
        
        if not team_emails:
            return
        
        message = f"""
        <h3>Changement d'étape: {self.deal_name}</h3>
        <p>La transaction <b>{self.deal_name}</b> est passée à l'étape:</p>
        <p><b>{self.stage}</b></p>
        <p>Probabilité de succès: {self.probability}%</p>
        <p><a href="/app/deal/{self.name}">Voir la transaction</a></p>
        """
        
        frappe.sendmail(
            recipients=list(set(team_emails)),
            subject=f"Changement d'étape: {self.deal_name}",
            message=message,
            reference_doctype=self.doctype,
            reference_name=self.name
        )
    
    def create_timeline_entry(self):
        """Create timeline entry for important changes"""
        changes = []
        
        if self.has_value_changed("stage"):
            changes.append(f"Étape: {self.stage}")
        
        if self.has_value_changed("status"):
            changes.append(f"Statut: {self.status}")
        
        if self.has_value_changed("value"):
            changes.append(f"Valeur: {frappe.utils.fmt_money(self.value, currency=self.currency)}")
        
        if changes:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": self.doctype,
                "reference_name": self.name,
                "content": "<br>".join(changes)
            }).insert(ignore_permissions=True)
    
    def send_notification(self):
        """Send notification when new deal is created"""
        if self.lead_advisor:
            message = f"""
            <h3>Nouvelle transaction créée</h3>
            <p>Une nouvelle transaction a été créée:</p>
            <p><b>{self.deal_name}</b></p>
            <p>Type: {self.deal_type}</p>
            <p>Client: {self.client or 'N/A'}</p>
            <p><a href="/app/deal/{self.name}">Voir la transaction</a></p>
            """
            
            frappe.sendmail(
                recipients=[self.lead_advisor],
                subject=f"Nouvelle transaction: {self.deal_name}",
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
    
    @frappe.whitelist()
    def get_dashboard_data(self):
        """Get dashboard data for this deal"""
        data = {
            "fieldname": "deal",
            "non_standard_fieldnames": {},
            "transactions": [
                {
                    "label": _("Valorisation et Financier"),
                    "items": ["Valuation"]
                },
                {
                    "label": _("Due Diligence"),
                    "items": ["Due Diligence Item"]
                },
                {
                    "label": _("Projets et Tâches"),
                    "items": ["Project", "Task"]
                }
            ]
        }
        
        return data
    
    def get_feed(self):
        """Feed for timeline"""
        return f"{self.stage} - {self.status}"
