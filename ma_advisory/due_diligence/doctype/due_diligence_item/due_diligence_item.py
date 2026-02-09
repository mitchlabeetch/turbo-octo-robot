"""Due Diligence Item DocType controller"""

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate

class DueDiligenceItem(Document):
    """Due Diligence Item for tracking DD checklist"""
    
    def validate(self):
        """Validate due diligence item"""
        self.validate_dates()
        self.validate_documents()
        self.auto_complete_status()
    
    def validate_dates(self):
        """Validate completion and due dates"""
        if self.completion_date and self.due_date:
            if getdate(self.completion_date) < getdate(self.due_date):
                # Completed early - this is good
                pass
        
        # Auto-set completion date when marked as completed
        if self.status == "Terminé" and not self.completion_date:
            self.completion_date = nowdate()
    
    def validate_documents(self):
        """Validate document counts"""
        if self.documents_received > self.documents_required:
            frappe.msgprint(
                "Le nombre de documents reçus dépasse le nombre requis",
                indicator="orange"
            )
    
    def auto_complete_status(self):
        """Auto-update status based on documents"""
        if self.documents_required > 0:
            if self.documents_received == self.documents_required:
                if self.status != "Terminé":
                    self.status = "Terminé"
                    if not self.completion_date:
                        self.completion_date = nowdate()
    
    def on_update(self):
        """Called after saving"""
        # Notify assigned user
        if self.assigned_to and self.has_value_changed("assigned_to"):
            self.notify_assignee()
        
        # Update deal dashboard
        self.update_deal_dashboard()
    
    def notify_assignee(self):
        """Send notification to assigned user"""
        if not self.assigned_to:
            return
        
        message = f"""
        <p>Vous avez été assigné à un élément de due diligence:</p>
        <p><b>{self.item_name}</b></p>
        <p>Catégorie: {self.category}</p>
        <p>Transaction: {self.deal}</p>
        <p>Échéance: {self.due_date or 'Non définie'}</p>
        """
        
        frappe.sendmail(
            recipients=[self.assigned_to],
            subject=f"Assignation DD: {self.item_name}",
            message=message,
            reference_doctype=self.doctype,
            reference_name=self.name
        )
    
    def update_deal_dashboard(self):
        """Update the deal's DD progress"""
        # This will be caught by the deal's dashboard
        frappe.publish_realtime(
            "dd_item_updated",
            {"deal": self.deal, "item": self.name},
            user=frappe.session.user
        )
