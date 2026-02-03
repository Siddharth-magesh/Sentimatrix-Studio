# Results API

The Results API allows you to query and manage sentiment analysis results.

## Endpoints

### List Results

Get results for a project with filtering and pagination.

```
GET /api/v1/projects/{project_id}/results
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (max 100) |
| `sentiment` | string | - | Filter: positive, neutral, negative, very_positive, very_negative |
| `emotion` | string | - | Filter by emotion: joy, anger, sadness, etc. |
| `platform` | string | - | Filter by platform: amazon, steam, youtube, etc. |
| `target_id` | string | - | Filter by specific target |
| `start_date` | string | - | Start of date range (ISO 8601) |
| `end_date` | string | - | End of date range (ISO 8601) |
| `min_score` | float | - | Minimum sentiment score (-1 to 1) |
| `max_score` | float | - | Maximum sentiment score (-1 to 1) |
| `search` | string | - | Search in text content |
| `sort` | string | -created_at | Sort field |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "res_abc123def456",
      "project_id": "proj_xyz789",
      "target_id": "tgt_123456",
      "job_id": "job_789abc",
      "platform": "amazon",
      "source_url": "https://amazon.com/dp/B123456",
      "text": "Great product! The battery life is amazing and the camera quality exceeds my expectations.",
      "author": "JohnDoe123",
      "rating": 5,
      "date": "2024-01-10",
      "sentiment": {
        "label": "positive",
        "score": 0.85,
        "confidence": 0.92
      },
      "emotions": [
        {"emotion": "joy", "confidence": 0.88},
        {"emotion": "admiration", "confidence": 0.72}
      ],
      "metadata": {
        "helpful_votes": 42,
        "verified_purchase": true
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 523,
  "page": 1,
  "per_page": 20,
  "pages": 27,
  "aggregations": {
    "sentiment_distribution": {
      "positive": 312,
      "neutral": 125,
      "negative": 86
    },
    "average_score": 0.42
  }
}
```

---

### Get Result

Get a specific result by ID.

```
GET /api/v1/results/{result_id}
```

**Response:** `200 OK`

```json
{
  "id": "res_abc123def456",
  "project_id": "proj_xyz789",
  "target_id": "tgt_123456",
  "job_id": "job_789abc",
  "platform": "amazon",
  "source_url": "https://amazon.com/dp/B123456",
  "text": "Great product! The battery life is amazing and the camera quality exceeds my expectations.",
  "author": "JohnDoe123",
  "rating": 5,
  "date": "2024-01-10",
  "sentiment": {
    "label": "positive",
    "score": 0.85,
    "confidence": 0.92,
    "raw_response": "..."
  },
  "emotions": [
    {"emotion": "joy", "confidence": 0.88},
    {"emotion": "admiration", "confidence": 0.72},
    {"emotion": "excitement", "confidence": 0.65}
  ],
  "insights": {
    "pros": ["battery life", "camera quality"],
    "cons": [],
    "topics": ["performance", "photography"]
  },
  "metadata": {
    "helpful_votes": 42,
    "verified_purchase": true,
    "review_id": "R123ABC"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "analyzed_at": "2024-01-15T10:30:05Z"
}
```

---

### Delete Result

Delete a specific result.

```
DELETE /api/v1/results/{result_id}
```

**Response:** `204 No Content`

---

### Bulk Delete Results

Delete multiple results at once.

```
POST /api/v1/results/bulk-delete
```

**Request Body:**

```json
{
  "result_ids": ["res_abc123", "res_def456", "res_ghi789"]
}
```

Or delete by filter:

```json
{
  "project_id": "proj_xyz789",
  "filters": {
    "sentiment": "negative",
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  }
}
```

**Response:** `200 OK`

```json
{
  "deleted_count": 45
}
```

---

### Export Results

Export results to a file.

```
POST /api/v1/results/export
```

**Request Body:**

```json
{
  "project_id": "proj_xyz789",
  "format": "csv",
  "filters": {
    "sentiment": "positive",
    "start_date": "2024-01-01"
  },
  "fields": ["text", "sentiment", "emotions", "author", "date"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | string | Required. Project to export from |
| `format` | string | csv, json, xlsx |
| `filters` | object | Same as list filters |
| `fields` | array | Fields to include (optional, defaults to all) |

**Response:** `200 OK`

For small exports (< 1000 results), returns the file directly.

For large exports, returns a job:

```json
{
  "export_id": "exp_abc123",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

### Get Export Status

```
GET /api/v1/results/exports/{export_id}
```

**Response:** `200 OK`

```json
{
  "export_id": "exp_abc123",
  "status": "completed",
  "download_url": "https://storage.sentimatrix.io/exports/exp_abc123.csv",
  "expires_at": "2024-01-16T10:30:00Z",
  "file_size": 1234567,
  "results_count": 5000
}
```

---

### Get Result Aggregations

Get aggregated statistics for results.

```
GET /api/v1/projects/{project_id}/results/aggregations
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `group_by` | string | date, platform, target, emotion |
| `start_date` | string | Start of date range |
| `end_date` | string | End of date range |
| `granularity` | string | hour, day, week, month (for date grouping) |

**Response:** `200 OK`

Group by date:

```json
{
  "group_by": "date",
  "granularity": "day",
  "data": [
    {
      "date": "2024-01-15",
      "count": 45,
      "average_sentiment": 0.42,
      "sentiment_distribution": {
        "positive": 28,
        "neutral": 10,
        "negative": 7
      }
    },
    {
      "date": "2024-01-14",
      "count": 52,
      "average_sentiment": 0.38
    }
  ]
}
```

Group by platform:

```json
{
  "group_by": "platform",
  "data": [
    {
      "platform": "amazon",
      "count": 320,
      "average_sentiment": 0.45
    },
    {
      "platform": "steam",
      "count": 180,
      "average_sentiment": 0.32
    }
  ]
}
```

Group by emotion:

```json
{
  "group_by": "emotion",
  "data": [
    {"emotion": "joy", "count": 156, "average_confidence": 0.78},
    {"emotion": "admiration", "count": 89, "average_confidence": 0.72},
    {"emotion": "anger", "count": 45, "average_confidence": 0.81}
  ]
}
```

---

### Re-analyze Result

Re-run sentiment analysis on a result with updated settings.

```
POST /api/v1/results/{result_id}/reanalyze
```

**Request Body (optional):**

```json
{
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.2
  }
}
```

**Response:** `200 OK`

Returns the updated result with new analysis.

---

## Result Object

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique result identifier |
| `project_id` | string | Parent project ID |
| `target_id` | string | Parent target ID |
| `job_id` | string | Job that scraped this result |
| `platform` | string | Source platform |
| `source_url` | string | Original content URL |
| `text` | string | Review/comment text |
| `author` | string | Author username (if available) |
| `rating` | integer | Star rating (if available) |
| `date` | string | Original post date |
| `sentiment` | object | Sentiment analysis result |
| `emotions` | array | Detected emotions |
| `insights` | object | Extracted insights |
| `metadata` | object | Platform-specific metadata |
| `created_at` | datetime | When result was scraped |
| `analyzed_at` | datetime | When analysis completed |

### Sentiment Object

```json
{
  "label": "positive",      // very_positive, positive, neutral, negative, very_negative
  "score": 0.85,            // -1.0 to 1.0
  "confidence": 0.92        // 0.0 to 1.0
}
```

### Emotion Object

```json
{
  "emotion": "joy",         // joy, love, admiration, anger, fear, sadness, etc.
  "confidence": 0.88        // 0.0 to 1.0
}
```

### Insights Object

```json
{
  "pros": ["battery life", "camera quality"],
  "cons": ["price", "no headphone jack"],
  "topics": ["performance", "value"],
  "summary": "Overall positive review..."
}
```

---

## Examples

### cURL

```bash
# List results with filters
curl "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/results?sentiment=positive&per_page=50" \
  -H "Authorization: Bearer TOKEN"

# Export to CSV
curl -X POST https://api.sentimatrix.io/api/v1/results/export \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xyz789",
    "format": "csv"
  }' \
  -o results.csv

# Get aggregations by date
curl "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/results/aggregations?group_by=date&granularity=day" \
  -H "Authorization: Bearer TOKEN"
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Get positive results
results = requests.get(
    "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/results",
    headers=headers,
    params={
        "sentiment": "positive",
        "min_score": 0.5,
        "per_page": 100
    }
).json()

# Export results
export = requests.post(
    "https://api.sentimatrix.io/api/v1/results/export",
    headers=headers,
    json={
        "project_id": "proj_xyz789",
        "format": "csv",
        "filters": {"sentiment": "negative"}
    }
)

# For large exports, poll status
if export.json().get("export_id"):
    export_id = export.json()["export_id"]
    while True:
        status = requests.get(
            f"https://api.sentimatrix.io/api/v1/results/exports/{export_id}",
            headers=headers
        ).json()
        if status["status"] == "completed":
            # Download file
            break
        time.sleep(5)
```

### JavaScript

```javascript
const headers = { 'Authorization': `Bearer ${token}` };

// Get results with pagination
async function getAllResults(projectId) {
  const results = [];
  let page = 1;

  while (true) {
    const response = await fetch(
      `https://api.sentimatrix.io/api/v1/projects/${projectId}/results?page=${page}&per_page=100`,
      { headers }
    );
    const data = await response.json();

    results.push(...data.items);

    if (page >= data.pages) break;
    page++;
  }

  return results;
}

// Get emotion breakdown
const aggregations = await fetch(
  `https://api.sentimatrix.io/api/v1/projects/${projectId}/results/aggregations?group_by=emotion`,
  { headers }
).then(r => r.json());
```
