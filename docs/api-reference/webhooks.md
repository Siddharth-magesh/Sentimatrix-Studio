# Webhooks API

The Webhooks API allows you to receive real-time notifications when events occur in Sentimatrix Studio.

## Endpoints

### List Webhooks

Get all webhooks for the authenticated user.

```
GET /api/v1/webhooks
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
      "id": "wh_abc123def456",
      "url": "https://example.com/webhook",
      "events": ["job.completed", "job.failed"],
      "enabled": true,
      "label": "Production Webhook",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "stats": {
        "total_deliveries": 150,
        "successful_deliveries": 148,
        "failed_deliveries": 2,
        "last_delivery": "2024-01-15T10:25:00Z",
        "last_status": "success"
      }
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

---

### Create Webhook

Create a new webhook.

```
POST /api/v1/webhooks
```

**Request Body:**

```json
{
  "url": "https://example.com/webhook",
  "events": ["job.completed", "job.failed"],
  "secret": "my-webhook-secret",
  "label": "Production Webhook"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | HTTPS endpoint URL |
| `events` | array | Yes | List of event types to subscribe to |
| `secret` | string | No | Shared secret for signature verification |
| `label` | string | No | Friendly label for identification |

**Response:** `201 Created`

```json
{
  "id": "wh_abc123def456",
  "url": "https://example.com/webhook",
  "events": ["job.completed", "job.failed"],
  "enabled": true,
  "label": "Production Webhook",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_URL` | URL is not valid HTTPS |
| 422 | `INVALID_EVENT` | Unknown event type |

---

### Get Webhook

Get a specific webhook.

```
GET /api/v1/webhooks/{webhook_id}
```

**Response:** `200 OK`

Returns the webhook object with delivery statistics.

---

### Update Webhook

Update a webhook's configuration.

```
PUT /api/v1/webhooks/{webhook_id}
```

**Request Body:**

```json
{
  "url": "https://new-url.com/webhook",
  "events": ["job.completed", "job.failed", "job.started"],
  "secret": "new-secret",
  "label": "Updated Label"
}
```

All fields are optional.

**Response:** `200 OK`

---

### Delete Webhook

Delete a webhook.

```
DELETE /api/v1/webhooks/{webhook_id}
```

**Response:** `204 No Content`

---

### Toggle Webhook

Enable or disable a webhook.

```
POST /api/v1/webhooks/{webhook_id}/toggle
```

**Response:** `200 OK`

```json
{
  "id": "wh_abc123def456",
  "enabled": false,
  ...
}
```

---

### Test Webhook

Send a test payload to verify the webhook endpoint.

```
POST /api/v1/webhooks/{webhook_id}/test
```

**Response:** `200 OK`

```json
{
  "success": true,
  "status_code": 200,
  "response_time_ms": 234,
  "response_body": "OK"
}
```

If the test fails:

```json
{
  "success": false,
  "error": "Connection timeout",
  "status_code": null
}
```

---

### List Available Events

Get all available webhook events.

```
GET /api/v1/webhooks/events/available
```

**Response:** `200 OK`

```json
[
  {
    "event": "job.started",
    "description": "A scrape job has started",
    "category": "jobs"
  },
  {
    "event": "job.completed",
    "description": "A scrape job has completed successfully",
    "category": "jobs"
  },
  {
    "event": "job.failed",
    "description": "A scrape job has failed",
    "category": "jobs"
  },
  {
    "event": "job.progress",
    "description": "A scrape job has made progress (25%, 50%, 75%)",
    "category": "jobs"
  },
  {
    "event": "project.created",
    "description": "A new project was created",
    "category": "projects"
  },
  {
    "event": "project.updated",
    "description": "A project was updated",
    "category": "projects"
  },
  {
    "event": "project.deleted",
    "description": "A project was deleted",
    "category": "projects"
  },
  {
    "event": "results.new",
    "description": "New results are available",
    "category": "results"
  },
  {
    "event": "results.analyzed",
    "description": "Results have been analyzed by LLM",
    "category": "results"
  }
]
```

---

### Get Delivery History

Get webhook delivery history.

```
GET /api/v1/webhooks/{webhook_id}/deliveries
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `per_page` | integer | Items per page |
| `status` | string | Filter: success, failed, pending |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "del_xyz789",
      "event": "job.completed",
      "status": "success",
      "status_code": 200,
      "request_body": "{...}",
      "response_body": "OK",
      "response_time_ms": 234,
      "attempts": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "delivered_at": "2024-01-15T10:30:01Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

---

### Retry Delivery

Retry a failed delivery.

```
POST /api/v1/webhooks/deliveries/{delivery_id}/retry
```

**Response:** `200 OK`

```json
{
  "id": "del_xyz789",
  "status": "pending",
  "attempts": 2,
  ...
}
```

---

## Webhook Payloads

### Common Structure

All webhooks share this structure:

```json
{
  "event": "job.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    // Event-specific data
  },
  "metadata": {
    "webhook_id": "wh_abc123",
    "delivery_id": "del_xyz789"
  }
}
```

### job.started

```json
{
  "event": "job.started",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job_abc123",
    "project_id": "proj_xyz789",
    "project_name": "iPhone Reviews",
    "targets_count": 5,
    "started_at": "2024-01-15T10:30:00Z"
  }
}
```

### job.completed

```json
{
  "event": "job.completed",
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "job_id": "job_abc123",
    "project_id": "proj_xyz789",
    "project_name": "iPhone Reviews",
    "status": "completed",
    "targets_scraped": 5,
    "results_count": 450,
    "duration_seconds": 300,
    "summary": {
      "positive": 280,
      "neutral": 100,
      "negative": 70,
      "average_sentiment": 0.42
    }
  }
}
```

### job.failed

```json
{
  "event": "job.failed",
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "job_id": "job_abc123",
    "project_id": "proj_xyz789",
    "project_name": "iPhone Reviews",
    "status": "failed",
    "error": "Rate limit exceeded",
    "error_code": "RATE_LIMIT",
    "targets_completed": 2,
    "targets_failed": 3,
    "partial_results": 180
  }
}
```

### results.new

```json
{
  "event": "results.new",
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "project_id": "proj_xyz789",
    "project_name": "iPhone Reviews",
    "job_id": "job_abc123",
    "new_results_count": 50,
    "total_results": 500
  }
}
```

---

## Signature Verification

When a secret is configured, webhooks include a signature header for verification.

### Headers

```
X-Webhook-ID: wh_abc123
X-Delivery-ID: del_xyz789
X-Signature-256: sha256=abc123def456...
X-Timestamp: 1705316400
Content-Type: application/json
User-Agent: Sentimatrix-Webhook/1.0
```

### Verification Algorithm

1. Get the raw request body (before JSON parsing)
2. Get the signature from `X-Signature-256` header
3. Compute HMAC-SHA256 of the body using your secret
4. Compare signatures using constant-time comparison

### Python Example

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# In your webhook handler
@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Signature-256", "")

    if not verify_webhook(body, signature, "your-secret"):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = json.loads(body)
    # Process webhook...
```

### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

// Express handler
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-signature-256'];

  if (!verifyWebhook(req.body, signature, 'your-secret')) {
    return res.status(401).send('Invalid signature');
  }

  const data = JSON.parse(req.body);
  // Process webhook...
  res.status(200).send('OK');
});
```

---

## Best Practices

1. **Always verify signatures** when using secrets
2. **Respond quickly** (within 5 seconds) to avoid timeouts
3. **Process asynchronously** - acknowledge receipt, then process
4. **Handle duplicates** - use delivery_id for idempotency
5. **Monitor failures** - set up alerts for delivery issues
6. **Use HTTPS** - webhooks only send to HTTPS endpoints
7. **Rotate secrets** periodically for security
