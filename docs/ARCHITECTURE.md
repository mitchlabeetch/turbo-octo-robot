# Architecture Overview - M&A Advisory ERP

## System Architecture

M&A Advisory ERP is built on the Frappe Framework and extends ERPNext with M&A-specific functionality. The architecture follows Frappe's Model-View-Controller (MVC) pattern with additional layers for API and customization.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web UI    │  │   Mobile    │  │  Custom     │        │
│  │  (French)   │  │     App     │  │  Frontend   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              White Label / API Layer                         │
│  ┌──────────────────────────────────────────────┐          │
│  │   REST API (JSON)  │  WebSocket  │  Webhooks │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Layer (Python)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Deal Mgmt   │  │  Valuation   │  │ Due Diligence│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Clients    │  │  Documents   │  │   Reports    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Frappe Framework Layer                          │
│  ┌──────────────────────────────────────────────┐          │
│  │  ORM  │  Permissions  │  Workflows  │  Jobs  │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   MariaDB    │  │    Redis     │  │   File Store │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Core Modules

#### Deal Management (`ma_advisory/deal_management`)
- **Purpose**: Manage M&A transaction pipeline
- **Key Features**:
  - Deal lifecycle tracking
  - Stage progression (Origination → Closing)
  - Probability estimation
  - Team assignment
- **DocTypes**: Deal, Deal Team Member
- **Controllers**: Auto-calculate probabilities, validate dates

#### Valuation (`ma_advisory/valuation`)
- **Purpose**: Financial valuation and analysis
- **Key Features**:
  - Multiple valuation methods
  - Auto-calculation of EV and equity value
  - Scenario comparison
- **DocTypes**: Valuation
- **Controllers**: Calculate enterprise value, equity value from multiples

#### White Label (`ma_advisory/config`)
- **Purpose**: Branding and customization
- **Key Features**:
  - Custom logo and colors
  - Hide Frappe branding
  - Domain-specific configuration
- **DocTypes**: White Label Settings
- **Boot Session**: Dynamic branding injection

### 2. API Layer (`ma_advisory/api`)

#### REST Endpoints
- Standard CRUD operations via Frappe's `/api/resource/`
- Custom methods for complex operations:
  - `get_deal_pipeline()`: Pipeline view data
  - `get_valuation_data()`: Valuation history
  - `get_due_diligence_status()`: DD progress

#### Authentication
- API Key/Secret authentication
- Session-based authentication
- JWT token support (via Frappe)

#### CORS Configuration
- Configurable origins in `hooks.py`
- Supports headless frontend integration

### 3. Task Scheduler (`ma_advisory/tasks`)

#### Daily Tasks
- Send pipeline summary emails
- Alert on upcoming closings
- Update deal statuses

#### Weekly Tasks
- Generate activity reports
- Send management summaries
- Archive old data

### 4. Dashboard Layer (`ma_advisory/dashboards`)

#### Custom Dashboards
- Lead Dashboard: M&A opportunity tracking
- Client Dashboard: Client transaction history
- Deal Pipeline: Visual pipeline management

### 5. Translation Layer (`ma_advisory/translations`)

#### French Localization
- 70+ M&A-specific terms
- UI element translations
- Financial terminology
- Document type translations

### 6. Frontend Layer (`ma_advisory/public`)

#### JavaScript (`ma_advisory.js`)
- White label initialization
- Deal pipeline visualization
- Valuation calculator
- French number/date formatting
- MAAApi helper object for headless integration

#### CSS (`ma_advisory.css`)
- French typography
- White label theming
- Responsive design
- M&A-specific components

## Data Model

### Key DocTypes

```
Deal
├── name (auto)
├── deal_name (string)
├── deal_type (select)
├── stage (select)
├── status (select)
├── client (link to Customer)
├── target_company (string)
├── value (currency)
├── probability (percent)
├── expected_close_date (date)
├── lead_advisor (link to User)
└── advisor_team (table)

Valuation
├── name (auto)
├── deal (link to Deal)
├── company_name (string)
├── valuation_method (select)
├── ebitda (currency)
├── ebitda_multiple (float)
├── enterprise_value (currency, auto-calc)
├── equity_value (currency, auto-calc)
├── debt (currency)
└── cash (currency)

White Label Settings (Single)
├── app_name (string)
├── app_logo_url (image)
├── brand_color (color)
├── hide_frappe_branding (check)
├── default_language (select)
└── custom_css (code)
```

## Integration Points

### 1. ERPNext Integration

M&A Advisory extends ERPNext modules:
- **Customer**: Extended for M&A client management
- **Lead**: Customized for deal origination
- **Project**: Can be linked for transaction management
- **File**: Document management
- **Email**: Communication tracking

### 2. External Integrations (via API)

```python
# Example: CRM Integration
deals = frappe.get_all("Deal", filters={"status": "Active"})
for deal in deals:
    sync_to_crm(deal)

# Example: Accounting Integration
valuations = frappe.get_all("Valuation", filters={"deal": deal_name})
sync_to_accounting_system(valuations)
```

### 3. Webhook Support

Configure webhooks for real-time sync:
- Deal stage changes
- Valuation updates
- Document uploads

## Security Architecture

### 1. Role-Based Access Control

```
System Manager
    └─ Full access to all features
        ├─ White Label Settings
        └─ System Configuration

M&A Manager
    └─ Full access to M&A modules
        ├─ Create/Edit/Delete Deals
        ├─ Manage Valuations
        └─ View Reports

M&A Analyst
    └─ Limited access
        ├─ Create/Edit Deals
        ├─ Create/Edit Valuations
        └─ View Reports (no delete)

M&A Client
    └─ Read-only access
        ├─ View assigned deals
        └─ Download documents
```

### 2. Data Security

- Row-level security via Frappe permissions
- Field-level encryption for sensitive data
- Audit trail for all changes
- Document-level permissions

### 3. API Security

- API key authentication
- Rate limiting
- CORS restrictions
- Input validation
- SQL injection prevention (via ORM)

## Scalability

### Horizontal Scaling

```
Load Balancer
    ├─ App Server 1 (Frappe)
    ├─ App Server 2 (Frappe)
    └─ App Server 3 (Frappe)
         │
         ▼
    MariaDB Cluster
         │
         ▼
    Redis Cache
```

### Caching Strategy

1. **Redis**: Session and query caching
2. **Browser**: Static assets (CSS, JS)
3. **CDN**: Images and documents

### Performance Optimization

- Database indexing on frequently queried fields
- Lazy loading of related documents
- Pagination for large datasets
- Background jobs for heavy operations

## Deployment Architecture

### Development

```
Developer Machine
    └─ Bench (Development Mode)
        ├─ Frappe
        ├─ ERPNext
        └─ M&A Advisory
```

### Production

```
Web Server (Nginx)
    ├─ SSL Termination
    ├─ Static Files
    └─ Reverse Proxy
        │
        ▼
Application Servers (Gunicorn)
    ├─ Frappe Workers
    └─ Background Jobs (RQ)
        │
        ▼
Database (MariaDB)
Cache (Redis)
File Storage (S3/Local)
```

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: Frappe 14+
- **Database**: MariaDB 10.6+
- **Cache**: Redis 5+
- **Queue**: Redis Queue (RQ)

### Frontend
- **JavaScript**: Vanilla JS + Frappe UI
- **CSS**: Custom CSS with CSS variables
- **Icons**: Octicons

### Infrastructure
- **Web Server**: Nginx
- **App Server**: Gunicorn
- **Process Manager**: Supervisor
- **OS**: Ubuntu 20.04+ / Debian

## Development Workflow

```
Developer
    ↓
Git Repository
    ↓
CI/CD Pipeline
    ↓
Staging Environment
    ↓ (after testing)
Production Environment
```

## Monitoring & Logging

### Application Logs
- Frappe error logs
- Access logs
- Background job logs
- Custom module logs

### Monitoring Metrics
- API response times
- Database query performance
- Background job status
- System resource usage

## Future Enhancements

1. **Advanced Analytics**: Deal pipeline analytics, win/loss analysis
2. **AI/ML Integration**: Deal probability prediction, valuation suggestions
3. **Mobile Apps**: Native iOS/Android apps
4. **Advanced Workflows**: Approval workflows, automated notifications
5. **Document Templates**: Generate CIMs, teasers, presentations
6. **Data Rooms**: Virtual data room integration
7. **E-signature**: Integrated electronic signature

## References

- [Frappe Framework Architecture](https://frappeframework.com/docs/user/en/architecture)
- [ERPNext Architecture](https://docs.erpnext.com/docs/user/en/architecture)
- [MariaDB Documentation](https://mariadb.org/documentation/)
- [Redis Documentation](https://redis.io/documentation)

---

**Version**: 1.0.0  
**Last Updated**: 2024-02-09
