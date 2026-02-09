"""MA Interaction DocType - Tracks all communications and interactions"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


class MAInteraction(Document):
    """Interaction tracking for M&A advisory"""

    def before_insert(self):
        """Set defaults"""
        if not self.created_date:
            self.created_date = now_datetime()
        if not self.created_by:
            self.created_by = frappe.session.user

    def on_update(self):
        """Update related contact metrics"""
        self.update_contact_metrics()
        self.create_follow_up_task()

    def update_contact_metrics(self):
        """Refresh contact interaction counts"""
        if self.contact:
            contact = frappe.get_doc("MA Contact", self.contact)
            contact.update_interaction_metrics()
            contact.update_relationship_strength()
            contact.save()

    def create_follow_up_task(self):
        """Create task if follow-up required"""
        if self.follow_up_required and self.follow_up_date and not frappe.db.exists(
            "Task",
            {
                "custom_interaction": self.name,
                "status": ["!=", "Completed"]
            }
        ):
            task = frappe.get_doc({
                "doctype": "Task",
                "subject": _("Follow up: {0}").format(self.subject),
                "description": self.follow_up_action,
                "due_date": self.follow_up_date,
                "custom_interaction": self.name
            })
            task.insert()

    @frappe.whitelist()
    def log_email(self, email_subject, email_body):
        """Log an email interaction"""
        self.interaction_type = "Email"
        self.subject = email_subject
        self.notes = email_body
        self.interaction_date = getdate()
        self.save()
        return {"success": True, "interaction": self.name}

    @frappe.whitelist()
    def log_call(self, duration_minutes, call_notes):
        """Log a phone call interaction"""
        self.interaction_type = "Phone Call"
        self.duration_minutes = duration_minutes
        self.notes = call_notes
        self.interaction_date = getdate()
        self.save()
        return {"success": True, "interaction": self.name}

    @frappe.whitelist()
    def log_meeting(self, attendees_list, meeting_notes, duration=None):
        """Log an in-person meeting"""
        self.interaction_type = "In-Person Meeting"
        self.attendees = attendees_list
        self.notes = meeting_notes
        if duration:
            self.duration_minutes = duration
        self.interaction_date = getdate()
        self.save()
        return {"success": True, "interaction": self.name}

    def get_related_interactions(self):
        """Get related interactions for same contact"""
        return frappe.get_all(
            "MA Interaction",
            filters={"contact": self.contact, "name": ["!=", self.name]},
            fields=["name", "interaction_date", "interaction_type", "subject"],
            order_by="interaction_date desc",
            limit_page_length=10
        )
