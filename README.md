# M&A Advisory ERP

**Status**: ✅ **v2.0 - Modern FastAPI Implementation** | 🚀 Production-Ready CRM + Headless API

## Overview

**M&A Advisory ERP** is a modern **open-source CRM+ERP platform** purpose-built for mid-cap M&A advisory firms (1-100 employees). Built with **FastAPI** and **SQLAlchemy**, it provides a lightweight, cloud-native alternative to Salesforce, DealCloud, and ERPNext.

**Supported in French** 🇫🇷 and English 🇬🇧 with roadmap for 20+ languages.

### 🎯 Architecture

- **Active Implementation**: `/standalone/` — Modern FastAPI + SQLAlchemy (production)
- **Legacy Reference**: `/ma_advisory/` — Original Frappe code (deprecated, see [DEPRECATED.md](ma_advisory/DEPRECATED.md))

For detailed architecture analysis: see [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md)

## ✨ Version 2.0 - Modern FastAPI Architecture

M&A Advisory ERP v2.0 delivers a **best-in-class CRM+API platform** for mid-cap M&A advisory, with:
- ✅ **Lightweight & Fast**: FastAPI startup <1s, install in 15s
- ✅ **Cloud-Native**: Docker container, microservices-ready, auto-scalable
- ✅ **Complete CRM**: Contacts, companies, interactions, documents, email integration
- ✅ **Headless API**: 50+ REST endpoints for mobile and SPA integration
- ✅ **Modern Stack**: Python 3.10+, SQLAlchemy 2.0, async-first design
- ✅ **Open Source**: MIT license, fully transparent, no vendor lock-in

### 📦 Installation (Quick Start)

```bash
# Clone and navigate
git clone https://github.com/mitchlabeetch/turbo-octo-robot.git
cd turbo-octo-robot/standalone

# Install and run
pip install -e .
python -m uvicorn app.main:app --reload
```

**Server**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

### 🐳 Docker Deployment

```bash
cd standalone/
docker compose up --build
```

See [INSTALL.md](INSTALL.md) for detailed deployment options.

### 🎯 Features Implemented (v2.0)

#### 🤝 Contact & Relationship Management
- ✅ **Companies**: Sector, revenue, employee tracking
- ✅ **Contacts**: Decision makers, relationship mapping, interaction history
- ✅ **Interactions**: Email, call, meeting, note types with automatic capture
- ✅ **Email Integration**: Webhook support for Gmail & Microsoft 365
- ✅ **Relationship Intelligence**: Network mapping, influence scoring (roadmap: Q1 2026)

#### 📄 Document Management
- ✅ **Version Control**: Full history, restore capabilities
- ✅ **Secure Sharing**: Token-based access, NDA confirmation, expiry dates
- ✅ **Confidentiality Flags**: Sensitive document protection
- ✅ **Deal Association**: Document linkage to transactions

#### 📊 Prospecting & Origination
- ✅ **Target Lists**: Criteria-based filtering, campaign association
- ✅ **Origination Campaigns**: ROI tracking, prospect recommendations (roadmap: Q1 2026)

#### 🔐 Security & Compliance
- ✅ **JWT Authentication**: Stateless, scalable user sessions
- ✅ **OAuth2 Support**: Google, Microsoft, custom providers
- ✅ **Audit Logging**: Track all document access
- ✅ **Access Control**: Role-based permissions, document-level restrictions

#### 🔗 API & Integration
- ✅ **REST API**: 50+ endpoints for full data access
- ✅ **CORS Support**: Frontend integration across domains
- ✅ **Bulk Export**: CSV & JSON export for all entities
- ✅ **Webhooks**: Custom integrations (roadmap: Q2 2026)

### 🚧 Roadmap - Missing Components (ERP Layer)

**To reach production M&A advisory platform status**, the following features are planned:

| Feature | Timeline | Priority |
|---------|----------|----------|
| **General Ledger & AR/AP** | Q1 2026 (3 weeks) | 🔴 CRITICAL |
| **Invoicing & Revenue Recognition** | Q1 2026 (2 weeks) | 🔴 CRITICAL |
| **Time Tracking & Billable Hours** | Q2 2026 (2 weeks) | 🟠 HIGH |
| **Project-Based Costing** | Q2 2026 (3 weeks) | 🟠 HIGH |
| **Multi-Currency Support** | Q2 2026 (2 weeks) | 🟠 HIGH |
| **Reporting & Analytics Engine** | Q2 2026 (3 weeks) | 🟠 HIGH |
| **Workflow Automation** | Q2 2026 (2 weeks) | 🟠 HIGH |
| **Multi-Language Support (20+)** | Q3 2026 (3 weeks) | 🟡 MEDIUM |
| **Predictive Analytics** | Q3 2026 (2 weeks) | 🟡 MEDIUM |

**Current Completeness**: 35% CRM / 5% ERP / 10% International = 17% Overall

See [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) for detailed gap analysis and [VISUAL_COMPARISON.md](VISUAL_COMPARISON.md) for feature matrix.

## Documentation

### 📖 Core Documentation
- **[CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md)** — Architectural analysis, feature gaps, effort estimates
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** — Strategic recommendations and timeline
- **[VISUAL_COMPARISON.md](VISUAL_COMPARISON.md)** — Feature matrix vs ERPNext/Strapi
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** — Transitioning from Frappe-based implementation
- **[STANDALONE_ERP_CMS_STRATEGY.md](STANDALONE_ERP_CMS_STRATEGY.md)** — Phased strategy for ERP+CMS delivery
- **[PHASE_0_EXECUTION.md](PHASE_0_EXECUTION.md)** — Phase 0 execution tracker and deliverables
- **[INSTALL.md](INSTALL.md)** — Deployment options (Docker, standalone, cloud)
- **[API.md](docs/API_v2.md)** — Complete REST API reference

### ⚠️ Legacy Implementation
The original Frappe/ERPNext-based implementation is now **deprecated** in favor of the modern FastAPI stack.  
See [ma_advisory/DEPRECATED.md](ma_advisory/DEPRECATED.md) for details on why and how to migrate.

### 🗂️ Directory Structure

```
├── standalone/              # ✅ ACTIVE: FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── models.py       # SQLAlchemy data models
│   │   ├── schemas.py      # Pydantic request/response schemas
│   │   ├── routers/        # API endpoint definitions
│   │   ├── utils/          # Helpers (export, import, audit, watermark)
│   │   └── *.py            # Auth, config, storage, security
│   ├── pyproject.toml      # Python dependencies (11 packages)
│   ├── docker-compose.yml  # Docker deployment config
│   └── README.md           # Standalone-specific documentation
│
├── ma_advisory/            # ⚠️ DEPRECATED: Original Frappe code
│   ├── DEPRECATED.md       # Deprecation notice (read this!)
│   └── [legacy code]
│
├── docs/                   # Documentation
│   ├── API_v2.md          # REST API reference
│   ├── ARCHITECTURE.md    # System design
│   └── ...
│
└── pyproject.toml         # Root metapackage (uses /standalone/)
```

## Architecture Principles

1. **Lightweight** — <100MB total, <15s installation
2. **Cloud-Native** — Containerized, stateless, auto-scalable
3. **Headless API** — Front-end agnostic, integration-friendly
4. **Open Source** — MIT license, full transparency, no vendor lock-in
5. **Modern Stack** — FastAPI, SQLAlchemy 2.0, async-first
6. **Developer-Friendly** — Type hints, comprehensive APIs, detailed logs

## Development

### Local Setup
```bash
cd standalone/
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Running Tests
```bash
cd standalone/
pytest --cov=app
```

### Code Quality
```bash
ruff check .
black --check .
```
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
