# Collection Details

## Overview

This document provides detailed information about each MongoDB collection, including validation rules and example documents.

## users

### Validation Schema

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["email", "password_hash", "name", "role", "plan", "status", "created_at"],
    properties: {
      email: {
        bsonType: "string",
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      },
      password_hash: {
        bsonType: "string",
        minLength: 60
      },
      name: {
        bsonType: "string",
        minLength: 1,
        maxLength: 100
      },
      role: {
        enum: ["user", "admin"]
      },
      plan: {
        enum: ["starter", "standard", "advanced", "enterprise"]
      },
      status: {
        enum: ["active", "suspended", "deleted"]
      }
    }
  }
}
```

### Example Document

```javascript
{
  _id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  email: "user@example.com",
  password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.JqJYmFgvGpH0y6",
  name: "John Doe",
  company: "Acme Inc",
  avatar_url: null,
  role: "user",
  plan: "standard",
  settings: {
    timezone: "America/New_York",
    email_notifications: true,
    weekly_digest: true,
    default_preset: "standard",
    results_per_page: 20,
    dashboard_layout: "grid"
  },
  oauth: {
    google_id: null,
    github_id: "12345678"
  },
  usage: {
    projects_count: 3,
    scrapes_this_month: 45,
    api_calls_this_month: 1250,
    last_reset_at: ISODate("2026-02-01T00:00:00Z")
  },
  status: "active",
  email_verified: true,
  email_verified_at: ISODate("2026-01-01T12:00:00Z"),
  created_at: ISODate("2026-01-01T10:00:00Z"),
  updated_at: ISODate("2026-02-02T08:00:00Z"),
  last_login_at: ISODate("2026-02-02T08:00:00Z"),
  deleted_at: null
}
```

---

## projects

### Validation Schema

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["user_id", "name", "status", "preset", "config", "created_at"],
    properties: {
      name: {
        bsonType: "string",
        minLength: 1,
        maxLength: 100
      },
      status: {
        enum: ["active", "paused", "error", "archived"]
      },
      preset: {
        enum: ["starter", "standard", "advanced", "budget", "custom"]
      }
    }
  }
}
```

### Example Document

```javascript
{
  _id: ObjectId("65a2b3c4d5e6f7a8b9c0d1e2"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  name: "Amazon Product Tracker",
  description: "Track competitor product reviews",
  status: "active",
  preset: "standard",
  config: {
    scrapers: {
      platforms: ["amazon"],
      commercial_provider: null,
      commercial_config: null
    },
    llm: {
      provider: "groq",
      model: "llama-3.1-70b-versatile",
      api_key_id: ObjectId("65a3b4c5d6e7f8a9b0c1d2e3"),
      temperature: 0.7,
      max_tokens: 1000
    },
    analysis: {
      sentiment: true,
      sentiment_classes: 3,
      emotions: true,
      emotion_model: "ekman",
      summarize: false,
      extract_insights: false
    },
    schedule: {
      enabled: true,
      frequency: "daily",
      time: "09:00",
      timezone: "America/New_York",
      days: [1, 2, 3, 4, 5],
      next_run_at: ISODate("2026-02-03T14:00:00Z")
    },
    limits: {
      max_reviews_per_target: 100,
      max_requests_per_day: 500,
      rate_limit_delay: 1.0
    }
  },
  stats: {
    total_targets: 5,
    total_results: 1250,
    total_scrapes: 15,
    avg_sentiment: 0.72,
    sentiment_distribution: {
      positive: 850,
      neutral: 250,
      negative: 150
    },
    last_scrape_at: ISODate("2026-02-02T09:00:00Z"),
    last_analysis_at: ISODate("2026-02-02T09:05:00Z")
  },
  created_at: ISODate("2026-01-15T10:00:00Z"),
  updated_at: ISODate("2026-02-02T09:05:00Z"),
  archived_at: null
}
```

---

## targets

### Example Document

```javascript
{
  _id: ObjectId("65a3b4c5d6e7f8a9b0c1d2e3"),
  project_id: ObjectId("65a2b3c4d5e6f7a8b9c0d1e2"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  url: "https://www.amazon.com/dp/B08N5WRWNW",
  label: "Product A - Wireless Headphones",
  platform: "amazon",
  detected_type: "product",
  platform_data: {
    asin: "B08N5WRWNW",
    product_name: "Wireless Bluetooth Headphones"
  },
  options: {
    country: "us",
    sort_by: "recent",
    verified_only: false
  },
  metadata: {
    category: "Electronics",
    competitor: "Acme Audio"
  },
  stats: {
    results_count: 250,
    last_scraped_at: ISODate("2026-02-02T09:00:00Z"),
    last_result_date: ISODate("2026-02-01T15:30:00Z")
  },
  status: "active",
  error_message: null,
  created_at: ISODate("2026-01-15T10:30:00Z"),
  updated_at: ISODate("2026-02-02T09:00:00Z")
}
```

---

## results

### Example Document

```javascript
{
  _id: ObjectId("65a4b5c6d7e8f9a0b1c2d3e4"),
  project_id: ObjectId("65a2b3c4d5e6f7a8b9c0d1e2"),
  target_id: ObjectId("65a3b4c5d6e7f8a9b0c1d2e3"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  scrape_job_id: ObjectId("65a5b6c7d8e9f0a1b2c3d4e5"),
  content: {
    text: "These headphones are amazing! The sound quality is incredible and the battery lasts forever. Best purchase I've made this year.",
    title: "Best headphones ever!",
    author: "MusicLover123",
    rating: 5,
    date: ISODate("2026-01-28T10:00:00Z"),
    url: "https://www.amazon.com/gp/customer-reviews/R1ABC123DEF",
    platform_id: "R1ABC123DEF"
  },
  analysis: {
    sentiment: {
      label: "positive",
      score: 0.92,
      confidence: 0.95,
      scores: {
        very_positive: 0.75,
        positive: 0.17,
        neutral: 0.05,
        negative: 0.02,
        very_negative: 0.01
      },
      analyzed_at: ISODate("2026-02-02T09:05:00Z")
    },
    emotions: {
      model: "ekman",
      primary: "joy",
      primary_score: 0.85,
      detected: [
        { emotion: "joy", score: 0.85 },
        { emotion: "surprise", score: 0.45 }
      ],
      analyzed_at: ISODate("2026-02-02T09:05:00Z")
    },
    summary: null,
    insights: null
  },
  platform: "amazon",
  language: "en",
  word_count: 28,
  created_at: ISODate("2026-02-02T09:00:00Z"),
  updated_at: ISODate("2026-02-02T09:05:00Z")
}
```

---

## scrape_jobs

### Example Document

```javascript
{
  _id: ObjectId("65a5b6c7d8e9f0a1b2c3d4e5"),
  project_id: ObjectId("65a2b3c4d5e6f7a8b9c0d1e2"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  status: "completed",
  progress: 100,
  targets: [
    {
      target_id: ObjectId("65a3b4c5d6e7f8a9b0c1d2e3"),
      status: "completed",
      progress: 100,
      results_count: 50,
      error: null
    },
    {
      target_id: ObjectId("65a3b4c5d6e7f8a9b0c1d2e4"),
      status: "completed",
      progress: 100,
      results_count: 45,
      error: null
    }
  ],
  options: {
    max_results: 50,
    include_replies: false,
    date_from: ISODate("2026-01-01T00:00:00Z"),
    date_to: null
  },
  stats: {
    targets_total: 2,
    targets_completed: 2,
    results_total: 95,
    requests_made: 12,
    errors_count: 0
  },
  trigger: "scheduled",
  triggered_by: null,
  started_at: ISODate("2026-02-02T09:00:00Z"),
  completed_at: ISODate("2026-02-02T09:03:45Z"),
  error_message: null,
  created_at: ISODate("2026-02-02T08:59:55Z")
}
```

---

## api_keys

### Example Document

```javascript
{
  _id: ObjectId("65a3b4c5d6e7f8a9b0c1d2e3"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  name: "Groq API Key",
  provider: "groq",
  encrypted_key: Binary("..."),
  key_nonce: Binary("..."),
  key_tag: Binary("..."),
  masked_key: "gsk_...xyz789",
  last_used_at: ISODate("2026-02-02T09:00:00Z"),
  last_validated_at: ISODate("2026-02-01T10:00:00Z"),
  is_valid: true,
  created_at: ISODate("2026-01-15T10:00:00Z"),
  updated_at: ISODate("2026-02-02T09:00:00Z")
}
```

---

## webhooks

### Example Document

```javascript
{
  _id: ObjectId("65a6b7c8d9e0f1a2b3c4d5e6"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  name: "Slack Notifications",
  url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
  events: ["scrape.completed", "analysis.completed", "alert.sentiment_drop"],
  project_ids: [ObjectId("65a2b3c4d5e6f7a8b9c0d1e2")],
  headers: {
    "X-Custom-Header": "custom-value"
  },
  secret: "whsec_abc123xyz789",
  active: true,
  success_rate: 0.98,
  last_triggered_at: ISODate("2026-02-02T09:05:00Z"),
  consecutive_failures: 0,
  created_at: ISODate("2026-01-20T14:00:00Z"),
  updated_at: ISODate("2026-02-02T09:05:00Z")
}
```

---

## presets

### Example Document (System Preset)

```javascript
{
  _id: ObjectId("65a7b8c9d0e1f2a3b4c5d6e7"),
  user_id: null,                    // null = system preset
  name: "standard",
  display_name: "Standard",
  description: "Full analysis capabilities with Groq LLM",
  is_system: true,
  config: {
    scrapers: {
      platforms: [],
      commercial_provider: null
    },
    llm: {
      provider: "groq",
      model: "llama-3.1-70b-versatile",
      temperature: 0.7,
      max_tokens: 1000
    },
    analysis: {
      sentiment: true,
      sentiment_classes: 3,
      emotions: true,
      emotion_model: "ekman",
      summarize: false,
      extract_insights: false
    },
    schedule: {
      enabled: false,
      frequency: "daily",
      time: "09:00"
    },
    limits: {
      max_reviews_per_target: 100,
      max_requests_per_day: 500,
      rate_limit_delay: 1.0
    }
  },
  features: ["sentiment", "emotions"],
  recommended: true,
  order: 2,
  created_at: ISODate("2026-01-01T00:00:00Z"),
  updated_at: ISODate("2026-01-01T00:00:00Z")
}
```

---

## audit_logs

### Example Document

```javascript
{
  _id: ObjectId("65a8b9c0d1e2f3a4b5c6d7e8"),
  user_id: ObjectId("65a1b2c3d4e5f6a7b8c9d0e1"),
  event_type: "auth.login",
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  success: true,
  metadata: {
    method: "password",
    email: "user@example.com"
  },
  created_at: ISODate("2026-02-02T08:00:00Z")
}
```
