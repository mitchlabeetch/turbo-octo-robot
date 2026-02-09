"""Hooks for M&A Advisory ERP"""

from . import __version__ as app_version

app_name = "ma_advisory"
app_title = "M&A Advisory ERP"
app_publisher = "Custom"
app_description = "ERP system for M&A advisory firms based on ERPNext"
app_icon = "octicon octicon-briefcase"
app_color = "blue"
app_email = "contact@example.com"
app_license = "MIT"

# Application setup
# ------------------

# Required apps
required_apps = ["frappe", "erpnext"]

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "*": {
        "on_update": "ma_advisory.api.on_update",
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "ma_advisory.tasks.daily.send_deal_pipeline_summary"
    ],
    "weekly": [
        "ma_advisory.tasks.weekly.generate_activity_report"
    ]
}

# Website
# --------
website_route_rules = [
    {"from_route": "/deals/<path:name>", "to_route": "deals"},
]

# Override standard Frappe/ERPNext methods
# -----------------------------------------
override_whitelisted_methods = {
    "frappe.desk.form.load.getdoc": "ma_advisory.api.override_getdoc"
}

# Default Settings Override
# -------------------------
app_include_js = "/assets/ma_advisory/js/ma_advisory.min.js"
app_include_css = "/assets/ma_advisory/css/ma_advisory.min.css"

# White Label Configuration
# -------------------------
boot_session = "ma_advisory.boot.get_boot_session"

# API Configuration for Headless Mode
# ------------------------------------
# Enable CORS for headless frontend
allow_cors = "*"

# REST API Configuration
# ----------------------
# Override standard API endpoints
override_doctype_dashboards = {
    "Lead": "ma_advisory.dashboards.lead_dashboard",
    "Customer": "ma_advisory.dashboards.client_dashboard"
}

# Translation
# -----------
# Default language set to French
default_language = "fr"

# Additional translations
# Override or extend ERPNext translations with M&A specific terms
app_include_files = [
    "ma_advisory/translations/fr.csv"
]
