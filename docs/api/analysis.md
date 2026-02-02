# Analysis API

## Overview

The Analysis API provides endpoints for running sentiment analysis, emotion detection, and text summarization on scraped data.

## Endpoints

### Run Analysis

Execute analysis on scraped results.

```http
POST /v1/analysis/run
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "project_id": "proj_abc123",
  "result_ids": ["res_123", "res_456"],
  "options": {
    "sentiment": {
      "enabled": true,
      "classes": 5,
      "include_confidence": true
    },
    "emotions": {
      "enabled": true,
      "model": "goemotions",
      "threshold": 0.3
    },
    "summarize": {
      "enabled": true,
      "max_length": 200
    },
    "insights": {
      "enabled": true,
      "extract_pros_cons": true
    }
  }
}
```

**Analysis Options:**

| Option | Type | Description |
|--------|------|-------------|
| sentiment.enabled | boolean | Run sentiment analysis |
| sentiment.classes | integer | 3 or 5 class classification |
| sentiment.include_confidence | boolean | Include confidence scores |
| emotions.enabled | boolean | Run emotion detection |
| emotions.model | string | ekman, goemotions, plutchik |
| emotions.threshold | float | Minimum confidence threshold |
| summarize.enabled | boolean | Generate summaries |
| summarize.max_length | integer | Maximum summary length |
| insights.enabled | boolean | Extract insights |
| insights.extract_pros_cons | boolean | Extract pros/cons lists |

**Response (202):**

```json
{
  "success": true,
  "data": {
    "job_id": "analysis_ghi789",
    "status": "queued",
    "items_count": 100,
    "estimated_time": 30,
    "created_at": "2026-02-02T12:00:00Z"
  }
}
```

---

### Re-analyze Results

Re-run analysis with different settings.

```http
POST /v1/analysis/reanalyze
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "project_id": "proj_abc123",
  "date_range": {
    "from": "2026-01-01",
    "to": "2026-01-31"
  },
  "options": {
    "sentiment": {
      "enabled": true,
      "classes": 5
    }
  },
  "overwrite": true
}
```

**Response (202):**

```json
{
  "success": true,
  "data": {
    "job_id": "analysis_xyz123",
    "items_to_analyze": 500,
    "status": "queued"
  }
}
```

---

### Get Analysis Job Status

Get status of an analysis job.

```http
GET /v1/analysis/jobs/{job_id}
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "analysis_ghi789",
    "project_id": "proj_abc123",
    "status": "running",
    "progress": 75,
    "stats": {
      "total_items": 100,
      "processed": 75,
      "sentiment_analyzed": 75,
      "emotions_detected": 75,
      "summaries_generated": 50,
      "errors": 0
    },
    "started_at": "2026-02-02T12:00:00Z",
    "estimated_completion": "2026-02-02T12:00:45Z"
  }
}
```

---

### List Analysis Jobs

Get list of analysis jobs.

```http
GET /v1/analysis/jobs
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
      "id": "analysis_ghi789",
      "project_id": "proj_abc123",
      "status": "completed",
      "items_count": 100,
      "started_at": "2026-02-02T12:00:00Z",
      "completed_at": "2026-02-02T12:01:00Z"
    }
  ]
}
```

---

## Analysis Models

### Sentiment Models

| Model | Classes | Description |
|-------|---------|-------------|
| quick | 3 | Positive, Neutral, Negative |
| fine_grained | 5 | Very Positive, Positive, Neutral, Negative, Very Negative |

**Output Format:**

```json
{
  "sentiment": {
    "label": "positive",
    "score": 0.85,
    "confidence": 0.92,
    "scores": {
      "very_positive": 0.15,
      "positive": 0.70,
      "neutral": 0.10,
      "negative": 0.04,
      "very_negative": 0.01
    }
  }
}
```

### Emotion Models

**Ekman (6 basic emotions):**

| Emotion | Description |
|---------|-------------|
| joy | Happiness, delight |
| sadness | Sorrow, grief |
| anger | Rage, annoyance |
| fear | Anxiety, worry |
| disgust | Revulsion, contempt |
| surprise | Astonishment, wonder |

**GoEmotions (28 emotions):**

| Category | Emotions |
|----------|----------|
| Positive | admiration, amusement, approval, caring, desire, excitement, gratitude, joy, love, optimism, pride, relief |
| Negative | anger, annoyance, disappointment, disapproval, disgust, embarrassment, fear, grief, nervousness, remorse, sadness |
| Ambiguous | confusion, curiosity, realization, surprise |
| Neutral | neutral |

**Output Format:**

```json
{
  "emotions": {
    "model": "goemotions",
    "primary": "joy",
    "primary_score": 0.75,
    "detected": [
      {"emotion": "joy", "score": 0.75},
      {"emotion": "gratitude", "score": 0.45},
      {"emotion": "approval", "score": 0.32}
    ]
  }
}
```

### Summarization

LLM-powered summarization of text content.

**Output Format:**

```json
{
  "summary": {
    "text": "Customers praise the product quality and fast shipping...",
    "word_count": 45,
    "key_points": [
      "Excellent build quality",
      "Fast shipping",
      "Good value for money"
    ]
  }
}
```

### Insights Extraction

Extract structured insights from reviews.

**Output Format:**

```json
{
  "insights": {
    "pros": [
      "Durable construction",
      "Easy to use",
      "Great customer service"
    ],
    "cons": [
      "Higher price point",
      "Limited color options"
    ],
    "common_topics": [
      {"topic": "quality", "mentions": 45, "sentiment": "positive"},
      {"topic": "price", "mentions": 30, "sentiment": "neutral"},
      {"topic": "shipping", "mentions": 25, "sentiment": "positive"}
    ]
  }
}
```

---

## Aggregated Analysis

### Get Aggregated Statistics

Get aggregated analysis statistics for a project.

```http
GET /v1/analysis/aggregate
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| project_id | string | required | Project ID |
| period | string | 30d | Time period |
| group_by | string | day | Grouping (day, week, month) |
| target_id | string | - | Filter by target |

**Response (200):**

```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2026-01-02",
      "to": "2026-02-02"
    },
    "totals": {
      "results_analyzed": 1500,
      "avg_sentiment_score": 0.72
    },
    "sentiment_distribution": {
      "positive": 1050,
      "neutral": 300,
      "negative": 150
    },
    "emotion_distribution": {
      "joy": 500,
      "trust": 350,
      "anticipation": 200,
      "sadness": 150,
      "anger": 100,
      "fear": 80,
      "disgust": 70,
      "surprise": 50
    },
    "trends": [
      {
        "date": "2026-01-02",
        "sentiment_avg": 0.68,
        "results_count": 50
      },
      {
        "date": "2026-01-03",
        "sentiment_avg": 0.71,
        "results_count": 55
      }
    ],
    "top_topics": [
      {"topic": "quality", "mentions": 450, "sentiment": 0.82},
      {"topic": "price", "mentions": 320, "sentiment": 0.55},
      {"topic": "delivery", "mentions": 280, "sentiment": 0.78}
    ]
  }
}
```

---

## LLM Provider Configuration

Analysis features that use LLMs respect the project's LLM configuration.

### Supported Features by Provider

| Feature | Local Models | Groq | OpenAI | Anthropic |
|---------|--------------|------|--------|-----------|
| Sentiment (3-class) | Yes | Yes | Yes | Yes |
| Sentiment (5-class) | Yes | Yes | Yes | Yes |
| Emotions | Yes | Yes | Yes | Yes |
| Summarization | Limited | Yes | Yes | Yes |
| Insights | No | Yes | Yes | Yes |
| Batch Processing | Yes | Yes | Yes | Yes |

### Cost Estimation

Estimated costs per 1000 results:

| Provider | Sentiment | Emotions | Summarization | Full Analysis |
|----------|-----------|----------|---------------|---------------|
| Local | Free | Free | Free | Free |
| Groq | ~$0.01 | ~$0.01 | ~$0.05 | ~$0.10 |
| OpenAI | ~$0.10 | ~$0.10 | ~$0.50 | ~$1.00 |
| Anthropic | ~$0.15 | ~$0.15 | ~$0.75 | ~$1.50 |

Note: Costs are estimates and may vary based on text length and model selection.
