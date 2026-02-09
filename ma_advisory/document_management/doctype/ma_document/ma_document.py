"""MA Document DocType - Document management with version control"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime
import os


class MADocument(Document):
    """Document management with version control"""

    def on_update(self):
        """Update version history on save"""
        self.update_file_metadata()
        self.create_version_snapshot()

    def update_file_metadata(self):
        """Update file size and metadata"""
        if self.document_file:
            # Get file size
            file_doc = frappe.get_doc("File", {"file_url": self.document_file})
            if file_doc:
                self.file_size = str(file_doc.file_size)
            
            self.last_modified_by = frappe.session.user
            self.last_modified_date = now_datetime()

    def create_version_snapshot(self):
        """Create version history entry"""
        if not self.document_file:
            return
        
        # Check if new version needed
        version_entry = frappe.get_all(
            "MA Document Version",
            filters={
                "parent": self.name,
                "version_number": self.version,
                "file_url": self.document_file
            }
        )
        
        if not version_entry:
            # Create new version entry
            self.append("version_history", {
                "version_number": self.version,
                "file_url": self.document_file,
                "created_by": frappe.session.user,
                "created_date": now_datetime(),
                "change_notes": "Version created"
            })

    def create_new_version(self, new_file):
        """Create a new version of the document"""
        self.version = (self.version or 1) + 1
        self.document_file = new_file
        self.status = "Draft"
        self.save()
        
        frappe.msgprint(_("New version {0} created").format(self.version))
        return self

    @frappe.whitelist()
    def get_version_history(self):
        """Get complete version history"""
        return frappe.get_all(
            "MA Document Version",
            filters={"parent": self.name},
            fields=["version_number", "file_url", "created_by", "created_date", "change_notes"],
            order_by="created_date desc"
        )

    @frappe.whitelist()
    def restore_version(self, version_number):
        """Restore a previous version"""
        version = frappe.get_value(
            "MA Document Version",
            filters={"parent": self.name, "version_number": version_number},
            fieldname=["file_url", "version_number"]
        )
        
        if version:
            self.version = self.version + 1
            self.document_file = version[0]
            self.status = "Draft"
            self.save()
            return {"success": True, "new_version": self.version}
        
        return {"success": False, "message": _("Version not found")}

    def get_access_users(self):
        """Get users with access to this document"""
        if not self.is_confidential:
            return None  # All users have access
        
        if self.access_restrictions:
            users = self.access_restrictions.split(",")
            return [user.strip() for user in users]
        
        return []
    
    def check_user_access(self, user=None):
        """Check if current user has access to document"""
        user = user or frappe.session.user
        
        if not self.is_confidential:
            return True
        
        allowed_users = self.get_access_users()
        return user in allowed_users or user == self.owner
