# Getting Started with Sentimatrix Studio

Welcome to Sentimatrix Studio! This guide will help you get up and running with sentiment analysis in minutes.

## What is Sentimatrix Studio?

Sentimatrix Studio is a no-code web platform for sentiment analysis powered by the Sentimatrix library. It allows you to:

- **Scrape reviews and comments** from Amazon, Steam, YouTube, Reddit, and more
- **Analyze sentiment** with AI-powered models
- **Detect emotions** in text content
- **Visualize insights** with charts and dashboards
- **Automate analysis** with scheduled jobs and webhooks

## Quick Start

### 1. Create an Account

1. Go to the Sentimatrix Studio website
2. Click **Sign Up** and fill in your details
3. Verify your email address
4. Log in to your dashboard

### 2. Create Your First Project

1. From the dashboard, click **Create Project**
2. Enter a project name and description
3. Choose a preset configuration:
   - **Starter**: Basic sentiment analysis with 50 reviews
   - **Standard**: 5-class sentiment + emotions with 100 reviews (recommended)
   - **Advanced**: Full features with scheduling and 200 reviews
4. Click **Create**

### 3. Add Targets

Targets are the URLs you want to scrape and analyze.

1. Open your project
2. Go to the **Targets** tab
3. Click **Add Target**
4. Paste a URL (e.g., `https://www.amazon.com/dp/B09V3KXJPB`)
5. The platform will automatically detect the platform
6. Click **Save**

**Supported Platforms:**
- Amazon (product reviews)
- Steam (game reviews)
- YouTube (video comments)
- Reddit (post comments)
- Trustpilot (business reviews)
- Yelp (local business reviews)
- Google Reviews

### 4. Run Your First Scrape

1. Go to the **Overview** tab
2. Click **Run Scrape**
3. Select targets to scrape (or leave blank for all)
4. Set the maximum number of results
5. Click **Start**

The job will run in the background. You can monitor progress in real-time.

### 5. View Results

Once the scrape completes:

1. Go to the **Results** tab
2. View individual results with sentiment and emotions
3. Use filters to find specific content
4. Export results to CSV or JSON

## Understanding Results

### Sentiment Analysis

Each result includes a sentiment label:
- **Positive**: The text expresses favorable opinions
- **Neutral**: The text is objective or mixed
- **Negative**: The text expresses unfavorable opinions

The sentiment score ranges from -1 (very negative) to +1 (very positive).

### Emotion Detection

When enabled, results include detected emotions:
- Joy, Love, Admiration
- Anger, Disgust, Fear
- Sadness, Disappointment
- Surprise, Curiosity
- And more...

## Next Steps

- [Configure LLM Settings](./llm-configuration.md)
- [Set Up Schedules](./scheduling.md)
- [Create Webhooks](./webhooks.md)
- [Explore Analytics](./analytics.md)

## Getting Help

- Check the [FAQ](./faq.md)
- Join our community forum
- Contact support at support@sentimatrix.io
