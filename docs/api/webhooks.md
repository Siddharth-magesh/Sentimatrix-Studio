# Webhooks API

## Overview

Webhooks allow you to receive real-time notifications when events occur in Sentimatrix Studio.

## Endpoints

### List Webhooks

Get all webhooks for the authenticated user.

```http
GET /v1/webhooks
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "wh_abc123",
      "name": "Slack Notifications",
      "url": "https://hooks.slack.com/services/xxx",
      "events": ["scrape.completed", "analysis.completed"],
      "active": true,
      "secret": "whsec_...xyz",
      "created_at": "2026-01-15T10:00:00Z",
      "last_triggered_at": "2026-02-01T15:30:00Z",
      "success_rate": 0.98
    }
  ]
}
```

---

### Create Webhook

Create a new webhook.

```http
POST /v1/webhooks
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Slack Notifications",
  "url": "https://hooks.slack.com/services/xxx",
  "events": ["scrape.completed", "analysis.completed"],
  "project_ids": ["proj_abc123"],
  "headers": {
    "X-Custom-Header": "value"
  },
  "secret": "my_webhook_secret"
}
```

**Configuration Options:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Webhook name |
| url | string | Yes | Webhook endpoint URL |
| events | array | Yes | Events to subscribe to |
| project_ids | array | No | Filter by projects (all if empty) |
| headers | object | No | Custom headers to include |
| secret | string | No | Signing secret (auto-generated if not provided) |

**Response (201):**

```json
{
  "success": true,
  "data": {
    "id": "wh_new456",
    "name": "Slack Notifications",
    "url": "https://hooks.slack.com/services/xxx",
    "events": ["scrape.completed", "analysis.completed"],
    "secret": "whsec_generated_secret",
    "active": true,
    "created_at": "2026-02-02T12:00:00Z"
  }
}
```

---

### Update Webhook

Update an existing webhook.

```http
PUT /v1/webhooks/{webhook_id}
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Updated Name",
  "events": ["scrape.completed"],
  "active": false
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "wh_abc123",
    "name": "Updated Name",
    "active": false,
    "updated_at": "2026-02-02T12:00:00Z"
  }
}
```

---

### Delete Webhook

Delete a webhook.

```http
DELETE /v1/webhooks/{webhook_id}
Authorization: Bearer <access_token>
```

**Response (204):**

No content.

---

### Test Webhook

Send a test event to a webhook.

```http
POST /v1/webhooks/{webhook_id}/test
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "delivered": true,
    "status_code": 200,
    "response_time_ms": 150,
    "response_body": "OK"
  }
}
```

**Error Response:**

```json
{
  "success": true,
  "data": {
    "delivered": false,
    "error": "Connection timeout",
    "status_code": null
  }
}
```

---

### Get Webhook Logs

Get delivery logs for a webhook.

```http
GET /v1/webhooks/{webhook_id}/logs
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page |
| status | string | - | Filter by status (success, failed) |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "log_abc123",
      "event": "scrape.completed",
      "status": "success",
      "status_code": 200,
      "response_time_ms": 145,
      "triggered_at": "2026-02-01T15:30:00Z",
      "payload_size_bytes": 1250
    },
    {
      "id": "log_def456",
      "event": "scrape.completed",
      "status": "failed",
      "status_code": 500,
      "error": "Internal Server Error",
      "triggered_at": "2026-02-01T14:00:00Z",
      "retry_count": 3
    }
  ]
}
```

---

## Webhook Events

### Available Events

| Event | Description |
|-------|-------------|
| `scrape.started` | Scraping job started |
| `scrape.progress` | Scraping progress update (25%, 50%, 75%) |
| `scrape.completed` | Scraping job completed |
| `scrape.failed` | Scraping job failed |
| `analysis.started` | Analysis job started |
| `analysis.completed` | Analysis job completed |
| `analysis.failed` | Analysis job failed |
| `project.created` | New project created |
| `project.updated` | Project configuration updated |
| `project.deleted` | Project deleted |
| `alert.sentiment_drop` | Sentiment dropped below threshold |
| `alert.negative_spike` | Spike in negative sentiment |

---

## Webhook Payload

### Payload Structure

```json
{
  "id": "evt_abc123",
  "event": "scrape.completed",
  "timestamp": "2026-02-02T12:00:00Z",
  "data": {
    "project_id": "proj_abc123",
    "project_name": "Amazon Tracker",
    "job_id": "job_def456",
    "results_count": 150,
    "duration_seconds": 45
  }
}
```

### Event-Specific Payloads

**scrape.completed:**

```json
{
  "event": "scrape.completed",
  "data": {
    "project_id": "proj_abc123",
    "project_name": "Amazon Tracker",
    "job_id": "job_def456",
    "status": "completed",
    "targets_scraped": 5,
    "results_count": 150,
    "new_results": 25,
    "duration_seconds": 45,
    "errors": []
  }
}
```

**analysis.completed:**

```json
{
  "event": "analysis.completed",
  "data": {
    "project_id": "proj_abc123",
    "project_name": "Amazon Tracker",
    "job_id": "analysis_ghi789",
    "results_analyzed": 150,
    "summary": {
      "avg_sentiment": 0.72,
      "positive_count": 105,
      "neutral_count": 30,
      "negative_count": 15
    }
  }
}
```

**alert.sentiment_drop:**

```json
{
  "event": "alert.sentiment_drop",
  "data": {
    "project_id": "proj_abc123",
    "project_name": "Amazon Tracker",
    "target_id": "tgt_xyz789",
    "target_label": "Product A",
    "previous_sentiment": 0.75,
    "current_sentiment": 0.55,
    "change": -0.20,
    "period": "24h"
  }
}
```

---

## Webhook Security

### Signature Verification

All webhook requests include a signature header for verification:

```
X-Sentimatrix-Signature: sha256=xxx
```

**Verification (Python):**

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

**Verification (Node.js):**

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
    const expected = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');
    return signature === `sha256=${expected}`;
}
```

### Headers Included

| Header | Description |
|--------|-------------|
| `X-Sentimatrix-Signature` | HMAC signature |
| `X-Sentimatrix-Event` | Event type |
| `X-Sentimatrix-Delivery` | Unique delivery ID |
| `X-Sentimatrix-Timestamp` | Event timestamp |
| `Content-Type` | application/json |

---

## Retry Policy

Failed webhook deliveries are retried automatically:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |

After 5 failed attempts, the delivery is marked as failed.

A webhook is considered failed if:
- Connection timeout (30 seconds)
- HTTP status code >= 400
- Network error

---

## WebSocket Events

In addition to HTTP webhooks, real-time events are available via WebSocket.

### Connection

```javascript
const ws = new WebSocket('wss://api.studio.sentimatrix.dev/v1/ws?token=ACCESS_TOKEN');

ws.onopen = () => {
    // Subscribe to project events
    ws.send(JSON.stringify({
        type: 'subscribe',
        project_id: 'proj_abc123'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data.event, data.data);
};
```

### WebSocket Events

Same events as HTTP webhooks, delivered in real-time.

### Ping/Pong

The server sends ping frames every 30 seconds. Clients should respond with pong frames to maintain the connection.
