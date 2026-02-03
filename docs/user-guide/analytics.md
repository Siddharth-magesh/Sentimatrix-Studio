# Analytics & Insights

Sentimatrix Studio provides powerful analytics tools to help you understand sentiment trends, identify patterns, and make data-driven decisions.

## Dashboard Overview

The analytics dashboard provides a bird's-eye view of your data:

### Key Metrics

- **Total Results**: Number of analyzed reviews/comments
- **Average Sentiment**: Overall sentiment score (-1 to +1)
- **Sentiment Distribution**: Breakdown by positive/neutral/negative
- **Top Emotions**: Most frequently detected emotions
- **Active Projects**: Projects with recent activity

### Quick Stats

The dashboard cards show:

| Metric | Description |
|--------|-------------|
| **Today's Results** | New results in the last 24 hours |
| **Weekly Trend** | Sentiment change vs. last week |
| **Active Jobs** | Currently running scrape jobs |
| **Pending Analysis** | Results awaiting LLM processing |

## Sentiment Analysis

### Understanding Sentiment Scores

Sentiment scores range from -1 to +1:

| Score Range | Label | Interpretation |
|-------------|-------|----------------|
| 0.6 to 1.0 | Very Positive | Strong approval, enthusiasm |
| 0.2 to 0.6 | Positive | General satisfaction |
| -0.2 to 0.2 | Neutral | Objective or mixed |
| -0.6 to -0.2 | Negative | Dissatisfaction |
| -1.0 to -0.6 | Very Negative | Strong disapproval |

### Sentiment Charts

#### Distribution Chart

The pie/donut chart shows the breakdown of sentiment:

- Green: Positive results
- Gray: Neutral results
- Red: Negative results

#### Trend Chart

The line chart shows sentiment over time:

- Track how sentiment changes
- Identify events that impact perception
- Compare different time periods

### Filtering Results

Filter your analysis by:

- **Date Range**: Last 7 days, 30 days, custom range
- **Project**: Specific project or all projects
- **Target**: Specific URL or all targets
- **Platform**: Amazon, Steam, YouTube, etc.
- **Sentiment**: Positive, neutral, or negative only

## Emotion Detection

### Available Emotions

Sentimatrix detects these emotions:

**Positive Emotions:**
- Joy, Happiness
- Love, Affection
- Admiration, Appreciation
- Excitement, Enthusiasm
- Trust, Confidence

**Negative Emotions:**
- Anger, Frustration
- Disgust, Contempt
- Fear, Anxiety
- Sadness, Disappointment
- Grief, Despair

**Neutral/Mixed:**
- Surprise (positive or negative)
- Curiosity, Interest
- Confusion, Uncertainty

### Emotion Charts

#### Emotion Distribution

Bar chart showing frequency of each emotion:

- Most common emotions at the top
- Color-coded by positive/negative
- Click to filter results by emotion

#### Emotion Trends

Track emotion changes over time:

- Identify emotional triggers
- Monitor reaction to changes
- Compare before/after events

### Emotion Confidence

Each emotion has a confidence score (0-1):

| Confidence | Interpretation |
|------------|----------------|
| 0.8 - 1.0 | Very confident |
| 0.6 - 0.8 | Confident |
| 0.4 - 0.6 | Moderate |
| 0.0 - 0.4 | Low confidence |

## Insights & Summaries

### AI-Generated Insights

When enabled, Sentimatrix generates:

#### Pros
Commonly mentioned positive aspects:
- Extracted from positive reviews
- Ranked by frequency
- Grouped by category

#### Cons
Commonly mentioned negative aspects:
- Extracted from negative reviews
- Ranked by frequency
- Grouped by category

#### Feature Requests
Suggestions from users:
- New features desired
- Improvements requested
- Missing functionality

#### Key Themes
Recurring topics across all reviews:
- Common discussion points
- Trending topics
- Category breakdown

### Executive Summary

AI-generated summary of your data:

- Overall sentiment assessment
- Key positive and negative points
- Comparison to previous period
- Recommendations

## Comparative Analysis

### Cross-Project Comparison

Compare sentiment across projects:

1. Go to **Analytics** > **Compare**
2. Select 2-5 projects
3. View side-by-side metrics
4. Identify differences and patterns

### Time Period Comparison

Compare different time periods:

1. Select a date range
2. Click **Compare to Previous**
3. See changes in sentiment, volume, emotions
4. Understand trends and triggers

### Target Comparison

Compare performance across targets:

1. Open a project
2. Go to **Analytics** > **Targets**
3. View per-target sentiment
4. Identify best and worst performers

## Custom Reports

### Creating Reports

Build custom reports:

1. Go to **Analytics** > **Reports**
2. Click **New Report**
3. Select metrics and visualizations
4. Configure filters and date range
5. Save the report

### Report Components

Available components:

- **Sentiment Summary**: Overview stats
- **Distribution Chart**: Pie/bar charts
- **Trend Chart**: Line graphs over time
- **Emotion Heatmap**: Emotion by time/target
- **Word Cloud**: Common terms
- **Data Table**: Raw results

### Scheduling Reports

Receive reports automatically:

1. Open a report
2. Click **Schedule**
3. Choose frequency (daily, weekly, monthly)
4. Enter email recipients
5. Reports are sent as PDF attachments

## Exporting Data

### Export Formats

Export your data in multiple formats:

| Format | Best For |
|--------|----------|
| **CSV** | Spreadsheet analysis, import to other tools |
| **JSON** | API integration, programmatic access |
| **PDF** | Sharing reports, presentations |
| **Excel** | Advanced analysis with formulas |

### What's Included

Exports include:

- Result text and metadata
- Sentiment scores and labels
- Detected emotions with confidence
- Source URL and platform
- Timestamps
- Custom fields

### Filtering Exports

Export specific subsets:

1. Apply filters in the Results view
2. Click **Export**
3. Choose format
4. Only filtered results are exported

## Dashboard Customization

### Widget Layout

Customize your dashboard:

1. Click **Customize**
2. Drag widgets to reorder
3. Resize widgets as needed
4. Add or remove widgets
5. Click **Save Layout**

### Available Widgets

- Sentiment Distribution (pie chart)
- Sentiment Trend (line chart)
- Emotion Breakdown (bar chart)
- Recent Results (table)
- Job Status (status cards)
- Quick Actions (buttons)
- Summary Stats (numbers)

### Multiple Dashboards

Create purpose-specific dashboards:

1. Click **Dashboards** > **New**
2. Name your dashboard
3. Add and configure widgets
4. Switch between dashboards as needed

## Best Practices

### Analyzing Results

1. **Look at trends, not just numbers**: A score of 0.4 trending up is better than 0.6 trending down
2. **Consider volume**: 100 negative reviews matter more than 10
3. **Check confidence scores**: Low confidence results need manual review
4. **Segment your data**: Different platforms/targets may have different patterns

### Setting Baselines

1. Collect initial data for 2-4 weeks
2. Establish baseline sentiment and emotion profiles
3. Set up alerts for significant deviations
4. Compare future data against baselines

### Taking Action

1. Identify patterns in negative feedback
2. Prioritize issues by frequency and severity
3. Track sentiment changes after making improvements
4. Document cause-and-effect relationships

## Troubleshooting

### No data showing

- Verify date range includes results
- Check filters aren't too restrictive
- Ensure projects have completed scrapes
- Run a new scrape if data is old

### Charts not loading

- Refresh the page
- Clear browser cache
- Check for JavaScript errors
- Try a different browser

### Unexpected results

- Review individual results for accuracy
- Check LLM configuration
- Look for sarcasm or context issues
- Consider adjusting analysis settings
