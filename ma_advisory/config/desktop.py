"""Desktop configuration for M&A Advisory ERP"""

from frappe import _

def get_data():
    """Return desktop icons configuration for M&A Advisory"""
    return [
        {
            "module_name": "Gestion des Deals",  # Deal Management in French
            "category": "Modules",
            "label": _("Gestion des Deals"),
            "color": "#3498db",
            "icon": "octicon octicon-briefcase",
            "type": "module",
            "description": _("Gérer le pipeline de deals M&A")
        },
        {
            "module_name": "Clients",
            "category": "Modules",
            "label": _("Clients"),
            "color": "#2ecc71",
            "icon": "octicon octicon-organization",
            "type": "module",
            "description": _("Gestion des clients et sociétés cibles")
        },
        {
            "module_name": "Valorisation",
            "category": "Modules",
            "label": _("Valorisation"),
            "color": "#e74c3c",
            "icon": "octicon octicon-graph",
            "type": "module",
            "description": _("Outils de valorisation et analyse financière")
        },
        {
            "module_name": "Due Diligence",
            "category": "Modules",
            "label": _("Due Diligence"),
            "color": "#f39c12",
            "icon": "octicon octicon-checklist",
            "type": "module",
            "description": _("Suivi et gestion de la due diligence")
        },
        {
            "module_name": "Documents",
            "category": "Modules",
            "label": _("Documents"),
            "color": "#9b59b6",
            "icon": "octicon octicon-file",
            "type": "module",
            "description": _("Gestion documentaire pour transactions M&A")
        }
    ]
