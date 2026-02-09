"""Boot session configuration for white label support"""

import frappe

def get_boot_session(bootinfo):
    """
    Customize boot session for white label configuration
    This allows dynamic branding based on configuration
    """
    
    # Get white label settings
    settings = frappe.get_single("White Label Settings")
    
    if settings:
        # Override branding
        bootinfo.custom_branding = {
            "app_name": settings.get("app_name") or "M&A Advisory ERP",
            "app_logo": settings.get("app_logo_url"),
            "favicon": settings.get("favicon_url"),
            "brand_color": settings.get("brand_color") or "#3498db",
            "login_background": settings.get("login_background_url"),
            "hide_frappe_branding": settings.get("hide_frappe_branding", 1)
        }
        
        # Override system settings
        bootinfo.sysdefaults.country = settings.get("default_country") or "France"
        bootinfo.sysdefaults.currency = settings.get("default_currency") or "EUR"
        bootinfo.sysdefaults.language = settings.get("default_language") or "fr"
        
    # Add M&A Advisory specific boot data
    bootinfo.ma_advisory = {
        "version": "1.0.0",
        "modules": ["Gestion des Deals", "Clients", "Valorisation", "Due Diligence", "Documents"]
    }
    
    return bootinfo
