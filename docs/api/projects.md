# Projects API

## Overview

Projects are the primary organizational unit in Sentimatrix Studio. Each project contains scraper configurations, LLM settings, target URLs, and analysis results.

## Endpoints

### List Projects

Get all projects for the authenticated user.

```http
GET /v1/projects
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page (max 100) |
| sort | string | -created_at | Sort field |
| status | string | - | Filter by status |
| search | string | - | Search in name/description |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "proj_abc123",
      "name": "Amazon Product Tracker",
      "description": "Track competitor product reviews",
      "status": "active",
      "preset": "standard",
      "platforms": ["amazon"],
      "targets_count": 5,
      "results_count": 1250,
      "last_scrape_at": "2026-02-01T15:30:00Z",
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-02-01T15:30:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

---

### Create Project

Create a new project with configuration.

```http
POST /v1/projects
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Amazon Product Tracker",
  "description": "Track competitor product reviews",
  "preset": "standard",
  "config": {
    "scrapers": {
      "platforms": ["amazon"],
      "commercial_provider": null
    },
    "llm": {
      "provider": "groq",
      "model": "llama-3.1-70b-versatile",
      "api_key": "gsk_xxx..."
    },
    "targets": [
      {
        "url": "https://www.amazon.com/dp/B08N5WRWNW",
        "label": "Product A"
      }
    ],
    "analysis": {
      "sentiment": true,
      "emotions": true,
      "summarize": true
    },
    "schedule": {
      "enabled": false,
      "frequency": "daily",
      "time": "09:00"
    },
    "limits": {
      "max_reviews_per_target": 100,
      "max_requests_per_day": 500
    }
  }
}
```

**Configuration Schema:**

```json
{
  "scrapers": {
    "platforms": ["amazon", "steam", "youtube", "reddit"],
    "commercial_provider": "scraperapi" | "apify" | null
  },
  "llm": {
    "provider": "groq" | "openai" | "anthropic" | ...,
    "model": "model_name",
    "api_key": "encrypted_key",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "targets": [
    {
      "url": "string",
      "label": "string",
      "platform": "auto" | "amazon" | ...,
      "metadata": {}
    }
  ],
  "analysis": {
    "sentiment": true,
    "sentiment_classes": 3 | 5,
    "emotions": true,
    "emotion_model": "ekman" | "goemotions",
    "summarize": true,
    "extract_insights": true
  },
  "schedule": {
    "enabled": false,
    "frequency": "hourly" | "daily" | "weekly",
    "time": "HH:MM",
    "timezone": "UTC",
    "days": [0, 1, 2, 3, 4, 5, 6]
  },
  "limits": {
    "max_reviews_per_target": 100,
    "max_requests_per_day": 500,
    "rate_limit_delay": 1.0
  }
}
```

**Response (201):**

```json
{
  "success": true,
  "data": {
    "id": "proj_abc123",
    "name": "Amazon Product Tracker",
    "status": "active",
    "created_at": "2026-02-02T12:00:00Z"
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 400 | Invalid configuration |
| 402 | Plan limit reached |
| 422 | Validation error |

---

### Get Project

Get project details including full configuration.

```http
GET /v1/projects/{project_id}
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "proj_abc123",
    "name": "Amazon Product Tracker",
    "description": "Track competitor product reviews",
    "status": "active",
    "preset": "standard",
    "config": {
      "scrapers": {
        "platforms": ["amazon"],
        "commercial_provider": null
      },
      "llm": {
        "provider": "groq",
        "model": "llama-3.1-70b-versatile",
        "api_key_configured": true
      },
      "targets": [
        {
          "id": "tgt_xyz789",
          "url": "https://www.amazon.com/dp/B08N5WRWNW",
          "label": "Product A",
          "status": "active",
          "last_scraped_at": "2026-02-01T15:30:00Z"
        }
      ],
      "analysis": {
        "sentiment": true,
        "emotions": true,
        "summarize": true
      },
      "schedule": {
        "enabled": false
      },
      "limits": {
        "max_reviews_per_target": 100,
        "max_requests_per_day": 500
      }
    },
    "stats": {
      "total_results": 1250,
      "total_scrapes": 15,
      "avg_sentiment": 0.72,
      "sentiment_distribution": {
        "positive": 850,
        "neutral": 250,
        "negative": 150
      }
    },
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-02-01T15:30:00Z"
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 404 | Project not found |
| 403 | Access denied |

---

### Update Project

Update project configuration.

```http
PUT /v1/projects/{project_id}
Authorization: Bearer <access_token>
```

**Request Body:**

Partial update supported. Only include fields to update.

```json
{
  "name": "Updated Project Name",
  "config": {
    "schedule": {
      "enabled": true,
      "frequency": "daily",
      "time": "09:00"
    }
  }
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "proj_abc123",
    "name": "Updated Project Name",
    "updated_at": "2026-02-02T12:00:00Z"
  }
}
```

---

### Delete Project

Delete a project and all associated data.

```http
DELETE /v1/projects/{project_id}
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| delete_results | boolean | true | Also delete results |

**Response (204):**

No content.

**Errors:**

| Code | Description |
|------|-------------|
| 404 | Project not found |
| 403 | Access denied |

---

### Get Project Statistics

Get detailed statistics for a project.

```http
GET /v1/projects/{project_id}/stats
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | 30d | Time period (7d, 30d, 90d, all) |

**Response (200):**

```json
{
  "success": true,
  "data": {
    "overview": {
      "total_results": 1250,
      "total_scrapes": 15,
      "avg_results_per_scrape": 83
    },
    "sentiment": {
      "average_score": 0.72,
      "distribution": {
        "positive": 850,
        "neutral": 250,
        "negative": 150
      },
      "trend": [
        {"date": "2026-01-01", "score": 0.68},
        {"date": "2026-01-08", "score": 0.70},
        {"date": "2026-01-15", "score": 0.75}
      ]
    },
    "emotions": {
      "distribution": {
        "joy": 450,
        "trust": 320,
        "anticipation": 180,
        "sadness": 120,
        "anger": 80,
        "fear": 50,
        "disgust": 30,
        "surprise": 20
      }
    },
    "targets": [
      {
        "id": "tgt_xyz789",
        "label": "Product A",
        "results_count": 500,
        "avg_sentiment": 0.78
      }
    ],
    "activity": {
      "scrapes_this_period": 10,
      "last_scrape_at": "2026-02-01T15:30:00Z",
      "next_scheduled_scrape": "2026-02-02T09:00:00Z"
    }
  }
}
```

---

## Project Status

| Status | Description |
|--------|-------------|
| active | Project is active and can run scrapes |
| paused | Project is paused, scheduled scrapes disabled |
| error | Project has configuration errors |
| archived | Project is archived, read-only |

## Presets

Projects can be created with presets that provide default configurations:

| Preset | Description | LLM | Features |
|--------|-------------|-----|----------|
| starter | Basic analysis | Local/Free | Sentiment only |
| standard | Full analysis | Groq | Sentiment + Emotions |
| advanced | Complete suite | OpenAI/Anthropic | All features |
| budget | Cost-effective | Groq | Sentiment + Summaries |
| enterprise | High volume | Custom | All features + Webhooks |

See [presets.md](../guides/presets.md) for detailed preset configurations.
