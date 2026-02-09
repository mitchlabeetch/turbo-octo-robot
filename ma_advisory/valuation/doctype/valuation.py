"""Valuation DocType controller"""

import frappe
from frappe.model.document import Document

class Valuation(Document):
    """Valuation document class"""
    
    def validate(self):
        """Validate valuation before saving"""
        self.calculate_values()
    
    def calculate_values(self):
        """Calculate enterprise value and equity value"""
        # Calculate enterprise value using multiples
        if self.ebitda and self.ebitda_multiple:
            self.enterprise_value = self.ebitda * self.ebitda_multiple
        elif self.revenue and self.revenue_multiple:
            self.enterprise_value = self.revenue * self.revenue_multiple
        
        # Calculate equity value
        if self.enterprise_value:
            net_debt = (self.debt or 0) - (self.cash or 0)
            self.equity_value = self.enterprise_value - net_debt
