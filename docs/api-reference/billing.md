# Billing API

The Billing API allows you to manage subscriptions, view usage statistics, and handle payments.

## Subscription

### Get Subscription

Get the current user's subscription details.

```
GET /api/v1/billing/subscription
```

**Response:** `200 OK`

```json
{
  "id": "sub_abc123def456",
  "plan_id": "pro",
  "plan_name": "Pro",
  "status": "active",
  "current_period_start": "2024-01-01T00:00:00Z",
  "current_period_end": "2024-02-01T00:00:00Z",
  "cancel_at_period_end": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Subscription Statuses:**

| Status | Description |
|--------|-------------|
| `active` | Subscription is active |
| `trialing` | In trial period |
| `past_due` | Payment failed, still active |
| `canceled` | Canceled but not expired |
| `incomplete` | Initial payment pending |
| `unpaid` | Multiple failed payments |

---

### Cancel Subscription

Cancel the current subscription at period end.

```
POST /api/v1/billing/subscription/cancel
```

**Response:** `200 OK`

```json
{
  "success": true,
  "cancels_at": "2024-02-01T00:00:00Z",
  "message": "Subscription will be canceled at the end of the billing period"
}
```

---

### Resume Subscription

Resume a canceled subscription before it expires.

```
POST /api/v1/billing/subscription/resume
```

**Response:** `200 OK`

```json
{
  "id": "sub_abc123def456",
  "plan_id": "pro",
  "status": "active",
  "cancel_at_period_end": false
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `NOT_CANCELABLE` | Subscription is not scheduled for cancellation |
| 400 | `ALREADY_EXPIRED` | Subscription has already expired |

---

## Usage Statistics

### Get Usage Stats

Get usage statistics for the current billing period.

```
GET /api/v1/billing/usage
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | month | day, week, month, year |

**Response:** `200 OK`

```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "projects": {
    "used": 5,
    "limit": 10,
    "percentage": 50
  },
  "results": {
    "used": 2500,
    "limit": 10000,
    "percentage": 25
  },
  "api_calls": {
    "used": 1500,
    "limit": 50000,
    "percentage": 3
  },
  "storage_mb": {
    "used": 125,
    "limit": 1000,
    "percentage": 12.5
  },
  "scrape_jobs": {
    "used": 45,
    "limit": 100,
    "percentage": 45
  },
  "history": [
    {
      "date": "2024-01-15",
      "api_calls": 150,
      "results": 250,
      "scrape_jobs": 3
    },
    {
      "date": "2024-01-14",
      "api_calls": 120,
      "results": 200,
      "scrape_jobs": 2
    }
  ]
}
```

---

## Plans

### List Plans

Get all available subscription plans.

```
GET /api/v1/billing/plans
```

**Response:** `200 OK`

```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "description": "Get started with basic features",
      "price_monthly": 0,
      "price_yearly": 0,
      "features": [
        "1 project",
        "100 results/month",
        "Basic sentiment analysis",
        "Community support"
      ],
      "limits": {
        "projects": 1,
        "results_per_month": 100,
        "api_calls_per_month": 1000,
        "storage_mb": 100,
        "scrape_jobs_per_month": 10
      }
    },
    {
      "id": "pro",
      "name": "Pro",
      "description": "For professionals and small teams",
      "price_monthly": 29,
      "price_yearly": 290,
      "is_popular": true,
      "features": [
        "10 projects",
        "10,000 results/month",
        "Full sentiment + emotions",
        "Scheduling",
        "Webhooks",
        "Priority support"
      ],
      "limits": {
        "projects": 10,
        "results_per_month": 10000,
        "api_calls_per_month": 50000,
        "storage_mb": 1000,
        "scrape_jobs_per_month": 100
      }
    },
    {
      "id": "business",
      "name": "Business",
      "description": "For growing businesses",
      "price_monthly": 99,
      "price_yearly": 990,
      "features": [
        "Unlimited projects",
        "50,000 results/month",
        "Full feature access",
        "Team collaboration",
        "API access",
        "Dedicated support"
      ],
      "limits": {
        "projects": -1,
        "results_per_month": 50000,
        "api_calls_per_month": 200000,
        "storage_mb": 5000,
        "scrape_jobs_per_month": 500
      }
    },
    {
      "id": "enterprise",
      "name": "Enterprise",
      "description": "For large organizations",
      "price_monthly": null,
      "price_yearly": null,
      "contact_sales": true,
      "features": [
        "Unlimited everything",
        "Custom integrations",
        "SLA guarantee",
        "Dedicated account manager",
        "On-premise option"
      ],
      "limits": {
        "projects": -1,
        "results_per_month": -1,
        "api_calls_per_month": -1,
        "storage_mb": -1,
        "scrape_jobs_per_month": -1
      }
    }
  ]
}
```

Note: `-1` indicates unlimited.

---

## Checkout

### Create Checkout Session

Create a Stripe checkout session for subscription.

```
POST /api/v1/billing/checkout
```

**Request Body:**

```json
{
  "plan_id": "pro",
  "billing_cycle": "monthly",
  "success_url": "https://app.sentimatrix.io/billing?success=true",
  "cancel_url": "https://app.sentimatrix.io/billing?canceled=true"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_id` | string | Yes | Plan to subscribe to |
| `billing_cycle` | string | No | monthly (default) or yearly |
| `success_url` | string | No | Redirect URL after success |
| `cancel_url` | string | No | Redirect URL after cancel |

**Response:** `200 OK`

```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_abc123...",
  "session_id": "cs_test_abc123def456"
}
```

Redirect the user to `checkout_url` to complete payment.

---

### Get Customer Portal URL

Get a Stripe customer portal URL for managing billing.

```
GET /api/v1/billing/portal
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `return_url` | string | URL to return to after portal |

**Response:** `200 OK`

```json
{
  "portal_url": "https://billing.stripe.com/p/session/abc123..."
}
```

The customer portal allows users to:
- Update payment method
- View invoices
- Change subscription
- Cancel subscription

---

## Invoices

### List Invoices

Get all invoices for the authenticated user.

```
GET /api/v1/billing/invoices
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page |
| `status` | string | - | Filter: paid, open, draft, void |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "inv_abc123def456",
      "number": "INV-2024-0015",
      "amount": 2900,
      "currency": "usd",
      "status": "paid",
      "period_start": "2024-01-01T00:00:00Z",
      "period_end": "2024-01-31T23:59:59Z",
      "paid_at": "2024-01-01T00:05:00Z",
      "pdf_url": "https://pay.stripe.com/invoice/abc123/pdf",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

**Invoice Statuses:**

| Status | Description |
|--------|-------------|
| `draft` | Not yet finalized |
| `open` | Awaiting payment |
| `paid` | Successfully paid |
| `void` | Canceled |
| `uncollectible` | Payment failed |

---

### Get Invoice

Get a specific invoice.

```
GET /api/v1/billing/invoices/{invoice_id}
```

**Response:** `200 OK`

```json
{
  "id": "inv_abc123def456",
  "number": "INV-2024-0015",
  "amount": 2900,
  "amount_paid": 2900,
  "amount_remaining": 0,
  "currency": "usd",
  "status": "paid",
  "description": "Pro Plan - Monthly",
  "line_items": [
    {
      "description": "Pro Plan (Jan 1 - Jan 31, 2024)",
      "amount": 2900,
      "quantity": 1
    }
  ],
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-01-31T23:59:59Z",
  "paid_at": "2024-01-01T00:05:00Z",
  "pdf_url": "https://pay.stripe.com/invoice/abc123/pdf",
  "hosted_invoice_url": "https://invoice.stripe.com/i/abc123",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Examples

### cURL

```bash
# Get subscription
curl "https://api.sentimatrix.io/api/v1/billing/subscription" \
  -H "Authorization: Bearer TOKEN"

# Get usage stats
curl "https://api.sentimatrix.io/api/v1/billing/usage?period=month" \
  -H "Authorization: Bearer TOKEN"

# List plans
curl "https://api.sentimatrix.io/api/v1/billing/plans" \
  -H "Authorization: Bearer TOKEN"

# Create checkout session
curl -X POST "https://api.sentimatrix.io/api/v1/billing/checkout" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "pro",
    "billing_cycle": "yearly"
  }'

# Cancel subscription
curl -X POST "https://api.sentimatrix.io/api/v1/billing/subscription/cancel" \
  -H "Authorization: Bearer TOKEN"

# Get customer portal URL
curl "https://api.sentimatrix.io/api/v1/billing/portal?return_url=https://app.sentimatrix.io/billing" \
  -H "Authorization: Bearer TOKEN"

# List invoices
curl "https://api.sentimatrix.io/api/v1/billing/invoices" \
  -H "Authorization: Bearer TOKEN"
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Get subscription
subscription = requests.get(
    "https://api.sentimatrix.io/api/v1/billing/subscription",
    headers=headers
).json()

print(f"Plan: {subscription['plan_name']}, Status: {subscription['status']}")

# Get usage
usage = requests.get(
    "https://api.sentimatrix.io/api/v1/billing/usage",
    headers=headers,
    params={"period": "month"}
).json()

print(f"Results used: {usage['results']['used']}/{usage['results']['limit']}")

# List plans
plans = requests.get(
    "https://api.sentimatrix.io/api/v1/billing/plans",
    headers=headers
).json()

for plan in plans["plans"]:
    price = plan["price_monthly"] or "Contact sales"
    print(f"{plan['name']}: ${price}/month")

# Upgrade to Pro
checkout = requests.post(
    "https://api.sentimatrix.io/api/v1/billing/checkout",
    headers=headers,
    json={
        "plan_id": "pro",
        "billing_cycle": "monthly"
    }
).json()

print(f"Redirect to: {checkout['checkout_url']}")
```

### JavaScript

```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};

// Get subscription
const subscription = await fetch(
  'https://api.sentimatrix.io/api/v1/billing/subscription',
  { headers }
).then(r => r.json());

console.log(`Plan: ${subscription.plan_name}, Status: ${subscription.status}`);

// Get usage
const usage = await fetch(
  'https://api.sentimatrix.io/api/v1/billing/usage?period=month',
  { headers }
).then(r => r.json());

console.log(`Results: ${usage.results.used}/${usage.results.limit}`);

// Create checkout session and redirect
const checkout = await fetch('https://api.sentimatrix.io/api/v1/billing/checkout', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    plan_id: 'pro',
    billing_cycle: 'yearly',
    success_url: window.location.origin + '/billing?success=true',
    cancel_url: window.location.origin + '/billing?canceled=true',
  }),
}).then(r => r.json());

// Redirect to Stripe checkout
window.location.href = checkout.checkout_url;
```

---

## Webhooks

Stripe sends webhooks for billing events. Handle these in your backend:

| Event | Description |
|-------|-------------|
| `customer.subscription.created` | New subscription |
| `customer.subscription.updated` | Subscription changed |
| `customer.subscription.deleted` | Subscription canceled |
| `invoice.paid` | Payment successful |
| `invoice.payment_failed` | Payment failed |

Configure your webhook endpoint in the Stripe dashboard.
