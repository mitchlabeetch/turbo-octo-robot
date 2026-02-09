"""Deal DocType controller"""

import frappe
from frappe.model.document import Document

class Deal(Document):
    """Deal document class for M&A transactions"""
    
    def validate(self):
        """Validate deal before saving"""
        self.validate_dates()
        self.calculate_probability()
    
    def validate_dates(self):
        """Ensure dates are logical"""
        if self.expected_close_date and self.created_date:
            if self.expected_close_date < self.created_date:
                frappe.throw("La date de clôture prévue ne peut pas être antérieure à la date de création")
    
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
        
        if not self.probability and self.stage:
            self.probability = stage_probability.get(self.stage, 50)
    
    def on_update(self):
        """Called when deal is updated"""
        # Update related documents
        self.update_valuation_status()
    
    def update_valuation_status(self):
        """Update status on related valuation documents"""
        if self.status == "Terminé":
            valuations = frappe.get_all(
                "Valuation",
                filters={"deal": self.name}
            )
            for val in valuations:
                val_doc = frappe.get_doc("Valuation", val.name)
                val_doc.status = "Archivé"
                val_doc.save()
