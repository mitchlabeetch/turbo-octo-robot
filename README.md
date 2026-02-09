# M&A Advisory ERP

## Vue d'ensemble

M&A Advisory ERP est une version dérivée d'ERPNext spécialement conçue pour les cabinets de conseil en fusions-acquisitions de taille moyenne (mid-cap). Le système est entièrement localisé en français et offre des capacités de white label pour une intégration transparente dans votre marque.

## Caractéristiques principales

### 🤝 Gestion des Transactions M&A
- Pipeline de deals avec suivi en temps réel
- Gestion des étapes de transaction (teaser, NDA, CIM, due diligence, etc.)
- Suivi des probabilités et dates de clôture
- Gestion des équipes de conseil

### 💰 Valorisation
- Méthodes multiples : DCF, multiples de marché, multiples de transaction
- Calcul automatique de la valeur d'entreprise et des capitaux propres
- Ajustements pour dette nette et trésorerie
- Documentation et traçabilité des hypothèses

### 🔍 Due Diligence
- Checklists personnalisables par catégorie (financière, juridique, commerciale, etc.)
- Suivi de l'avancement par domaine
- Assignation des tâches et délais
- Gestion documentaire intégrée

### 👥 Gestion des Clients
- Base de données clients et sociétés cibles
- Historique des interactions
- Gestion des mandats et honoraires
- Tableaux de bord personnalisés

### 🎨 White Label
- Personnalisation complète de la marque
- Logo et couleurs personnalisés
- Interface sans référence
- Configuration par domaine

### 🌐 Architecture Headless
- API REST complète
- Support CORS pour frontends découplés
- Authentification JWT
- Webhooks pour intégrations

## Installation rapide

Voir [INSTALL.md](INSTALL.md) pour les instructions d'installation détaillées.

```bash
# Installer Frappe Bench
pip install frappe-bench
bench init --frappe-branch version-14 frappe-bench
cd frappe-bench

# Créer un site et installer ERPNext
bench new-site ma-advisory.local
bench get-app erpnext --branch version-14
bench --site ma-advisory.local install-app erpnext

# Installer M&A Advisory
bench get-app https://github.com/mitchlabeetch/turbo-octo-robot
bench --site ma-advisory.local install-app ma_advisory

# Démarrer
bench start
```

## Documentation

- [Guide d'installation complet](INSTALL.md)
- [Documentation API](docs/API.md)
- [Guide de personnalisation](docs/CUSTOMIZATION.md)

## Structure du projet

```
ma_advisory/
├── api/                    # API endpoints
├── config/                 # Configuration et settings
├── dashboards/            # Dashboard configurations
├── deal_management/       # Module gestion des deals
├── valuation/             # Module valorisation
├── due_diligence/         # Module due diligence
├── public/                # Assets statiques (CSS, JS)
│   ├── css/              # Styles personnalisés
│   └── js/               # Scripts personnalisés
├── tasks/                 # Tâches planifiées
├── templates/             # Templates web
├── translations/          # Fichiers de traduction
├── hooks.py              # Hooks Frappe
└── boot.py               # Configuration white label
```

## Basé sur

- [Frappe Framework](https://github.com/frappe/frappe) - Framework web Python
- [ERPNext](https://github.com/frappe/erpnext) - ERP open source

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## Support

Pour toute question ou support :
- Issues : https://github.com/mitchlabeetch/turbo-octo-robot/issues
- Email : contact@example.com
