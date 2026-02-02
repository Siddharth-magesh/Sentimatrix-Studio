# Index Strategy

## Overview

This document describes the indexing strategy for Sentimatrix Studio's MongoDB collections.

## Index Design Principles

1. **Query-Driven**: Indexes are designed based on actual query patterns
2. **Selectivity**: High-selectivity fields are indexed first in compound indexes
3. **Coverage**: Create covering indexes where possible
4. **Balance**: Consider write performance vs read performance tradeoffs

## Collection Indexes

### users

```javascript
// Primary queries: login, profile lookup
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ "oauth.google_id": 1 }, { sparse: true });
db.users.createIndex({ "oauth.github_id": 1 }, { sparse: true });
db.users.createIndex({ created_at: -1 });
db.users.createIndex({ status: 1, created_at: -1 });
```

| Index | Query Pattern | Notes |
|-------|---------------|-------|
| `{ email: 1 }` | Login, uniqueness | Unique index |
| `{ "oauth.google_id": 1 }` | OAuth login | Sparse (only if exists) |
| `{ "oauth.github_id": 1 }` | OAuth login | Sparse (only if exists) |
| `{ created_at: -1 }` | Admin user list | Descending for recent first |

---

### projects

```javascript
// User's project list (most common)
db.projects.createIndex({ user_id: 1, status: 1, created_at: -1 });

// Scheduler queries
db.projects.createIndex(
  { "config.schedule.enabled": 1, "config.schedule.next_run_at": 1 },
  { partialFilterExpression: { "config.schedule.enabled": true } }
);

// Archive lookup
db.projects.createIndex({ user_id: 1, archived_at: 1 });
```

| Index | Query Pattern | Notes |
|-------|---------------|-------|
| `{ user_id: 1, status: 1, created_at: -1 }` | List user's active projects | Covers filtering and sorting |
| `{ "config.schedule.enabled": 1, "config.schedule.next_run_at": 1 }` | Scheduler | Partial index for efficiency |
| `{ user_id: 1, archived_at: 1 }` | Archived projects | Null archived_at = active |

---

### targets

```javascript
// List targets for a project
db.targets.createIndex({ project_id: 1, status: 1 });

// Find by URL (duplicate detection)
db.targets.createIndex({ project_id: 1, url: 1 }, { unique: true });

// User-level queries
db.targets.createIndex({ user_id: 1, platform: 1 });
```

| Index | Query Pattern | Notes |
|-------|---------------|-------|
| `{ project_id: 1, status: 1 }` | List project targets | Common query |
| `{ project_id: 1, url: 1 }` | Duplicate check | Unique per project |
| `{ user_id: 1, platform: 1 }` | Cross-project platform stats | Analytics |

---

### results

```javascript
// Project results (paginated)
db.results.createIndex({ project_id: 1, created_at: -1 });

// Target-specific results
db.results.createIndex({ target_id: 1, created_at: -1 });

// Sentiment filtering
db.results.createIndex(
  { project_id: 1, "analysis.sentiment.label": 1, created_at: -1 }
);

// Date range queries
db.results.createIndex({ project_id: 1, "content.date": -1 });

// Job results
db.results.createIndex({ scrape_job_id: 1 });

// Text search
db.results.createIndex(
  { "content.text": "text", "content.title": "text" },
  { default_language: "english", weights: { "content.title": 2, "content.text": 1 } }
);

// Aggregation queries
db.results.createIndex(
  { project_id: 1, "analysis.sentiment.label": 1 },
  { partialFilterExpression: { "analysis.sentiment.label": { $exists: true } } }
);
```

| Index | Query Pattern | Notes |
|-------|---------------|-------|
| `{ project_id: 1, created_at: -1 }` | Paginated results | Most common |
| `{ target_id: 1, created_at: -1 }` | Target-specific | Detail view |
| `{ project_id: 1, "analysis.sentiment.label": 1, created_at: -1 }` | Filter by sentiment | With sorting |
| `{ project_id: 1, "content.date": -1 }` | Date range filter | Original content date |
| Text index | Full-text search | Weighted for title |

---

### scrape_jobs

```javascript
// Job history for project
db.scrape_jobs.createIndex({ project_id: 1, created_at: -1 });

// Active jobs
db.scrape_jobs.createIndex(
  { status: 1, created_at: -1 },
  { partialFilterExpression: { status: { $in: ["queued", "running"] } } }
);

// User's job history
db.scrape_jobs.createIndex({ user_id: 1, created_at: -1 });
```

| Index | Query Pattern | Notes |
|-------|---------------|-------|
| `{ project_id: 1, created_at: -1 }` | Project job history | Recent first |
| `{ status: 1, created_at: -1 }` | Active/pending jobs | Partial for active only |
| `{ user_id: 1, created_at: -1 }` | User's all jobs | Dashboard |

---

### api_keys

```javascript
// User's keys
db.api_keys.createIndex({ user_id: 1, provider: 1 });

// Unique key per user/provider
db.api_keys.createIndex(
  { user_id: 1, provider: 1, name: 1 },
  { unique: true }
);
```

---

### webhooks

```javascript
// User's webhooks
db.webhooks.createIndex({ user_id: 1 });

// Event triggering
db.webhooks.createIndex(
  { active: 1, events: 1 },
  { partialFilterExpression: { active: true } }
);

// Project-specific webhooks
db.webhooks.createIndex({ project_ids: 1 });
```

---

### audit_logs

```javascript
// User audit trail
db.audit_logs.createIndex({ user_id: 1, created_at: -1 });

// Event type filtering
db.audit_logs.createIndex({ event_type: 1, created_at: -1 });

// TTL for automatic deletion
db.audit_logs.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 31536000 }  // 1 year
);
```

---

## Index Maintenance

### Monitoring

```javascript
// Check index usage
db.results.aggregate([
  { $indexStats: {} }
]);

// Find slow queries
db.setProfilingLevel(1, { slowms: 100 });
db.system.profile.find().sort({ ts: -1 }).limit(10);
```

### Optimization

```javascript
// Analyze query explain plan
db.results.find({ project_id: ObjectId("...") })
  .sort({ created_at: -1 })
  .limit(20)
  .explain("executionStats");
```

### Index Size

Estimate index sizes and monitor growth:

```javascript
db.results.stats().indexSizes;
```

## Best Practices

1. **Use Partial Indexes**: For queries that filter on specific values
2. **Use Sparse Indexes**: For optional fields
3. **Avoid Over-Indexing**: Each index adds write overhead
4. **Monitor Usage**: Remove unused indexes
5. **Consider TTL**: For time-series data with retention requirements
