// Deal Form Script - Enhanced UX and functionality

frappe.ui.form.on('Deal', {
    refresh: function(frm) {
        // Add custom buttons
        add_custom_buttons(frm);
        
        // Setup dashboard
        setup_dashboard(frm);
        
        // Add indicators
        add_status_indicators(frm);
        
        // Setup real-time updates
        setup_realtime_updates(frm);
    },
    
    stage: function(frm) {
        // Auto-update probability when stage changes
        update_probability_from_stage(frm);
    },
    
    status: function(frm) {
        // Handle status changes
        handle_status_change(frm);
    },
    
    client: function(frm) {
        // Fetch client details
        if (frm.doc.client) {
            fetch_client_details(frm);
        }
    },
    
    deal_type: function(frm) {
        // Suggest default values based on deal type
        suggest_deal_defaults(frm);
    },
    
    onload: function(frm) {
        // Set query filters
        setup_query_filters(frm);
    }
});

function add_custom_buttons(frm) {
    if (frm.doc.__islocal) return;
    
    // Add "Create Valuation" button
    frm.add_custom_button(__('Créer Valorisation'), function() {
        frappe.new_doc('Valuation', {
            deal: frm.doc.name,
            company_name: frm.doc.target_company
        });
    }, __('Créer'));
    
    // Add "Create DD Item" button
    frm.add_custom_button(__('Créer Item DD'), function() {
        frappe.new_doc('Due Diligence Item', {
            deal: frm.doc.name
        });
    }, __('Créer'));
    
    // Add "View Project" button
    if (frm.doc.status !== 'Annulé') {
        frm.add_custom_button(__('Voir Projet'), function() {
            frappe.db.get_value('Project', {deal: frm.doc.name}, 'name', function(r) {
                if (r && r.name) {
                    frappe.set_route('Form', 'Project', r.name);
                } else {
                    frappe.msgprint(__('Aucun projet lié trouvé'));
                }
            });
        });
    }
    
    // Add "Send Update" button
    frm.add_custom_button(__('Envoyer Mise à Jour'), function() {
        send_deal_update(frm);
    });
    
    // Add stage progression buttons
    if (frm.doc.status === 'Actif') {
        add_stage_buttons(frm);
    }
}

function add_stage_buttons(frm) {
    const stages = [
        'Origination', 'Mandat Signé', 'Teaser Envoyé', 'NDA Signés',
        'CIM Distribué', 'Offres Indicatives', 'Due Diligence',
        'Offres Finales', 'Négociation', 'Signing', 'Closing'
    ];
    
    const current_index = stages.indexOf(frm.doc.stage);
    
    if (current_index < stages.length - 1) {
        const next_stage = stages[current_index + 1];
        frm.add_custom_button(__('Avancer à: {0}', [next_stage]), function() {
            frm.set_value('stage', next_stage);
            frm.save();
        }, __('Pipeline'));
    }
}

function setup_dashboard(frm) {
    if (frm.doc.__islocal) return;
    
    // Create dashboard section
    frm.dashboard.reset();
    
    // Add pipeline progress
    add_pipeline_progress(frm);
    
    // Add key metrics
    add_key_metrics(frm);
    
    // Add DD progress
    add_dd_progress(frm);
}

function add_pipeline_progress(frm) {
    const stages = [
        'Origination', 'Mandat Signé', 'Teaser Envoyé', 'NDA Signés',
        'CIM Distribué', 'Offres Indicatives', 'Due Diligence',
        'Offres Finales', 'Négociation', 'Signing', 'Closing'
    ];
    
    const current_index = stages.indexOf(frm.doc.stage);
    const progress = ((current_index + 1) / stages.length) * 100;
    
    frm.dashboard.add_progress(__('Pipeline Progress'), progress);
}

function add_key_metrics(frm) {
    // Add transaction value
    if (frm.doc.value) {
        frm.dashboard.add_indicator(
            __('Valeur: {0}', [format_currency(frm.doc.value, frm.doc.currency)]),
            'blue'
        );
    }
    
    // Add probability
    if (frm.doc.probability) {
        const color = frm.doc.probability >= 70 ? 'green' : 
                     frm.doc.probability >= 40 ? 'orange' : 'red';
        frm.dashboard.add_indicator(
            __('Probabilité: {0}%', [frm.doc.probability]),
            color
        );
    }
    
    // Add days until close
    if (frm.doc.expected_close_date) {
        const days = frappe.datetime.get_day_diff(frm.doc.expected_close_date, frappe.datetime.nowdate());
        const color = days < 30 ? 'orange' : 'blue';
        frm.dashboard.add_indicator(
            __('Jours restants: {0}', [days]),
            color
        );
    }
}

function add_dd_progress(frm) {
    frappe.call({
        method: 'ma_advisory.api.get_due_diligence_status',
        args: {
            deal_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                let total = 0, completed = 0;
                Object.values(r.message).forEach(cat => {
                    total += cat.total;
                    completed += cat.completed;
                });
                
                if (total > 0) {
                    const progress = (completed / total) * 100;
                    frm.dashboard.add_progress(__('Due Diligence'), progress);
                }
            }
        }
    });
}

function add_status_indicators(frm) {
    // Color-code status
    const status_colors = {
        'Actif': 'green',
        'En Attente': 'orange',
        'Terminé': 'blue',
        'Annulé': 'red'
    };
    
    if (frm.doc.status) {
        frm.set_indicator_formatter('status',
            function(doc) {
                return status_colors[doc.status] || 'gray';
            }
        );
    }
}

function setup_realtime_updates(frm) {
    if (frm.doc.__islocal) return;
    
    // Listen for DD updates
    frappe.realtime.on('dd_item_updated', function(data) {
        if (data.deal === frm.doc.name) {
            // Refresh DD progress
            add_dd_progress(frm);
            frappe.show_alert({
                message: __('Due diligence mise à jour'),
                indicator: 'green'
            });
        }
    });
}

function update_probability_from_stage(frm) {
    const stage_probability = {
        'Origination': 10,
        'Mandat Signé': 20,
        'Teaser Envoyé': 30,
        'NDA Signés': 40,
        'CIM Distribué': 50,
        'Offres Indicatives': 60,
        'Due Diligence': 70,
        'Offres Finales': 80,
        'Négociation': 85,
        'Signing': 95,
        'Closing': 100
    };
    
    if (frm.doc.stage) {
        const suggested_prob = stage_probability[frm.doc.stage];
        if (suggested_prob) {
            frappe.msgprint({
                title: __('Probabilité suggérée'),
                message: __('Probabilité suggérée pour cette étape: {0}%', [suggested_prob]),
                primary_action: {
                    label: __('Appliquer'),
                    action: function() {
                        frm.set_value('probability', suggested_prob);
                    }
                }
            });
        }
    }
}

function handle_status_change(frm) {
    if (frm.doc.status === 'Terminé' && !frm.doc.closing_date) {
        frm.set_value('closing_date', frappe.datetime.nowdate());
    }
    
    if (frm.doc.status === 'Terminé' && frm.doc.stage !== 'Closing') {
        frm.set_value('stage', 'Closing');
        frm.set_value('probability', 100);
    }
}

function fetch_client_details(frm) {
    frappe.db.get_doc('Customer', frm.doc.client)
        .then(customer => {
            if (customer.customer_group) {
                frappe.show_alert({
                    message: __('Client: {0}', [customer.customer_name]),
                    indicator: 'green'
                });
            }
        });
}

function suggest_deal_defaults(frm) {
    // Suggest default values based on deal type
    const defaults = {
        'Acquisition': {
            stage: 'Origination',
            probability: 10
        },
        'Fusion': {
            stage: 'Origination',
            probability: 10
        },
        'Cession': {
            stage: 'Origination',
            probability: 10
        }
    };
    
    if (frm.doc.deal_type && defaults[frm.doc.deal_type]) {
        const def = defaults[frm.doc.deal_type];
        if (!frm.doc.stage) {
            frm.set_value('stage', def.stage);
        }
        if (!frm.doc.probability) {
            frm.set_value('probability', def.probability);
        }
    }
}

function setup_query_filters(frm) {
    // Filter advisor team users
    frm.fields_dict['lead_advisor'].get_query = function() {
        return {
            filters: {
                'enabled': 1
            }
        };
    };
    
    // Filter clients
    frm.fields_dict['client'].get_query = function() {
        return {
            filters: {
                'disabled': 0
            }
        };
    };
}

function send_deal_update(frm) {
    const d = new frappe.ui.Dialog({
        title: __('Envoyer Mise à Jour'),
        fields: [
            {
                fieldname: 'recipients',
                fieldtype: 'MultiSelect',
                label: __('Destinataires'),
                reqd: 1,
                get_data: function() {
                    // Get team members
                    let members = [];
                    if (frm.doc.lead_advisor) {
                        members.push({value: frm.doc.lead_advisor, description: 'Lead Advisor'});
                    }
                    frm.doc.advisor_team.forEach(function(member) {
                        if (member.email) {
                            members.push({value: member.email, description: member.full_name});
                        }
                    });
                    return members;
                }
            },
            {
                fieldname: 'subject',
                fieldtype: 'Data',
                label: __('Sujet'),
                default: __('Mise à jour: {0}', [frm.doc.deal_name]),
                reqd: 1
            },
            {
                fieldname: 'message',
                fieldtype: 'Text Editor',
                label: __('Message'),
                reqd: 1
            }
        ],
        primary_action_label: __('Envoyer'),
        primary_action: function(values) {
            frappe.call({
                method: 'frappe.core.doctype.communication.email.make',
                args: {
                    recipients: values.recipients,
                    subject: values.subject,
                    content: values.message,
                    doctype: frm.doctype,
                    name: frm.doc.name
                },
                callback: function() {
                    frappe.show_alert({
                        message: __('Email envoyé'),
                        indicator: 'green'
                    });
                    d.hide();
                }
            });
        }
    });
    d.show();
}

// Team member table scripts
frappe.ui.form.on('Deal Team Member', {
    user: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.user) {
            frappe.db.get_value('User', row.user, ['full_name', 'email', 'phone'], function(r) {
                if (r) {
                    frappe.model.set_value(cdt, cdn, 'full_name', r.full_name);
                    frappe.model.set_value(cdt, cdn, 'email', r.email);
                    frappe.model.set_value(cdt, cdn, 'phone', r.phone);
                }
            });
        }
    }
});
