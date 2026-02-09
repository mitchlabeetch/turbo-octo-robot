# Quick Start Guide - M&A Advisory ERP

## Overview

This guide will help you quickly set up and start using M&A Advisory ERP for your M&A advisory firm.

## Prerequisites

Before you begin, ensure you have:
- A working Frappe/ERPNext installation (v14 or later)
- Administrator access to your site
- Basic understanding of ERPNext concepts

## Quick Setup (5 minutes)

### Step 1: Install the App

```bash
cd frappe-bench
bench get-app https://github.com/mitchlabeetch/turbo-octo-robot
bench --site your-site.local install-app ma_advisory
bench restart
```

### Step 2: Configure Language

The app defaults to French. To confirm:

1. Login as Administrator
2. Go to **Paramètres Système** (System Settings)
3. Verify **Langue** (Language) is set to `fr`

### Step 3: Setup White Label (Optional but Recommended)

1. Navigate to: **Paramètres > White Label Settings**
2. Configure your branding:
   - **Nom de l'Application**: Your firm name (e.g., "ABC Advisory")
   - **Logo**: Upload your company logo (PNG, 200x50px recommended)
   - **Couleur de la Marque**: Your primary brand color (e.g., #003366)
   - **Masquer la Marque Frappe**: ✓ (Keep checked for white label)
3. Click **Enregistrer** (Save)

### Step 4: Create Your First Deal

1. Go to **Gestion des Deals** (Deal Management)
2. Click **Nouveau** (New)
3. Fill in the details:
   - **Nom de la Transaction**: e.g., "Acquisition Société ABC"
   - **Type de Transaction**: Select from dropdown (Acquisition, Fusion, etc.)
   - **Étape**: Start with "Origination"
   - **Valeur**: Enter deal value
   - **Devise**: EUR (or your currency)
   - **Date de Clôture Prévue**: Expected closing date
4. Click **Enregistrer** (Save)

### Step 5: Create a Valuation

1. Go to **Valorisation** module
2. Click **Nouveau** (New)
3. Fill in:
   - **Transaction**: Link to your deal
   - **Nom de l'Entreprise**: Target company name
   - **Méthode de Valorisation**: Choose valuation method
   - **EBITDA**: Enter EBITDA value
   - **Multiple d'EBITDA**: Enter multiple (e.g., 8.5)
4. The system will auto-calculate **Valeur d'Entreprise** (Enterprise Value)
5. Enter **Dette Nette** and **Trésorerie** to calculate **Valeur des Capitaux Propres**

## Key Features to Explore

### 1. Deal Pipeline View

View all your active deals in one place:
- Navigate to **Gestion des Deals > Vue Liste**
- See deals organized by stage
- Filter by status, client, or date

### 2. Dashboard

Access your personalized dashboard:
- Click **Tableau de Bord** from the home page
- View key metrics: active deals, total pipeline value, upcoming closings
- Customize widgets to suit your needs

### 3. Client Management

Manage your clients:
- Go to **Clients** module
- Create new clients or link to existing ERPNext customers
- View client history and related deals

### 4. Due Diligence Tracking

Track due diligence progress:
- Create **Due Diligence Items** for each deal
- Categorize by type (Financial, Legal, Commercial, etc.)
- Assign to team members
- Track completion status

## API Access (for Headless Integration)

If you want to build a custom frontend:

### 1. Generate API Keys

```bash
bench --site your-site.local add-user-api-keys your@email.com
```

Save the generated API key and secret.

### 2. Test API Access

```bash
curl -X GET "https://your-site.com/api/resource/Deal" \
  -H "Authorization: token API_KEY:API_SECRET"
```

### 3. Use JavaScript Client

```javascript
const client = new MAAClient('https://your-site.com', 'API_KEY', 'API_SECRET');
const deals = await client.getDeals();
console.log(deals);
```

See [API.md](docs/API.md) for complete API documentation.

## Daily Workflow

### Morning Routine

1. **Check Dashboard**: Review overnight updates
2. **Pipeline Review**: Review active deals and their stages
3. **Tasks**: Check due diligence items due today

### During the Day

1. **Update Deals**: Move deals through pipeline stages
2. **Client Communications**: Log calls and meetings
3. **Document Management**: Upload NDAs, CIMs, term sheets

### End of Day

1. **Update Progress**: Update deal probabilities and notes
2. **Tomorrow's Prep**: Review upcoming closings and tasks
3. **Team Sync**: Check team assignments and workload

## Common Tasks

### Moving a Deal Through Stages

1. Open the deal
2. Change **Étape** (Stage) field to next stage
3. Update **Probabilité** (Probability) if needed
4. Add notes in **Description**
5. Save

### Adding Team Members to a Deal

1. Open the deal
2. Scroll to **Équipe Conseil** (Advisor Team)
3. Click **Ajouter une ligne** (Add Row)
4. Select team member
5. Define their role
6. Save

### Running Valuation Scenarios

1. Create multiple Valuation documents for same deal
2. Use different methods or multiples
3. Compare results
4. Mark final valuation as "Validé" (Validated)

## Tips & Best Practices

### 1. Consistent Naming

Use a consistent naming convention for deals:
- Format: `[Type] - [Target Company] - [Year]`
- Example: "Acquisition - ABC SAS - 2024"

### 2. Regular Updates

- Update deal stages weekly (at minimum)
- Keep probability estimates current
- Log all client interactions

### 3. Document Everything

- Upload all documents to respective deals
- Use consistent file naming
- Tag documents by type (NDA, CIM, etc.)

### 4. Use Custom Fields

Add custom fields for firm-specific data:
```bash
bench --site your-site.local add-custom-field \
  --doctype Deal \
  --fieldname "industry_subsector" \
  --fieldtype Data \
  --label "Sous-secteur"
```

### 5. Set Up Notifications

Configure email notifications for:
- Deal stage changes
- Upcoming closing dates
- Overdue due diligence items

## Troubleshooting

### Can't See M&A Modules?

- Verify app is installed: `bench --site your-site.local list-apps`
- Clear cache: `bench --site your-site.local clear-cache`
- Restart: `bench restart`

### White Label Not Showing?

- Ensure White Label Settings are saved
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)

### API Not Working?

- Verify API keys are correct
- Check CORS settings in site_config.json
- Ensure user has appropriate permissions

## Getting Help

- **Documentation**: Check README.md and docs/ folder
- **Issues**: Report bugs at GitHub Issues
- **Email**: contact@example.com

## Next Steps

1. **Import Data**: Import existing clients and deals
2. **Customize**: Add custom fields for your workflow
3. **Integrate**: Connect to your other tools via API
4. **Train Team**: Onboard team members and assign roles
5. **Optimize**: Create custom reports and dashboards

## Resources

- [Full Installation Guide](INSTALL.md)
- [API Documentation](docs/API.md)
- [GitHub Repository](https://github.com/mitchlabeetch/turbo-octo-robot)
- [Frappe Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)

---

*Bonne chance avec votre nouveau système M&A Advisory ERP!* 🎉
