# Configuration Presets

## Overview

Sentimatrix Studio provides pre-configured presets to help users get started quickly. Each preset is optimized for different use cases and budget levels.

## Available Presets

### Starter

**Best for:** Learning, small-scale testing, budget-conscious users

| Feature | Setting |
|---------|---------|
| LLM Provider | None (local models) |
| Sentiment Analysis | Yes (3-class) |
| Emotion Detection | No |
| Summarization | No |
| Insights Extraction | No |
| Scraper Type | Direct (no proxy) |
| Rate Limit | 1 req/2 seconds |
| Max Results/Target | 50 |

**Estimated Cost:** Free (except hosting)

**Configuration:**

```json
{
  "preset": "starter",
  "config": {
    "llm": {
      "provider": null
    },
    "analysis": {
      "sentiment": true,
      "sentiment_classes": 3,
      "emotions": false,
      "summarize": false,
      "extract_insights": false
    },
    "scrapers": {
      "commercial_provider": null
    },
    "limits": {
      "max_reviews_per_target": 50,
      "rate_limit_delay": 2.0
    }
  }
}
```

---

### Standard

**Best for:** Most users, balanced features and cost

| Feature | Setting |
|---------|---------|
| LLM Provider | Groq (free tier) |
| Sentiment Analysis | Yes (3-class) |
| Emotion Detection | Yes (Ekman 6) |
| Summarization | No |
| Insights Extraction | No |
| Scraper Type | Direct |
| Rate Limit | 1 req/second |
| Max Results/Target | 100 |

**Estimated Cost:** Free (Groq free tier)

**Configuration:**

```json
{
  "preset": "standard",
  "config": {
    "llm": {
      "provider": "groq",
      "model": "llama-3.1-70b-versatile",
      "temperature": 0.7
    },
    "analysis": {
      "sentiment": true,
      "sentiment_classes": 3,
      "emotions": true,
      "emotion_model": "ekman",
      "summarize": false,
      "extract_insights": false
    },
    "scrapers": {
      "commercial_provider": null
    },
    "limits": {
      "max_reviews_per_target": 100,
      "rate_limit_delay": 1.0
    }
  }
}
```

---

### Advanced

**Best for:** Power users, detailed analysis needs

| Feature | Setting |
|---------|---------|
| LLM Provider | OpenAI (GPT-4o-mini) |
| Sentiment Analysis | Yes (5-class) |
| Emotion Detection | Yes (GoEmotions 28) |
| Summarization | Yes |
| Insights Extraction | Yes |
| Scraper Type | Commercial (ScraperAPI) |
| Rate Limit | API managed |
| Max Results/Target | 500 |

**Estimated Cost:** ~$50-100/month

**Configuration:**

```json
{
  "preset": "advanced",
  "config": {
    "llm": {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "temperature": 0.7
    },
    "analysis": {
      "sentiment": true,
      "sentiment_classes": 5,
      "emotions": true,
      "emotion_model": "goemotions",
      "summarize": true,
      "extract_insights": true
    },
    "scrapers": {
      "commercial_provider": "scraperapi"
    },
    "limits": {
      "max_reviews_per_target": 500,
      "rate_limit_delay": 0.5
    }
  }
}
```

---

### Budget

**Best for:** Cost-conscious users who need more than Starter

| Feature | Setting |
|---------|---------|
| LLM Provider | Groq |
| Sentiment Analysis | Yes (3-class) |
| Emotion Detection | No |
| Summarization | Yes |
| Insights Extraction | No |
| Scraper Type | Direct |
| Rate Limit | 1 req/second |
| Max Results/Target | 100 |

**Estimated Cost:** Free

**Configuration:**

```json
{
  "preset": "budget",
  "config": {
    "llm": {
      "provider": "groq",
      "model": "llama-3.1-8b-instant"
    },
    "analysis": {
      "sentiment": true,
      "sentiment_classes": 3,
      "emotions": false,
      "summarize": true,
      "extract_insights": false
    },
    "scrapers": {
      "commercial_provider": null
    },
    "limits": {
      "max_reviews_per_target": 100,
      "rate_limit_delay": 1.0
    }
  }
}
```

---

### Enterprise

**Best for:** High-volume users, full feature access

| Feature | Setting |
|---------|---------|
| LLM Provider | Anthropic (Claude 3.5) |
| Sentiment Analysis | Yes (5-class) |
| Emotion Detection | Yes (GoEmotions 28) |
| Summarization | Yes |
| Insights Extraction | Yes |
| Scraper Type | Commercial (Bright Data) |
| Rate Limit | High throughput |
| Max Results/Target | Unlimited |
| Webhooks | Enabled |
| Scheduling | Full access |

**Estimated Cost:** $500+/month

**Configuration:**

```json
{
  "preset": "enterprise",
  "config": {
    "llm": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "analysis": {
      "sentiment": true,
      "sentiment_classes": 5,
      "emotions": true,
      "emotion_model": "goemotions",
      "summarize": true,
      "extract_insights": true
    },
    "scrapers": {
      "commercial_provider": "brightdata"
    },
    "limits": {
      "max_reviews_per_target": -1,
      "rate_limit_delay": 0.1
    }
  }
}
```

---

## Comparison Table

| Feature | Starter | Standard | Advanced | Budget | Enterprise |
|---------|---------|----------|----------|--------|------------|
| LLM Provider | - | Groq | OpenAI | Groq | Anthropic |
| Sentiment | 3-class | 3-class | 5-class | 3-class | 5-class |
| Emotions | No | Ekman | GoEmotions | No | GoEmotions |
| Summaries | No | No | Yes | Yes | Yes |
| Insights | No | No | Yes | No | Yes |
| Commercial Scraper | No | No | Yes | No | Yes |
| Max Results | 50 | 100 | 500 | 100 | Unlimited |
| Webhooks | No | No | Yes | No | Yes |
| Cost/month | Free | Free | ~$50-100 | Free | $500+ |

---

## Custom Presets

Users can create custom presets based on their needs:

1. Start from an existing preset
2. Modify configuration as needed
3. Save as custom preset
4. Reuse for new projects

Custom presets are stored per-user and can be shared within organizations (future feature).

---

## Preset Selection

### During Registration

Users select a preset during the registration wizard. This becomes the default for new projects.

### When Creating Projects

Users can choose:
- Use default preset
- Select different preset
- Start from scratch (custom)

### Changing Presets

Existing projects can switch presets, but:
- New configuration applies to future scrapes
- Existing results retain original analysis
- Re-analysis available with new settings
