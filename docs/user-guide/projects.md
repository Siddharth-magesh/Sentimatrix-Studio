# Managing Projects

Projects are the core organizational unit in Sentimatrix Studio. Each project contains targets, results, and configurations.

## Creating a Project

### Using Presets

Presets provide pre-configured settings for common use cases:

| Preset | Best For | Reviews | Features |
|--------|----------|---------|----------|
| **Starter** | Getting started | 50 | Basic sentiment |
| **Standard** | Most users | 100 | Sentiment + emotions |
| **Advanced** | Power users | 200 | Full features + scheduling |
| **Budget** | Cost savings | 25 | Minimal API usage |
| **Enterprise** | High volume | 500 | Maximum throughput |

### Custom Configuration

For full control, choose "Custom" and configure:

#### Scraper Settings
- **Platforms**: Select which platforms to support
- **Commercial Provider**: Optional paid scraping service for reliability
- **Proxies**: Enable proxy rotation for high-volume scraping

#### LLM Settings
- **Provider**: Choose Groq (fast, free), OpenAI (reliable), or Anthropic (quality)
- **Model**: Select the specific model
- **Temperature**: Control randomness (0.0 = focused, 1.0 = creative)

#### Analysis Settings
- **Sentiment Classes**: 3-class (pos/neu/neg) or 5-class (very pos to very neg)
- **Emotions**: Enable emotion detection
- **Summarization**: Generate AI summaries
- **Insights**: Extract pros, cons, and key topics

#### Limits
- **Max Reviews per Target**: Limit results per URL
- **Max Requests per Day**: Daily API limit
- **Rate Limit Delay**: Seconds between requests

## Project Status

Projects can have the following statuses:

- **Active**: Normal operation
- **Paused**: Temporarily stopped
- **Error**: Something went wrong
- **Archived**: Soft-deleted, can be restored

## Project Statistics

The overview shows key metrics:

- **Total Targets**: Number of URLs
- **Total Results**: Number of analyzed items
- **Scrape Jobs**: Completed and running jobs
- **Average Sentiment**: Overall sentiment score
- **Last Scrape**: When data was last collected

## Project Actions

### Run Scrape
Start a new scrape job for all or selected targets.

### Export Data
Download all results as CSV or JSON.

### Edit Configuration
Change project settings. Note: Some changes require re-scraping.

### Archive Project
Soft-delete the project. Data is preserved and can be restored.

### Delete Permanently
Permanently remove the project and all associated data. This cannot be undone.

## Best Practices

1. **Use descriptive names**: "iPhone 15 Reviews Q4 2024" is better than "Project 1"
2. **Start with presets**: Customize later as needed
3. **Group related targets**: One project per product or topic
4. **Monitor usage**: Keep an eye on API limits
5. **Schedule regular scrapes**: Keep data fresh
6. **Export backups**: Download your data periodically

## Troubleshooting

### Project won't create
- Check that the project name is unique
- Ensure you haven't exceeded your project limit

### Configuration changes not taking effect
- Some changes require a new scrape job
- Try running a fresh scrape after changes

### Can't delete project
- Ensure no scrape jobs are running
- Check for dependent schedules
