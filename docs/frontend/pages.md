# Page Structure

## Overview

This document describes all pages in Sentimatrix Studio, their purpose, and key components.

## Authentication Pages

### Login Page

**Route:** `/login`

**Purpose:** User authentication with email/password or OAuth.

**Components:**
- LoginForm
- OAuthButtons
- ForgotPasswordLink

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│                    Logo                              │
├─────────────────────────────────────────────────────┤
│                                                      │
│           ┌─────────────────────────┐               │
│           │      Login Form          │               │
│           │  ┌───────────────────┐  │               │
│           │  │ Email             │  │               │
│           │  └───────────────────┘  │               │
│           │  ┌───────────────────┐  │               │
│           │  │ Password          │  │               │
│           │  └───────────────────┘  │               │
│           │  [Forgot Password?]     │               │
│           │  [      Login      ]    │               │
│           │                         │               │
│           │  ─────── or ───────     │               │
│           │                         │               │
│           │  [Google] [GitHub]      │               │
│           │                         │               │
│           │  Don't have account?    │               │
│           │  [Register]             │               │
│           └─────────────────────────┘               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### Register Page

**Route:** `/register`

**Purpose:** New user registration with configuration preset selection.

**Components:**
- RegistrationStepper
- AccountForm
- PresetSelector
- LLMConfigForm
- ScraperConfigForm

**Steps:**
1. Account Details (email, password, name)
2. Select Preset (starter, standard, advanced, budget)
3. LLM Configuration (provider selection, API key)
4. Scraper Configuration (platforms, targets)
5. Review and Create

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│                    Logo                              │
├─────────────────────────────────────────────────────┤
│  Step 1 ─── Step 2 ─── Step 3 ─── Step 4 ─── Step 5│
├─────────────────────────────────────────────────────┤
│                                                      │
│           ┌─────────────────────────┐               │
│           │   Step Content Area      │               │
│           │                         │               │
│           │   [Form Fields]         │               │
│           │                         │               │
│           │                         │               │
│           └─────────────────────────┘               │
│                                                      │
│           [Back]              [Next]                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Dashboard Pages

### Main Dashboard

**Route:** `/dashboard`

**Purpose:** Overview of all projects and recent activity.

**Components:**
- StatsCards (total projects, total results, avg sentiment)
- RecentActivity
- QuickActions
- SentimentTrendChart
- ProjectsOverview

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│  Sidebar  │                    Header                          │
├───────────┼────────────────────────────────────────────────────┤
│           │                                                    │
│  Dashboard│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  Projects │  │ Projects │ │ Results  │ │ Avg Sent │ │Scrapes ││
│  Config   │  │    5     │ │  12,500  │ │   0.72   │ │  45    ││
│  Settings │  └──────────┘ └──────────┘ └──────────┘ └────────┘│
│           │                                                    │
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │         Sentiment Trend (30 days)           │  │
│           │  │    [Line Chart]                             │  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
│           │  ┌─────────────────────┐ ┌─────────────────────┐  │
│           │  │   Recent Activity   │ │   Quick Actions     │  │
│           │  │   - Scrape completed│ │   [New Project]     │  │
│           │  │   - Analysis done   │ │   [Run Scrape]      │  │
│           │  │   - Project created │ │   [Export Data]     │  │
│           │  └─────────────────────┘ └─────────────────────┘  │
│           │                                                    │
└───────────┴────────────────────────────────────────────────────┘
```

---

### Analytics Page

**Route:** `/dashboard/analytics`

**Purpose:** Detailed analytics across all projects.

**Components:**
- DateRangePicker
- ProjectFilter
- SentimentDistributionChart
- EmotionBreakdownChart
- TopicsWordCloud
- TrendComparison

---

## Project Pages

### Projects List

**Route:** `/projects`

**Purpose:** List and manage all projects.

**Components:**
- ProjectsTable
- ProjectFilters
- ProjectCard (grid view)
- CreateProjectButton

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│  Sidebar  │  Projects                    [+ New Project]       │
├───────────┼────────────────────────────────────────────────────┤
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │ Search...          [Status v] [Sort v]      │  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │ Amazon Tracker          Active    150 results│  │
│           │  │ Last scraped: 2 hours ago                   │  │
│           │  ├─────────────────────────────────────────────┤  │
│           │  │ Steam Reviews           Active    500 results│  │
│           │  │ Last scraped: 1 day ago                     │  │
│           │  ├─────────────────────────────────────────────┤  │
│           │  │ Reddit Sentiment        Paused    0 results │  │
│           │  │ Last scraped: Never                         │  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
│           │  < 1 2 3 ... 5 >                                  │
└───────────┴────────────────────────────────────────────────────┘
```

---

### New Project

**Route:** `/projects/new`

**Purpose:** Create a new project with guided configuration.

**Components:**
- ProjectWizard
- PresetCards
- ScraperConfigForm
- LLMConfigForm
- TargetInputForm
- ScheduleConfigForm

**Steps:**
1. Basic Info (name, description)
2. Choose Preset or Custom
3. Configure Scrapers
4. Configure LLM
5. Add Targets
6. Set Schedule (optional)
7. Review and Create

---

### Project Details

**Route:** `/projects/[id]`

**Purpose:** View project overview and trigger actions.

**Components:**
- ProjectHeader
- ProjectStats
- TargetsList
- RecentResults
- SentimentChart
- ActionButtons (Scrape, Analyze, Export)

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│  Sidebar  │  Amazon Tracker                [Edit] [Delete]     │
├───────────┼────────────────────────────────────────────────────┤
│           │  Status: Active    Preset: Standard                │
│           │  Last Scrape: 2 hours ago                          │
│           │                                                    │
│           │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│           │  │ Results  │ │ Avg Sent │ │ Positive │           │
│           │  │  1,250   │ │   0.72   │ │   68%    │           │
│           │  └──────────┘ └──────────┘ └──────────┘           │
│           │                                                    │
│           │  [Run Scrape]  [Analyze]  [Export]                │
│           │                                                    │
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │         Sentiment Over Time                 │  │
│           │  │    [Line Chart]                             │  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
│           │  Targets (5)                                      │
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │ Product A    amazon.com/dp/...    250 results│  │
│           │  │ Product B    amazon.com/dp/...    180 results│  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
└───────────┴────────────────────────────────────────────────────┘
```

---

### Project Results

**Route:** `/projects/[id]/results`

**Purpose:** View and filter project results.

**Components:**
- ResultsFilters
- ResultsTable
- SentimentFilter
- DateRangePicker
- ExportButton
- ResultDetailModal

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│  Sidebar  │  Results - Amazon Tracker                          │
├───────────┼────────────────────────────────────────────────────┤
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │ Search...   [Sentiment v] [Target v] [Date] │  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
│           │  ┌─────────────────────────────────────────────┐  │
│           │  │ Text           │ Sentiment │ Emotions │ Date │  │
│           │  ├─────────────────────────────────────────────┤  │
│           │  │ Great product! │ Positive  │ Joy      │ 2/1  │  │
│           │  │ Not worth...   │ Negative  │ Anger    │ 2/1  │  │
│           │  │ Works as exp...│ Neutral   │ -        │ 1/31 │  │
│           │  └─────────────────────────────────────────────┘  │
│           │                                                    │
│           │  Showing 1-20 of 1,250    [Export CSV] [Export JSON]│
│           │                                                    │
└───────────┴────────────────────────────────────────────────────┘
```

---

## Configuration Pages

### Scrapers Configuration

**Route:** `/config/scrapers`

**Purpose:** Manage scraper settings and API keys.

**Components:**
- PlatformsList
- CommercialProvidersList
- APIKeyManager

---

### LLM Configuration

**Route:** `/config/llm`

**Purpose:** Configure LLM providers and test connections.

**Components:**
- ProvidersList
- ProviderConfigForm
- ConnectionTester

---

### Presets

**Route:** `/config/presets`

**Purpose:** View and manage configuration presets.

**Components:**
- PresetsList
- PresetDetails
- CreatePresetForm

---

## Settings Pages

### User Settings

**Route:** `/settings`

**Purpose:** Manage user profile and preferences.

**Components:**
- ProfileForm
- PreferencesForm
- PasswordChangeForm
- DangerZone (delete account)

---

### API Keys

**Route:** `/settings/api-keys`

**Purpose:** Manage stored API keys for third-party services.

**Components:**
- APIKeysList
- AddAPIKeyModal
- TestAPIKeyButton

---

### Webhooks

**Route:** `/settings/webhooks`

**Purpose:** Configure webhook notifications.

**Components:**
- WebhooksList
- WebhookForm
- WebhookLogs

---

### Billing

**Route:** `/settings/billing`

**Purpose:** View usage and manage subscription.

**Components:**
- UsageStats
- PlanComparison
- BillingHistory
