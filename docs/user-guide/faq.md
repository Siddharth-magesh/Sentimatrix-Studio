# Frequently Asked Questions

## General Questions

### What is Sentimatrix Studio?

Sentimatrix Studio is a no-code web platform for sentiment analysis. It allows you to scrape reviews and comments from various platforms, analyze them using AI, and visualize insights through an intuitive dashboard.

### Do I need coding knowledge?

No. Sentimatrix Studio is designed for non-technical users. Everything can be done through the web interface with clicks and simple configurations.

### What platforms can I scrape?

Currently supported platforms:
- Amazon (product reviews)
- Steam (game reviews)
- YouTube (video comments)
- Reddit (post comments)
- Trustpilot (business reviews)
- Yelp (local business reviews)
- Google Reviews

### Is web scraping legal?

Web scraping for personal analysis is generally legal, but always:
- Respect the platform's terms of service
- Don't scrape private or personal data
- Use reasonable request rates
- Don't redistribute scraped content

We recommend consulting with legal counsel for commercial applications.

## Account & Pricing

### Is there a free tier?

Yes! The free tier includes:
- 1 project
- 100 results per month
- Basic sentiment analysis
- Community support

### What payment methods are accepted?

We accept:
- Credit/debit cards (Visa, Mastercard, Amex)
- PayPal
- Bank transfer (Enterprise plans)

### Can I cancel anytime?

Yes. Cancel your subscription at any time from Account Settings. You'll retain access until the end of your billing period.

### What happens to my data if I downgrade?

Your data is preserved. However, you may lose access to advanced features. We recommend exporting data before downgrading.

## Scraping

### Why did my scrape fail?

Common reasons:
- **Invalid URL**: The URL format is incorrect
- **Platform blocked**: The site is blocking requests
- **No content**: The page has no reviews
- **Rate limited**: Too many requests too quickly

Check the job details for specific error messages.

### How long does scraping take?

It depends on:
- Number of reviews to collect
- Platform response times
- Your rate limit settings

Typically, 100 reviews take 1-5 minutes.

### Can I scrape private content?

No. Sentimatrix Studio only scrapes publicly available content. Login-protected content is not accessible.

### Why are some reviews missing?

- The platform may limit visible reviews
- Some reviews may be filtered by the platform
- Very old reviews may not be accessible
- Pagination limits may be reached

### How often should I scrape?

Depends on your needs:
- Active products: Daily
- Stable products: Weekly
- Historical analysis: Monthly

## Analysis

### How accurate is the sentiment analysis?

Accuracy varies by content and model:
- Simple reviews: 85-95% accuracy
- Complex/sarcastic content: 70-85% accuracy
- Multi-language content: 65-80% accuracy

Using larger models improves accuracy.

### Why is a review marked as positive when it seems negative?

Possible reasons:
- Sarcasm or irony wasn't detected
- The overall text was mixed
- Technical jargon confused the model
- The review had positive and negative parts

You can manually correct labels if needed.

### Can I analyze content in other languages?

Yes, most LLM providers support multiple languages. Quality varies by language popularity:
- English: Best quality
- Spanish, French, German: Very good
- Other languages: Good to moderate

### What's the difference between 3-class and 5-class sentiment?

**3-class**: Positive, Neutral, Negative
- Simpler, faster, cheaper
- Good for basic analysis

**5-class**: Very Positive, Positive, Neutral, Negative, Very Negative
- More granular insights
- Better for detailed analysis

## LLM & API Keys

### Which LLM provider should I use?

| Priority | Provider |
|----------|----------|
| Speed | Groq |
| Quality | OpenAI or Anthropic |
| Cost | Groq (free tier) |
| Privacy | Local models (coming soon) |

### Are my API keys secure?

Yes. API keys are:
- Encrypted before storage
- Never logged or exposed
- Only used for your analyses
- Deletable at any time

### What if I run out of API credits?

- Analysis jobs will fail
- You'll receive a notification
- Add credits to your LLM provider
- Jobs can be retried

### Can I use my own API key?

Yes. Add your own keys in Settings > API Keys. This gives you:
- Full control over costs
- Access to latest models
- Higher rate limits

## Data & Privacy

### Where is my data stored?

Data is stored on secure servers with:
- Encryption at rest
- Encryption in transit
- Regular backups
- Access controls

### Can I delete all my data?

Yes. Go to Account Settings > Delete Account. This permanently removes:
- Your account
- All projects
- All results
- All configurations

This action cannot be undone.

### Do you share my data?

No. Your data is never:
- Sold to third parties
- Used for advertising
- Shared without consent

We only use data to provide the service.

### Can I export my data?

Yes. Export from any view using:
- CSV format
- JSON format
- PDF format
- Excel format

## Technical Issues

### The dashboard is slow

Try:
- Reducing the date range
- Applying filters
- Using a modern browser
- Clearing browser cache
- Checking your internet connection

### I can't log in

- Check your email/password
- Reset your password
- Clear browser cookies
- Try incognito mode
- Contact support

### Webhooks aren't working

Verify:
- URL is accessible from internet
- HTTPS certificate is valid
- Endpoint returns 2xx status
- Firewall allows our IPs
- Secret is correct

### Jobs are stuck "in progress"

Jobs shouldn't take more than 30 minutes. If stuck:
- Check system status
- Cancel and retry
- Contact support for long-running jobs

## Features

### Can I schedule scrapes?

Yes. Set up schedules with:
- Hourly, daily, weekly, or monthly frequency
- Custom time and timezone
- Automatic execution

### Can I get notifications?

Yes, via:
- Email notifications
- Webhooks to your apps
- In-app notifications

### Can I share projects with my team?

Team features are available on Business and Enterprise plans:
- Invite team members
- Set permissions
- Share projects
- Collaborate on analysis

### Is there an API?

Yes. The REST API allows:
- Programmatic access
- Integration with your apps
- Automation workflows

API documentation is available in the developer docs.

## Support

### How do I get help?

- **Documentation**: You're reading it!
- **FAQ**: Check common issues
- **Email**: support@sentimatrix.io
- **Community Forum**: Ask other users
- **Premium Support**: Priority help (paid plans)

### How long until I get a response?

| Plan | Response Time |
|------|---------------|
| Free | 48-72 hours |
| Pro | 24 hours |
| Business | 4 hours |
| Enterprise | 1 hour |

### Can I request a feature?

Yes! Submit feature requests:
- Via email to feedback@sentimatrix.io
- On our community forum
- Through the feedback button in the app

We prioritize based on user demand.

### How do I report a bug?

Report bugs with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Browser/OS information
- Screenshots if possible

Email: bugs@sentimatrix.io
