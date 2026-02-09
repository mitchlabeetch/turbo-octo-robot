frappe.pages['deal-pipeline'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Pipeline de Transactions M&A',
        single_column: true
    });
    
    new DealPipeline(page);
};

class DealPipeline {
    constructor(page) {
        this.page = page;
        this.make_page();
    }
    
    make_page() {
        this.$container = $('<div class="deal-pipeline-container">').appendTo(this.page.main);
        this.setup_filters();
        this.load_data();
    }
    
    setup_filters() {
        // Add refresh button
        this.page.set_primary_action(__('Actualiser'), () => {
            this.load_data();
        }, 'octicon octicon-sync');
        
        // Add view selector
        this.page.add_menu_item(__('Vue Kanban'), () => {
            this.show_kanban_view();
        });
        
        this.page.add_menu_item(__('Vue Liste'), () => {
            this.show_list_view();
        });
        
        this.page.add_menu_item(__('Vue Analytique'), () => {
            this.show_analytics_view();
        });
        
        // Status filter
        this.page.add_field({
            fieldtype: 'Select',
            fieldname: 'status_filter',
            label: __('Statut'),
            options: ['Tous', 'Actif', 'En Attente', 'Terminé', 'Annulé'],
            default: 'Actif',
            change: () => {
                this.load_data();
            }
        });
    }
    
    load_data() {
        frappe.show_progress(__('Chargement...'), 50, 100, __('Récupération des données'));
        
        frappe.call({
            method: 'ma_advisory.api.get_deal_pipeline_by_stage',
            callback: (r) => {
                frappe.hide_progress();
                if (r.message) {
                    this.pipeline_data = r.message;
                    this.show_kanban_view();
                }
            },
            error: () => {
                frappe.hide_progress();
                frappe.msgprint(__('Erreur lors du chargement des données'));
            }
        });
    }
    
    show_kanban_view() {
        this.$container.empty();
        
        // Add header with totals
        this.add_header();
        
        // Create Kanban board
        const $kanban = $('<div class="kanban-board">').appendTo(this.$container);
        
        const stages = [
            'Origination', 'Mandat Signé', 'Teaser Envoyé', 'NDA Signés',
            'CIM Distribué', 'Offres Indicatives', 'Due Diligence',
            'Offres Finales', 'Négociation', 'Signing', 'Closing'
        ];
        
        stages.forEach(stage => {
            const stage_data = this.pipeline_data[stage] || {deals: [], count: 0, total_value: 0, weighted_value: 0};
            this.add_stage_column($kanban, stage, stage_data);
        });
    }
    
    add_header() {
        const total_deals = Object.values(this.pipeline_data).reduce((sum, stage) => sum + stage.count, 0);
        const total_value = Object.values(this.pipeline_data).reduce((sum, stage) => sum + stage.total_value, 0);
        const total_weighted = Object.values(this.pipeline_data).reduce((sum, stage) => sum + stage.weighted_value, 0);
        
        const $header = $(`
            <div class="pipeline-header">
                <div class="pipeline-stats">
                    <div class="stat-card">
                        <div class="stat-label">Transactions Actives</div>
                        <div class="stat-value">${total_deals}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Valeur Totale</div>
                        <div class="stat-value">${format_currency(total_value, 'EUR')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Valeur Pondérée</div>
                        <div class="stat-value">${format_currency(total_weighted, 'EUR')}</div>
                    </div>
                </div>
            </div>
        `).appendTo(this.$container);
    }
    
    add_stage_column($kanban, stage, stage_data) {
        const $column = $(`
            <div class="kanban-column">
                <div class="kanban-column-header">
                    <h4>${stage}</h4>
                    <div class="stage-stats">
                        <span class="badge">${stage_data.count}</span>
                        <span class="stage-value">${format_currency(stage_data.total_value, 'EUR')}</span>
                    </div>
                </div>
                <div class="kanban-column-cards"></div>
            </div>
        `).appendTo($kanban);
        
        const $cards = $column.find('.kanban-column-cards');
        
        stage_data.deals.forEach(deal => {
            this.add_deal_card($cards, deal);
        });
    }
    
    add_deal_card($container, deal) {
        const prob_color = deal.probability >= 70 ? 'green' : 
                          deal.probability >= 40 ? 'orange' : 'red';
        
        const $card = $(`
            <div class="kanban-card" data-deal="${deal.name}">
                <div class="card-header">
                    <strong>${deal.deal_name}</strong>
                </div>
                <div class="card-body">
                    <div class="card-field">
                        <span class="field-label">Client:</span>
                        <span class="field-value">${deal.client || 'N/A'}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Valeur:</span>
                        <span class="field-value">${format_currency(deal.value, deal.currency)}</span>
                    </div>
                    <div class="card-field">
                        <span class="field-label">Probabilité:</span>
                        <span class="badge badge-${prob_color}">${deal.probability}%</span>
                    </div>
                </div>
            </div>
        `).appendTo($container);
        
        $card.on('click', () => {
            frappe.set_route('Form', 'Deal', deal.name);
        });
    }
    
    show_list_view() {
        this.$container.empty();
        
        // Add header
        this.add_header();
        
        // Create table
        const $table = $(`
            <div class="pipeline-table">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Client</th>
                            <th>Étape</th>
                            <th>Valeur</th>
                            <th>Probabilité</th>
                            <th>Valeur Pondérée</th>
                            <th>Date Clôture</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        `).appendTo(this.$container);
        
        const $tbody = $table.find('tbody');
        
        // Flatten pipeline data
        Object.values(this.pipeline_data).forEach(stage => {
            stage.deals.forEach(deal => {
                const weighted_value = (deal.value * deal.probability) / 100;
                const $row = $(`
                    <tr class="clickable-row" data-deal="${deal.name}">
                        <td>${deal.deal_name}</td>
                        <td>${deal.client || 'N/A'}</td>
                        <td>${deal.stage || 'N/A'}</td>
                        <td>${format_currency(deal.value, deal.currency)}</td>
                        <td><span class="badge">${deal.probability}%</span></td>
                        <td>${format_currency(weighted_value, deal.currency)}</td>
                        <td>${deal.expected_close_date || 'N/A'}</td>
                    </tr>
                `).appendTo($tbody);
                
                $row.on('click', () => {
                    frappe.set_route('Form', 'Deal', deal.name);
                });
            });
        });
    }
    
    show_analytics_view() {
        this.$container.empty();
        
        frappe.call({
            method: 'ma_advisory.api.get_deal_analytics',
            callback: (r) => {
                if (r.message) {
                    this.render_analytics(r.message);
                }
            }
        });
    }
    
    render_analytics(data) {
        const $analytics = $(`
            <div class="analytics-container">
                <h3>Analyse du Pipeline</h3>
                <div class="analytics-grid"></div>
            </div>
        `).appendTo(this.$container);
        
        const $grid = $analytics.find('.analytics-grid');
        
        // Summary cards
        $grid.append(`
            <div class="analytics-card">
                <h4>Vue d'Ensemble</h4>
                <ul>
                    <li>Total Transactions: <strong>${data.total_deals}</strong></li>
                    <li>Actives: <strong>${data.active_deals}</strong></li>
                    <li>Terminées: <strong>${data.completed_deals}</strong></li>
                    <li>Annulées: <strong>${data.cancelled_deals}</strong></li>
                    <li>Valeur Totale: <strong>${format_currency(data.total_value, 'EUR')}</strong></li>
                    <li>Valeur Pondérée: <strong>${format_currency(data.weighted_value, 'EUR')}</strong></li>
                </ul>
            </div>
        `);
        
        // By type
        let type_html = '<div class="analytics-card"><h4>Par Type</h4><ul>';
        for (const [type, stats] of Object.entries(data.by_type)) {
            type_html += `<li>${type}: <strong>${stats.count}</strong> (${format_currency(stats.total_value, 'EUR')})</li>`;
        }
        type_html += '</ul></div>';
        $grid.append(type_html);
        
        // By stage
        let stage_html = '<div class="analytics-card"><h4>Par Étape</h4><ul>';
        for (const [stage, stats] of Object.entries(data.by_stage)) {
            stage_html += `<li>${stage}: <strong>${stats.count}</strong> (${format_currency(stats.total_value, 'EUR')})</li>`;
        }
        stage_html += '</ul></div>';
        $grid.append(stage_html);
    }
}

// Helper function
function format_currency(value, currency) {
    return frappe.format(value, {fieldtype: 'Currency', options: currency || 'EUR'});
}
