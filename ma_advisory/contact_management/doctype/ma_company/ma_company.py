"""MA Company DocType - Manages companies for M&A transactions"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


class MACompany(Document):
    """Company document for M&A advisory"""

    def before_insert(self):
        """Set defaults before insert"""
        if not self.created_date:
            self.created_date = getdate()
        if not self.owner_user:
            self.owner_user = frappe.session.user

    def on_update(self):
        """Update related records"""
        self.update_deal_count()
        self.notify_activity_update()

    def update_deal_count(self):
        """Update deal count based on linked deals"""
        if self.linked_deals:
            self.deal_count = len(self.linked_deals)
        else:
            self.deal_count = 0

    def update_last_interaction(self):
        """Update last interaction date"""
        interactions = frappe.get_all(
            "MA Interaction",
            filters={
                "company": self.name,
                "docstatus": 1
            },
            fields=["interaction_date"],
            order_by="interaction_date desc",
            limit_page_length=1
        )
        
        if interactions:
            self.last_interaction_date = interactions[0]["interaction_date"]
        
        interactions_count = frappe.db.count(
            "MA Interaction",
            filters={"company": self.name, "docstatus": 1}
        )
        self.interaction_count = interactions_count

    def notify_activity_update(self):
        """Notify team of company updates"""
        if self.owner_user:
            frappe.share.add(
                self.doctype,
                self.name,
                self.owner_user,
                read=1,
                write=1
            )

    def get_related_deals(self):
        """Get all deals linked to this company"""
        if self.linked_deals:
            deal_names = [row.deal_name for row in self.linked_deals]
            return frappe.get_all(
                "Deal",
                filters={"name": ["in", deal_names]},
                fields=["name", "deal_name", "stage", "value", "probability"]
            )
        return []

    def get_contacts(self):
        """Get all contacts linked to this company"""
        return frappe.get_all(
            "MA Contact",
            filters={"company": self.name},
            fields=["name", "first_name", "last_name", "email", "phone", "job_title"]
        )

    def get_interaction_summary(self):
        """Get summary of interactions"""
        return frappe.get_all(
            "MA Interaction",
            filters={"company": self.name, "docstatus": 1},
            fields=["interaction_type", "COUNT(*) as count"],
            group_by="interaction_type"
        )

    @frappe.whitelist()
    def sync_from_external_database(self, data):
        """Sync company data from external sources (Dealroom, Crunchbase, etc.)"""
        # Update company details from external source
        if data.get("website"):
            self.website = data["website"]
        if data.get("annual_revenue"):
            self.annual_revenue = data["annual_revenue"]
        if data.get("employee_count"):
            self.employee_count = data["employee_count"]
        if data.get("description"):
            self.description = data["description"]
        
        self.save()
        return {"success": True, "message": _("Company data synchronized")}
