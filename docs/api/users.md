# Users API

## Overview

The Users API provides endpoints for managing user profiles, API keys, and account settings.

## Endpoints

### Get Current User

Get the authenticated user's profile.

```http
GET /v1/users/me
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "company": "Acme Inc",
    "avatar_url": null,
    "role": "user",
    "plan": "standard",
    "usage": {
      "projects": 3,
      "projects_limit": 10,
      "scrapes_this_month": 45,
      "scrapes_limit": 500,
      "api_calls_this_month": 1250,
      "api_calls_limit": 10000
    },
    "settings": {
      "timezone": "America/New_York",
      "email_notifications": true,
      "weekly_digest": true
    },
    "created_at": "2026-01-01T10:00:00Z",
    "last_login_at": "2026-02-02T08:00:00Z"
  }
}
```

---

### Update Current User

Update the authenticated user's profile.

```http
PUT /v1/users/me
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "John Smith",
  "company": "New Company Inc",
  "settings": {
    "timezone": "Europe/London",
    "email_notifications": false
  }
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "usr_abc123",
    "name": "John Smith",
    "company": "New Company Inc",
    "updated_at": "2026-02-02T12:00:00Z"
  }
}
```

---

### Delete Account

Delete the user's account and all associated data.

```http
DELETE /v1/users/me
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "password": "CurrentPassword123",
  "confirmation": "DELETE"
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "message": "Account scheduled for deletion",
    "deletion_date": "2026-03-02T12:00:00Z"
  }
}
```

Note: Account deletion has a 30-day grace period during which the user can recover their account.

---

### Change Password

Change the user's password.

```http
PUT /v1/users/me/password
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "current_password": "CurrentPassword123",
  "new_password": "NewSecurePass456"
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "message": "Password changed successfully"
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 400 | Current password incorrect |
| 422 | New password does not meet requirements |

---

## API Keys

### List API Keys

Get list of user's API keys (for third-party service integrations).

```http
GET /v1/users/me/api-keys
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "key_abc123",
      "name": "OpenAI Production",
      "provider": "openai",
      "created_at": "2026-01-15T10:00:00Z",
      "last_used_at": "2026-02-01T15:30:00Z",
      "masked_key": "sk-...abc123"
    },
    {
      "id": "key_def456",
      "name": "Groq API",
      "provider": "groq",
      "created_at": "2026-01-20T14:00:00Z",
      "last_used_at": "2026-02-02T08:00:00Z",
      "masked_key": "gsk_...xyz789"
    }
  ]
}
```

---

### Add API Key

Store an API key for a third-party service.

```http
POST /v1/users/me/api-keys
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "OpenAI Production",
  "provider": "openai",
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**Supported Providers:**

| Provider | Key Format |
|----------|------------|
| openai | sk-* |
| anthropic | sk-ant-* |
| groq | gsk_* |
| google | AIza* |
| mistral | * |
| cohere | * |
| together | * |
| scraperapi | * |
| apify | apify_api_* |
| scrapingbee | * |

**Response (201):**

```json
{
  "success": true,
  "data": {
    "id": "key_new789",
    "name": "OpenAI Production",
    "provider": "openai",
    "created_at": "2026-02-02T12:00:00Z",
    "masked_key": "sk-...xxxx"
  }
}
```

---

### Delete API Key

Delete a stored API key.

```http
DELETE /v1/users/me/api-keys/{key_id}
Authorization: Bearer <access_token>
```

**Response (204):**

No content.

---

### Test API Key

Test if an API key is valid.

```http
POST /v1/users/me/api-keys/{key_id}/test
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "valid": true,
    "provider": "openai",
    "details": {
      "organization": "Acme Inc",
      "models_available": ["gpt-4", "gpt-3.5-turbo"]
    }
  }
}
```

**Error Response:**

```json
{
  "success": true,
  "data": {
    "valid": false,
    "error": "Invalid API key"
  }
}
```

---

## User Settings

### Available Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| timezone | string | UTC | User's timezone |
| email_notifications | boolean | true | Receive email notifications |
| weekly_digest | boolean | true | Receive weekly digest email |
| default_preset | string | standard | Default project preset |
| results_per_page | integer | 20 | Results pagination size |
| dashboard_layout | string | grid | Dashboard layout preference |

---

## Usage and Limits

### Get Usage Statistics

```http
GET /v1/users/me/usage
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | month | Time period (day, week, month) |

**Response (200):**

```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2026-02-01",
      "to": "2026-02-28"
    },
    "plan": {
      "name": "Standard",
      "projects_limit": 10,
      "scrapes_per_month": 500,
      "api_calls_per_month": 10000,
      "results_retention_days": 90
    },
    "current_usage": {
      "projects": 3,
      "scrapes": 45,
      "api_calls": 1250,
      "storage_mb": 125
    },
    "daily_breakdown": [
      {
        "date": "2026-02-01",
        "scrapes": 5,
        "api_calls": 150,
        "results": 450
      }
    ]
  }
}
```

---

## Export User Data

Request export of all user data (GDPR compliance).

```http
POST /v1/users/me/export
Authorization: Bearer <access_token>
```

**Response (202):**

```json
{
  "success": true,
  "data": {
    "export_id": "exp_abc123",
    "status": "processing",
    "estimated_time": 300,
    "message": "You will receive an email when your export is ready"
  }
}
```

Export includes:
- User profile data
- All projects and configurations
- All scraping results
- All analysis data
- Audit logs

Export format: ZIP archive containing JSON files.
