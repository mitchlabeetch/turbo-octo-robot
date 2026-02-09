"""Lead dashboard configuration for M&A advisory context"""

from frappe import _

def lead_dashboard():
    """Customize lead dashboard for M&A advisory"""
    return {
        "fieldname": "lead",
        "transactions": [
            {
                "label": _("Opportunités"),
                "items": ["Deal", "Mandate"]
            },
            {
                "label": _("Communications"),
                "items": ["Email", "Call Log", "Meeting"]
            },
            {
                "label": _("Documents"),
                "items": ["NDA", "Teaser"]
            }
        ]
    }
