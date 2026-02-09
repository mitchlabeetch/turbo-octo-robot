"""Relationship Intelligence Features - Network Mapping and Analysis"""

import frappe
from frappe import _
from frappe.utils import getdate


@frappe.whitelist()
def build_relationship_graph(center_contact=None, depth=2):
    """Build a relationship graph showing connections"""
    if not center_contact:
        center_contact = frappe.session.user
    
    graph = {
        "nodes": [],
        "edges": [],
        "center": center_contact
    }
    
    # Add center contact
    contact = frappe.get_doc("MA Contact", center_contact)
    graph["nodes"].append({
        "id": contact.name,
        "label": contact.get_full_name(),
        "type": "contact",
        "job_title": contact.job_title,
        "company": contact.company,
        "relationship_strength": contact.relationship_strength
    })
    
    # Get direct connections (people in same company)
    if contact.company:
        company_contacts = frappe.get_all(
            "MA Contact",
            filters={"company": contact.company, "name": ["!=", center_contact]},
            fields=["name", "first_name", "last_name", "job_title", "relationship_strength"]
        )
        
        for cc in company_contacts:
            # Add node
            graph["nodes"].append({
                "id": cc.name,
                "label": f"{cc.first_name} {cc.last_name}",
                "type": "contact",
                "job_title": cc.job_title,
                "company": contact.company,
                "relationship_strength": cc.relationship_strength
            })
            
            # Add edge
            graph["edges"].append({
                "from": center_contact,
                "to": cc.name,
                "relationship": "Works at same company"
            })
    
    # Add company node
    if contact.company:
        graph["nodes"].append({
            "id": contact.company,
            "label": contact.company,
            "type": "company"
        })
        graph["edges"].append({
            "from": center_contact,
            "to": contact.company,
            "relationship": "Works at"
        })
    
    return graph


@frappe.whitelist()
def get_network_influence_score(contact_name):
    """Calculate influence score based on connections and interactions"""
    contact = frappe.get_doc("MA Contact", contact_name)
    
    score = 0
    
    # Base score from decision maker status
    if contact.decision_maker:
        score += 50
    
    # Bonus for influence level
    influence_bonuses = {
        "Executive": 40,
        "DepartmentHead": 30,
        "Key Influencer": 25,
        "Supporter": 10
    }
    score += influence_bonuses.get(contact.decision_influence, 0)
    
    # Bonus for interactions
    score += min(contact.interaction_count * 5, 100)
    
    # Bonus for role in deals
    deals = frappe.get_all(
        "Deal",
        filters={"client": contact.company},
        fields=["name"]
    )
    score += len(deals) * 10
    
    return {
        "contact": contact_name,
        "influence_score": min(score, 500),  # Normalize to 500
        "decision_maker": contact.decision_maker,
        "interaction_count": contact.interaction_count,
        "related_deals": len(deals)
    }


@frappe.whitelist()
def identify_relationship_gaps(company_name):
    """Identify missing relationships or key contacts not yet engaged"""
    company = frappe.get_doc("MA Company", company_name)
    
    # Get our known contacts
    known_contacts = frappe.get_all(
        "MA Contact",
        filters={"company": company_name},
        fields=["first_name", "last_name", "job_title", "decision_influence"]
    )
    
    # Get their interaction frequency
    contact_interactions = frappe.db.sql("""
        SELECT c.name, COUNT(mi.name) as interaction_count
        FROM `tabMA Contact` c
        LEFT JOIN `tabMA Interaction` mi ON c.name = mi.contact
        WHERE c.company = %s
        GROUP BY c.name
    """, (company_name,), as_dict=True)
    
    # Identify gaps
    gaps = []
    
    # Check for decision makers without interaction
    decision_makers = [c for c in known_contacts if c.decision_influence == "Executive"]
    engaged = [c["name"] for c in contact_interactions if c["interaction_count"] > 0]
    
    for dm in decision_makers:
        if dm["first_name"] not in [e.split("-")[0] for e in engaged]:
            gaps.append({
                "type": "Unengaged Executive",
                "contact": f"{dm['first_name']} {dm['last_name']}",
                "role": dm["job_title"],
                "priority": "High"
            })
    
    return {
        "company": company_name,
        "total_contacts": len(known_contacts),
        "identified_gaps": gaps,
        "recommendation": "Consider reaching out to identified unengaged executives"
    }


@frappe.whitelist()
def get_contact_timeline(contact_name):
    """Get complete timeline of interactions with a contact"""
    interactions = frappe.get_all(
        "MA Interaction",
        filters={"contact": contact_name},
        fields=["name", "interaction_date", "interaction_type", "subject", "outcome"],
        order_by="interaction_date desc"
    )
    
    # Add deals context
    contact = frappe.get_doc("MA Contact", contact_name)
    deals = frappe.get_all(
        "Deal",
        filters={"client": contact.company},
        fields=["name", "deal_name", "created_date", "stage"]
    ) if contact.company else []
    
    timeline = []
    
    # Merge interactions and deals
    for i in interactions:
        timeline.append({
            "type": "interaction",
            "date": i.interaction_date,
            "description": i.subject,
            "details": i
        })
    
    for d in deals:
        timeline.append({
            "type": "deal",
            "date": d.created_date,
            "description": f"Deal: {d.deal_name}",
            "details": d
        })
    
    # Sort by date descending
    timeline.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "contact": contact_name,
        "timeline": timeline,
        "total_events": len(timeline)
    }


@frappe.whitelist()
def map_buyer_seller_networks(deal_name):
    """Map buyer and seller networks for a deal"""
    deal = frappe.get_doc("Deal", deal_name)
    
    networks = {
        "seller_network": {
            "company": deal.client,
            "contacts": [],
            "deals_count": 0
        },
        "buyer_interested": {
            "companies": [],
            "contacts": [],
            "deals_count": 0
        }
    }
    
    # Get seller company contacts
    if deal.client:
        seller_contacts = frappe.get_all(
            "MA Contact",
            filters={"company": deal.client},
            fields=["name", "first_name", "last_name", "job_title", "interaction_count"]
        )
        networks["seller_network"]["contacts"] = seller_contacts
    
    # Get buyer networks (from deal team)
    if deal.advisor_team:
        buyer_contacts = []
        for member in deal.advisor_team:
            if member.get("email"):
                buyer_contacts.append({
                    "name": member.get("user"),
                    "full_name": member.get("full_name"),
                    "email": member.get("email"),
                    "role": member.get("role")
                })
        networks["buyer_interested"]["contacts"] = buyer_contacts
    
    return networks
