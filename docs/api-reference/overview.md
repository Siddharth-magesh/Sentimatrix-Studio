# API Reference

Welcome to the Sentimatrix Studio API documentation. This API allows you to programmatically access all features of Sentimatrix Studio.

## Base URL

All API endpoints are relative to:

```
https://api.sentimatrix.io/api/v1
```

For self-hosted installations, replace with your domain.

## Authentication

The API uses JWT (JSON Web Token) authentication.

### Obtaining Tokens

```bash
curl -X POST https://api.sentimatrix.io/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Tokens

Include the access token in the Authorization header:

```bash
curl https://api.sentimatrix.io/api/v1/projects \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Refreshing Tokens

Access tokens expire after 30 minutes. Use the refresh token to get new tokens:

```bash
curl -X POST https://api.sentimatrix.io/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

## Rate Limiting

API requests are rate limited to ensure fair usage:

| Endpoint Type | Limit |
|---------------|-------|
| Authentication | 10 requests / 15 minutes |
| Read endpoints | 100 requests / minute |
| Write endpoints | 50 requests / minute |

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## Response Format

### Successful Responses

All successful responses return JSON with appropriate HTTP status codes:

- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST (resource created)
- `204 No Content`: Successful DELETE

```json
{
  "id": "proj_abc123",
  "name": "My Project",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Paginated Responses

List endpoints return paginated results:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

### Error Responses

Errors return appropriate HTTP status codes with details:

```json
{
  "detail": "Project not found",
  "code": "NOT_FOUND"
}
```

Common error codes:

| Status | Description |
|--------|-------------|
| `400 Bad Request` | Invalid input data |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | Resource doesn't exist |
| `422 Unprocessable Entity` | Validation error |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Server error |

## Pagination

List endpoints support pagination parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | 1 | Page number (1-indexed) |
| `per_page` | 20 | Items per page (max 100) |

Example:

```bash
curl "https://api.sentimatrix.io/api/v1/projects?page=2&per_page=10" \
  -H "Authorization: Bearer TOKEN"
```

## Filtering

Many endpoints support filtering via query parameters:

```bash
# Filter results by sentiment
curl "https://api.sentimatrix.io/api/v1/results?sentiment=positive" \
  -H "Authorization: Bearer TOKEN"

# Filter by date range
curl "https://api.sentimatrix.io/api/v1/results?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer TOKEN"
```

## Sorting

Use the `sort` parameter to order results:

```bash
# Sort by created date descending
curl "https://api.sentimatrix.io/api/v1/projects?sort=-created_at" \
  -H "Authorization: Bearer TOKEN"

# Sort ascending (no prefix)
curl "https://api.sentimatrix.io/api/v1/projects?sort=name" \
  -H "Authorization: Bearer TOKEN"
```

## API Endpoints

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate tokens
- `GET /auth/me` - Get current user

### Projects
- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `GET /projects/{id}/statistics` - Get project stats

### Targets
- `GET /projects/{id}/targets` - List targets
- `POST /projects/{id}/targets` - Add target
- `GET /targets/{id}` - Get target
- `PUT /targets/{id}` - Update target
- `DELETE /targets/{id}` - Delete target

### Scrape Jobs
- `GET /projects/{id}/jobs` - List jobs
- `POST /projects/{id}/jobs` - Start scrape
- `GET /jobs/{id}` - Get job status
- `POST /jobs/{id}/cancel` - Cancel job

### Results
- `GET /projects/{id}/results` - List results
- `GET /results/{id}` - Get result
- `DELETE /results/{id}` - Delete result
- `POST /results/export` - Export results

### Schedules
- `GET /schedules` - List schedules
- `POST /schedules` - Create schedule
- `GET /schedules/project/{id}` - Get project schedule
- `PUT /schedules/project/{id}` - Update schedule
- `DELETE /schedules/project/{id}` - Delete schedule
- `POST /schedules/project/{id}/toggle` - Toggle schedule

### Webhooks
- `GET /webhooks` - List webhooks
- `POST /webhooks` - Create webhook
- `GET /webhooks/{id}` - Get webhook
- `PUT /webhooks/{id}` - Update webhook
- `DELETE /webhooks/{id}` - Delete webhook
- `POST /webhooks/{id}/toggle` - Toggle webhook
- `GET /webhooks/events/available` - List available events

### Settings
- `GET /settings/llm/providers` - List LLM providers
- `GET /settings/llm/providers/{id}` - Get provider details
- `GET /settings/api-keys` - List API keys
- `POST /settings/api-keys` - Add API key
- `DELETE /settings/api-keys/{provider}` - Delete API key
- `GET /settings/presets` - List presets
- `GET /settings/presets/{id}` - Get preset details

### Dashboard
- `GET /dashboard/statistics` - Get dashboard stats
- `GET /dashboard/recent-activity` - Get recent activity

## SDKs

Official SDKs are available for popular languages:

- **Python**: `pip install sentimatrix-sdk`
- **JavaScript/TypeScript**: `npm install @sentimatrix/sdk`

### Python Example

```python
from sentimatrix import SentimatrixClient

client = SentimatrixClient(
    api_key="your-api-key",
    base_url="https://api.sentimatrix.io"
)

# List projects
projects = client.projects.list()

# Create project
project = client.projects.create(
    name="My Project",
    preset="standard"
)

# Start scrape
job = client.jobs.create(project_id=project.id)

# Get results
results = client.results.list(project_id=project.id)
```

### JavaScript Example

```javascript
import { SentimatrixClient } from '@sentimatrix/sdk';

const client = new SentimatrixClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.sentimatrix.io',
});

// List projects
const projects = await client.projects.list();

// Create project
const project = await client.projects.create({
  name: 'My Project',
  preset: 'standard',
});

// Start scrape
const job = await client.jobs.create({ projectId: project.id });

// Get results
const results = await client.results.list({ projectId: project.id });
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:

```
https://api.sentimatrix.io/openapi.json
```

Interactive documentation (Swagger UI):

```
https://api.sentimatrix.io/docs
```

Alternative documentation (ReDoc):

```
https://api.sentimatrix.io/redoc
```
