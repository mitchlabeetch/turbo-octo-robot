"""MA Contact DocType - Manages contacts with relationship intelligence"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


class MAContact(Document):
    """Contact document for M&A advisory with relationship intelligence"""

    def before_insert(self):
        """Set defaults before insert"""
        if not self.first_contact_date:
            self.first_contact_date = getdate()

    def on_update(self):
        """Update related records and refresh metrics"""
        self.update_interaction_metrics()
        self.update_relationship_strength()
        self.notify_assignment()

    def update_interaction_metrics(self):
        """Calculate interaction counts from MA Interaction records"""
        base_filter = {"contact": self.name, "docstatus": 1}
        
        # Total interactions
        self.interaction_count = frappe.db.count("MA Interaction", filters=base_filter)
        
        # By type
        self.email_count = frappe.db.count(
            "MA Interaction",
            filters={**base_filter, "interaction_type": "Email"}
        )
        self.call_count = frappe.db.count(
            "MA Interaction",
            filters={**base_filter, "interaction_type": "Call"}
        )
        self.meeting_count = frappe.db.count(
            "MA Interaction",
            filters={**base_filter, "interaction_type": "Meeting"}
        )
        
        # Update last contact date
        last_interaction = frappe.get_all(
            "MA Interaction",
            filters=base_filter,
            fields=["interaction_date"],
            order_by="interaction_date desc",
            limit_page_length=1
        )
        if last_interaction:
            self.last_contact_date = last_interaction[0]["interaction_date"]

    def update_relationship_strength(self):
        """Update relationship strength based on interaction count"""
        if self.interaction_count >= 6:
            self.relationship_strength = "Very Strong (Regular engagement)"
        elif self.interaction_count >= 3:
            self.relationship_strength = "Strong (6+ interactions)"
        elif self.interaction_count >= 1:
            self.relationship_strength = "Moderate (3-5 interactions)"
        else:
            self.relationship_strength = "Weak (1-2 interactions)"

    def notify_assignment(self):
        """Notify assigned user of contact"""
        if self.owner_user and self.owner_user != frappe.session.user:
            frappe.share.add(
                self.doctype,
                self.name,
                self.owner_user,
                read=1,
                write=1
            )

    def get_full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    def get_interaction_history(self):
        """Get all interactions with this contact"""
        return frappe.get_all(
            "MA Interaction",
            filters={"contact": self.name, "docstatus": 1},
            fields=["name", "interaction_date", "interaction_type", "subject", "notes"],
            order_by="interaction_date desc"
        )

    def get_related_deals(self):
        """Get deals where this person is involved"""
        if not self.company:
            return []
        
        return frappe.get_all(
            "Deal",
            filters={"client": self.company},
            fields=["name", "deal_name", "stage", "value"]
        )

    @frappe.whitelist()
    def create_interaction(self, interaction_type, subject, notes):
        """Create a new interaction record"""
        interaction = frappe.get_doc({
            "doctype": "MA Interaction",
            "contact": self.name,
            "company": self.company,
            "interaction_type": interaction_type,
            "interaction_date": getdate(),
            "subject": subject,
            "notes": notes,
            "attendees": self.email
        })
        interaction.insert()
        
        # Refresh metrics
        self.on_update()
        self.save()
        
        return {"success": True, "interaction": interaction.name}

    @frappe.whitelist()
    def add_to_deal(self, deal_name):
        """Add this contact as a team member to a deal"""
        deal = frappe.get_doc("Deal", deal_name)
        
        # Check if already in team
        for member in deal.advisor_team or []:
            if member.user == self.email:
                return {"success": False, "message": _("Contact already in deal team")}
        
        # Add to team
        deal.append("advisor_team", {
            "user": self.email,
            "full_name": self.get_full_name(),
            "email": self.email,
            "phone": self.mobile or self.phone,
            "role": self.job_title
        })
        deal.save()
        
        return {"success": True, "message": _("Contact added to deal team")}
