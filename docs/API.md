# API Documentation - M&A Advisory ERP

## Overview

The M&A Advisory ERP provides a comprehensive REST API for headless integration. All endpoints follow RESTful conventions and return JSON responses.

## Authentication

### API Key/Secret

```bash
# Generate API keys for a user
bench --site ma-advisory.local add-user-api-keys username@example.com
```

Use the generated key and secret in requests:

```python
import requests

headers = {
    'Authorization': f'token {api_key}:{api_secret}'
}

response = requests.get('https://your-domain.com/api/resource/Deal', headers=headers)
```

### Session-based (for web apps)

```python
# Login
response = requests.post('https://your-domain.com/api/method/login', data={
    'usr': 'user@example.com',
    'pwd': 'password'
})

# Use session cookie in subsequent requests
session = requests.Session()
session.post('https://your-domain.com/api/method/login', data={'usr': 'user@example.com', 'pwd': 'password'})
response = session.get('https://your-domain.com/api/resource/Deal')
```

## Core Resources

### Deal (Transaction)

#### List Deals

```
GET /api/resource/Deal
```

Query parameters:
- `fields`: Comma-separated list of fields
- `filters`: JSON array of filters
- `limit_start`: Pagination start (default: 0)
- `limit_page_length`: Items per page (default: 20)

Example:

```bash
curl -X GET "https://your-domain.com/api/resource/Deal?fields=[\"name\",\"deal_name\",\"value\",\"stage\"]&filters=[[\"status\",\"=\",\"Actif\"]]" \
  -H "Authorization: token api_key:api_secret"
```

Response:

```json
{
  "data": [
    {
      "name": "DEAL-2024-001",
      "deal_name": "Acquisition ABC",
      "value": 10000000,
      "stage": "Due Diligence"
    }
  ]
}
```

#### Get Deal

```
GET /api/resource/Deal/{name}
```

Example:

```bash
curl -X GET "https://your-domain.com/api/resource/Deal/DEAL-2024-001" \
  -H "Authorization: token api_key:api_secret"
```

Response:

```json
{
  "data": {
    "name": "DEAL-2024-001",
    "deal_name": "Acquisition ABC",
    "deal_type": "Acquisition",
    "stage": "Due Diligence",
    "status": "Actif",
    "client": "CLIENT-001",
    "target_company": "ABC SAS",
    "value": 10000000,
    "currency": "EUR",
    "probability": 70,
    "expected_close_date": "2024-06-30",
    "lead_advisor": "user@example.com"
  }
}
```

#### Create Deal

```
POST /api/resource/Deal
```

Request body:

```json
{
  "deal_name": "Acquisition ABC",
  "deal_type": "Acquisition",
  "stage": "Origination",
  "status": "Actif",
  "value": 10000000,
  "currency": "EUR",
  "expected_close_date": "2024-06-30"
}
```

Example:

```bash
curl -X POST "https://your-domain.com/api/resource/Deal" \
  -H "Authorization: token api_key:api_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "deal_name": "Acquisition ABC",
    "deal_type": "Acquisition",
    "stage": "Origination",
    "status": "Actif",
    "value": 10000000,
    "currency": "EUR"
  }'
```

#### Update Deal

```
PUT /api/resource/Deal/{name}
```

Request body (partial update):

```json
{
  "stage": "Offres Indicatives",
  "probability": 60
}
```

#### Delete Deal

```
DELETE /api/resource/Deal/{name}
```

### Valuation

#### List Valuations

```
GET /api/resource/Valuation
```

#### Get Valuation

```
GET /api/resource/Valuation/{name}
```

#### Create Valuation

```
POST /api/resource/Valuation
```

Request body:

```json
{
  "deal": "DEAL-2024-001",
  "company_name": "ABC SAS",
  "valuation_date": "2024-01-15",
  "valuation_method": "Multiples de Marché",
  "revenue": 50000000,
  "ebitda": 8000000,
  "ebitda_multiple": 8.5,
  "debt": 5000000,
  "cash": 2000000
}
```

Response includes auto-calculated fields:

```json
{
  "data": {
    "name": "VAL-2024-001",
    "enterprise_value": 68000000,
    "equity_value": 65000000
  }
}
```

## Custom Methods

### Get Deal Pipeline

Get active deals with key information.

```
GET /api/method/ma_advisory.api.get_deal_pipeline
```

Response:

```json
{
  "message": [
    {
      "name": "DEAL-2024-001",
      "deal_name": "Acquisition ABC",
      "stage": "Due Diligence",
      "value": 10000000,
      "probability": 70,
      "expected_close_date": "2024-06-30"
    }
  ]
}
```

### Get Valuation Data

Get all valuations for a deal.

```
GET /api/method/ma_advisory.api.get_valuation_data?deal_name=DEAL-2024-001
```

Response:

```json
{
  "message": [
    {
      "name": "VAL-2024-001",
      "company_name": "ABC SAS",
      "valuation_method": "Multiples de Marché",
      "enterprise_value": 68000000,
      "equity_value": 65000000
    }
  ]
}
```

### Get Due Diligence Status

Get due diligence progress by category.

```
GET /api/method/ma_advisory.api.get_due_diligence_status?deal_name=DEAL-2024-001
```

Response:

```json
{
  "message": {
    "Financière": {
      "total": 25,
      "completed": 18,
      "pending": 7
    },
    "Juridique": {
      "total": 15,
      "completed": 10,
      "pending": 5
    }
  }
}
```

## JavaScript API (for Browser)

When using the Frappe web interface, the `MAAApi` global object provides convenient methods:

```javascript
// Get a deal
MAAApi.getDeal('DEAL-2024-001').then(r => {
    console.log(r.message);
});

// Get valuations for a deal
MAAApi.getValuation('DEAL-2024-001').then(r => {
    console.log(r.message);
});

// Get due diligence status
MAAApi.getDueDiligenceStatus('DEAL-2024-001').then(r => {
    console.log(r.message);
});
```

## Webhooks

Configure webhooks for real-time notifications:

1. Go to **Integrations > Webhook**
2. Create new webhook
3. Configure:
   - Document Type: `Deal`
   - Events: `on_update`, `after_insert`
   - Request URL: Your webhook endpoint
   - Request Structure: JSON

Example webhook payload:

```json
{
  "doctype": "Deal",
  "name": "DEAL-2024-001",
  "data": {
    "deal_name": "Acquisition ABC",
    "stage": "Offres Finales",
    "value": 10000000
  }
}
```

## Error Handling

All API responses include standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:

```json
{
  "exc": "[Error details]",
  "exc_type": "ValidationError",
  "_server_messages": "[\"Error message\"]"
}
```

## Rate Limiting

Default rate limits:
- 100 requests per minute per user
- 1000 requests per hour per user

Exceeded rate limits return `429 Too Many Requests`.

## CORS

CORS is configured in hooks.py:

```python
allow_cors = "*"  # Or specific origins
```

## Examples

### Python Client

```python
import requests
import json

class MAAClient:
    def __init__(self, base_url, api_key, api_secret):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'token {api_key}:{api_secret}',
            'Content-Type': 'application/json'
        }
    
    def get_deals(self, filters=None):
        url = f"{self.base_url}/api/resource/Deal"
        params = {}
        if filters:
            params['filters'] = json.dumps(filters)
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def create_deal(self, data):
        url = f"{self.base_url}/api/resource/Deal"
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def get_pipeline(self):
        url = f"{self.base_url}/api/method/ma_advisory.api.get_deal_pipeline"
        response = requests.get(url, headers=self.headers)
        return response.json()

# Usage
client = MAAClient('https://your-domain.com', 'api_key', 'api_secret')
deals = client.get_deals(filters=[["status", "=", "Actif"]])
print(deals)
```

### JavaScript Client

```javascript
class MAAClient {
    constructor(baseUrl, apiKey, apiSecret) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `token ${apiKey}:${apiSecret}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getDeals(filters = null) {
        const url = new URL(`${this.baseUrl}/api/resource/Deal`);
        if (filters) {
            url.searchParams.append('filters', JSON.stringify(filters));
        }
        const response = await fetch(url, { headers: this.headers });
        return response.json();
    }
    
    async createDeal(data) {
        const response = await fetch(`${this.baseUrl}/api/resource/Deal`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return response.json();
    }
    
    async getPipeline() {
        const response = await fetch(
            `${this.baseUrl}/api/method/ma_advisory.api.get_deal_pipeline`,
            { headers: this.headers }
        );
        return response.json();
    }
}

// Usage
const client = new MAAClient('https://your-domain.com', 'api_key', 'api_secret');
const deals = await client.getDeals([["status", "=", "Actif"]]);
console.log(deals);
```

## Support

For API support:
- GitHub Issues: https://github.com/mitchlabeetch/turbo-octo-robot/issues
- Email: contact@example.com
