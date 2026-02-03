# Targets API

The Targets API allows you to manage scrape targets (URLs) within projects.

## Endpoints

### List Targets

Get all targets for a project.

```
GET /api/v1/projects/{project_id}/targets
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page |
| `platform` | string | - | Filter by platform |
| `status` | string | - | Filter: active, paused, error |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "tgt_abc123def456",
      "project_id": "proj_xyz789",
      "url": "https://www.amazon.com/dp/B09V3KXJPB",
      "platform": "amazon",
      "platform_id": "B09V3KXJPB",
      "name": "iPhone 14 Pro",
      "status": "active",
      "last_scraped": "2024-01-15T10:30:00Z",
      "results_count": 150,
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

### Create Target

Add a new target to a project.

```
POST /api/v1/projects/{project_id}/targets
```

**Request Body:**

```json
{
  "url": "https://www.amazon.com/dp/B09V3KXJPB",
  "name": "iPhone 14 Pro"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Valid URL to scrape |
| `name` | string | No | Friendly name (auto-detected if not provided) |

**Response:** `201 Created`

```json
{
  "id": "tgt_abc123def456",
  "project_id": "proj_xyz789",
  "url": "https://www.amazon.com/dp/B09V3KXJPB",
  "platform": "amazon",
  "platform_id": "B09V3KXJPB",
  "name": "iPhone 14 Pro",
  "status": "active",
  "results_count": 0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Platform Auto-Detection:**

The API automatically detects the platform from the URL:

| URL Pattern | Platform |
|-------------|----------|
| `amazon.com/dp/*` | amazon |
| `store.steampowered.com/app/*` | steam |
| `youtube.com/watch?v=*` | youtube |
| `reddit.com/r/*/comments/*` | reddit |
| `trustpilot.com/review/*` | trustpilot |
| `yelp.com/biz/*` | yelp |
| `google.com/maps/place/*` | google_reviews |

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_URL` | URL format is invalid |
| 400 | `UNSUPPORTED_PLATFORM` | Platform not supported |
| 400 | `DUPLICATE_TARGET` | URL already exists in project |

---

### Bulk Create Targets

Add multiple targets at once.

```
POST /api/v1/projects/{project_id}/targets/bulk
```

**Request Body:**

```json
{
  "targets": [
    {"url": "https://amazon.com/dp/B09V3KXJPB"},
    {"url": "https://amazon.com/dp/B0BDHWDR12"},
    {"url": "https://store.steampowered.com/app/1245620"}
  ]
}
```

**Response:** `201 Created`

```json
{
  "created": 3,
  "failed": 0,
  "targets": [
    {"id": "tgt_1", "url": "...", "status": "created"},
    {"id": "tgt_2", "url": "...", "status": "created"},
    {"id": "tgt_3", "url": "...", "status": "created"}
  ],
  "errors": []
}
```

If some targets fail:

```json
{
  "created": 2,
  "failed": 1,
  "targets": [...],
  "errors": [
    {"url": "invalid-url", "error": "Invalid URL format"}
  ]
}
```

---

### Get Target

Get a specific target.

```
GET /api/v1/targets/{target_id}
```

**Response:** `200 OK`

Returns the full target object with statistics.

---

### Update Target

Update a target's configuration.

```
PUT /api/v1/targets/{target_id}
```

**Request Body:**

```json
{
  "name": "Updated Name",
  "status": "paused"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Friendly name |
| `status` | string | active, paused |

**Response:** `200 OK`

---

### Delete Target

Remove a target from the project.

```
DELETE /api/v1/targets/{target_id}
```

**Response:** `204 No Content`

---

### Get Target Statistics

Get detailed statistics for a target.

```
GET /api/v1/targets/{target_id}/statistics
```

**Response:** `200 OK`

```json
{
  "target_id": "tgt_abc123",
  "total_results": 150,
  "sentiment": {
    "average": 0.45,
    "distribution": {
      "positive": 85,
      "neutral": 40,
      "negative": 25
    }
  },
  "emotions": {
    "joy": 45,
    "admiration": 30,
    "anger": 12
  },
  "scrape_history": [
    {
      "job_id": "job_123",
      "date": "2024-01-15T10:30:00Z",
      "results_count": 50,
      "status": "completed"
    }
  ],
  "last_scraped": "2024-01-15T10:30:00Z"
}
```

---

## Target Object

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique target identifier |
| `project_id` | string | Parent project ID |
| `url` | string | Target URL |
| `platform` | string | Detected platform |
| `platform_id` | string | Platform-specific ID (ASIN, app ID, etc.) |
| `name` | string | Friendly name |
| `status` | string | active, paused, error |
| `last_scraped` | datetime | Last scrape timestamp |
| `results_count` | integer | Total results scraped |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Supported Platforms

| Platform | URL Pattern | ID Extracted |
|----------|-------------|--------------|
| `amazon` | `/dp/{ASIN}` | ASIN |
| `steam` | `/app/{appid}` | App ID |
| `youtube` | `/watch?v={videoid}` | Video ID |
| `reddit` | `/r/{subreddit}/comments/{postid}` | Post ID |
| `trustpilot` | `/review/{domain}` | Domain |
| `yelp` | `/biz/{business}` | Business ID |
| `google_reviews` | `/maps/place/{place}` | Place ID |

---

## Examples

### cURL

```bash
# Add target
curl -X POST "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/targets" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://amazon.com/dp/B09V3KXJPB"}'

# Bulk add targets
curl -X POST "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/targets/bulk" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targets": [
      {"url": "https://amazon.com/dp/B09V3KXJPB"},
      {"url": "https://amazon.com/dp/B0BDHWDR12"}
    ]
  }'

# List targets
curl "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/targets?platform=amazon" \
  -H "Authorization: Bearer TOKEN"

# Delete target
curl -X DELETE "https://api.sentimatrix.io/api/v1/targets/tgt_abc123" \
  -H "Authorization: Bearer TOKEN"
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Add target
target = requests.post(
    f"https://api.sentimatrix.io/api/v1/projects/{project_id}/targets",
    headers=headers,
    json={"url": "https://amazon.com/dp/B09V3KXJPB"}
).json()

# Bulk add from list
urls = [
    "https://amazon.com/dp/B09V3KXJPB",
    "https://amazon.com/dp/B0BDHWDR12",
    "https://store.steampowered.com/app/1245620"
]

result = requests.post(
    f"https://api.sentimatrix.io/api/v1/projects/{project_id}/targets/bulk",
    headers=headers,
    json={"targets": [{"url": url} for url in urls]}
).json()

print(f"Created: {result['created']}, Failed: {result['failed']}")
```

### JavaScript

```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};

// Add single target
const target = await fetch(
  `https://api.sentimatrix.io/api/v1/projects/${projectId}/targets`,
  {
    method: 'POST',
    headers,
    body: JSON.stringify({ url: 'https://amazon.com/dp/B09V3KXJPB' }),
  }
).then(r => r.json());

// Add multiple targets
const urls = [
  'https://amazon.com/dp/B09V3KXJPB',
  'https://amazon.com/dp/B0BDHWDR12',
];

const result = await fetch(
  `https://api.sentimatrix.io/api/v1/projects/${projectId}/targets/bulk`,
  {
    method: 'POST',
    headers,
    body: JSON.stringify({ targets: urls.map(url => ({ url })) }),
  }
).then(r => r.json());
```
