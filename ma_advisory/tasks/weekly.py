"""Weekly scheduled tasks"""

import frappe
from frappe import _
from frappe.utils import get_first_day_of_week, get_last_day_of_week

def generate_activity_report():
    """Generate weekly activity report"""
    
    week_start = get_first_day_of_week()
    week_end = get_last_day_of_week()
    
    # Get deals created this week
    new_deals = frappe.get_all(
        "Deal",
        filters={
            "creation": ["between", [week_start, week_end]]
        }
    )
    
    # Get deals closed this week
    closed_deals = frappe.get_all(
        "Deal",
        filters={
            "status": "Completed",
            "closing_date": ["between", [week_start, week_end]]
        }
    )
    
    # Generate report
    report_data = {
        "period": f"{week_start} - {week_end}",
        "new_deals": len(new_deals),
        "closed_deals": len(closed_deals)
    }
    
    # Send to management
    send_activity_report(report_data)

def send_activity_report(report_data):
    """Send weekly activity report to management"""
    
    # Get users with Manager role
    managers = frappe.get_all(
        "Has Role",
        fields=["parent"],
        filters={"role": "M&A Manager", "parenttype": "User"}
    )
    
    if not managers:
        return
    
    recipients = [m.get("parent") for m in managers]
    
    subject = _("Rapport d'activité hebdomadaire M&A")
    message = f"""
    <h3>Rapport d'activité hebdomadaire</h3>
    <p>Période: {report_data.get('period')}</p>
    <ul>
        <li>Nouveaux deals: {report_data.get('new_deals')}</li>
        <li>Deals clôturés: {report_data.get('closed_deals')}</li>
    </ul>
    """
    
    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message
    )
