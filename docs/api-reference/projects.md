# Projects API

The Projects API allows you to manage sentiment analysis projects.

## Endpoints

### List Projects

Get all projects for the authenticated user.

```
GET /api/v1/projects
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (max 100) |
| `status` | string | - | Filter by status: active, paused, error, archived |
| `sort` | string | -created_at | Sort field (prefix with - for descending) |
| `search` | string | - | Search in name and description |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "proj_abc123def456",
      "name": "iPhone 15 Reviews",
      "description": "Analyzing iPhone 15 product reviews",
      "status": "active",
      "preset": "standard",
      "config": {
        "scraper": {
          "platforms": ["amazon", "reddit"],
          "commercial_provider": null,
          "proxies_enabled": false
        },
        "llm": {
          "provider": "groq",
          "model": "llama-3.1-70b-versatile",
          "temperature": 0.3
        },
        "analysis": {
          "sentiment_classes": 5,
          "emotions_enabled": true,
          "summarization_enabled": true,
          "insights_enabled": true
        },
        "limits": {
          "max_reviews_per_target": 100,
          "max_requests_per_day": 1000,
          "rate_limit_delay": 1.0
        }
      },
      "statistics": {
        "total_targets": 3,
        "total_results": 245,
        "average_sentiment": 0.42,
        "last_scrape": "2024-01-15T10:30:00Z"
      },
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

---

### Create Project

Create a new project.

```
POST /api/v1/projects
```

**Request Body:**

```json
{
  "name": "My New Project",
  "description": "Optional description",
  "preset": "standard"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Project name (1-100 chars) |
| `description` | string | No | Project description |
| `preset` | string | Yes* | Preset ID (starter, standard, advanced, budget, enterprise) |
| `config` | object | Yes* | Custom configuration (if preset not used) |

*Either `preset` or `config` is required.

**Using Custom Config:**

```json
{
  "name": "Custom Project",
  "config": {
    "scraper": {
      "platforms": ["amazon", "steam"],
      "commercial_provider": "scraperapi",
      "proxies_enabled": true
    },
    "llm": {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "temperature": 0.2,
      "max_tokens": 500
    },
    "analysis": {
      "sentiment_classes": 5,
      "emotions_enabled": true,
      "summarization_enabled": true,
      "insights_enabled": true
    },
    "limits": {
      "max_reviews_per_target": 200,
      "max_requests_per_day": 5000,
      "rate_limit_delay": 0.5
    }
  }
}
```

**Response:** `201 Created`

Returns the created project object.

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `NAME_EXISTS` | Project name already exists |
| 400 | `INVALID_PRESET` | Preset ID not found |
| 422 | `VALIDATION_ERROR` | Invalid configuration |

---

### Get Project

Get a specific project by ID.

```
GET /api/v1/projects/{project_id}
```

**Response:** `200 OK`

Returns the full project object with statistics.

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `NOT_FOUND` | Project not found |

---

### Update Project

Update a project's configuration.

```
PUT /api/v1/projects/{project_id}
```

**Request Body:**

```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "config": {
    "llm": {
      "temperature": 0.5
    }
  }
}
```

All fields are optional. Only provided fields are updated.

**Response:** `200 OK`

Returns the updated project object.

---

### Delete Project

Permanently delete a project and all associated data.

```
DELETE /api/v1/projects/{project_id}
```

**Response:** `204 No Content`

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `JOBS_RUNNING` | Cannot delete while jobs are running |

---

### Archive Project

Soft-delete a project (can be restored).

```
POST /api/v1/projects/{project_id}/archive
```

**Response:** `200 OK`

```json
{
  "id": "proj_abc123def456",
  "status": "archived",
  ...
}
```

---

### Restore Project

Restore an archived project.

```
POST /api/v1/projects/{project_id}/restore
```

**Response:** `200 OK`

Returns the project with status "active".

---

### Get Project Statistics

Get detailed statistics for a project.

```
GET /api/v1/projects/{project_id}/statistics
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start of date range (ISO 8601) |
| `end_date` | string | End of date range (ISO 8601) |

**Response:** `200 OK`

```json
{
  "total_targets": 5,
  "total_results": 523,
  "total_jobs": 12,
  "sentiment": {
    "average": 0.42,
    "distribution": {
      "very_positive": 89,
      "positive": 187,
      "neutral": 112,
      "negative": 98,
      "very_negative": 37
    }
  },
  "emotions": {
    "joy": 156,
    "admiration": 89,
    "anger": 45,
    "sadness": 23,
    "surprise": 67
  },
  "trends": {
    "daily": [
      {"date": "2024-01-15", "count": 45, "avg_sentiment": 0.38},
      {"date": "2024-01-14", "count": 52, "avg_sentiment": 0.45}
    ]
  },
  "top_insights": {
    "pros": ["Great battery life", "Excellent camera"],
    "cons": ["Expensive", "No headphone jack"]
  },
  "last_scrape": "2024-01-15T10:30:00Z",
  "next_scheduled": "2024-01-16T09:00:00Z"
}
```

---

### Duplicate Project

Create a copy of a project with a new name.

```
POST /api/v1/projects/{project_id}/duplicate
```

**Request Body:**

```json
{
  "name": "Copy of My Project"
}
```

**Response:** `201 Created`

Returns the new project object.

---

## Project Configuration

### Scraper Config

```json
{
  "scraper": {
    "platforms": ["amazon", "steam", "youtube", "reddit", "trustpilot", "yelp"],
    "commercial_provider": "scraperapi|scrapingbee|apify|brightdata|null",
    "proxies_enabled": true,
    "user_agent_rotation": true
  }
}
```

### LLM Config

```json
{
  "llm": {
    "provider": "groq|openai|anthropic",
    "model": "model-id",
    "temperature": 0.3,
    "max_tokens": 500,
    "timeout": 30
  }
}
```

### Analysis Config

```json
{
  "analysis": {
    "sentiment_classes": 3|5,
    "emotions_enabled": true,
    "summarization_enabled": true,
    "insights_enabled": true,
    "language_detection": true
  }
}
```

### Limits Config

```json
{
  "limits": {
    "max_reviews_per_target": 100,
    "max_requests_per_day": 1000,
    "rate_limit_delay": 1.0,
    "timeout": 30
  }
}
```

---

## Examples

### cURL

```bash
# Create project
curl -X POST https://api.sentimatrix.io/api/v1/projects \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Reviews",
    "preset": "standard"
  }'

# List projects with filter
curl "https://api.sentimatrix.io/api/v1/projects?status=active&sort=-updated_at" \
  -H "Authorization: Bearer TOKEN"

# Update project
curl -X PUT https://api.sentimatrix.io/api/v1/projects/proj_abc123 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "llm": {"temperature": 0.5}
    }
  }'
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Create project
project = requests.post(
    "https://api.sentimatrix.io/api/v1/projects",
    headers=headers,
    json={"name": "Product Reviews", "preset": "standard"}
).json()

# List projects
projects = requests.get(
    "https://api.sentimatrix.io/api/v1/projects",
    headers=headers,
    params={"status": "active"}
).json()

# Get statistics
stats = requests.get(
    f"https://api.sentimatrix.io/api/v1/projects/{project['id']}/statistics",
    headers=headers
).json()
```

### JavaScript

```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};

// Create project
const project = await fetch('https://api.sentimatrix.io/api/v1/projects', {
  method: 'POST',
  headers,
  body: JSON.stringify({ name: 'Product Reviews', preset: 'standard' }),
}).then(r => r.json());

// List projects
const projects = await fetch(
  'https://api.sentimatrix.io/api/v1/projects?status=active',
  { headers }
).then(r => r.json());

// Get statistics
const stats = await fetch(
  `https://api.sentimatrix.io/api/v1/projects/${project.id}/statistics`,
  { headers }
).then(r => r.json());
```
