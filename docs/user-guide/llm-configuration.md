# LLM Configuration

Sentimatrix Studio uses Large Language Models (LLMs) to analyze sentiment, detect emotions, and generate insights. This guide explains how to configure and optimize your LLM settings.

## Supported Providers

### Groq (Recommended for Speed)

Groq offers the fastest inference speeds, making it ideal for high-volume analysis.

**Models:**
- **LLaMA 3.1 70B**: Best balance of speed and quality
- **LLaMA 3.1 8B**: Fastest, good for basic sentiment
- **Mixtral 8x7B**: Great for nuanced analysis

**Setup:**
1. Create an account at [groq.com](https://groq.com)
2. Generate an API key from the console
3. Add the key in Settings > API Keys

### OpenAI

OpenAI provides reliable, high-quality analysis with extensive model options.

**Models:**
- **GPT-4o**: Highest quality, best for complex analysis
- **GPT-4o-mini**: Good balance of cost and quality
- **GPT-3.5 Turbo**: Fast and economical

**Setup:**
1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Generate an API key
3. Add the key in Settings > API Keys

### Anthropic

Anthropic's Claude models excel at nuanced understanding and safety.

**Models:**
- **Claude 3.5 Sonnet**: Best overall quality
- **Claude 3 Haiku**: Fast and efficient

**Setup:**
1. Create an account at [anthropic.com](https://anthropic.com)
2. Generate an API key
3. Add the key in Settings > API Keys

## Adding API Keys

1. Go to **Settings** > **API Keys**
2. Click **Add API Key**
3. Select the provider
4. Paste your API key
5. Add an optional label for identification
6. Click **Save**

Your API keys are encrypted and stored securely. Only you can access them.

## Project LLM Settings

Each project can have its own LLM configuration:

### Provider Selection

Choose the provider based on your needs:

| Priority | Recommended Provider |
|----------|---------------------|
| Speed | Groq |
| Quality | OpenAI (GPT-4o) or Anthropic |
| Cost | Groq or OpenAI (GPT-3.5) |
| Privacy | Self-hosted (coming soon) |

### Model Selection

After choosing a provider, select a specific model. Consider:

- **Larger models** = Higher quality, slower, more expensive
- **Smaller models** = Lower quality, faster, cheaper

### Temperature

Temperature controls the randomness of responses:

- **0.0**: Deterministic, consistent results
- **0.3**: Slight variation (recommended for analysis)
- **0.7**: More creative, varied responses
- **1.0**: Maximum creativity/randomness

For sentiment analysis, we recommend **0.0 to 0.3** for consistency.

### Max Tokens

Controls the maximum response length. For sentiment analysis:

- **Basic sentiment**: 100-200 tokens
- **With emotions**: 300-500 tokens
- **Full insights**: 500-1000 tokens

## Analysis Features

### Sentiment Classes

Choose between two classification schemes:

**3-Class (Simple):**
- Positive
- Neutral
- Negative

**5-Class (Detailed):**
- Very Positive
- Positive
- Neutral
- Negative
- Very Negative

5-class provides more granular insights but requires more processing.

### Emotion Detection

When enabled, the LLM identifies emotions in text:

**Primary Emotions:**
- Joy, Love, Admiration
- Anger, Disgust, Fear
- Sadness, Disappointment, Grief
- Surprise, Curiosity, Confusion

Each emotion includes a confidence score (0-1).

### Summarization

Generate AI summaries of review collections:

- **Executive Summary**: High-level overview
- **Key Themes**: Common topics and patterns
- **Sentiment Trends**: Changes over time

### Insight Extraction

Extract structured insights:

- **Pros**: Positive aspects mentioned
- **Cons**: Negative aspects mentioned
- **Feature Requests**: Suggested improvements
- **Common Issues**: Recurring problems

## Cost Management

### Monitoring Usage

Track your API usage in **Settings** > **Usage**:

- Requests per day/week/month
- Tokens consumed
- Estimated costs by provider

### Setting Limits

Prevent unexpected costs:

1. Go to project settings
2. Set **Max Requests per Day**
3. Set **Max Reviews per Target**
4. Enable rate limiting

### Cost Optimization Tips

1. **Use appropriate models**: Don't use GPT-4o for simple sentiment
2. **Batch similar requests**: Process reviews in batches
3. **Cache results**: Enable caching for repeated analyses
4. **Use Groq for high volume**: Groq's free tier is generous

## Troubleshooting

### "API key invalid"

- Verify the key is correct
- Check the key hasn't expired
- Ensure you have API access enabled

### "Rate limit exceeded"

- Wait for the rate limit to reset
- Reduce concurrent requests
- Consider upgrading your API plan

### "Model not available"

- Check if the model is available in your region
- Verify your API plan includes this model
- Try an alternative model

### Inconsistent results

- Lower the temperature setting
- Use a larger model
- Increase max tokens if responses are truncated

## Best Practices

1. **Start with defaults**: Presets are optimized for common use cases
2. **Test before production**: Run small batches first
3. **Monitor costs**: Set up alerts for usage thresholds
4. **Keep keys secure**: Never share or expose API keys
5. **Use appropriate models**: Match model capability to task complexity
