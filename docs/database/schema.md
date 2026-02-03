# Database Schema

## Overview

Sentimatrix Studio uses MongoDB as its primary database. This document describes the schema design and data models.

## Database Structure

```
sentimatrix_studio/
├── users                    # User accounts
├── projects                 # Analysis projects
├── targets                  # Scraping targets
├── scrape_jobs              # Scraping job records
├── results                  # Scraped and analyzed data
├── schedules                # Scheduled job configurations
├── api_keys                 # Stored API keys (encrypted with AES-256)
├── webhooks                 # Webhook configurations
├── webhook_deliveries       # Webhook delivery logs
├── audit_logs               # Security audit logs
└── refresh_tokens           # JWT refresh tokens
```

## Technology Stack

- **Database**: MongoDB 6.0+
- **Driver**: Motor (async MongoDB driver for Python)
- **ODM**: Pydantic models with custom repository pattern
- **Encryption**: Fernet (AES-256) with PBKDF2 key derivation

## Collections

### users

User account information.

```javascript
{
  _id: ObjectId,
  email: String,                    // Unique, indexed
  password_hash: String,            // bcrypt hash
  name: String,
  company: String,                  // Optional
  avatar_url: String,               // Optional
  role: String,                     // "user", "admin"
  plan: String,                     // "starter", "standard", "advanced", "enterprise"

  settings: {
    timezone: String,               // Default: "UTC"
    email_notifications: Boolean,   // Default: true
    weekly_digest: Boolean,         // Default: true
    default_preset: String,         // Default: "standard"
    results_per_page: Number,       // Default: 20
    dashboard_layout: String,       // "grid" | "list"
  },

  oauth: {
    google_id: String,              // Optional
    github_id: String,              // Optional
  },

  usage: {
    projects_count: Number,
    scrapes_this_month: Number,
    api_calls_this_month: Number,
    last_reset_at: Date,            // Monthly reset
  },

  status: String,                   // "active", "suspended", "deleted"
  email_verified: Boolean,
  email_verified_at: Date,

  created_at: Date,
  updated_at: Date,
  last_login_at: Date,
  deleted_at: Date,                 // Soft delete
}

// Indexes
{ email: 1 }                        // Unique
{ "oauth.google_id": 1 }
{ "oauth.github_id": 1 }
{ created_at: -1 }
```

---

### projects

Analysis project configurations.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,                // Reference to users
  name: String,
  description: String,
  status: String,                   // "active", "paused", "error", "archived"
  preset: String,                   // "starter", "standard", "advanced", "budget", "custom"

  config: {
    scrapers: {
      platforms: [String],          // ["amazon", "steam", "youtube", "reddit"]
      commercial_provider: String,  // "scraperapi", "apify", null
      commercial_config: {
        api_key_id: ObjectId,       // Reference to api_keys
        render_js: Boolean,
        country: String,
        premium_proxy: Boolean,
      },
    },

    llm: {
      provider: String,             // "groq", "openai", "anthropic", etc.
      model: String,
      api_key_id: ObjectId,         // Reference to api_keys
      temperature: Number,          // Default: 0.7
      max_tokens: Number,           // Default: 1000
    },

    analysis: {
      sentiment: Boolean,           // Default: true
      sentiment_classes: Number,    // 3 or 5
      emotions: Boolean,            // Default: false
      emotion_model: String,        // "ekman", "goemotions", "plutchik"
      summarize: Boolean,           // Default: false
      extract_insights: Boolean,    // Default: false
    },

    schedule: {
      enabled: Boolean,             // Default: false
      frequency: String,            // "hourly", "daily", "weekly"
      time: String,                 // "HH:MM"
      timezone: String,             // Default: "UTC"
      days: [Number],               // [0-6] for weekly (0=Sunday)
      next_run_at: Date,
    },

    limits: {
      max_reviews_per_target: Number, // Default: 100
      max_requests_per_day: Number,   // Default: 500
      rate_limit_delay: Number,       // Default: 1.0 (seconds)
    },
  },

  stats: {
    total_targets: Number,
    total_results: Number,
    total_scrapes: Number,
    avg_sentiment: Number,
    sentiment_distribution: {
      positive: Number,
      neutral: Number,
      negative: Number,
    },
    last_scrape_at: Date,
    last_analysis_at: Date,
  },

  created_at: Date,
  updated_at: Date,
  archived_at: Date,
}

// Indexes
{ user_id: 1 }
{ user_id: 1, status: 1 }
{ "config.schedule.next_run_at": 1 }  // For scheduler queries
{ created_at: -1 }
```

---

### targets

Scraping targets within projects.

```javascript
{
  _id: ObjectId,
  project_id: ObjectId,             // Reference to projects
  user_id: ObjectId,                // Denormalized for queries

  url: String,
  label: String,                    // User-friendly name
  platform: String,                 // "amazon", "steam", etc.
  detected_type: String,            // "product", "game", "video", "post"

  platform_data: {
    // Platform-specific parsed data
    asin: String,                   // Amazon
    app_id: Number,                 // Steam
    video_id: String,               // YouTube
    post_id: String,                // Reddit
    place_id: String,               // Google
  },

  options: {
    // Platform-specific options
    country: String,                // Amazon country
    language: String,               // Steam language
    sort_by: String,                // Sorting preference
    filter: Object,                 // Additional filters
  },

  metadata: Object,                 // User-defined metadata

  stats: {
    results_count: Number,
    last_scraped_at: Date,
    last_result_date: Date,
  },

  status: String,                   // "active", "paused", "error"
  error_message: String,            // Last error if any

  created_at: Date,
  updated_at: Date,
}

// Indexes
{ project_id: 1 }
{ project_id: 1, status: 1 }
{ user_id: 1 }
{ url: 1 }
```

---

### results

Scraped and analyzed data.

```javascript
{
  _id: ObjectId,
  project_id: ObjectId,             // Reference to projects
  target_id: ObjectId,              // Reference to targets
  user_id: ObjectId,                // Denormalized for queries
  scrape_job_id: ObjectId,          // Reference to scrape_jobs

  // Original scraped data
  content: {
    text: String,                   // Main text content
    title: String,                  // Optional title
    author: String,                 // Author/username
    rating: Number,                 // Numeric rating if available
    date: Date,                     // Original post date
    url: String,                    // Direct link to content
    platform_id: String,            // Platform's unique ID
  },

  // Analysis results
  analysis: {
    sentiment: {
      label: String,                // "positive", "neutral", "negative"
      score: Number,                // -1 to 1
      confidence: Number,           // 0 to 1
      scores: {                     // For 5-class
        very_positive: Number,
        positive: Number,
        neutral: Number,
        negative: Number,
        very_negative: Number,
      },
      analyzed_at: Date,
    },

    emotions: {
      model: String,                // "ekman", "goemotions"
      primary: String,              // Primary emotion
      primary_score: Number,
      detected: [{
        emotion: String,
        score: Number,
      }],
      analyzed_at: Date,
    },

    summary: {
      text: String,
      key_points: [String],
      generated_at: Date,
    },

    insights: {
      pros: [String],
      cons: [String],
      topics: [{
        topic: String,
        sentiment: Number,
      }],
      extracted_at: Date,
    },
  },

  // Metadata
  platform: String,
  language: String,                 // Detected language
  word_count: Number,

  created_at: Date,                 // When scraped
  updated_at: Date,                 // When analysis updated
}

// Indexes
{ project_id: 1, created_at: -1 }
{ target_id: 1, created_at: -1 }
{ user_id: 1 }
{ scrape_job_id: 1 }
{ "analysis.sentiment.label": 1 }
{ "content.date": -1 }
{ platform: 1 }

// Text index for search
{ "content.text": "text", "content.title": "text" }
```

---

### scrape_jobs

Scraping job records.

```javascript
{
  _id: ObjectId,
  project_id: ObjectId,
  user_id: ObjectId,

  status: String,                   // "queued", "running", "completed", "failed", "cancelled"
  progress: Number,                 // 0-100

  targets: [{
    target_id: ObjectId,
    status: String,
    progress: Number,
    results_count: Number,
    error: String,
  }],

  options: {
    max_results: Number,
    include_replies: Boolean,
    date_from: Date,
    date_to: Date,
  },

  stats: {
    targets_total: Number,
    targets_completed: Number,
    results_total: Number,
    requests_made: Number,
    errors_count: Number,
  },

  trigger: String,                  // "manual", "scheduled", "api"
  triggered_by: ObjectId,           // User who triggered (if manual)

  started_at: Date,
  completed_at: Date,
  error_message: String,

  created_at: Date,
}

// Indexes
{ project_id: 1, created_at: -1 }
{ user_id: 1 }
{ status: 1 }
{ created_at: -1 }
```

---

### api_keys

Encrypted API key storage.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,

  name: String,                     // User-friendly name
  provider: String,                 // "openai", "groq", "scraperapi", etc.

  // Encrypted storage
  encrypted_key: Binary,            // AES-256-GCM encrypted
  key_nonce: Binary,                // Encryption nonce
  key_tag: Binary,                  // Authentication tag

  masked_key: String,               // "sk-...abc123" for display

  last_used_at: Date,
  last_validated_at: Date,
  is_valid: Boolean,

  created_at: Date,
  updated_at: Date,
}

// Indexes
{ user_id: 1 }
{ user_id: 1, provider: 1 }
```

---

### schedules

Scheduled job configurations.

```javascript
{
  _id: ObjectId,
  project_id: ObjectId,             // Reference to projects (unique)
  user_id: ObjectId,

  frequency: String,                // "hourly", "daily", "weekly", "monthly"
  time: String,                     // "HH:MM" format
  timezone: String,                 // IANA timezone, default "UTC"

  day_of_week: Number,              // 0-6 for weekly (0=Monday)
  day_of_month: Number,             // 1-28 for monthly

  enabled: Boolean,                 // Default: true
  next_run: Date,                   // Calculated next execution time
  last_run: Date,

  run_history: [{
    job_id: ObjectId,
    started_at: Date,
    status: String,                 // "completed", "failed"
    results_count: Number,
  }],

  created_at: Date,
  updated_at: Date,
}

// Indexes
{ project_id: 1 }                   // Unique
{ user_id: 1 }
{ enabled: 1, next_run: 1 }         // Scheduler queries
```

---

### webhooks

Webhook configurations.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,

  url: String,                      // HTTPS endpoint
  events: [String],                 // ["job.completed", "job.failed", "results.new"]
  label: String,                    // User-friendly name

  secret: String,                   // HMAC signing secret (optional)
  enabled: Boolean,                 // Default: true

  stats: {
    total_deliveries: Number,
    successful_deliveries: Number,
    failed_deliveries: Number,
    last_delivery: Date,
    last_status: String,            // "success", "failed"
  },

  consecutive_failures: Number,     // Auto-disable after 5 failures

  created_at: Date,
  updated_at: Date,
}

// Indexes
{ user_id: 1 }
{ enabled: 1, events: 1 }
```

---

### webhook_deliveries

Webhook delivery history.

```javascript
{
  _id: ObjectId,
  webhook_id: ObjectId,
  user_id: ObjectId,

  event: String,                    // Event type that triggered delivery
  status: String,                   // "success", "failed", "pending"

  request: {
    url: String,
    headers: Object,
    body: String,                   // JSON payload
  },

  response: {
    status_code: Number,
    headers: Object,
    body: String,
    time_ms: Number,                // Response time in ms
  },

  error: String,                    // Error message if failed
  attempts: Number,                 // Number of delivery attempts

  created_at: Date,
  delivered_at: Date,
}

// Indexes
{ webhook_id: 1, created_at: -1 }
{ user_id: 1 }
{ status: 1 }

// TTL index - auto-delete after 7 days
{ created_at: 1 }, { expireAfterSeconds: 604800 }
```

---

### audit_logs

Security audit trail.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,

  event_type: String,               // "auth.login", "project.delete", etc.
  ip_address: String,
  user_agent: String,

  success: Boolean,
  metadata: Object,                 // Event-specific data

  created_at: Date,
}

// Indexes
{ user_id: 1, created_at: -1 }
{ event_type: 1 }
{ created_at: -1 }

// TTL index for automatic deletion
{ created_at: 1 }, { expireAfterSeconds: 31536000 } // 1 year
```

---

## Index Strategy

### Query Patterns

| Pattern | Index |
|---------|-------|
| User's projects | `{ user_id: 1, status: 1 }` |
| Project results | `{ project_id: 1, created_at: -1 }` |
| Scheduled jobs | `{ "config.schedule.next_run_at": 1 }` |
| Text search | `{ "content.text": "text" }` |

### Compound Indexes

Compound indexes are ordered for common query patterns:
1. Equality conditions first
2. Sort fields second
3. Range conditions last

---

## Data Retention

| Collection | Retention | Policy |
|------------|-----------|--------|
| results | 90 days (default) | Configurable per plan |
| scrape_jobs | 30 days | Automatic cleanup |
| audit_logs | 1 year | TTL index |
| webhook_logs | 7 days | TTL index |
