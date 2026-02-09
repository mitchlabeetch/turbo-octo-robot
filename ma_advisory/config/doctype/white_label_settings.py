"""White Label Settings DocType controller"""

import frappe
from frappe.model.document import Document

class WhiteLabelSettings(Document):
    """White Label Settings for customizing the application branding"""
    
    def validate(self):
        """Validate settings before saving"""
        pass
    
    def on_update(self):
        """Apply white label settings when updated"""
        self.clear_cache()
    
    def clear_cache(self):
        """Clear cache to apply new settings"""
        frappe.clear_cache()
