# Quick Start Guide

## Overview

Get started with Sentimatrix Studio in 5 minutes. This guide walks you through creating your first sentiment analysis project.

## Prerequisites

- Web browser (Chrome, Firefox, Safari, Edge)
- API key for LLM provider (optional, Groq free tier available)

## Step 1: Create Account

1. Navigate to [studio.sentimatrix.dev](https://studio.sentimatrix.dev)
2. Click **Get Started** or **Sign Up**
3. Enter your email and create a password
4. Verify your email address

## Step 2: Choose Your Preset

During registration, you will select a configuration preset:

| Preset | Best For | Cost |
|--------|----------|------|
| **Starter** | Learning, testing | Free |
| **Standard** | Most users | Free (Groq) |
| **Advanced** | Power users | ~$50/mo |
| **Budget** | Cost-conscious | Free |

For beginners, we recommend **Standard** preset.

## Step 3: Configure LLM (Optional)

If you selected Standard or higher:

1. Choose your LLM provider (Groq recommended for free tier)
2. Enter your API key
3. Click **Test Connection** to verify

**Getting a Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate an API key
4. Copy and paste into Sentimatrix Studio

## Step 4: Create Your First Project

1. Click **New Project** from the dashboard
2. Enter a project name (e.g., "My First Analysis")
3. Add a description (optional)
4. Click **Next**

## Step 5: Add Targets

Add URLs you want to analyze:

**Amazon Product:**
```
https://www.amazon.com/dp/B08N5WRWNW
```

**Steam Game:**
```
https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/
```

**Reddit Post:**
```
https://www.reddit.com/r/technology/comments/abc123/example_post/
```

1. Paste URL in the target input
2. Optionally add a label (e.g., "Product A")
3. Click **Add Target**
4. Repeat for more URLs
5. Click **Next**

## Step 6: Configure Analysis

Select what analysis to run:

- [x] **Sentiment Analysis** - Classify positive/neutral/negative
- [x] **Emotion Detection** - Detect emotions (joy, anger, etc.)
- [ ] **Summarization** - Generate summary (requires LLM)
- [ ] **Insights** - Extract pros/cons (requires LLM)

Click **Create Project**

## Step 7: Run Your First Scrape

1. From your project page, click **Run Scrape**
2. Set options:
   - Max results per target: 50 (default)
   - Include replies: No (faster)
3. Click **Start Scraping**
4. Wait for scraping to complete (1-5 minutes)

You will see real-time progress as reviews are collected.

## Step 8: View Results

Once scraping completes:

1. Navigate to **Results** tab
2. View sentiment distribution chart
3. Browse individual results in the table
4. Filter by sentiment (positive, neutral, negative)
5. Search within results

## Step 9: Export Data

To export your results:

1. Click **Export** button
2. Choose format:
   - CSV - Spreadsheet compatible
   - JSON - For developers
3. Click **Download**

## Next Steps

### Explore More Features

- **Schedule Scraping** - Automatically scrape daily/weekly
- **Multiple Targets** - Add more URLs to track
- **Emotion Analysis** - Enable detailed emotion detection
- **Webhooks** - Get notified when scrapes complete

### Recommended Reading

- [Project Management Guide](configuration.md)
- [Scraper Configuration](configuration.md#scrapers)
- [LLM Provider Setup](configuration.md#llm)
- [Understanding Results](configuration.md#results)

### Get Help

- Check [Troubleshooting Guide](troubleshooting.md)
- Browse [FAQ](#faq)
- Contact support at support@sentimatrix.dev

---

## FAQ

### How much does it cost?

Sentimatrix Studio is free to use. Costs come from:
- LLM providers (Groq free tier available)
- Commercial scraping APIs (optional)

### What platforms are supported?

- Amazon (all regions)
- Steam
- YouTube
- Reddit
- IMDB
- Yelp
- Trustpilot
- Google Reviews

### How many reviews can I scrape?

Depends on your preset and plan:
- Starter: 50 per target
- Standard: 100 per target
- Advanced: 500 per target
- Enterprise: Unlimited

### Can I use my own API keys?

Yes, you can bring your own API keys for:
- LLM providers (OpenAI, Anthropic, Groq, etc.)
- Commercial scrapers (ScraperAPI, Apify, etc.)

### Is my data secure?

Yes:
- API keys are encrypted at rest
- All data transmitted over HTTPS
- Data can be deleted on request
- See [Security Documentation](../architecture/security.md)
