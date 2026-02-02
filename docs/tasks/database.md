# Database Tasks

## Overview

Database setup and management tasks for Sentimatrix Studio.

**Technology:** MongoDB 6.0+

---

## Phase 1: Setup

### 1.1 Local Development [P0]

- [ ] Docker Compose configuration for MongoDB
- [ ] Connection string configuration
- [ ] Database initialization script

### 1.2 Collections [P0]

- [ ] Create users collection
- [ ] Create projects collection
- [ ] Create targets collection
- [ ] Create results collection
- [ ] Create scrape_jobs collection
- [ ] Create analysis_jobs collection
- [ ] Create api_keys collection
- [ ] Create webhooks collection
- [ ] Create webhook_logs collection
- [ ] Create presets collection
- [ ] Create audit_logs collection

---

## Phase 2: Indexes

### 2.1 User Indexes [P0]

- [ ] Unique index on email
- [ ] Sparse index on oauth.google_id
- [ ] Sparse index on oauth.github_id
- [ ] Index on created_at

### 2.2 Project Indexes [P0]

- [ ] Compound index: user_id, status, created_at
- [ ] Partial index on schedule.next_run_at
- [ ] Index on user_id, archived_at

### 2.3 Target Indexes [P0]

- [ ] Index on project_id, status
- [ ] Unique compound: project_id, url
- [ ] Index on user_id, platform

### 2.4 Result Indexes [P0]

- [ ] Compound: project_id, created_at
- [ ] Compound: target_id, created_at
- [ ] Compound: project_id, sentiment.label, created_at
- [ ] Text index on content.text, content.title
- [ ] Index on scrape_job_id

### 2.5 Job Indexes [P0]

- [ ] Index on project_id, created_at
- [ ] Partial index on status (active jobs)
- [ ] Index on user_id, created_at

### 2.6 Other Indexes [P1]

- [ ] api_keys: user_id, provider
- [ ] webhooks: user_id, active
- [ ] audit_logs: user_id, created_at (TTL)

---

## Phase 3: Validation

### 3.1 Schema Validation [P1]

- [ ] users collection validation rules
- [ ] projects collection validation rules
- [ ] targets collection validation rules
- [ ] results collection validation rules

---

## Phase 4: Seeding

### 4.1 System Data [P0]

- [ ] Seed system presets (starter, standard, advanced, budget)
- [ ] Create admin user script
- [ ] Create test data script (development)

### 4.2 Test Data [P2]

- [ ] Generate mock users
- [ ] Generate mock projects
- [ ] Generate mock results
- [ ] Generate mock jobs

---

## Phase 5: Maintenance

### 5.1 Scripts [P1]

- [ ] Index creation script
- [ ] Index rebuild script
- [ ] Data cleanup script
- [ ] Backup script

### 5.2 Monitoring [P2]

- [ ] Query performance monitoring setup
- [ ] Index usage monitoring
- [ ] Collection stats reporting

---

## Phase 6: Production

### 6.1 MongoDB Atlas [P1]

- [ ] Atlas cluster setup
- [ ] Network access configuration
- [ ] Database user creation
- [ ] Connection string (SRV)

### 6.2 Security [P0]

- [ ] Enable authentication
- [ ] Create application user (limited permissions)
- [ ] IP whitelist configuration

### 6.3 Backup [P1]

- [ ] Enable automated backups
- [ ] Configure retention policy
- [ ] Test restore procedure

---

## Checklist

### Collection Schema Status

| Collection | Schema | Indexes | Validation | Seed |
|------------|--------|---------|------------|------|
| users | [ ] | [ ] | [ ] | [ ] |
| projects | [ ] | [ ] | [ ] | [ ] |
| targets | [ ] | [ ] | [ ] | - |
| results | [ ] | [ ] | [ ] | - |
| scrape_jobs | [ ] | [ ] | [ ] | - |
| analysis_jobs | [ ] | [ ] | [ ] | - |
| api_keys | [ ] | [ ] | [ ] | - |
| webhooks | [ ] | [ ] | [ ] | - |
| webhook_logs | [ ] | [ ] | [ ] | - |
| presets | [ ] | [ ] | [ ] | [ ] |
| audit_logs | [ ] | [ ] | [ ] | - |

---

## Scripts

### Initialize Database

```python
# scripts/init_db.py
async def init_database():
    """Initialize database with collections and indexes."""
    await create_collections()
    await create_indexes()
    await seed_presets()
```

### Create Indexes

```python
# scripts/create_indexes.py
INDEXES = {
    "users": [
        IndexModel([("email", 1)], unique=True),
        # ...
    ],
    "projects": [
        IndexModel([("user_id", 1), ("status", 1), ("created_at", -1)]),
        # ...
    ],
    # ...
}
```

### Seed Presets

```python
# scripts/seed_presets.py
SYSTEM_PRESETS = [
    {
        "name": "starter",
        "display_name": "Starter",
        "description": "Basic sentiment analysis",
        # ...
    },
    # ...
]
```
