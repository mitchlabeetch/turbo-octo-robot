"""API module for M&A Advisory ERP"""

import frappe
from frappe import _

def on_update(doc, method):
    """Hook called on document update"""
    # Add custom logic for document updates
    pass

@frappe.whitelist()
def override_getdoc(doctype, name, user=None):
    """Override getdoc method to add custom logic"""
    # Get the document
    doc = frappe.get_doc(doctype, name)
    
    # Add custom processing for M&A specific doctypes
    if doctype == "Deal":
        # Add calculated fields or additional data
        pass
    
    return doc

@frappe.whitelist()
def get_deal_pipeline():
    """Get deal pipeline data for dashboard"""
    deals = frappe.get_all(
        "Deal",
        fields=["name", "deal_name", "stage", "value", "probability", "expected_close_date"],
        filters={"status": "Active"},
        order_by="expected_close_date asc"
    )
    
    return deals

@frappe.whitelist()
def get_valuation_data(deal_name):
    """Get valuation data for a specific deal"""
    # This would fetch valuation models and calculations
    valuation = frappe.get_all(
        "Valuation",
        fields=["*"],
        filters={"deal": deal_name}
    )
    
    return valuation

@frappe.whitelist()
def get_due_diligence_status(deal_name):
    """Get due diligence checklist status"""
    dd_items = frappe.get_all(
        "Due Diligence Item",
        fields=["category", "status", "assigned_to", "completion_date"],
        filters={"deal": deal_name}
    )
    
    # Group by category
    status_by_category = {}
    for item in dd_items:
        category = item.get("category")
        if category not in status_by_category:
            status_by_category[category] = {
                "total": 0,
                "completed": 0,
                "pending": 0
            }
        
        status_by_category[category]["total"] += 1
        if item.get("status") == "Completed":
            status_by_category[category]["completed"] += 1
        else:
            status_by_category[category]["pending"] += 1
    
    return status_by_category
