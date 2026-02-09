"""API module for M&A Advisory ERP"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_days

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
        doc.dd_completion = get_dd_completion_percentage(name)
        doc.days_in_stage = get_days_in_current_stage(doc)
    
    return doc

@frappe.whitelist()
def get_deal_pipeline():
    """Get deal pipeline data for dashboard"""
    deals = frappe.get_all(
        "Deal",
        fields=["name", "deal_name", "stage", "value", "probability", "expected_close_date", "status", "currency"],
        filters={"status": ["in", ["Actif", "En Attente"]]},
        order_by="expected_close_date asc"
    )
    
    # Enrich with additional data
    for deal in deals:
        deal['dd_completion'] = get_dd_completion_percentage(deal['name'])
        deal['weighted_value'] = flt(deal.get('value', 0)) * flt(deal.get('probability', 0)) / 100
    
    return deals

@frappe.whitelist()
def get_deal_pipeline_by_stage():
    """Get pipeline grouped by stage"""
    stages = [
        'Origination', 'Mandat Signé', 'Teaser Envoyé', 'NDA Signés',
        'CIM Distribué', 'Offres Indicatives', 'Due Diligence',
        'Offres Finales', 'Négociation', 'Signing', 'Closing'
    ]
    
    pipeline = {}
    for stage in stages:
        deals = frappe.get_all(
            "Deal",
            fields=["name", "deal_name", "value", "probability", "currency", "client"],
            filters={"stage": stage, "status": ["in", ["Actif", "En Attente"]]},
            order_by="value desc"
        )
        
        total_value = sum([flt(d.get('value', 0)) for d in deals])
        weighted_value = sum([flt(d.get('value', 0)) * flt(d.get('probability', 0)) / 100 for d in deals])
        
        pipeline[stage] = {
            "deals": deals,
            "count": len(deals),
            "total_value": total_value,
            "weighted_value": weighted_value
        }
    
    return pipeline

@frappe.whitelist()
def get_valuation_data(deal_name):
    """Get valuation data for a specific deal"""
    valuations = frappe.get_all(
        "Valuation",
        fields=["name", "valuation_date", "valuation_method", "enterprise_value", 
                "equity_value", "ebitda", "ebitda_multiple", "status"],
        filters={"deal": deal_name},
        order_by="valuation_date desc"
    )
    
    # Calculate statistics
    if valuations:
        ev_values = [v['enterprise_value'] for v in valuations if v.get('enterprise_value')]
        eq_values = [v['equity_value'] for v in valuations if v.get('equity_value')]
        
        stats = {
            "count": len(valuations),
            "avg_enterprise_value": sum(ev_values) / len(ev_values) if ev_values else 0,
            "avg_equity_value": sum(eq_values) / len(eq_values) if eq_values else 0,
            "min_enterprise_value": min(ev_values) if ev_values else 0,
            "max_enterprise_value": max(ev_values) if ev_values else 0
        }
    else:
        stats = {}
    
    return {
        "valuations": valuations,
        "statistics": stats
    }

@frappe.whitelist()
def get_due_diligence_status(deal_name):
    """Get due diligence checklist status"""
    dd_items = frappe.get_all(
        "Due Diligence Item",
        fields=["category", "status", "assigned_to", "completion_date", "priority", "due_date"],
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
                "in_progress": 0,
                "pending": 0,
                "blocked": 0,
                "overdue": 0
            }
        
        status_by_category[category]["total"] += 1
        
        if item.get("status") == "Terminé":
            status_by_category[category]["completed"] += 1
        elif item.get("status") == "En Cours":
            status_by_category[category]["in_progress"] += 1
        elif item.get("status") == "Bloqué":
            status_by_category[category]["blocked"] += 1
        else:
            status_by_category[category]["pending"] += 1
        
        # Check if overdue
        if item.get("due_date") and item.get("status") != "Terminé":
            if getdate(item["due_date"]) < getdate(nowdate()):
                status_by_category[category]["overdue"] += 1
    
    # Calculate completion percentage per category
    for category, stats in status_by_category.items():
        if stats["total"] > 0:
            stats["completion_percentage"] = (stats["completed"] / stats["total"]) * 100
        else:
            stats["completion_percentage"] = 0
    
    return status_by_category

@frappe.whitelist()
def get_deal_analytics(deal_name=None):
    """Get comprehensive analytics for deals"""
    filters = {}
    if deal_name:
        filters["name"] = deal_name
    
    deals = frappe.get_all(
        "Deal",
        fields=["name", "deal_type", "stage", "status", "value", "probability", 
                "created_date", "expected_close_date", "closing_date", "currency"],
        filters=filters
    )
    
    analytics = {
        "total_deals": len(deals),
        "active_deals": len([d for d in deals if d['status'] == 'Actif']),
        "completed_deals": len([d for d in deals if d['status'] == 'Terminé']),
        "cancelled_deals": len([d for d in deals if d['status'] == 'Annulé']),
        "total_value": sum([flt(d['value']) for d in deals]),
        "weighted_value": sum([flt(d['value']) * flt(d['probability']) / 100 for d in deals]),
        "by_type": {},
        "by_stage": {},
        "by_status": {}
    }
    
    # Group by type
    for deal in deals:
        deal_type = deal['deal_type']
        if deal_type not in analytics["by_type"]:
            analytics["by_type"][deal_type] = {"count": 0, "total_value": 0}
        analytics["by_type"][deal_type]["count"] += 1
        analytics["by_type"][deal_type]["total_value"] += flt(deal['value'])
    
    # Group by stage
    for deal in deals:
        stage = deal['stage']
        if stage not in analytics["by_stage"]:
            analytics["by_stage"][stage] = {"count": 0, "total_value": 0}
        analytics["by_stage"][stage]["count"] += 1
        analytics["by_stage"][stage]["total_value"] += flt(deal['value'])
    
    # Group by status
    for deal in deals:
        status = deal['status']
        if status not in analytics["by_status"]:
            analytics["by_status"][status] = {"count": 0, "total_value": 0}
        analytics["by_status"][status]["count"] += 1
        analytics["by_status"][status]["total_value"] += flt(deal['value'])
    
    return analytics

@frappe.whitelist()
def create_dd_checklist_from_template(deal_name, template_name="Standard"):
    """Create DD checklist from template"""
    if frappe.db.exists("Due Diligence Item", {"deal": deal_name}):
        frappe.throw(_("Des éléments de due diligence existent déjà pour cette transaction"))
    
    # Get template
    templates = get_dd_templates()
    template = templates.get(template_name, templates["Standard"])
    
    created_items = []
    for category, items in template.items():
        for item_data in items:
            dd_item = frappe.get_doc({
                "doctype": "Due Diligence Item",
                "deal": deal_name,
                "category": category,
                "item_name": item_data["name"],
                "priority": item_data.get("priority", "Moyenne"),
                "documents_required": item_data.get("documents", 0),
                "status": "À Faire"
            })
            dd_item.insert(ignore_permissions=True)
            created_items.append(dd_item.name)
    
    frappe.db.commit()
    
    return {
        "success": True,
        "message": _("{0} éléments de DD créés").format(len(created_items)),
        "items": created_items
    }

def get_dd_templates():
    """Return DD checklist templates"""
    return {
        "Standard": {
            "Financière": [
                {"name": "États financiers 3 dernières années", "priority": "Haute", "documents": 3},
                {"name": "Liasse fiscale", "priority": "Haute", "documents": 1},
                {"name": "Budget et prévisions", "priority": "Moyenne", "documents": 1},
                {"name": "Dette et engagements financiers", "priority": "Haute", "documents": 1},
                {"name": "Analyse du BFR", "priority": "Moyenne", "documents": 1},
                {"name": "Comptes de résultat détaillés", "priority": "Moyenne", "documents": 3}
            ],
            "Juridique": [
                {"name": "Statuts et K-bis", "priority": "Critique", "documents": 1},
                {"name": "Pacte d'actionnaires", "priority": "Haute", "documents": 1},
                {"name": "Contrats principaux", "priority": "Haute", "documents": 5},
                {"name": "Litiges en cours", "priority": "Haute", "documents": 1},
                {"name": "Propriété intellectuelle", "priority": "Moyenne", "documents": 1},
                {"name": "Conformité réglementaire", "priority": "Haute", "documents": 1}
            ],
            "Commerciale": [
                {"name": "Liste des clients principaux", "priority": "Haute", "documents": 1},
                {"name": "Contrats commerciaux", "priority": "Moyenne", "documents": 3},
                {"name": "Pipeline commercial", "priority": "Moyenne", "documents": 1},
                {"name": "Analyse de la concurrence", "priority": "Basse", "documents": 1}
            ],
            "Sociale/RH": [
                {"name": "Organigramme", "priority": "Moyenne", "documents": 1},
                {"name": "Contrats de travail clés", "priority": "Haute", "documents": 3},
                {"name": "Convention collective", "priority": "Moyenne", "documents": 1},
                {"name": "Litiges prud'homaux", "priority": "Haute", "documents": 1}
            ],
            "Fiscale": [
                {"name": "Déclarations fiscales 3 ans", "priority": "Haute", "documents": 3},
                {"name": "Contrôles fiscaux", "priority": "Haute", "documents": 1},
                {"name": "Déficits reportables", "priority": "Moyenne", "documents": 1}
            ]
        }
    }

def get_dd_completion_percentage(deal_name):
    """Calculate DD completion percentage"""
    total = frappe.db.count("Due Diligence Item", {"deal": deal_name})
    if total == 0:
        return 0
    
    completed = frappe.db.count("Due Diligence Item", {"deal": deal_name, "status": "Terminé"})
    return (completed / total) * 100

def get_days_in_current_stage(deal_doc):
    """Calculate days in current stage"""
    # Get last stage change from comments
    last_change = frappe.db.sql("""
        SELECT creation FROM `tabComment`
        WHERE reference_doctype = 'Deal'
        AND reference_name = %(deal)s
        AND content LIKE '%%Étape%%'
        ORDER BY creation DESC LIMIT 1
    """, {"deal": deal_doc.name}, as_dict=True)
    
    if last_change:
        from frappe.utils import date_diff
        return date_diff(nowdate(), getdate(last_change[0]['creation']))
    else:
        # Use creation date if no stage changes
        from frappe.utils import date_diff
        return date_diff(nowdate(), getdate(deal_doc.created_date or deal_doc.creation))

@frappe.whitelist()
def export_deal_report(deal_name):
    """Export comprehensive deal report"""
    deal = frappe.get_doc("Deal", deal_name)
    
    # Get related data
    valuations = get_valuation_data(deal_name)
    dd_status = get_due_diligence_status(deal_name)
    
    report_data = {
        "deal": deal.as_dict(),
        "valuations": valuations,
        "due_diligence": dd_status,
        "team": [member.as_dict() for member in deal.advisor_team] if deal.advisor_team else []
    }
    
    return report_data
