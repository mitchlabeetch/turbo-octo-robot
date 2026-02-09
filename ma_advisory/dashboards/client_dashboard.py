"""Client dashboard configuration"""

from frappe import _

def client_dashboard():
    """Customize client dashboard for M&A advisory"""
    return {
        "fieldname": "client",
        "transactions": [
            {
                "label": _("Transactions"),
                "items": ["Deal", "Mandate", "Valuation"]
            },
            {
                "label": _("Due Diligence"),
                "items": ["Due Diligence Item", "DD Report"]
            },
            {
                "label": _("Documents"),
                "items": ["CIM", "Term Sheet", "SPA"]
            },
            {
                "label": _("Facturation"),
                "items": ["Invoice", "Payment"]
            }
        ]
    }
