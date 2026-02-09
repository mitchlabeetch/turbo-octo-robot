"""Daily scheduled tasks"""

import frappe
from frappe import _
from frappe.utils import today, add_days

def send_deal_pipeline_summary():
    """Send daily deal pipeline summary to relevant users"""
    
    # Get all active deals
    active_deals = frappe.get_all(
        "Deal",
        fields=["name", "deal_name", "stage", "value", "expected_close_date", "owner"],
        filters={
            "status": "Active",
            "expected_close_date": ["<=", add_days(today(), 30)]
        }
    )
    
    if not active_deals:
        return
    
    # Group deals by owner
    deals_by_owner = {}
    for deal in active_deals:
        owner = deal.get("owner")
        if owner not in deals_by_owner:
            deals_by_owner[owner] = []
        deals_by_owner[owner].append(deal)
    
    # Send email to each owner
    for owner, deals in deals_by_owner.items():
        send_pipeline_email(owner, deals)

def send_pipeline_email(user, deals):
    """Send pipeline summary email to user"""
    
    subject = _("Résumé quotidien du pipeline de deals")
    
    # Build email content
    message = _("Bonjour,<br><br>")
    message += _("Voici le résumé de vos deals actifs :<br><br>")
    
    for deal in deals:
        message += f"<b>{deal.get('deal_name')}</b><br>"
        message += f"Étape: {deal.get('stage')}<br>"
        message += f"Valeur: {deal.get('value')}<br>"
        message += f"Date de clôture prévue: {deal.get('expected_close_date')}<br><br>"
    
    # Send email
    frappe.sendmail(
        recipients=[user],
        subject=subject,
        message=message
    )
