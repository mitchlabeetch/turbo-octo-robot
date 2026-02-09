# Getting Started with Contact & Document Management

**Module Version**: 2.0  
**Updated**: January 2024

## Quick Start Guide

### 5-Minute Setup

#### Step 1: Enable New Modules
The contact management and document management modules are installed by default. Verify in Desk > Customize > Sidebar config.

#### Step 2: Add First Company
1. Go to **Contact Management > Companies**
2. Click **New**
3. Fill in:
   - Company Name (e.g., "ABC Corporation")
   - Company Type: "Target Company"
   - Sector: Select from sector list
   - Annual Revenue: €100,000,000

#### Step 3: Add Contacts
1. Go to **Contact Management > Contacts**
2. Click **New**
3. Fill in:
   - First Name & Last Name
   - Email (required)
   - Company: Link to company created above
   - Job Title: "CFO"
   - Decision Maker: Check if C-level

#### Step 4: Log Interactions
1. Open contact record
2. Click **New Interaction** button
3. Select type: "Email", "Phone Call", "Meeting"
4. Fill subject and notes
5. Save

#### Step 5: View Relationship Map
1. Open contact record
2. Scroll to **Relationship Network** section
3. See all connections and deals

---

## Feature Overview

### Company Management

#### Finding Companies
```
Path: Contact Management > Companies
Search: Use global search to find by name or website
Filter: By sector, relationship type, annual revenue range
```

#### Company Timeline
- View all interactions with company
- See all related deals
- Track engagement history
- Identify relationship gaps

#### Company Profiles
- Financial metrics
- Sector classification
- Key contacts
- Deal history
- Parent/subsidiary relationships

---

### Contact Management

#### Creating Contacts
**Manual Entry**:
1. Go to Contacts > New
2. Enter name and email (required)
3. Link to company
4. Add job title
5. Set relationship type
6. Save

**From Email**:
```
Use API:
POST /api/method/ma_advisory.contact_management.api.create_contact_from_email
{
  "email": "john.doe@company.com",
  "auto_enrich": true
}
```

#### Contact Profile Information
- Personal: Name, email, phone, LinkedIn
- Professional: Job title, company, role
- Relationship: Type, strength, contact dates
- Activity: All interactions, meetings, calls
- Background: Education, expertise, biography

#### Relationship Tracking
- **Strength Calculation**: Automatic based on interaction count
  - Weak (1-2 interactions)
  - Moderate (3-5)
  - Strong (6+)
  - Very Strong (Regular engagement)
- **Decision Influence**: Executive, Department Head, Influencer, Supporter
- **Contact History**: First and last contact dates tracked

---

### Interaction Logging

#### Creating Interactions
```
1. Open Contact record
2. Click "Create Interaction" button
3. Choose type:
   - Email
   - Phone Call
   - In-Person Meeting
   - Video Conference
   - LinkedIn Message
   - Conference/Event
   - Other
```

#### Interaction Details
- **Subject**: What the interaction was about
- **Notes**: Detailed notes and outcome
- **Attendees**: Names of participants
- **Duration**: For calls/meetings
- **Outcome**: Information gathering, pitch, negotiation, decision, etc.
- **Follow-up**: Mark if follow-up needed and set date
- **Related Deal**: Link to active deal

#### Automatic Metrics
After logging interaction:
- Contact relationship strength updates
- Interaction count increments
- Last contact date updates
- Follow-up tasks created if needed

---

### Document Management

#### Uploading Documents
```
Path: Document Management > Documents
1. Click New
2. Document Name: "CIM - ABC Corporation"
3. Document Type: "CIM (Information Memorandum)"
4. Deal: Link to related deal
5. Upload file
6. Set status: "Draft"
7. Save
```

#### Version Control
```
To create new version:
1. Open document
2. Click "Create New Version"
3. Upload new file
4. Note: Current version → version 2
5. Previous file preserved in history
```

#### Access Control
```
For Confidential Documents:
1. Check "Is Confidential"
2. Add users/roles in "Access Restrictions"
3. Only listed users can view
```

#### Document Search
```
Search for documents:
- By name: "CIM"
- By type: "Information Memorandum"
- By deal: Select deal
- Returns version history
```

---

## Common Workflows

### Workflow 1: Initial Company Research
```
1. Search company by name
2. Go to MA Company record
3. View:
   - Company profile (sector, size, website)
   - Key contacts (from Contacts module)
   - Related deals
   - Engagement history
4. Identify key decision makers
5. Plan initial outreach
```

### Workflow 2: Contact Engagement Tracking
```
1. Create contact record
2. Log email interaction
3. Schedule follow-up meeting
4. Log meeting interaction
5. Check relationship strength update
6. Create next action task
7. Track in timeline
```

### Workflow 3: Deal Documentation
```
1. New deal created
2. Create Teaser document
3. Upload teaser file
4. Mark as Draft
5. After review, create v2
6. Mark as Final
7. Link NDA document
8. Version control maintains history
```

### Workflow 4: Network Mapping for Deal
```
1. Open deal (e.g., ABC Acquisition)
2. Via API: map_buyer_seller_networks()
3. Analyze:
   - Seller contacts (from ABC Corp)
   - Buyer contacts (from deal team)
   - Decision makers on both sides
4. Identify relationship gaps
5. Plan engagement strategy
```

---

## Best Practices

### Contact Management
✓ **Add comprehensive emails** - Essential for communications
✓ **Link companies properly** - Enables network analysis
✓ **Log interactions regularly** - In real-time after meetings
✓ **Keep notes detailed** - Future context for team members
✓ **Tag contacts** - Use tags for quick filtering
✓ **Update job titles** - Track career progression

### Company Management
✓ **Verify financial data** - accuracy for valuation models
✓ **Set relationship type** - Prospect vs. Active vs. Closed
✓ **Assign owner** - Clear accountability
✓ **Track parent relationships** - For group deals
✓ **Note key contacts** - Identify lead contact for outreach

### Document Management
✓ **Version continuously** - Each draft is a version
✓ **Document sources** - Note where each version came from
✓ **Mark confidential** - For sensitive docs
✓ **Link to deals** - Context is crucial
✓ **Archive old versions** - Keep clean history
✓ **Use templates** - Consistency in documents

### Interaction Logging
✓ **Log immediately** - After calls/meetings while fresh
✓ **Specific outcomes** - What was achieved/next steps
✓ **Include attendees** - Track who was involved
✓ **Link to deals** - Context for interactions
✓ **Set follow-ups** - Auto-creates tasks
✓ **Complete notes** - For team context

---

## Analytics & Reports

### Available Analytics

#### Contact Analytics
```
Metrics:
- Total contacts by relationship strength
- Contact distribution by company
- Interaction frequency by type
- Average touches per contact
```

#### Company Intelligence
```
Shows:
- Key contacts per company
- Related deals
- Interaction timeline
- Engagement health
```

#### Relationship Network
```
Visualizes:
- Direct connections
- Company relationships
- Deal involvement
- Network influence scores
```

#### Document Status
```
Tracks:
- Documents by status (Draft/Final)
- Version history
- Access restrictions
- Deal document completeness
```

---

## Troubleshooting

### Contact Not Appearing in Deal
**Solution**: 
1. Verify contact has email
2. Check contact is saved properly
3. Email must match ERPNext user (if team member)
4. Manual add via "Add Deal Team Member"

### Relationship Strength Not Updating
**Solution**:
1. Save interaction properly
2. Verify interaction docstatus = 1
3. Manually recalculate: Open contact > Save

### Document File Not Uploading
**Solution**:
1. Check file size limits
2. Verify file format supported
3. Check storage space
4. Try smaller file first

### Search Not Finding Contact
**Solution**:
1. Use global search (Ctrl+K)
2. Search by email, first name, or last name
3. Check spelling
4. Note: Searches active contacts only

---

## API Quick Reference

### Most-Used Endpoints

```bash
# Get all relations for a contact
curl "https://your-instance.frappe.cloud/api/method/ma_advisory.contact_management.api/get_relationship_network?contact_name=Contact-ID"

# Search contacts
curl "https://your-instance.frappe.cloud/api/method/ma_advisory.contact_management.api/search_contacts?query=Pierre"

# Get company intelligence
curl "https://your-instance.frappe.cloud/api/method/ma_advisory.contact_management.api/get_company_intelligence?company_name=ABC Corp"

# Get deal documents
curl "https://your-instance.frappe.cloud/api/method/ma_advisory.document_management.api/get_deal_documents?deal_name=ACQ-2024-0001"
```

See [API v2 Documentation](API_v2.md) for complete reference.

---

## Tips & Tricks

### Speed Up Contact Entry
- Use **keyboard shortcuts**: Ctrl+S to save
- **Auto-fill**: Company auto-fills from dropdown
- **Bulk import**: Use CSV import for existing leads
- **Templates**: Create contact templates by company

### Organize Contacts
- **Tags**: Use #technology, #investorrelations, #legal
- **Filters**: Filter by company, sector, decision maker
- **Reports**: Build custom contact lists

### Track Relationship Health
- **Interaction frequency**: Monitor engagement gap
- **Relationship strength**: Track growing relationships
- **Follow-up dates**: Never miss a reconnect
- **Deal involvement**: See where contacts contribute

### Streamline Documents
- **Templates**: Create standard documents
- **Quick upload**: Attach files during deal update
- **Version naming**: Use v1.0, v1.1, v2.0 format
- **Status tracking**: Know document approval status

---

## Advanced Features

### Relationship Gap Analysis
```
Identifies unengaged decision makers:
- Compare known contacts to org structure
- Flag executives with no interactions
- Recommend relationship development priority
```

### Warm Introduction Mapping
```
Find mutual connections:
- Identify common network members
- Suggest introduction paths
- Reduce cold outreach
```

### Influence Scoring
```
Calculate relationship value:
- Decision maker status: +50
- Role seniority: +10-40
- Interaction count: +5 each
- Deal involvement: +10 each
```

---

## Training Resources

- **Video Tutorials**: Coming soon
- **Webinars**: Monthly training sessions (planned)
- **Documentation**: Complete guides in [Docs](../docs/)
- **API Reference**: [API v2 Documentation](API_v2.md)
- **Community Forum**: Support discussions (planned)

---

## Next Steps

1. ✓ Add your company database
2. ✓ Import existing contacts
3. ✓ Start logging interactions
4. ✓ Create deal-related documents
5. ✓ Run relationship analytics
6. ✓ Build automated workflows
7. Integrate email system (v2.1)
8. Enable multi-language UI (v2.2)

---

**Questions?** See [API v2 Documentation](API_v2.md) or contact support.
