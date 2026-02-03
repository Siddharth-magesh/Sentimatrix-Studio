# Scheduling Scrape Jobs

Automate your data collection with scheduled scrape jobs. This guide explains how to set up and manage schedules.

## Overview

Schedules allow you to automatically run scrape jobs at specified times. This is useful for:

- Keeping data fresh with regular updates
- Monitoring sentiment changes over time
- Collecting data during off-peak hours
- Building historical datasets

## Creating a Schedule

### From Project Settings

1. Open your project
2. Go to **Settings** > **Schedule**
3. Click **Enable Schedule**
4. Configure the schedule options
5. Click **Save**

### Schedule Options

#### Frequency

Choose how often to run scrapes:

| Frequency | Description | Best For |
|-----------|-------------|----------|
| **Hourly** | Every hour | Real-time monitoring |
| **Daily** | Once per day | Most use cases |
| **Weekly** | Once per week | Low-volume products |
| **Monthly** | Once per month | Periodic reports |

#### Time

Set the time of day for the scrape to run:

- Use 24-hour format (e.g., "09:00", "14:30")
- Times are in your configured timezone
- Choose off-peak hours for better reliability

#### Timezone

Select your timezone for accurate scheduling:

- Common: UTC, America/New_York, Europe/London, Asia/Tokyo
- The schedule runs at the specified time in this timezone
- Daylight saving time is handled automatically

#### Day of Week (Weekly Schedules)

For weekly schedules, choose which day:

- 0 = Monday
- 1 = Tuesday
- 2 = Wednesday
- 3 = Thursday
- 4 = Friday
- 5 = Saturday
- 6 = Sunday

#### Day of Month (Monthly Schedules)

For monthly schedules, choose which day (1-28):

- Use 1-28 to avoid issues with shorter months
- The 1st is common for monthly reports
- The 15th for mid-month updates

## Managing Schedules

### Viewing Schedule Status

In your project, the schedule panel shows:

- **Status**: Enabled or Disabled
- **Next Run**: When the next scrape will start
- **Last Run**: When the last scrape completed
- **Last Status**: Success or failure of last run

### Enabling/Disabling

Toggle schedules on or off without deleting:

1. Go to project settings
2. Click the schedule toggle
3. Disabled schedules retain their configuration

### Editing a Schedule

1. Go to project settings
2. Click **Edit Schedule**
3. Modify the options
4. Click **Save**

Changes take effect for the next scheduled run.

### Deleting a Schedule

1. Go to project settings
2. Click **Delete Schedule**
3. Confirm the deletion

This permanently removes the schedule. You can create a new one later.

## Schedule Execution

### What Happens During Execution

When a scheduled scrape runs:

1. System creates a new scrape job
2. All active targets are scraped
3. Results are analyzed with your LLM settings
4. Statistics are updated
5. Webhooks are triggered (if configured)

### Monitoring Scheduled Jobs

View scheduled job history:

1. Go to **Jobs** tab in your project
2. Filter by "Scheduled" in the source dropdown
3. View job details and results

### Handling Failures

If a scheduled job fails:

- The failure is logged
- You receive a notification (if configured)
- The schedule continues for the next run
- Check job details for error information

## Notifications

### Setting Up Notifications

Get notified about scheduled jobs:

1. Go to **Settings** > **Notifications**
2. Enable email notifications
3. Choose which events to receive:
   - Job Started
   - Job Completed
   - Job Failed

### Webhook Notifications

For automated workflows, use webhooks:

1. Create a webhook (see [Webhooks Guide](./webhooks.md))
2. Subscribe to job events
3. Your endpoint receives real-time updates

## Best Practices

### Choosing Frequency

| Scenario | Recommended Frequency |
|----------|----------------------|
| New product launch | Hourly (first week), then daily |
| Established product | Daily or weekly |
| Seasonal products | Daily during peak, weekly otherwise |
| Competitor monitoring | Daily |
| Historical analysis | Monthly |

### Optimizing Schedule Times

1. **Avoid peak hours**: Run during low-traffic periods
2. **Stagger schedules**: Don't run all projects at once
3. **Consider source sites**: Some sites are slower at certain times
4. **Account for analysis time**: Large jobs need more time

### Managing Multiple Projects

For many projects:

1. Create a schedule spreadsheet
2. Distribute jobs across hours
3. Prioritize critical projects for prime times
4. Use lower frequencies for less important projects

## Troubleshooting

### Schedule not running

- Check that the schedule is enabled
- Verify the timezone is correct
- Ensure you haven't hit rate limits
- Check system status for outages

### Jobs running late

- Large jobs may delay subsequent runs
- Check job queue status
- Consider reducing job scope
- Upgrade plan for more concurrent jobs

### Missing data

- Verify targets are still valid
- Check scraper status
- Review job logs for errors
- Ensure API keys are valid

## Advanced Features

### Schedule Overrides

Run a one-time scrape without affecting the schedule:

1. Go to project overview
2. Click **Run Scrape**
3. The manual job runs independently
4. Scheduled jobs continue as normal

### Pause All Schedules

For maintenance or cost control:

1. Go to **Settings** > **Schedules**
2. Click **Pause All**
3. All schedules are disabled
4. Click **Resume All** when ready

### Schedule Reports

Export schedule performance data:

1. Go to **Analytics** > **Schedules**
2. View success rates and timing
3. Export to CSV for analysis
