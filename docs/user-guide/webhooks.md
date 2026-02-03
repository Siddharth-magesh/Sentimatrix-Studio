# Webhooks

Webhooks allow Sentimatrix Studio to send real-time notifications to your applications when events occur. This guide explains how to set up and use webhooks effectively.

## Overview

Webhooks are HTTP callbacks that notify your servers when specific events happen in Sentimatrix Studio. Use them to:

- Trigger automated workflows
- Update external dashboards
- Send notifications to Slack, Discord, etc.
- Integrate with CI/CD pipelines
- Sync data with external systems

## Creating a Webhook

### Basic Setup

1. Go to **Settings** > **Webhooks**
2. Click **Create Webhook**
3. Enter the webhook URL (must be HTTPS)
4. Select the events to subscribe to
5. Optionally add a secret for verification
6. Click **Create**

### Webhook Configuration

| Field | Description | Required |
|-------|-------------|----------|
| **URL** | Your endpoint (HTTPS only) | Yes |
| **Events** | Which events trigger the webhook | Yes |
| **Secret** | Shared secret for signature verification | No |
| **Label** | Friendly name for identification | No |
| **Enabled** | Whether the webhook is active | Yes |

## Available Events

### Job Events

| Event | Triggered When |
|-------|----------------|
| `job.started` | A scrape job begins |
| `job.completed` | A scrape job finishes successfully |
| `job.failed` | A scrape job fails |
| `job.progress` | Job progress updates (25%, 50%, 75%) |

### Project Events

| Event | Triggered When |
|-------|----------------|
| `project.created` | A new project is created |
| `project.updated` | Project settings are changed |
| `project.deleted` | A project is deleted |

### Target Events

| Event | Triggered When |
|-------|----------------|
| `target.created` | A new target is added |
| `target.updated` | Target settings are changed |
| `target.deleted` | A target is removed |

### Result Events

| Event | Triggered When |
|-------|----------------|
| `results.new` | New results are available |
| `results.analyzed` | Results have been analyzed |

## Webhook Payload

### Payload Structure

All webhooks send JSON payloads with this structure:

```json
{
  "event": "job.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    // Event-specific data
  },
  "metadata": {
    "webhook_id": "wh_123abc",
    "delivery_id": "del_456def"
  }
}
```

### Job Event Payloads

**job.completed:**

```json
{
  "event": "job.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job_789xyz",
    "project_id": "proj_123",
    "project_name": "iPhone Reviews",
    "status": "completed",
    "targets_scraped": 5,
    "results_count": 450,
    "duration_seconds": 120,
    "summary": {
      "positive": 280,
      "neutral": 100,
      "negative": 70,
      "average_sentiment": 0.42
    }
  }
}
```

**job.failed:**

```json
{
  "event": "job.failed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job_789xyz",
    "project_id": "proj_123",
    "project_name": "iPhone Reviews",
    "status": "failed",
    "error": "Rate limit exceeded",
    "error_code": "RATE_LIMIT",
    "targets_completed": 2,
    "targets_failed": 3
  }
}
```

## Verifying Webhooks

### Signature Verification

When you provide a secret, Sentimatrix Studio signs each webhook:

1. We compute an HMAC-SHA256 signature of the payload
2. The signature is sent in the `X-Signature-256` header
3. Verify the signature to ensure authenticity

### Verification Code Examples

**Python:**

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

**Node.js:**

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
```

### Additional Headers

Each webhook includes these headers:

| Header | Description |
|--------|-------------|
| `X-Webhook-ID` | Unique webhook identifier |
| `X-Delivery-ID` | Unique delivery attempt ID |
| `X-Signature-256` | HMAC signature (if secret set) |
| `X-Timestamp` | Unix timestamp of sending |
| `Content-Type` | Always `application/json` |
| `User-Agent` | `Sentimatrix-Webhook/1.0` |

## Managing Webhooks

### Viewing Webhooks

1. Go to **Settings** > **Webhooks**
2. See all configured webhooks
3. View status, events, and delivery stats

### Editing a Webhook

1. Click the webhook to edit
2. Modify URL, events, or secret
3. Click **Save**

### Enabling/Disabling

Toggle webhooks without deleting:

1. Click the toggle next to the webhook
2. Disabled webhooks don't receive events
3. Re-enable anytime

### Deleting a Webhook

1. Click the webhook to open details
2. Click **Delete**
3. Confirm the deletion

## Delivery and Retries

### Delivery Behavior

- Webhooks are sent within seconds of events
- Timeout: 30 seconds per attempt
- Expected response: 2xx status code

### Retry Policy

Failed deliveries are retried with exponential backoff:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |

After 5 failures, the delivery is marked as failed.

### Viewing Delivery History

1. Go to **Settings** > **Webhooks**
2. Click the webhook
3. View **Delivery History**
4. See status, response, and timing for each attempt

## Testing Webhooks

### Test Delivery

Send a test payload to verify your endpoint:

1. Open the webhook details
2. Click **Send Test**
3. Check your endpoint received the payload
4. View the response in delivery history

### Test Payload

Test events use this format:

```json
{
  "event": "webhook.test",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "message": "This is a test webhook delivery"
  }
}
```

## Integration Examples

### Slack

Send job notifications to Slack:

1. Create a Slack Incoming Webhook
2. Add the Slack webhook URL to Sentimatrix Studio
3. Subscribe to job events

**Slack-compatible payload transformation** (use a middleware service):

```json
{
  "text": "Job completed: iPhone Reviews",
  "attachments": [{
    "color": "good",
    "fields": [
      {"title": "Results", "value": "450", "short": true},
      {"title": "Sentiment", "value": "+0.42", "short": true}
    ]
  }]
}
```

### Zapier

Connect to 5000+ apps via Zapier:

1. Create a Zapier Webhook (Catch Hook)
2. Add the Zapier URL to Sentimatrix Studio
3. Build your Zap to process events

### Custom Dashboard

Update a real-time dashboard:

1. Create an endpoint on your server
2. Subscribe to result events
3. Push updates to your dashboard via WebSocket

## Troubleshooting

### Webhooks not received

- Verify the URL is accessible from the internet
- Check that HTTPS is valid (not self-signed)
- Ensure firewall allows incoming requests
- Review delivery history for error details

### Signature verification failing

- Ensure you're using the raw payload (not parsed)
- Verify the secret matches exactly
- Check for encoding issues (UTF-8)
- Compare timing-safe to prevent timing attacks

### Duplicate events

- Use the `X-Delivery-ID` header to deduplicate
- Store processed delivery IDs
- Implement idempotent event handlers

### Events delayed

- Check system status for processing delays
- Large jobs may batch events
- High volume periods may slow delivery

## Best Practices

1. **Always verify signatures** in production
2. **Respond quickly** (under 5 seconds) to avoid timeouts
3. **Process asynchronously** - acknowledge receipt, then process
4. **Handle duplicates** - events may be sent multiple times
5. **Log everything** - keep records for debugging
6. **Use HTTPS** - required for security
7. **Rotate secrets** periodically
8. **Monitor delivery rates** - set up alerts for failures
