# M&A Advisory CRM+ERP - Complete API Reference

## Version 2.0 - January 2024

### Overview

This API reference documents all endpoints available in the M&A Advisory ERP, including the original Deal Management APIs and new Contact/Relationship Management APIs introduced in v2.0.

**Base URL**: `https://your-instance.frappe.cloud/api/method`

**Authentication**: Bearer token or API Key in header:
```
Authorization: Bearer {token}
```

---

## Contact Management APIs

### 1. Relationship Intelligence

#### Get Relationship Network
```
GET /ma_advisory/contact_management/api/get_relationship_network
Parameters:
  - contact_name (required): Name of the contact
  
Response:
{
  "contact": {
    "name": "Dupont-ABC-0001",
    "full_name": "Pierre Dupont",
    "company": "ABC Corp",
    "job_title": "CFO",
    "email": "pierre.dupont@abccorp.com"
  },
  "direct_relationships": [
    {
      "type": "Reports To",
      "contact": "Martin-ABC-0002",
      "name": "Jean Martin"
    }
  ],
  "company_network": {
    "parent": "Parent Corp",
    "subsidiaries": ["Sub1", "Sub2"]
  },
  "deal_involvement": [
    {
      "name": "ACQ-2024-0001",
      "deal_name": "ABC Acquisition",
      "stage": "Due Diligence",
      "value": 50000000
    }
  ],
  "interaction_summary": [
    {
      "interaction_type": "Email",
      "count": 15
    }
  ]
}
```

**Use Case**: Build contact relationship context for CRM dashboard

---

#### Get Company Intelligence
```
GET /ma_advisory/contact_management/api/get_company_intelligence
Parameters:
  - company_name (required): Name of the company

Response:
{
  "company": {
    "name": "ABC Corp",
    "company_name": "ABC Corporation",
    "company_type": "Target Company",
    "sector": "Technology",
    "annual_revenue": 100000000,
    "employee_count": 500,
    "website": "https://abc.com"
  },
  "contacts": [
    {
      "name": "Contact ID",
      "first_name": "Pierre",
      "last_name": "Dupont",
      "email": "pierre@abc.com",
      "job_title": "CFO",
      "interaction_count": 12
    }
  ],
  "deals": [
    {
      "name": "ACQ-2024-0001",
      "deal_name": "ABC Acquisition",
      "stage": "Negotiation",
      "value": 50000000
    }
  ],
  "interactions": [
    {
      "interaction_type": "Meeting",
      "count": 5
    }
  ],
  "key_contacts": [
    {
      "role": "CFO",
      "name": "Pierre Dupont",
      "interaction_count": 12
    }
  ],
  "organizational_structure": [...],
  "engagement_history": [...]
}
```

**Use Case**: Comprehensive company due diligence research

---

#### Get Network Influence Score
```
GET /ma_advisory/contact_management/api/get_network_influence_score
Parameters:
  - contact_name (required): Contact name

Response:
{
  "contact": "Dupont-ABC-0001",
  "influence_score": 285,  // 0-500 scale
  "decision_maker": true,
  "interaction_count": 15,
  "related_deals": 3
}
```

**Use Case**: Prioritize relationship development, identify key influencers

---

#### Get Warm Introduction Paths
```
GET /ma_advisory/contact_management/api/get_warm_introduction_paths
Parameters:
  - from_contact (required): Originating contact
  - to_contact (required): Target contact

Response:
{
  "from_contact": "Contact1",
  "to_contact": "Contact2",
  "mutual_connections": [
    {
      "name": "Contact3",
      "job_title": "CEO",
      "company": "XYZ Corp"
    }
  ],
  "introduction_path_exists": true
}
```

**Use Case**: Find warm introduction paths instead of cold outreach

---

### 2. Contact Search & Discovery

#### Search Contacts
```
GET /ma_advisory/contact_management/api/search_contacts
Parameters:
  - query (required): Search term
  - filters (optional): JSON with {"field": "value"}

Response:
[
  {
    "name": "Dupont-ABC-0001",
    "first_name": "Pierre",
    "last_name": "Dupont",
    "email": "pierre@abc.com",
    "job_title": "CFO",
    "company": "ABC Corp"
  }
]
```

**Searchable Fields**: First name, last name, email, job title

---

#### Search Companies
```
GET /ma_advisory/contact_management/api/search_companies
Parameters:
  - query (required): Search term
  - filters (optional): {"sector": "Technology"}

Response:
[
  {
    "name": "ABC Corp",
    "company_name": "ABC Corporation",
    "sector": "Technology",
    "website": "https://abc.com",
    "annual_revenue": 100000000,
    "employee_count": 500
  }
]
```

---

#### Get Origination Prospects
```
GET /ma_advisory/contact_management/api/get_origination_prospects

Response:
[
  {
    "name": "ABC Corp",
    "company_name": "ABC Corporation",
    "sector": "Technology",
    "annual_revenue": 75000000,
    "interaction_count": 3
  }
]
```

**Use Case**: Identify high-potential companies for business development

---

### 3. Analytics & Insights

#### Get Contact Analytics
```
GET /ma_advisory/contact_management/api/get_contact_analytics

Response:
{
  "total_contacts": 1250,
  "total_companies": 450,
  "total_interactions": 8900,
  "contacts_by_strength": [
    {"relationship_strength": "Weak", "count": 650},
    {"relationship_strength": "Moderate", "count": 400},
    {"relationship_strength": "Strong", "count": 150},
    {"relationship_strength": "Very Strong", "count": 50}
  ],
  "contacts_by_company": [
    {"company": "ABC Corp", "contact_count": 15},
    {"company": "XYZ Inc", "contact_count": 12}
  ],
  "interaction_types": [
    {"interaction_type": "Email", "count": 5000},
    {"interaction_type": "Phone", "count": 2500},
    {"interaction_type": "Meeting", "count": 1500}
  ],
  "average_interaction_frequency": 7.1
}
```

**Use Case**: Dashboard analytics and KPI tracking

---

#### Get Contact Timeline
```
GET /ma_advisory/contact_management/api/get_contact_timeline
Parameters:
  - contact_name (required): Contact name

Response:
{
  "contact": "Dupont-ABC-0001",
  "timeline": [
    {
      "type": "interaction",
      "date": "2024-01-15",
      "description": "Initial meeting with CFO",
      "details": {...}
    },
    {
      "type": "deal",
      "date": "2024-01-10",
      "description": "Deal: ABC Acquisition",
      "details": {...}
    }
  ],
  "total_events": 24
}
```

---

#### Map Buyer-Seller Networks
```
GET /ma_advisory/contact_management/api/map_buyer_seller_networks
Parameters:
  - deal_name (required): Deal name

Response:
{
  "seller_network": {
    "company": "ABC Corp",
    "contacts": [...],
    "deals_count": 5
  },
  "buyer_interested": {
    "companies": [...],
    "contacts": [...],
    "deals_count": 12
  }
}
```

---

#### Identify Relationship Gaps
```
GET /ma_advisory/contact_management/api/identify_relationship_gaps
Parameters:
  - company_name (required): Company name

Response:
{
  "company": "ABC Corp",
  "total_contacts": 8,
  "identified_gaps": [
    {
      "type": "Unengaged Executive",
      "contact": "Jean Martin",
      "role": "CEO",
      "priority": "High"
    }
  ],
  "recommendation": "Consider reaching out to identified unengaged executives"
}
```

---

### 4. Contact Management Operations

#### Create Contact from Email
```
POST /ma_advisory/contact_management/api/create_contact_from_email
Parameters:
  - email (required): Email address
  - auto_enrich (optional): true/false (default: true)

Response:
{
  "success": true,
  "contact": "Dupont-ABC-0001",
  "contact_name": "Pierre Dupont"
}
```

---

#### Get Deals by Contact
```
GET /ma_advisory/contact_management/api/get_deals_by_contact
Parameters:
  - contact_name (required): Contact name

Response:
[
  {
    "name": "ACQ-2024-0001",
    "deal_name": "ABC Acquisition",
    "stage": "Due Diligence",
    "value": 50000000,
    "probability": 75,
    "expected_close_date": "2024-06-30"
  }
]
```

---

## Document Management APIs

### 1. Document Operations

#### Get Deal Documents
```
GET /ma_advisory/document_management/api/get_deal_documents
Parameters:
  - deal_name (required): Deal name

Response:
[
  {
    "name": "DOC-ACQ-2024-0001",
    "document_name": "Teaser v3",
    "document_type": "Teaser",
    "version": 3,
    "status": "Final",
    "created_date": "2024-01-10"
  }
]
```

---

#### Search Documents
```
GET /ma_advisory/document_management/api/search_documents
Parameters:
  - query (required): Search term
  - deal_filter (optional): Deal name

Response:
[
  {
    "name": "DOC-ACQ-2024-0001",
    "document_name": "Teaser",
    "document_type": "Teaser",
    "version": 3,
    "status": "Final"
  }
]
```

---

#### Get Document by Type
```
GET /ma_advisory/document_management/api/get_document_by_type
Parameters:
  - deal_name (required): Deal name
  - document_type (required): Type (Teaser, NDA, CIM, etc.)

Response:
{
  "name": "DOC-ACQ-2024-0001",
  "document_name": "CIM v2",
  "version": 2,
  "status": "Final",
  "created_date": "2024-01-12"
}
```

---

#### Create Document from Template
```
POST /ma_advisory/document_management/api/create_document_from_template
Parameters:
  - deal_name (required): Deal name
  - document_type (required): Document type
  - template_data (optional): Template variables

Response:
{
  "success": true,
  "document": "DOC-ACQ-2024-0001"
}
```

---

## Deal Management APIs (Existing)

### 1. Pipeline Management

#### Get Deal Pipeline
```
GET /ma_advisory/api/get_deal_pipeline

Response:
[
  {
    "name": "ACQ-2024-0001",
    "deal_name": "ABC Acquisition",
    "stage": "Due Diligence",
    "value": 50000000,
    "probability": 75,
    "expected_close_date": "2024-06-30",
    "dd_completion": 65,
    "weighted_value": 37500000
  }
]
```

---

#### Get Deal Pipeline by Stage
```
GET /ma_advisory/api/get_deal_pipeline_by_stage

Response:
{
  "Origination": {
    "deals": [...],
    "count": 5,
    "total_value": 100000000,
    "weighted_value": 10000000
  },
  "Due Diligence": {
    "deals": [...],
    "count": 3,
    "total_value": 150000000,
    "weighted_value": 105000000
  }
  // ... for each stage
}
```

---

#### Get Valuation Data
```
GET /ma_advisory/api/get_valuation_data
Parameters:
  - deal_name (required): Deal name

Response:
[
  {
    "name": "VAL-001",
    "valuation_method": "DCF",
    "enterprise_value": 45000000,
    "equity_value": 40000000,
    "assumptions": {...}
  }
]
```

---

#### Get Due Diligence Status
```
GET /ma_advisory/api/get_due_diligence_status
Parameters:
  - deal_name (required): Deal name

Response:
{
  "Financière": {
    "total": 5,
    "completed": 3,
    "in_progress": 1,
    "pending": 1,
    "blocked": 0,
    "overdue": 0,
    "completion_percentage": 60
  },
  "Juridique": {...},
  "Commerciale": {...}
}
```

---

#### Get Deal Analytics
```
GET /ma_advisory/api/get_deal_analytics
Parameters:
  - deal_name (optional): Specific deal or all deals

Response:
{
  "total_deals": 20,
  "total_value": 500000000,
  "weighted_value": 280000000,
  "by_type": {
    "Acquisition": {
      "count": 12,
      "total_value": 300000000
    },
    "Fusion": {
      "count": 5,
      "total_value": 150000000
    },
    "Cession": {
      "count": 3,
      "total_value": 50000000
    }
  },
  "by_stage": {...},
  "by_status": {...}
}
```

---

## Standard CRUD Operations

### Create Resource
```
POST /api/resource/{doctype}
Body:
{
  "doctype": "MA Contact",
  "first_name": "Pierre",
  "last_name": "Dupont",
  "email": "pierre@abc.com"
}

Response:
{
  "data": {
    "name": "Dupont-ABC-0001",
    "first_name": "Pierre",
    ...
  }
}
```

---

### Read Resource
```
GET /api/resource/{doctype}/{name}

Response:
{
  "data": {
    "name": "Dupont-ABC-0001",
    "first_name": "Pierre",
    ...
  }
}
```

---

### Update Resource
```
PUT /api/resource/{doctype}/{name}
Body:
{
  "job_title": "Chief Financial Officer"
}

Response:
{
  "data": {
    "name": "Dupont-ABC-0001",
    "job_title": "Chief Financial Officer",
    ...
  }
}
```

---

### Delete Resource
```
DELETE /api/resource/{doctype}/{name}

Response:
{
  "ok": true
}
```

---

### List Resources
```
GET /api/resource/{doctype}?filters=[...]&fields=[...]&limit_page_length=20

Response:
{
  "data": [
    {...},
    {...}
  ]
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "exception": "frappe.exceptions.ValidationError",
  "message": "Email is mandatory",
  "_server_messages": [
    "Email is mandatory"
  ]
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

---

## Rate Limiting

- **Free tier**: 100 requests/minute
- **Pro tier**: 1000 requests/minute
- **Enterprise**: Custom limits

---

## Authentication

### API Key
```
Authorization: token {api_key}
```

### Bearer Token
```
Authorization: Bearer {jwt_token}
```

### Session Cookie
```
Cookie: sid={session_id}
```

---

## Pagination

```
GET /api/resource/MA Contact?limit_page_length=20&page_length=20&skip=0

Response:
{
  "data": [...],
  "keys": [...],
  "has_indicator": false
}
```

---

## Filters

```
GET /api/resource/MA Contact?filters=[["company","=","ABC Corp"],["decision_maker","=",1]]

Available operators:
- = (equals)
- != (not equals)
- > (greater than)
- < (less than)
- >= (greater than or equal)
- <= (less than or equal)
- like (pattern match)
- in (in list)
- not in (not in list)
```

---

## Webhooks

Register webhooks for document events:

```python
POST /api/resource/Webhook
{
  "doc_type": "MA Contact",
  "webhook_docevent": "after_insert",
  "webhook_url": "https://your-api.com/webhook"
}
```

---

## Batch Operations

### Bulk Import
```
POST /api/method/frappe.client.bulk_insert
{
  "docs": [
    {
      "doctype": "MA Contact",
      "first_name": "Pierre",
      "email": "pierre@abc.com"
    }
  ]
}
```

---

## SDK Examples

### JavaScript (Browser)
```javascript
// Using Frappe framework
frappe.call({
  method: 'ma_advisory.contact_management.api.get_relationship_network',
  args: {
    contact_name: 'Dupont-ABC-0001'
  },
  callback: function(r) {
    console.log(r.message);
  }
});
```

### Python
```python
import frappe

# Get relationship network
network = frappe.call(
    'ma_advisory.contact_management.api.get_relationship_network',
    contact_name='Dupont-ABC-0001'
)

# Create contact
contact = frappe.get_doc({
    'doctype': 'MA Contact',
    'first_name': 'Pierre',
    'last_name': 'Dupont',
    'email': 'pierre@abc.com',
    'company': 'ABC Corp'
})
contact.insert()
```

### cURL
```bash
curl -X GET \
  -H "Authorization: token YOUR_API_KEY" \
  "https://your-instance.frappe.cloud/api/method/ma_advisory.contact_management.api.get_relationship_network?contact_name=Dupont-ABC-0001"
```

---

## Best Practices

1. **Pagination**: Always use limit and skip for large result sets
2. **Caching**: Cache frequently accessed data like contacts and companies
3. **Rate limiting**: Implement back-off strategies for rate-limited responses
4. **Error handling**: Always handle validation and permission errors
5. **Webhooks**: Use webhooks instead of polling for real-time updates
6. **Batch operations**: Use bulk insert for importing multiple records
7. **Field selection**: Only request fields you need using `fields` parameter

---

## Versions

- **v2.0**: Contact management, document management, relationship intelligence
- **v1.0**: Deal management, valuation, due diligence

---

## Support

For API issues and questions:
- GitHub Issues: https://github.com/mitchlabeetch/turbo-octo-robot/issues
- Documentation: https://github.com/mitchlabeetch/turbo-octo-robot/wiki
- Email: contact@example.com
