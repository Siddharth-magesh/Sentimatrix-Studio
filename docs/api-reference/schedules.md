# Schedules API

The Schedules API allows you to create and manage automated scrape schedules for projects.

## Endpoints

### List Schedules

Get all schedules for the authenticated user.

```
GET /api/v1/schedules
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page |
| `enabled` | boolean | - | Filter by enabled status |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "sch_abc123def456",
      "project_id": "proj_xyz789",
      "project_name": "iPhone Reviews",
      "frequency": "daily",
      "time": "09:00",
      "timezone": "America/New_York",
      "enabled": true,
      "next_run": "2024-01-16T14:00:00Z",
      "last_run": "2024-01-15T14:00:00Z",
      "last_status": "completed",
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T14:00:00Z"
    }
  ],
  "total": 3,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

---

### Create Schedule

Create a new schedule for a project.

```
POST /api/v1/schedules
```

**Request Body:**

```json
{
  "project_id": "proj_xyz789",
  "frequency": "daily",
  "time": "09:00",
  "timezone": "America/New_York"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | Yes | Project to schedule |
| `frequency` | string | Yes | hourly, daily, weekly, monthly |
| `time` | string | Yes* | Time in HH:MM format (not for hourly) |
| `timezone` | string | No | IANA timezone (default: UTC) |
| `day_of_week` | integer | Yes** | 0-6 for weekly (0=Monday) |
| `day_of_month` | integer | Yes** | 1-28 for monthly |

*Required for daily, weekly, monthly frequencies
**Required for weekly and monthly frequencies respectively

**Response:** `201 Created`

```json
{
  "id": "sch_abc123def456",
  "project_id": "proj_xyz789",
  "frequency": "daily",
  "time": "09:00",
  "timezone": "America/New_York",
  "enabled": true,
  "next_run": "2024-01-16T14:00:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `SCHEDULE_EXISTS` | Project already has a schedule |
| 400 | `INVALID_FREQUENCY` | Invalid frequency value |
| 400 | `INVALID_TIME` | Invalid time format |
| 400 | `INVALID_TIMEZONE` | Invalid timezone |
| 404 | `PROJECT_NOT_FOUND` | Project doesn't exist |

---

### Get Project Schedule

Get the schedule for a specific project.

```
GET /api/v1/schedules/project/{project_id}
```

**Response:** `200 OK`

```json
{
  "id": "sch_abc123def456",
  "project_id": "proj_xyz789",
  "frequency": "daily",
  "time": "09:00",
  "timezone": "America/New_York",
  "enabled": true,
  "next_run": "2024-01-16T14:00:00Z",
  "last_run": "2024-01-15T14:00:00Z",
  "last_status": "completed",
  "run_history": [
    {
      "job_id": "job_123",
      "started_at": "2024-01-15T14:00:00Z",
      "completed_at": "2024-01-15T14:15:00Z",
      "status": "completed",
      "results_count": 150
    },
    {
      "job_id": "job_122",
      "started_at": "2024-01-14T14:00:00Z",
      "completed_at": "2024-01-14T14:12:00Z",
      "status": "completed",
      "results_count": 145
    }
  ],
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `NOT_FOUND` | No schedule for this project |

---

### Update Schedule

Update a project's schedule.

```
PUT /api/v1/schedules/project/{project_id}
```

**Request Body:**

```json
{
  "frequency": "weekly",
  "time": "10:00",
  "day_of_week": 1,
  "timezone": "Europe/London"
}
```

All fields are optional. Only provided fields are updated.

**Response:** `200 OK`

Returns the updated schedule object.

---

### Delete Schedule

Remove a project's schedule.

```
DELETE /api/v1/schedules/project/{project_id}
```

**Response:** `204 No Content`

---

### Toggle Schedule

Enable or disable a schedule.

```
POST /api/v1/schedules/project/{project_id}/toggle
```

**Request Body (optional):**

```json
{
  "enabled": false
}
```

If no body is provided, the schedule's enabled state is toggled.

**Response:** `200 OK`

```json
{
  "id": "sch_abc123def456",
  "enabled": false,
  "next_run": null
}
```

---

### Run Schedule Now

Trigger an immediate run of a scheduled job.

```
POST /api/v1/schedules/project/{project_id}/run
```

**Response:** `202 Accepted`

```json
{
  "job_id": "job_abc123",
  "status": "queued",
  "message": "Scrape job started"
}
```

---

## Schedule Frequencies

### Hourly

Runs every hour at the start of the hour.

```json
{
  "frequency": "hourly"
}
```

### Daily

Runs once per day at the specified time.

```json
{
  "frequency": "daily",
  "time": "09:00",
  "timezone": "America/New_York"
}
```

### Weekly

Runs once per week on the specified day and time.

```json
{
  "frequency": "weekly",
  "time": "09:00",
  "day_of_week": 1,
  "timezone": "America/New_York"
}
```

Days: 0=Monday, 1=Tuesday, ..., 6=Sunday

### Monthly

Runs once per month on the specified day and time.

```json
{
  "frequency": "monthly",
  "time": "09:00",
  "day_of_month": 15,
  "timezone": "America/New_York"
}
```

Day must be 1-28 to ensure all months are supported.

---

## Schedule Object

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique schedule identifier |
| `project_id` | string | Associated project ID |
| `frequency` | string | hourly, daily, weekly, monthly |
| `time` | string | Time in HH:MM format |
| `timezone` | string | IANA timezone |
| `day_of_week` | integer | 0-6 for weekly schedules |
| `day_of_month` | integer | 1-28 for monthly schedules |
| `enabled` | boolean | Whether schedule is active |
| `next_run` | datetime | Next scheduled execution |
| `last_run` | datetime | Last execution time |
| `last_status` | string | completed, failed |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

---

## Common Timezones

| Timezone | UTC Offset | Region |
|----------|------------|--------|
| `UTC` | +00:00 | Universal |
| `America/New_York` | -05:00 | US Eastern |
| `America/Los_Angeles` | -08:00 | US Pacific |
| `Europe/London` | +00:00 | UK |
| `Europe/Paris` | +01:00 | Central Europe |
| `Asia/Tokyo` | +09:00 | Japan |
| `Asia/Shanghai` | +08:00 | China |
| `Australia/Sydney` | +11:00 | Australia Eastern |

---

## Examples

### cURL

```bash
# Create daily schedule
curl -X POST "https://api.sentimatrix.io/api/v1/schedules" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xyz789",
    "frequency": "daily",
    "time": "09:00",
    "timezone": "America/New_York"
  }'

# Create weekly schedule (Mondays at 10am)
curl -X POST "https://api.sentimatrix.io/api/v1/schedules" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xyz789",
    "frequency": "weekly",
    "time": "10:00",
    "day_of_week": 0,
    "timezone": "UTC"
  }'

# Toggle schedule off
curl -X POST "https://api.sentimatrix.io/api/v1/schedules/project/proj_xyz789/toggle" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Run schedule immediately
curl -X POST "https://api.sentimatrix.io/api/v1/schedules/project/proj_xyz789/run" \
  -H "Authorization: Bearer TOKEN"

# Delete schedule
curl -X DELETE "https://api.sentimatrix.io/api/v1/schedules/project/proj_xyz789" \
  -H "Authorization: Bearer TOKEN"
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Create a daily schedule
schedule = requests.post(
    "https://api.sentimatrix.io/api/v1/schedules",
    headers=headers,
    json={
        "project_id": "proj_xyz789",
        "frequency": "daily",
        "time": "09:00",
        "timezone": "America/New_York"
    }
).json()

print(f"Next run: {schedule['next_run']}")

# Get schedule for a project
schedule = requests.get(
    f"https://api.sentimatrix.io/api/v1/schedules/project/{project_id}",
    headers=headers
).json()

# Toggle schedule
result = requests.post(
    f"https://api.sentimatrix.io/api/v1/schedules/project/{project_id}/toggle",
    headers=headers,
    json={"enabled": False}
).json()

# Trigger immediate run
job = requests.post(
    f"https://api.sentimatrix.io/api/v1/schedules/project/{project_id}/run",
    headers=headers
).json()

print(f"Job started: {job['job_id']}")
```

### JavaScript

```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};

// Create a weekly schedule
const schedule = await fetch('https://api.sentimatrix.io/api/v1/schedules', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    project_id: 'proj_xyz789',
    frequency: 'weekly',
    time: '10:00',
    day_of_week: 0, // Monday
    timezone: 'Europe/London',
  }),
}).then(r => r.json());

console.log(`Next run: ${schedule.next_run}`);

// Toggle schedule
const toggled = await fetch(
  `https://api.sentimatrix.io/api/v1/schedules/project/${projectId}/toggle`,
  {
    method: 'POST',
    headers,
    body: JSON.stringify({ enabled: !schedule.enabled }),
  }
).then(r => r.json());

// Run immediately
const job = await fetch(
  `https://api.sentimatrix.io/api/v1/schedules/project/${projectId}/run`,
  { method: 'POST', headers }
).then(r => r.json());
```
