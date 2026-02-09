"""MA Target List DocType - Prospecting and target management"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class MATargetList(Document):
    """Target list for prospecting and business development"""

    def on_update(self):
        """Update target statistics"""
        self.update_target_count()
        self.update_engagement_count()

    def update_target_count(self):
        """Update total target count"""
        self.target_count = len(self.targets) if self.targets else 0

    def update_engagement_count(self):
        """Count deals from targets in this list"""
        if not self.targets:
            self.engagement_count = 0
            return
        
        target_companies = [t.company for t in self.targets]
        deals_count = frappe.db.count(
            "Deal",
            filters={"client": ["in", target_companies]}
        )
        self.engagement_count = deals_count

    @frappe.whitelist()
    def add_companies_from_criteria(self):
        """Auto-populate target list based on selection criteria"""
        filters = {}
        
        if self.sector_focus:
            sectors = self.sector_focus.split(",") if isinstance(self.sector_focus, str) else self.sector_focus
            filters["sector"] = ["in", sectors]
        
        if self.revenue_min:
            filters["annual_revenue"] = [">=", self.revenue_min]
        
        if self.revenue_max:
            if "annual_revenue" in filters:
                # Add second condition
                filters["annual_revenue"] = ["between", [self.revenue_min, self.revenue_max]]
            else:
                filters["annual_revenue"] = ["<=", self.revenue_max]
        
        if self.employee_count_min:
            filters["employee_count"] = [">=", self.employee_count_min]
        
        if self.employee_count_max:
            filters["employee_count"] = ["<=", self.employee_count_max]
        
        # Find matching companies
        companies = frappe.get_all(
            "MA Company",
            filters=filters,
            fields=["name", "company_name", "sector", "annual_revenue"]
        )
        
        # Add to targets
        for company in companies:
            # Check if already in list
            existing = [t for t in self.targets if t.company == company["name"]]
            if not existing:
                self.append("targets", {
                    "company": company["name"],
                    "company_name": company["company_name"],
                    "sector": company["sector"],
                    "annual_revenue": company.get("annual_revenue")
                })
        
        self.save()
        return {
            "success": True,
            "companies_added": len(companies),
            "total_targets": self.target_count
        }

    @frappe.whitelist()
    def export_to_csv(self):
        """Export target list to CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["Company", "Sector", "Revenue", "Employees", "Interaction Status"]
        )
        writer.writeheader()
        
        for target in self.targets:
            company = frappe.get_doc("MA Company", target.company)
            interactions = frappe.db.count(
                "MA Interaction",
                filters={"company": target.company}
            )
            
            writer.writerow({
                "Company": company.company_name,
                "Sector": company.sector,
                "Revenue": company.annual_revenue or "",
                "Employees": company.employee_count or "",
                "Interaction Status": f"{interactions} interactions"
            })
        
        return output.getvalue()

    def get_engagement_opportunities(self):
        """Get engagement opportunities from this target list"""
        if not self.targets:
            return []
        
        target_companies = [t.company for t in self.targets]
        
        # Find companies with no interactions
        no_interaction = []
        for company_name in target_companies:
            interactions = frappe.db.count(
                "MA Interaction",
                filters={"company": company_name}
            )
            if interactions == 0:
                co = frappe.get_doc("MA Company", company_name)
                no_interaction.append({
                    "company": company_name,
                    "company_name": co.company_name,
                    "sector": co.sector,
                    "priority": "High"
                })
        
        return no_interaction
