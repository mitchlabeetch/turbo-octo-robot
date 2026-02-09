"""Contact Management API - Relationship intelligence and contact operations"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate
import json


@frappe.whitelist()
def get_relationship_network(contact_name):
    """Get relationship network for a contact - all connections and deals"""
    contact = frappe.get_doc("MA Contact", contact_name)
    
    return {
        "contact": {
            "name": contact_name,
            "full_name": contact.get_full_name(),
            "company": contact.company,
            "job_title": contact.job_title,
            "email": contact.email
        },
        "direct_relationships": get_direct_relationships(contact_name),
        "company_network": get_company_network(contact.company) if contact.company else [],
        "deal_involvement": get_contact_deal_involvement(contact_name),
        "interaction_summary": get_interaction_summary(contact_name)
    }


@frappe.whitelist()
def get_company_intelligence(company_name):
    """Get comprehensive company intelligence including network and deals"""
    company = frappe.get_doc("MA Company", company_name)
    
    return {
        "company": {
            "name": company_name,
            "company_name": company.company_name,
            "company_type": company.company_type,
            "sector": company.sector,
            "annual_revenue": company.annual_revenue,
            "employee_count": company.employee_count,
            "website": company.website
        },
        "contacts": company.get_contacts(),
        "deals": company.get_related_deals(),
        "interactions": company.get_interaction_summary(),
        "key_contacts": get_key_contacts_in_company(company_name),
        "organizational_structure": get_org_structure(company_name),
        "engagement_history": get_company_engagement_history(company_name)
    }


@frappe.whitelist()
def get_key_contacts_in_company(company_name):
    """Get key decision makers and influencers in a company"""
    contacts = frappe.get_all(
        "MA Contact",
        filters={"company": company_name, "decision_maker": 1},
        fields=["name", "first_name", "last_name", "job_title", "email", "interaction_count"],
        order_by="interaction_count desc"
    )
    
    return contacts


@frappe.whitelist()
def get_warm_introduction_paths(from_contact, to_contact):
    """Find warm introduction paths between two contacts"""
    # Get mutual connections
    from_connections = get_contact_connections(from_contact)
    to_connections = get_contact_connections(to_contact)
    
    common_contacts = []
    for conn1 in from_connections:
        for conn2 in to_connections:
            if conn1.name == conn2.name:
                common_contacts.append(conn1)
    
    return {
        "from_contact": from_contact,
        "to_contact": to_contact,
        "mutual_connections": common_contacts,
        "introduction_path_exists": len(common_contacts) > 0
    }


@frappe.whitelist()
def search_contacts(query, filters=None):
    """Search contacts by name, email, company, or job title"""
    filters = filters or {}
    
    # Default search in multiple fields
    contacts = frappe.get_all(
        "MA Contact",
        filters=filters,
        fields=["name", "first_name", "last_name", "email", "job_title", "company"],
        or_filters=[
            ["first_name", "like", f"%{query}%"],
            ["last_name", "like", f"%{query}%"],
            ["email", "like", f"%{query}%"],
            ["job_title", "like", f"%{query}%"]
        ],
        limit_page_length=20
    )
    
    return contacts


@frappe.whitelist()
def search_companies(query, filters=None):
    """Search companies by name, website, or sector"""
    filters = filters or {}
    
    companies = frappe.get_all(
        "MA Company",
        filters=filters,
        fields=["name", "company_name", "sector", "website", "annual_revenue", "employee_count"],
        or_filters=[
            ["company_name", "like", f"%{query}%"],
            ["website", "like", f"%{query}%"],
            ["sector", "like", f"%{query}%"]
        ],
        limit_page_length=20
    )
    
    return companies


@frappe.whitelist()
def get_contact_analytics():
    """Get analytics on contact base"""
    return {
        "total_contacts": frappe.db.count("MA Contact"),
        "total_companies": frappe.db.count("MA Company"),
        "total_interactions": frappe.db.count("MA Interaction"),
        "contacts_by_strength": get_contacts_by_relationship_strength(),
        "contacts_by_company": get_contacts_by_company_distribution(),
        "interaction_types": get_interaction_type_distribution(),
        "average_interaction_frequency": get_avg_interaction_frequency()
    }


@frappe.whitelist()
def create_contact_from_email(email, auto_enrich=True):
    """Create a contact from email address"""
    # Extract name from email if possible
    name_part = email.split("@")[0].replace(".", " ").title()
    
    contact = frappe.get_doc({
        "doctype": "MA Contact",
        "first_name": name_part.split()[0] if len(name_part.split()) > 0 else "Unknown",
        "last_name": name_part.split()[1] if len(name_part.split()) > 1 else "Contact",
        "email": email,
        "owner_user": frappe.session.user
    })
    contact.insert()
    
    if auto_enrich:
        # Attempt to enrich with external data
        enrich_contact_data(contact.name, email)
    
    return {"success": True, "contact": contact.name, "contact_name": contact.get_full_name()}


@frappe.whitelist()
def get_deals_by_contact(contact_name):
    """Get all deals where a contact is involved"""
    contact = frappe.get_doc("MA Contact", contact_name)
    
    if not contact.company:
        return []
    
    # Get deals for company
    deals = frappe.get_all(
        "Deal",
        filters={"client": contact.company},
        fields=["name", "deal_name", "stage", "value", "probability", "expected_close_date"]
    )
    
    return deals


@frappe.whitelist()
def get_origination_prospects():
    """Get high-potential prospects for origination"""
    # Get all companies with no active deals
    companies = frappe.get_all(
        "MA Company",
        filters={
            "relationship_type": "Prospect",
            "company_type": "Target Company"
        },
        fields=["name", "company_name", "sector", "annual_revenue", "interaction_count"],
        order_by="interaction_count desc"
    )
    
    return companies


# Helper functions

def get_direct_relationships(contact_name):
    """Get direct relationships for a contact"""
    contact = frappe.get_doc("MA Contact", contact_name)
    relationships = []
    
    if contact.reporting_to:
        manager = frappe.get_value("MA Contact", contact.reporting_to, ["first_name", "last_name"])
        relationships.append({
            "type": "Reports To",
            "contact": contact.reporting_to,
            "name": f"{manager[0]} {manager[1]}"
        })
    
    return relationships


def get_company_network(company_name):
    """Get network of related companies"""
    company = frappe.get_doc("MA Company", company_name)
    network = {}
    
    if company.parent_company:
        network["parent"] = company.parent_company
    
    if company.subsidiaries:
        network["subsidiaries"] = company.subsidiaries.split(",")
    
    return network


def get_contact_deal_involvement(contact_name):
    """Get deals where contact's company is involved"""
    contact = frappe.get_doc("MA Contact", contact_name)
    
    if not contact.company:
        return []
    
    return frappe.get_all(
        "Deal",
        filters={"client": contact.company},
        fields=["name", "deal_name", "stage", "value"]
    )


def get_interaction_summary(contact_name):
    """Get interaction summary for a contact"""
    interactions = frappe.get_all(
        "MA Interaction",
        filters={"contact": contact_name},
        fields=["interaction_type", "COUNT(*) as count"],
        group_by="interaction_type"
    )
    
    return interactions


def get_contact_connections(contact_name):
    """Get all connections of a contact"""
    contact = frappe.get_doc("MA Contact", contact_name)
    connections = []
    
    if contact.company:
        # Get all contacts in same company
        connections = frappe.get_all(
            "MA Contact",
            filters={"company": contact.company, "name": ["!=", contact_name]},
            fields=["name", "first_name", "last_name", "job_title"]
        )
    
    return connections


def get_org_structure(company_name):
    """Get organizational structure of a company"""
    # Get all contacts and their reporting relationships
    contacts = frappe.get_all(
        "MA Contact",
        filters={"company": company_name},
        fields=["name", "first_name", "last_name", "job_title", "reporting_to"],
        order_by="job_title"
    )
    
    return contacts


def get_company_engagement_history(company_name):
    """Get company engagement history"""
    company = frappe.get_doc("MA Company", company_name)
    
    interactions = frappe.get_all(
        "MA Interaction",
        filters={"company": company_name},
        fields=["interaction_date", "interaction_type", "contact", "subject"],
        order_by="interaction_date desc",
        limit_page_length=20
    )
    
    return interactions


def get_contacts_by_relationship_strength():
    """Get contact distribution by relationship strength"""
    return frappe.db.sql("""
        SELECT relationship_strength, COUNT(*) as count
        FROM `tabMA Contact`
        GROUP BY relationship_strength
    """, as_dict=True)


def get_contacts_by_company_distribution():
    """Get top companies by contact count"""
    return frappe.db.sql("""
        SELECT company, COUNT(*) as contact_count
        FROM `tabMA Contact`
        GROUP BY company
        ORDER BY contact_count DESC
        LIMIT 10
    """, as_dict=True)


def get_interaction_type_distribution():
    """Get distribution of interaction types"""
    return frappe.db.sql("""
        SELECT interaction_type, COUNT(*) as count
        FROM `tabMA Interaction`
        GROUP BY interaction_type
    """, as_dict=True)


def get_avg_interaction_frequency():
    """Get average interactions per contact"""
    total_interactions = frappe.db.count("MA Interaction")
    total_contacts = frappe.db.count("MA Contact")
    
    return total_interactions / total_contacts if total_contacts > 0 else 0


def enrich_contact_data(contact_name, email):
    """Attempt to enrich contact data from external sources"""
    # This would integrate with services like Clearbit, Hunter.io, or LinkedIn
    # Placeholder for future integration
    pass
