# Settings API

The Settings API allows you to manage API keys, view available LLM providers, and access configuration presets.

## API Keys

### List API Keys

Get all stored API keys for the authenticated user.

```
GET /api/v1/settings/api-keys
```

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "key_abc123def456",
      "provider": "groq",
      "name": "My Groq Key",
      "masked_key": "gsk-...abc123",
      "is_valid": true,
      "last_used": "2024-01-15T10:30:00Z",
      "last_validated": "2024-01-15T08:00:00Z",
      "created_at": "2024-01-10T08:00:00Z"
    },
    {
      "id": "key_xyz789ghi012",
      "provider": "openai",
      "name": "OpenAI Production",
      "masked_key": "sk-...xyz789",
      "is_valid": true,
      "last_used": "2024-01-14T15:20:00Z",
      "last_validated": "2024-01-14T15:00:00Z",
      "created_at": "2024-01-05T12:00:00Z"
    }
  ],
  "total": 2
}
```

---

### Add API Key

Store a new API key.

```
POST /api/v1/settings/api-keys
```

**Request Body:**

```json
{
  "provider": "groq",
  "api_key": "gsk_your_actual_api_key_here",
  "name": "My Groq Key"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | string | Yes | Provider ID (groq, openai, anthropic, scraperapi, etc.) |
| `api_key` | string | Yes | The actual API key |
| `name` | string | No | Friendly name for identification |

**Response:** `201 Created`

```json
{
  "id": "key_abc123def456",
  "provider": "groq",
  "name": "My Groq Key",
  "masked_key": "gsk-...abc123",
  "is_valid": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_PROVIDER` | Provider not supported |
| 400 | `KEY_EXISTS` | Key for this provider already exists |
| 422 | `INVALID_KEY_FORMAT` | API key format is invalid |

---

### Test API Key

Validate an API key by making a test request.

```
POST /api/v1/settings/api-keys/{provider}/test
```

**Response:** `200 OK`

```json
{
  "provider": "groq",
  "is_valid": true,
  "message": "API key is valid",
  "models_available": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
}
```

If invalid:

```json
{
  "provider": "groq",
  "is_valid": false,
  "message": "Invalid API key",
  "error": "Authentication failed"
}
```

---

### Delete API Key

Remove a stored API key.

```
DELETE /api/v1/settings/api-keys/{provider}
```

**Response:** `204 No Content`

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `KEY_IN_USE` | Key is being used by active projects |
| 404 | `NOT_FOUND` | No key found for this provider |

---

## LLM Providers

### List Providers

Get all available LLM providers and their configurations.

```
GET /api/v1/settings/llm/providers
```

**Response:** `200 OK`

```json
{
  "providers": [
    {
      "id": "groq",
      "name": "Groq",
      "description": "Fast inference with open-source models",
      "website": "https://groq.com",
      "has_free_tier": true,
      "models": [
        {
          "id": "llama-3.1-70b-versatile",
          "name": "LLaMA 3.1 70B",
          "context_length": 32768,
          "recommended": true
        },
        {
          "id": "llama-3.1-8b-instant",
          "name": "LLaMA 3.1 8B",
          "context_length": 32768,
          "recommended": false
        }
      ],
      "is_configured": true
    },
    {
      "id": "openai",
      "name": "OpenAI",
      "description": "Industry-leading GPT models",
      "website": "https://openai.com",
      "has_free_tier": false,
      "models": [
        {
          "id": "gpt-4o",
          "name": "GPT-4o",
          "context_length": 128000,
          "recommended": true
        },
        {
          "id": "gpt-4o-mini",
          "name": "GPT-4o Mini",
          "context_length": 128000,
          "recommended": false
        }
      ],
      "is_configured": false
    },
    {
      "id": "anthropic",
      "name": "Anthropic",
      "description": "Claude models with advanced reasoning",
      "website": "https://anthropic.com",
      "has_free_tier": false,
      "models": [
        {
          "id": "claude-3-5-sonnet-20241022",
          "name": "Claude 3.5 Sonnet",
          "context_length": 200000,
          "recommended": true
        },
        {
          "id": "claude-3-haiku-20240307",
          "name": "Claude 3 Haiku",
          "context_length": 200000,
          "recommended": false
        }
      ],
      "is_configured": false
    }
  ]
}
```

---

### Get Provider Details

Get detailed information about a specific provider.

```
GET /api/v1/settings/llm/providers/{provider_id}
```

**Response:** `200 OK`

```json
{
  "id": "groq",
  "name": "Groq",
  "description": "Fast inference with open-source models",
  "website": "https://groq.com",
  "documentation": "https://console.groq.com/docs",
  "has_free_tier": true,
  "pricing": {
    "input_per_1m_tokens": 0.05,
    "output_per_1m_tokens": 0.08
  },
  "models": [
    {
      "id": "llama-3.1-70b-versatile",
      "name": "LLaMA 3.1 70B Versatile",
      "description": "Best balance of speed and quality",
      "context_length": 32768,
      "max_output_tokens": 8192,
      "supported_features": ["sentiment", "emotions", "summarization", "insights"],
      "recommended": true,
      "pricing": {
        "input_per_1m_tokens": 0.59,
        "output_per_1m_tokens": 0.79
      }
    }
  ],
  "rate_limits": {
    "requests_per_minute": 30,
    "tokens_per_minute": 14400
  },
  "is_configured": true
}
```

---

## Presets

### List Presets

Get all available configuration presets.

```
GET /api/v1/settings/presets
```

**Response:** `200 OK`

```json
{
  "presets": [
    {
      "id": "starter",
      "name": "Starter",
      "description": "Basic sentiment analysis for getting started",
      "tier": "free",
      "features": {
        "sentiment_classes": 3,
        "emotions_enabled": false,
        "summarization_enabled": false,
        "insights_enabled": false,
        "max_reviews_per_target": 50
      },
      "recommended_for": ["learning", "testing", "small-scale"]
    },
    {
      "id": "standard",
      "name": "Standard",
      "description": "Balanced features for most use cases",
      "tier": "free",
      "features": {
        "sentiment_classes": 3,
        "emotions_enabled": true,
        "summarization_enabled": false,
        "insights_enabled": false,
        "max_reviews_per_target": 100
      },
      "recommended_for": ["general", "most-users"],
      "is_default": true
    },
    {
      "id": "advanced",
      "name": "Advanced",
      "description": "Full feature access for power users",
      "tier": "paid",
      "features": {
        "sentiment_classes": 5,
        "emotions_enabled": true,
        "summarization_enabled": true,
        "insights_enabled": true,
        "max_reviews_per_target": 500
      },
      "recommended_for": ["power-users", "detailed-analysis"]
    }
  ]
}
```

---

### Get Preset Details

Get full configuration for a specific preset.

```
GET /api/v1/settings/presets/{preset_id}
```

**Response:** `200 OK`

```json
{
  "id": "standard",
  "name": "Standard",
  "description": "Balanced features for most use cases",
  "config": {
    "scrapers": {
      "platforms": ["amazon", "steam", "youtube", "reddit", "trustpilot", "yelp"],
      "commercial_provider": null,
      "proxies_enabled": false
    },
    "llm": {
      "provider": "groq",
      "model": "llama-3.1-70b-versatile",
      "temperature": 0.7,
      "max_tokens": 500
    },
    "analysis": {
      "sentiment": true,
      "sentiment_classes": 3,
      "emotions": true,
      "emotion_model": "ekman",
      "summarize": false,
      "extract_insights": false
    },
    "limits": {
      "max_reviews_per_target": 100,
      "max_requests_per_day": 500,
      "rate_limit_delay": 1.0
    }
  },
  "estimated_cost": {
    "monthly_min": 0,
    "monthly_max": 10,
    "currency": "USD"
  }
}
```

---

## Examples

### cURL

```bash
# List API keys
curl "https://api.sentimatrix.io/api/v1/settings/api-keys" \
  -H "Authorization: Bearer TOKEN"

# Add API key
curl -X POST "https://api.sentimatrix.io/api/v1/settings/api-keys" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "groq",
    "api_key": "gsk_your_key_here",
    "name": "Production Key"
  }'

# Test API key
curl -X POST "https://api.sentimatrix.io/api/v1/settings/api-keys/groq/test" \
  -H "Authorization: Bearer TOKEN"

# Delete API key
curl -X DELETE "https://api.sentimatrix.io/api/v1/settings/api-keys/groq" \
  -H "Authorization: Bearer TOKEN"

# List LLM providers
curl "https://api.sentimatrix.io/api/v1/settings/llm/providers" \
  -H "Authorization: Bearer TOKEN"

# List presets
curl "https://api.sentimatrix.io/api/v1/settings/presets" \
  -H "Authorization: Bearer TOKEN"
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Add API key
result = requests.post(
    "https://api.sentimatrix.io/api/v1/settings/api-keys",
    headers=headers,
    json={
        "provider": "groq",
        "api_key": "gsk_your_key_here",
        "name": "Production Key"
    }
).json()

# Test the key
test = requests.post(
    "https://api.sentimatrix.io/api/v1/settings/api-keys/groq/test",
    headers=headers
).json()

if test["is_valid"]:
    print(f"Key is valid. Available models: {test['models_available']}")

# Get available providers
providers = requests.get(
    "https://api.sentimatrix.io/api/v1/settings/llm/providers",
    headers=headers
).json()

for provider in providers["providers"]:
    status = "configured" if provider["is_configured"] else "not configured"
    print(f"{provider['name']}: {status}")
```

### JavaScript

```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};

// Add API key
const key = await fetch('https://api.sentimatrix.io/api/v1/settings/api-keys', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    provider: 'groq',
    api_key: 'gsk_your_key_here',
    name: 'Production Key',
  }),
}).then(r => r.json());

// Test the key
const test = await fetch(
  'https://api.sentimatrix.io/api/v1/settings/api-keys/groq/test',
  { method: 'POST', headers }
).then(r => r.json());

if (test.is_valid) {
  console.log('Key is valid. Models:', test.models_available);
}

// Get presets
const presets = await fetch(
  'https://api.sentimatrix.io/api/v1/settings/presets',
  { headers }
).then(r => r.json());
```
