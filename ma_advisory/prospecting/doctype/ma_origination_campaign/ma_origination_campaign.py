"""MA Origination Campaign DocType"""

import frappe
from frappe.model.document import Document


class MAOriginationCampaign(Document):
    """Campaign tracking for origination and business development"""
    
    def on_update(self):
        """Update campaign statistics"""
        self.calculate_campaign_metrics()

    def calculate_campaign_metrics(self):
        """Calculate outreach metrics"""
        if not self.target_list:
            return
        
        target_list = frappe.get_doc("MA Target List", self.target_list)
        contacts_reached = 0
        deals_count = 0
        
        for target in target_list.targets:
            interactions = frappe.db.count(
                "MA Interaction",
                filters={"company": target.company}
            )
            if interactions > 0:
                contacts_reached += 1
            
            deals = frappe.db.count(
                "Deal",
                filters={"client": target.company}
            )
            deals_count += deals
        
        self.outreach_activities = frappe.db.count(
            "MA Interaction",
            filters={"company": ["in", [t.company for t in target_list.targets]]}
        )
        self.contacts_reached = contacts_reached
        self.deals_generated = deals_count
        
        if self.contacts_reached > 0:
            self.success_rate = (self.deals_generated / self.contacts_reached) * 100
