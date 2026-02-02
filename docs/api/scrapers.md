# Scrapers API

## Overview

The Scrapers API provides endpoints for configuring and executing web scraping jobs using Sentimatrix's scraper integrations.

## Platform Scrapers

### List Available Platforms

Get list of supported scraping platforms.

```http
GET /v1/scrapers/platforms
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "amazon",
      "name": "Amazon",
      "description": "Scrape Amazon product reviews",
      "supports": {
        "reviews": true,
        "product_info": true,
        "search": true
      },
      "countries": ["us", "uk", "de", "fr", "jp", "in"],
      "rate_limit": "1 request/second",
      "requires_browser": true
    },
    {
      "id": "steam",
      "name": "Steam",
      "description": "Scrape Steam game reviews",
      "supports": {
        "reviews": true,
        "game_info": true
      },
      "rate_limit": "2 requests/second",
      "requires_browser": false
    },
    {
      "id": "youtube",
      "name": "YouTube",
      "description": "Scrape YouTube video comments",
      "supports": {
        "comments": true,
        "video_info": true
      },
      "rate_limit": "API quota based",
      "requires_api_key": true
    },
    {
      "id": "reddit",
      "name": "Reddit",
      "description": "Scrape Reddit posts and comments",
      "supports": {
        "posts": true,
        "comments": true,
        "subreddit": true
      },
      "rate_limit": "1 request/second",
      "requires_browser": false
    },
    {
      "id": "imdb",
      "name": "IMDB",
      "description": "Scrape IMDB movie and TV reviews",
      "supports": {
        "reviews": true,
        "ratings": true
      },
      "rate_limit": "1 request/second",
      "requires_browser": true
    },
    {
      "id": "yelp",
      "name": "Yelp",
      "description": "Scrape Yelp business reviews",
      "supports": {
        "reviews": true,
        "business_info": true
      },
      "rate_limit": "1 request/2 seconds",
      "requires_browser": true
    },
    {
      "id": "trustpilot",
      "name": "Trustpilot",
      "description": "Scrape Trustpilot company reviews",
      "supports": {
        "reviews": true,
        "company_info": true
      },
      "rate_limit": "1 request/second",
      "requires_browser": false
    },
    {
      "id": "google_reviews",
      "name": "Google Reviews",
      "description": "Scrape Google Maps/Places reviews",
      "supports": {
        "reviews": true,
        "place_info": true
      },
      "rate_limit": "1 request/2 seconds",
      "requires_browser": true
    }
  ]
}
```

---

### List Commercial Providers

Get list of commercial scraping API providers.

```http
GET /v1/scrapers/commercial
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "scraperapi",
      "name": "ScraperAPI",
      "description": "40M+ proxy pool with JS rendering",
      "features": {
        "proxy_rotation": true,
        "js_rendering": true,
        "captcha_solving": true,
        "geotargeting": true
      },
      "pricing": "Starting at $49/month",
      "requires_api_key": true
    },
    {
      "id": "apify",
      "name": "Apify",
      "description": "2000+ pre-built actors",
      "features": {
        "pre_built_scrapers": true,
        "custom_actors": true,
        "cloud_execution": true,
        "dataset_storage": true
      },
      "pricing": "Pay-per-use",
      "requires_api_key": true
    },
    {
      "id": "brightdata",
      "name": "Bright Data",
      "description": "72M+ proxy pool, enterprise grade",
      "features": {
        "proxy_rotation": true,
        "js_rendering": true,
        "captcha_solving": true,
        "geotargeting": true,
        "residential_proxies": true
      },
      "pricing": "Starting at $500/month",
      "requires_credentials": true
    },
    {
      "id": "scrapingbee",
      "name": "ScrapingBee",
      "description": "Simple API with screenshots",
      "features": {
        "proxy_rotation": true,
        "js_rendering": true,
        "screenshots": true,
        "ai_extraction": true
      },
      "pricing": "Starting at $49/month",
      "requires_api_key": true
    }
  ]
}
```

---

### Validate Scraper Configuration

Validate scraper configuration before saving.

```http
POST /v1/scrapers/validate
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "platforms": ["amazon", "steam"],
  "commercial_provider": "scraperapi",
  "commercial_config": {
    "api_key": "xxx",
    "render_js": true,
    "country": "us"
  },
  "targets": [
    {
      "url": "https://www.amazon.com/dp/B08N5WRWNW",
      "platform": "amazon"
    }
  ]
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "valid": true,
    "targets": [
      {
        "url": "https://www.amazon.com/dp/B08N5WRWNW",
        "platform": "amazon",
        "detected_type": "product",
        "asin": "B08N5WRWNW"
      }
    ],
    "warnings": [
      "Commercial provider ScraperAPI will be used for rate-limited platforms"
    ]
  }
}
```

**Validation Errors:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid scraper configuration",
    "details": [
      {
        "field": "targets[0].url",
        "message": "URL is not a valid Amazon product URL"
      },
      {
        "field": "commercial_config.api_key",
        "message": "Invalid ScraperAPI key"
      }
    ]
  }
}
```

---

## Scrape Jobs

### Execute Scrape Job

Trigger a scraping job for a project.

```http
POST /v1/scrape/run
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "project_id": "proj_abc123",
  "targets": ["tgt_xyz789"],
  "options": {
    "max_results": 100,
    "include_replies": false,
    "date_from": "2026-01-01"
  }
}
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| max_results | integer | 100 | Maximum results per target |
| include_replies | boolean | false | Include reply comments |
| date_from | date | null | Filter by date |
| date_to | date | null | Filter by date |
| sort | string | recent | Sort order (recent, relevant, helpful) |

**Response (202):**

```json
{
  "success": true,
  "data": {
    "job_id": "job_def456",
    "status": "queued",
    "targets_count": 1,
    "estimated_time": 60,
    "created_at": "2026-02-02T12:00:00Z"
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 400 | Invalid request |
| 402 | Rate limit exceeded |
| 404 | Project or target not found |
| 429 | Too many concurrent jobs |

---

### List Scrape Jobs

Get list of scrape jobs.

```http
GET /v1/scrape/jobs
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| project_id | string | - | Filter by project |
| status | string | - | Filter by status |
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "job_def456",
      "project_id": "proj_abc123",
      "status": "completed",
      "progress": 100,
      "targets_count": 5,
      "results_count": 450,
      "started_at": "2026-02-02T12:00:00Z",
      "completed_at": "2026-02-02T12:05:30Z",
      "duration_seconds": 330
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 15
    }
  }
}
```

---

### Get Job Status

Get detailed status of a scrape job.

```http
GET /v1/scrape/jobs/{job_id}
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "job_def456",
    "project_id": "proj_abc123",
    "status": "running",
    "progress": 60,
    "current_target": {
      "id": "tgt_xyz789",
      "url": "https://www.amazon.com/dp/B08N5WRWNW",
      "progress": 60,
      "results_scraped": 60
    },
    "targets": [
      {
        "id": "tgt_xyz789",
        "status": "running",
        "progress": 60
      },
      {
        "id": "tgt_abc123",
        "status": "pending",
        "progress": 0
      }
    ],
    "stats": {
      "total_results": 60,
      "requests_made": 15,
      "errors": 0
    },
    "started_at": "2026-02-02T12:00:00Z",
    "estimated_completion": "2026-02-02T12:03:00Z"
  }
}
```

**Job Status Values:**

| Status | Description |
|--------|-------------|
| queued | Job is queued for execution |
| running | Job is currently running |
| completed | Job completed successfully |
| failed | Job failed with errors |
| cancelled | Job was cancelled by user |
| partial | Job completed with some errors |

---

### Cancel Job

Cancel a running scrape job.

```http
POST /v1/scrape/jobs/{job_id}/cancel
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "job_def456",
    "status": "cancelled",
    "results_saved": 60
  }
}
```

---

## Target Management

### Add Target to Project

Add a new scraping target to a project.

```http
POST /v1/projects/{project_id}/targets
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "url": "https://www.amazon.com/dp/B08N5WRWNW",
  "label": "Product A",
  "platform": "auto",
  "metadata": {
    "category": "Electronics",
    "competitor": "Acme Inc"
  }
}
```

**Response (201):**

```json
{
  "success": true,
  "data": {
    "id": "tgt_new123",
    "url": "https://www.amazon.com/dp/B08N5WRWNW",
    "label": "Product A",
    "platform": "amazon",
    "detected_type": "product",
    "status": "active",
    "created_at": "2026-02-02T12:00:00Z"
  }
}
```

---

### Remove Target

Remove a target from a project.

```http
DELETE /v1/projects/{project_id}/targets/{target_id}
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| delete_results | boolean | false | Also delete results |

**Response (204):**

No content.

---

## Platform-Specific Options

### Amazon

```json
{
  "country": "us",
  "sort_by": "recent",
  "filter_stars": null,
  "verified_only": false
}
```

### Steam

```json
{
  "language": "english",
  "filter": "all",
  "day_range": 30
}
```

### YouTube

```json
{
  "api_key": "AIza...",
  "order": "relevance",
  "max_results": 100
}
```

### Reddit

```json
{
  "sort": "hot",
  "time": "month",
  "include_comments": true
}
```
