# Data Flow

## Overview

This document describes how data flows through Sentimatrix Studio, from user input to analysis results.

## Authentication Flow

### Registration

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Fill form      │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ POST /register │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ Validate       │
     │                │                │ Hash password  │
     │                │                │                │
     │                │                │ Insert user    │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ Generate JWT   │
     │                │                │<───────────────│
     │                │                │                │
     │                │ Set cookies    │                │
     │                │<───────────────│                │
     │                │                │                │
     │ Redirect to    │                │                │
     │ dashboard      │                │                │
     │<───────────────│                │                │
     │                │                │                │
```

### Login

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Submit creds   │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ POST /login    │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ Find user      │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ User doc       │
     │                │                │<───────────────│
     │                │                │                │
     │                │                │ Verify password│
     │                │                │ Generate JWT   │
     │                │                │                │
     │                │ Tokens         │                │
     │                │<───────────────│                │
     │                │                │                │
     │ Dashboard      │                │                │
     │<───────────────│                │                │
```

## Project Creation Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Create project │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │ Configure:     │                │                │
     │ - Preset       │                │                │
     │ - Scrapers     │                │                │
     │ - LLM          │                │                │
     │ - Targets      │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ POST /projects │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ Validate config│
     │                │                │ Encrypt keys   │
     │                │                │                │
     │                │                │ Insert project │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ Project ID     │
     │                │                │<───────────────│
     │                │                │                │
     │                │ Project created│                │
     │                │<───────────────│                │
     │                │                │                │
     │ Success        │                │                │
     │<───────────────│                │                │
```

## Scraping Flow

### Manual Trigger

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │Sentimatrix│    │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │
     │ Click "Scrape" │                │                │                │
     │───────────────>│                │                │                │
     │                │                │                │                │
     │                │POST /scrape/run│                │                │
     │                │───────────────>│                │                │
     │                │                │                │                │
     │                │                │ Get config     │                │
     │                │                │───────────────────────────────>│
     │                │                │                │                │
     │                │                │ Config doc     │                │
     │                │                │<───────────────────────────────│
     │                │                │                │                │
     │                │                │ Create job     │                │
     │                │                │───────────────────────────────>│
     │                │                │                │                │
     │                │ Job ID         │                │                │
     │                │<───────────────│                │                │
     │                │                │                │                │
     │ "Scraping..."  │                │                │                │
     │<───────────────│                │                │                │
     │                │                │                │                │
     │                │           [Background Task]     │                │
     │                │                │                │                │
     │                │                │ Execute scraper│                │
     │                │                │───────────────>│                │
     │                │                │                │                │
     │                │                │                │ Fetch data     │
     │                │                │                │───────────────>│
     │                │                │                │  (External)    │
     │                │                │                │<───────────────│
     │                │                │                │                │
     │                │                │ Scraped data   │                │
     │                │                │<───────────────│                │
     │                │                │                │                │
     │                │                │ Store results  │                │
     │                │                │───────────────────────────────>│
     │                │                │                │                │
     │                │                │ Update job     │                │
     │                │                │───────────────────────────────>│
     │                │                │                │                │
     │                │  WebSocket     │                │                │
     │                │  notification  │                │                │
     │                │<───────────────│                │                │
     │                │                │                │                │
     │ Results ready  │                │                │                │
     │<───────────────│                │                │                │
```

### Scheduled Scraping

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Scheduler│     │ Backend  │     │Sentimatrix│    │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Trigger (cron) │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ Get scheduled  │                │
     │                │ projects       │                │
     │                │───────────────────────────────>│
     │                │                │                │
     │                │ Project list   │                │
     │                │<───────────────────────────────│
     │                │                │                │
     │                │ For each project:              │
     │                │                │                │
     │                │ Execute scraper│                │
     │                │───────────────>│                │
     │                │                │                │
     │                │ Results        │                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ Store + analyze│                │
     │                │───────────────────────────────>│
     │                │                │                │
     │                │ Send webhooks  │                │
     │                │ (if configured)│                │
```

## Analysis Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Backend  │     │Sentimatrix│    │   LLM    │     │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Get raw data   │                │                │
     │───────────────────────────────────────────────>│
     │                │                │                │
     │ Scraped items  │                │                │
     │<───────────────────────────────────────────────│
     │                │                │                │
     │ Analyze batch  │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ Sentiment      │                │
     │                │ analysis       │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │ Classifications│                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ Emotion        │                │
     │                │ detection      │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │ Emotions       │                │
     │                │<───────────────│                │
     │                │                │                │
     │ Analysis result│                │                │
     │<───────────────│                │                │
     │                │                │                │
     │ Store analysis │                │                │
     │───────────────────────────────────────────────>│
     │                │                │                │
     │ Update stats   │                │                │
     │───────────────────────────────────────────────>│
```

## Results Retrieval Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ View results   │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │GET /results    │                │
     │                │?project=X      │                │
     │                │&page=1         │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ Aggregation    │
     │                │                │ pipeline       │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ Results +      │
     │                │                │ pagination     │
     │                │                │<───────────────│
     │                │                │                │
     │                │ Results JSON   │                │
     │                │<───────────────│                │
     │                │                │                │
     │ Display table  │                │                │
     │ + charts       │                │                │
     │<───────────────│                │                │
```

## Export Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ MongoDB  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Export (CSV)   │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │POST /export    │                │
     │                │{format: "csv"} │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │ Fetch all      │
     │                │                │ results        │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ Results        │
     │                │                │<───────────────│
     │                │                │                │
     │                │                │ Generate CSV   │
     │                │                │                │
     │                │ CSV file       │                │
     │                │<───────────────│                │
     │                │                │                │
     │ Download       │                │                │
     │<───────────────│                │                │
```

## WebSocket Events

### Event Types

| Event | Direction | Description |
|-------|-----------|-------------|
| `scrape:started` | Server -> Client | Scraping job started |
| `scrape:progress` | Server -> Client | Progress update |
| `scrape:completed` | Server -> Client | Scraping completed |
| `scrape:failed` | Server -> Client | Scraping failed |
| `analysis:started` | Server -> Client | Analysis started |
| `analysis:completed` | Server -> Client | Analysis completed |
| `job:status` | Client -> Server | Request job status |

### Connection Flow

```
┌──────────┐                    ┌──────────┐
│ Frontend │                    │ Backend  │
└────┬─────┘                    └────┬─────┘
     │                               │
     │ WS Connect                    │
     │ /ws?token=JWT                 │
     │──────────────────────────────>│
     │                               │
     │ Connection accepted           │
     │<──────────────────────────────│
     │                               │
     │ Subscribe to project          │
     │ {type: "subscribe",           │
     │  project_id: "xxx"}           │
     │──────────────────────────────>│
     │                               │
     │        [Job runs]             │
     │                               │
     │ {type: "scrape:progress",     │
     │  progress: 50}                │
     │<──────────────────────────────│
     │                               │
     │ {type: "scrape:completed",    │
     │  results_count: 100}          │
     │<──────────────────────────────│
```
