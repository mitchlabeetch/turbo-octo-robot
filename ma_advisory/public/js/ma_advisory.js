// M&A Advisory ERP - Custom JavaScript for headless API and white label

(function() {
    'use strict';
    
    // White label initialization
    frappe.ready(function() {
        applyWhiteLabelBranding();
        initializeMAAFeatures();
    });
    
    // Apply white label branding from settings
    function applyWhiteLabelBranding() {
        if (frappe.boot.custom_branding) {
            const branding = frappe.boot.custom_branding;
            
            // Update page title
            if (branding.app_name) {
                document.title = branding.app_name;
            }
            
            // Update logo
            if (branding.app_logo) {
                $('.navbar-brand img').attr('src', branding.app_logo);
            }
            
            // Update favicon
            if (branding.favicon) {
                $('link[rel="icon"]').attr('href', branding.favicon);
            }
            
            // Apply brand color
            if (branding.brand_color) {
                $(':root').css('--ma-primary-color', branding.brand_color);
            }
            
            // Hide Frappe branding if configured
            if (branding.hide_frappe_branding) {
                $('body').addClass('hide-branding');
            }
        }
    }
    
    // Initialize M&A Advisory specific features
    function initializeMAAFeatures() {
        // Deal pipeline visualization
        if (frappe.get_route()[0] === 'List' && frappe.get_route()[1] === 'Deal') {
            addDealPipelineView();
        }
        
        // Valuation calculator
        if (frappe.get_route()[0] === 'Form' && frappe.get_route()[1] === 'Valuation') {
            addValuationCalculator();
        }
        
        // French locale formatting
        setupFrenchFormatting();
    }
    
    // Add pipeline view for deals
    function addDealPipelineView() {
        frappe.call({
            method: 'ma_advisory.api.get_deal_pipeline',
            callback: function(r) {
                if (r.message) {
                    renderDealPipeline(r.message);
                }
            }
        });
    }
    
    // Render deal pipeline
    function renderDealPipeline(deals) {
        // Group deals by stage
        const stages = {};
        deals.forEach(deal => {
            if (!stages[deal.stage]) {
                stages[deal.stage] = [];
            }
            stages[deal.stage].push(deal);
        });
        
        // Render pipeline view
        // This would create a Kanban-style board
        console.log('Deal Pipeline:', stages);
    }
    
    // Add valuation calculator
    function addValuationCalculator() {
        frappe.ui.form.on('Valuation', {
            ebitda: function(frm) {
                calculateValuation(frm);
            },
            ebitda_multiple: function(frm) {
                calculateValuation(frm);
            },
            revenue: function(frm) {
                calculateValuation(frm);
            },
            revenue_multiple: function(frm) {
                calculateValuation(frm);
            },
            debt: function(frm) {
                calculateEquityValue(frm);
            },
            cash: function(frm) {
                calculateEquityValue(frm);
            }
        });
    }
    
    // Calculate valuation
    function calculateValuation(frm) {
        let ev = 0;
        
        if (frm.doc.ebitda && frm.doc.ebitda_multiple) {
            ev = frm.doc.ebitda * frm.doc.ebitda_multiple;
        } else if (frm.doc.revenue && frm.doc.revenue_multiple) {
            ev = frm.doc.revenue * frm.doc.revenue_multiple;
        }
        
        if (ev > 0) {
            frm.set_value('enterprise_value', ev);
            calculateEquityValue(frm);
        }
    }
    
    // Calculate equity value
    function calculateEquityValue(frm) {
        if (frm.doc.enterprise_value) {
            const netDebt = (frm.doc.debt || 0) - (frm.doc.cash || 0);
            const equityValue = frm.doc.enterprise_value - netDebt;
            frm.set_value('equity_value', equityValue);
        }
    }
    
    // Setup French formatting
    function setupFrenchFormatting() {
        // French date format
        frappe.datetime.str_to_user = function(date_str) {
            if (!date_str) return '';
            const date = frappe.datetime.str_to_obj(date_str);
            return date.toLocaleDateString('fr-FR');
        };
        
        // French number format
        frappe.format_number = function(number, format) {
            if (format === undefined) format = frappe.boot.sysdefaults.number_format || '#,###.##';
            return Number(number).toLocaleString('fr-FR');
        };
    }
    
    // API helper for headless frontend integration
    window.MAAApi = {
        // Get deal data
        getDeal: function(dealName) {
            return frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Deal',
                    name: dealName
                }
            });
        },
        
        // Get valuation data
        getValuation: function(dealName) {
            return frappe.call({
                method: 'ma_advisory.api.get_valuation_data',
                args: {
                    deal_name: dealName
                }
            });
        },
        
        // Get due diligence status
        getDueDiligenceStatus: function(dealName) {
            return frappe.call({
                method: 'ma_advisory.api.get_due_diligence_status',
                args: {
                    deal_name: dealName
                }
            });
        }
    };
    
})();
