"""Document Management API"""

import frappe
from frappe import _


@frappe.whitelist()
def get_deal_documents(deal_name):
    """Get all documents related to a deal"""
    return frappe.get_all(
        "MA Document",
        filters={"deal": deal_name},
        fields=["name", "document_name", "document_type", "version", "status", "created_date"],
        order_by="created_date desc"
    )


@frappe.whitelist()
def search_documents(query, deal_filter=None):
    """Search documents by name and type"""
    filters = {}
    if deal_filter:
        filters["deal"] = deal_filter
    
    return frappe.get_all(
        "MA Document",
        filters=filters,
        or_filters=[
            ["document_name", "like", f"%{query}%"],
            ["description", "like", f"%{query}%"]
        ],
        fields=["name", "document_name", "document_type", "version", "status"],
        limit_page_length=20
    )


@frappe.whitelist()
def get_document_by_type(deal_name, document_type):
    """Get specific document type for a deal"""
    return frappe.get_all(
        "MA Document",
        filters={"deal": deal_name, "document_type": document_type},
        fields=["name", "document_name", "version", "status", "created_date"],
        order_by="version desc",
        limit_page_length=1
    )


@frappe.whitelist()
def create_document_from_template(deal_name, document_type, template_data):
    """Create a document from a template"""
    doc = frappe.get_doc({
        "doctype": "MA Document",
        "document_name": f"{document_type} - {deal_name}",
        "document_type": document_type,
        "deal": deal_name,
        "description": f"Generated from template for {deal_name}"
    })
    doc.insert()
    return {"success": True, "document": doc.name}
