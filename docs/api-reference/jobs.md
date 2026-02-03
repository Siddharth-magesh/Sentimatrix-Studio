# Scrape Jobs API

The Jobs API allows you to manage scrape jobs - the background tasks that collect and analyze data from targets.

## Endpoints

### List Jobs

Get all jobs for a project.

```
GET /api/v1/projects/{project_id}/jobs
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page |
| `status` | string | - | Filter: pending, running, completed, failed, cancelled |
| `source` | string | - | Filter: manual, scheduled, api |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "job_abc123def456",
      "project_id": "proj_xyz789",
      "status": "completed",
      "source": "manual",
      "config": {
        "max_results_per_target": 100,
        "targets": ["tgt_1", "tgt_2"]
      },
      "progress": {
        "total_targets": 2,
        "completed_targets": 2,
        "total_results": 180,
        "percentage": 100
      },
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:35:00Z",
      "duration_seconds": 300,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

---

### Create Job (Start Scrape)

Start a new scrape job.

```
POST /api/v1/projects/{project_id}/jobs
```

**Request Body:**

```json
{
  "target_ids": ["tgt_1", "tgt_2"],
  "max_results_per_target": 100
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_ids` | array | No | Specific targets (omit for all) |
| `max_results_per_target` | integer | No | Override project setting |

**Response:** `201 Created`

```json
{
  "id": "job_abc123def456",
  "project_id": "proj_xyz789",
  "status": "pending",
  "source": "manual",
  "config": {
    "max_results_per_target": 100,
    "targets": ["tgt_1", "tgt_2"]
  },
  "progress": {
    "total_targets": 2,
    "completed_targets": 0,
    "total_results": 0,
    "percentage": 0
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `NO_TARGETS` | Project has no targets |
| 400 | `JOB_RUNNING` | Another job is already running |
| 400 | `RATE_LIMITED` | Daily job limit exceeded |

---

### Get Job

Get a specific job with full details.

```
GET /api/v1/jobs/{job_id}
```

**Response:** `200 OK`

```json
{
  "id": "job_abc123def456",
  "project_id": "proj_xyz789",
  "status": "running",
  "source": "scheduled",
  "schedule_id": "sch_xyz123",
  "config": {
    "max_results_per_target": 100,
    "targets": ["tgt_1", "tgt_2", "tgt_3"]
  },
  "progress": {
    "total_targets": 3,
    "completed_targets": 1,
    "current_target": "tgt_2",
    "total_results": 85,
    "percentage": 45
  },
  "target_status": [
    {
      "target_id": "tgt_1",
      "status": "completed",
      "results_count": 85,
      "duration_seconds": 45
    },
    {
      "target_id": "tgt_2",
      "status": "running",
      "results_count": 42
    },
    {
      "target_id": "tgt_3",
      "status": "pending",
      "results_count": 0
    }
  ],
  "started_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Cancel Job

Cancel a running or pending job.

```
POST /api/v1/jobs/{job_id}/cancel
```

**Response:** `200 OK`

```json
{
  "id": "job_abc123def456",
  "status": "cancelled",
  "progress": {
    "total_targets": 3,
    "completed_targets": 1,
    "total_results": 85,
    "percentage": 33
  },
  "cancelled_at": "2024-01-15T10:32:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `CANNOT_CANCEL` | Job is not running or pending |

---

### Retry Job

Retry a failed job.

```
POST /api/v1/jobs/{job_id}/retry
```

**Response:** `201 Created`

Creates a new job with the same configuration.

```json
{
  "id": "job_new123456",
  "project_id": "proj_xyz789",
  "status": "pending",
  "source": "retry",
  "retry_of": "job_abc123def456",
  ...
}
```

---

### Get Job Logs

Get execution logs for a job.

```
GET /api/v1/jobs/{job_id}/logs
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | string | - | Filter: info, warning, error |
| `limit` | integer | 100 | Max log entries |

**Response:** `200 OK`

```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "info",
      "message": "Job started",
      "target_id": null
    },
    {
      "timestamp": "2024-01-15T10:30:01Z",
      "level": "info",
      "message": "Scraping target: amazon.com/dp/B09V3KXJPB",
      "target_id": "tgt_1"
    },
    {
      "timestamp": "2024-01-15T10:30:45Z",
      "level": "info",
      "message": "Target completed: 85 results",
      "target_id": "tgt_1"
    },
    {
      "timestamp": "2024-01-15T10:31:00Z",
      "level": "warning",
      "message": "Rate limited, waiting 5 seconds",
      "target_id": "tgt_2"
    }
  ]
}
```

---

## Job Object

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique job identifier |
| `project_id` | string | Parent project ID |
| `status` | string | pending, running, completed, failed, cancelled |
| `source` | string | manual, scheduled, api, retry |
| `schedule_id` | string | Schedule that triggered (if scheduled) |
| `retry_of` | string | Original job ID (if retry) |
| `config` | object | Job configuration |
| `progress` | object | Current progress |
| `target_status` | array | Per-target status |
| `error` | object | Error details (if failed) |
| `started_at` | datetime | When job started |
| `completed_at` | datetime | When job completed |
| `cancelled_at` | datetime | When job was cancelled |
| `duration_seconds` | integer | Total duration |
| `created_at` | datetime | When job was created |

### Status Values

| Status | Description |
|--------|-------------|
| `pending` | Job is queued, waiting to start |
| `running` | Job is currently executing |
| `completed` | Job finished successfully |
| `failed` | Job encountered an error |
| `cancelled` | Job was cancelled by user |

### Source Values

| Source | Description |
|--------|-------------|
| `manual` | Started via UI or API |
| `scheduled` | Started by scheduler |
| `api` | Started via external API call |
| `retry` | Retry of a failed job |

---

## WebSocket Updates

Subscribe to real-time job updates:

```
WS /api/v1/jobs/{job_id}/ws
```

**Message Format:**

```json
{
  "type": "progress",
  "data": {
    "job_id": "job_abc123",
    "status": "running",
    "percentage": 45,
    "current_target": "tgt_2",
    "results_count": 127
  }
}
```

**Event Types:**

| Type | Description |
|------|-------------|
| `progress` | Progress update |
| `target_started` | Started scraping a target |
| `target_completed` | Finished scraping a target |
| `target_failed` | Target scrape failed |
| `completed` | Job completed |
| `failed` | Job failed |

---

## Examples

### cURL

```bash
# Start a scrape job
curl -X POST "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/jobs" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"max_results_per_target": 100}'

# Get job status
curl "https://api.sentimatrix.io/api/v1/jobs/job_abc123" \
  -H "Authorization: Bearer TOKEN"

# Cancel job
curl -X POST "https://api.sentimatrix.io/api/v1/jobs/job_abc123/cancel" \
  -H "Authorization: Bearer TOKEN"

# List jobs
curl "https://api.sentimatrix.io/api/v1/projects/proj_xyz789/jobs?status=completed" \
  -H "Authorization: Bearer TOKEN"
```

### Python

```python
import requests
import time

headers = {"Authorization": f"Bearer {token}"}

# Start job
job = requests.post(
    f"https://api.sentimatrix.io/api/v1/projects/{project_id}/jobs",
    headers=headers,
    json={"max_results_per_target": 100}
).json()

job_id = job["id"]
print(f"Job started: {job_id}")

# Poll for completion
while True:
    status = requests.get(
        f"https://api.sentimatrix.io/api/v1/jobs/{job_id}",
        headers=headers
    ).json()

    print(f"Progress: {status['progress']['percentage']}%")

    if status["status"] in ["completed", "failed", "cancelled"]:
        break

    time.sleep(5)

print(f"Job {status['status']}: {status['progress']['total_results']} results")
```

### JavaScript with WebSocket

```javascript
const headers = { 'Authorization': `Bearer ${token}` };

// Start job
const job = await fetch(
  `https://api.sentimatrix.io/api/v1/projects/${projectId}/jobs`,
  {
    method: 'POST',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ max_results_per_target: 100 }),
  }
).then(r => r.json());

// Connect to WebSocket for updates
const ws = new WebSocket(
  `wss://api.sentimatrix.io/api/v1/jobs/${job.id}/ws?token=${token}`
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'progress') {
    console.log(`Progress: ${message.data.percentage}%`);
  }

  if (message.type === 'completed') {
    console.log(`Done! ${message.data.results_count} results`);
    ws.close();
  }

  if (message.type === 'failed') {
    console.error(`Failed: ${message.data.error}`);
    ws.close();
  }
};
```
