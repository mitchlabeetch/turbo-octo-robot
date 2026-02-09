"""Prospecting & Origination APIs"""

import frappe
from frappe import _


@frappe.whitelist()
def build_target_list(sector=None, min_revenue=None, max_revenue=None, min_employees=None, max_employees=None):
    """Build a target list based on criteria"""
    filters = {"company_type": "Target Company"}
    
    if sector:
        filters["sector"] = sector
    if min_revenue:
        filters["annual_revenue"] = [">=", min_revenue]
    if max_revenue:
        if "annual_revenue" in filters:
            filters["annual_revenue"] = ["between", [min_revenue, max_revenue]]
        else:
            filters["annual_revenue"] = ["<=", max_revenue]
    if min_employees:
        filters["employee_count"] = [">=", min_employees]
    if max_employees:
        filters["employee_count"] = ["<=", max_employees]
    
    companies = frappe.get_all(
        "MA Company",
        filters=filters,
        fields=["name", "company_name", "sector", "annual_revenue", "employee_count"],
        limit_page_length=100
    )
    
    return {
        "companies": companies,
        "total_count": len(companies)
    }


@frappe.whitelist()
def get_campaign_performance(campaign_name):
    """Get performance metrics for a campaign"""
    campaign = frappe.get_doc("MA Origination Campaign", campaign_name)
    
    return {
        "campaign": campaign_name,
        "campaign_type": campaign.campaign_type,
        "status": campaign.status,
        "outreach_activities": campaign.outreach_activities,
        "contacts_reached": campaign.contacts_reached,
        "deals_generated": campaign.deals_generated,
        "success_rate": campaign.success_rate
    }


@frappe.whitelist()
def get_prospect_recommendations():
    """Get recommended prospects for outreach"""
    # Companies with no interactions that meet typical deal criteria
    high_potential = frappe.db.sql("""
        SELECT m.name, m.company_name, m.sector, m.annual_revenue,
               COUNT(d.name) as deal_count,
               COUNT(i.name) as interaction_count
        FROM `tabMA Company` m
        LEFT JOIN `tabDeal` d ON m.name = d.client
        LEFT JOIN `tabMA Interaction` i ON m.name = i.company
        WHERE m.company_type = 'Target Company'
        AND m.relationship_type = 'Prospect'
        AND m.annual_revenue >= 10000000
        AND (i.name IS NULL OR i.name = '')
        GROUP BY m.name
        ORDER BY m.annual_revenue DESC
        LIMIT 20
    """, as_dict=True)
    
    return high_potential


@frappe.whitelist()
def get_outreach_next_steps(campaign_name):
    """Get recommended next outreach steps"""
    campaign = frappe.get_doc("MA Origination Campaign", campaign_name)
    
    if not campaign.target_list:
        return {"error": "No target list assigned"}
    
    target_list = frappe.get_doc("MA Target List", campaign.target_list)
    
    no_contact_targets = []
    for target in target_list.targets:
        if not target.engagement_status or target.engagement_status == "Not Started":
            interactions = frappe.db.count(
                "MA Interaction",
                filters={"company": target.company}
            )
            if interactions == 0:
                co = frappe.get_doc("MA Company", target.company)
                no_contact_targets.append({
                    "company": target.company,
                    "company_name": co.company_name,
                    "key_contacts": frappe.get_all(
                        "MA Contact",
                        filters={"company": target.company, "decision_maker": 1},
                        fields=["name", "first_name", "last_name", "email"],
                        limit_page_length=3
                    )
                })
    
    return {
        "campaign": campaign_name,
        "uncontacted_targets": no_contact_targets,
        "recommended_action": "Initiate outreach to key contacts in these companies"
    }
