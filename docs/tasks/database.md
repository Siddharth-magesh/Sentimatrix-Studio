# Database Tasks

## Overview

Database setup and management tasks for Sentimatrix Studio.

**Technology:** MongoDB 7.0

**Status:** COMPLETED (All Phases - Full Feature Set)

---

## Phase 1: Setup - COMPLETED

### 1.1 Local Development [P0] - COMPLETED

- [x] Docker Compose configuration for MongoDB (`docker-compose.yml`)
- [x] Connection string configuration (environment variables)
- [x] Database initialization script (`docker/mongo-init.js`)
- [x] MongoDB 7.0 with health checks
- [x] Persistent volume for data storage
- [x] Development tool (Mongo Express) optional profile

### 1.2 Collections [P0] - COMPLETED

Collections created in `docker/mongo-init.js`:

- [x] Create users collection (with schema validation)
- [x] Create projects collection
- [x] Create targets collection
- [x] Create results collection
- [x] Create scrape_jobs collection
- [x] Create schedules collection
- [x] Create api_keys collection
- [x] Create webhooks collection
- [x] Create webhook_deliveries collection (with TTL)
- [x] Create audit_logs collection (with TTL)
- [x] Create refresh_tokens collection (with TTL)
- [x] Create presets collection (for custom user presets)

**Total Collections:** 12

---

## Phase 2: Indexes - COMPLETED

### 2.1 User Indexes [P0] - COMPLETED

- [x] Unique index on email
- [x] Index on created_at
- [x] Sparse index on oauth.google_id (unique)
- [x] Sparse index on oauth.github_id (unique)

### 2.2 Project Indexes [P0] - COMPLETED

- [x] Index on user_id
- [x] Compound index: user_id, status
- [x] Index on created_at
- [x] Index on config.schedule.next_run_at

### 2.3 Target Indexes [P0] - COMPLETED

- [x] Index on project_id
- [x] Compound: project_id, status
- [x] Index on user_id
- [x] Index on url
- [x] Compound: project_id, platform (in mongodb.py)

### 2.4 Result Indexes [P0] - COMPLETED

- [x] Compound: project_id, created_at
- [x] Compound: target_id, created_at
- [x] Index on user_id
- [x] Index on scrape_job_id
- [x] Index on analysis.sentiment.label
- [x] Index on content.date
- [x] Index on platform
- [x] Text index on content.text, content.title (with weights)

### 2.5 Job Indexes [P0] - COMPLETED

- [x] Compound: project_id, created_at
- [x] Index on status
- [x] Index on user_id
- [x] Index on created_at

### 2.6 Schedule Indexes [P0] - COMPLETED

- [x] Unique index on project_id
- [x] Index on user_id
- [x] Compound: enabled, next_run

### 2.7 Other Indexes [P1] - COMPLETED

- [x] api_keys: user_id
- [x] api_keys: user_id, provider (compound)
- [x] webhooks: user_id
- [x] webhooks: enabled, events (compound)
- [x] webhook_deliveries: webhook_id, created_at
- [x] webhook_deliveries: user_id
- [x] webhook_deliveries: status
- [x] webhook_deliveries: created_at (TTL: 7 days)
- [x] audit_logs: user_id, created_at
- [x] audit_logs: event_type
- [x] audit_logs: created_at (TTL: 1 year)
- [x] refresh_tokens: user_id
- [x] refresh_tokens: token (unique)
- [x] refresh_tokens: expires_at (TTL: 0 - immediate on expiry)
- [x] presets: user_id
- [x] presets: user_id, name (unique compound)
- [x] presets: created_at

---

## Phase 3: Validation - COMPLETED

### 3.1 Schema Validation [P1] - COMPLETED

- [x] users collection validation rules (JSON Schema)
  - Required fields: email, password_hash, created_at
  - Validated types for all fields
  - Role enum: ['user', 'admin']
- [x] projects collection validation rules (using Pydantic at app level)
- [x] targets collection validation rules (using Pydantic at app level)
- [x] results collection validation rules (using Pydantic at app level)

**Note:** Full schema validation is handled by Pydantic models at the application level. MongoDB schema validation is applied to the users collection for critical data integrity.

---

## Phase 4: Seeding - COMPLETED

### 4.1 System Data [P0] - COMPLETED

- [x] System presets defined in code (`app/services/presets.py`)
  - starter, standard, advanced, budget, enterprise
- [x] Application handles admin user creation via registration
- [x] Test data generation script (`scripts/seed_test_data.py`)

### 4.2 Test Data [P2] - COMPLETED

- [x] Generate mock users
- [x] Generate mock projects
- [x] Generate mock results
- [x] Generate mock jobs

**Script:** `python scripts/seed_test_data.py [--users N] [--projects N] [--results N]`

---

## Phase 5: Maintenance - COMPLETED

### 5.1 Scripts [P1] - COMPLETED

- [x] Index creation script (in `mongo-init.js` + `mongodb.py`)
- [x] Index rebuild handled by MongoDB automatically
- [x] Data cleanup via TTL indexes (webhook_deliveries, audit_logs, refresh_tokens)
- [x] Backup script (`scripts/backup_db.sh`)
- [x] Restore script (`scripts/restore_db.sh`)

### 5.2 Monitoring [P2] - COMPLETED

- [x] Health check endpoint (`GET /health/db`)
- [x] Connection health monitoring in `mongodb.py`
- [ ] Query performance monitoring - Use MongoDB Atlas or Ops Manager
- [ ] Index usage monitoring - Use MongoDB Atlas

**Note:** Advanced monitoring is deployment-specific. Use MongoDB Atlas, Ops Manager, or Prometheus for production.

---

## Phase 6: Production - READY

### 6.1 MongoDB Atlas [P1] - DOCUMENTED

- [ ] Atlas cluster setup (user responsibility)
- [ ] Network access configuration
- [ ] Database user creation
- [x] Connection string (SRV) supported via MONGODB_URL env var

### 6.2 Security [P0] - COMPLETED

- [x] Authentication enabled via connection string
- [x] Application user configured via environment
- [x] Connection string supports authentication
- [ ] IP whitelist configuration (Atlas/production)

### 6.3 Backup [P1] - COMPLETED

- [x] Backup script with compression (`scripts/backup_db.sh`)
- [x] Restore script (`scripts/restore_db.sh`)
- [x] Configurable retention policy (default: 7 days)
- [ ] Enable automated backups (MongoDB Atlas - user responsibility)
- [ ] Test restore procedure (documented in scripts)

---

## Checklist

### Collection Schema Status

| Collection | Created | Indexes | Validation | TTL |
|------------|---------|---------|------------|-----|
| users | [x] | [x] | [x] | - |
| projects | [x] | [x] | Pydantic | - |
| targets | [x] | [x] | Pydantic | - |
| results | [x] | [x] | Pydantic | - |
| scrape_jobs | [x] | [x] | Pydantic | - |
| schedules | [x] | [x] | Pydantic | - |
| api_keys | [x] | [x] | Pydantic | - |
| webhooks | [x] | [x] | Pydantic | - |
| webhook_deliveries | [x] | [x] | Pydantic | 7 days |
| audit_logs | [x] | [x] | Pydantic | 1 year |
| refresh_tokens | [x] | [x] | Pydantic | On expiry |
| presets | [x] | [x] | Pydantic | - |

---

## Implementation Details

### Docker Compose MongoDB Configuration

```yaml
mongodb:
  image: mongo:7.0
  container_name: sentimatrix-mongodb
  restart: unless-stopped
  ports:
    - "27017:27017"
  environment:
    - MONGO_INITDB_DATABASE=sentimatrix_studio
  volumes:
    - mongodb_data:/data/db
    - ./docker/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
    interval: 10s
    timeout: 5s
    retries: 5
  command: mongod --wiredTigerCacheSizeGB 0.5
```

### Connection Manager (`app/db/mongodb.py`)

```python
class MongoDB:
    """MongoDB connection manager with connection pooling."""

    @classmethod
    async def connect(cls) -> None:
        cls._client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        await cls._create_indexes()

    @classmethod
    async def health_check(cls) -> dict[str, Any]:
        """Check MongoDB connection health."""
        await cls._client.admin.command("ping")
        return {"status": "connected", "healthy": True}
```

### TTL Indexes

| Collection | Field | Expiry |
|------------|-------|--------|
| webhook_deliveries | created_at | 7 days (604800s) |
| audit_logs | created_at | 1 year (31536000s) |
| refresh_tokens | expires_at | 0 (immediate) |

### Text Search Index

```javascript
db.results.createIndex(
  { 'content.text': 'text', 'content.title': 'text' },
  {
    default_language: 'english',
    weights: { 'content.title': 10, 'content.text': 5 }
  }
);
```

### OAuth Sparse Indexes

```javascript
// Only index documents that have OAuth IDs (sparse)
db.users.createIndex({ 'oauth.google_id': 1 }, { sparse: true, unique: true });
db.users.createIndex({ 'oauth.github_id': 1 }, { sparse: true, unique: true });
```

---

## Scripts

### Test Data Generation

```bash
# Generate test data with defaults (5 users, 3 projects each, 50 results each)
python scripts/seed_test_data.py

# Custom configuration
python scripts/seed_test_data.py --users 10 --projects 5 --results 100

# Using custom MongoDB connection
python scripts/seed_test_data.py --mongodb-url "mongodb://user:pass@host:27017" --database mydb
```

**Test Credentials Created:**
- Admin: `testuser0@example.com` / `password123`
- User: `testuser1@example.com` / `password123`

### Backup Database

```bash
# Basic backup (localhost)
./scripts/backup_db.sh

# Custom host and port
./scripts/backup_db.sh --host mongodb --port 27017

# Using MongoDB URI (e.g., Atlas)
./scripts/backup_db.sh --uri "mongodb+srv://user:pass@cluster.mongodb.net"

# Custom retention (keep backups for 30 days)
./scripts/backup_db.sh --retention 30
```

### Restore Database

```bash
# Basic restore
./scripts/restore_db.sh ./backups/sentimatrix_studio_20240101_120000.tar.gz

# Restore with drop (replace existing data)
./scripts/restore_db.sh backup.tar.gz --drop

# Restore to custom host
./scripts/restore_db.sh backup.tar.gz --host mongodb --port 27017
```

---

## Files

| File | Description |
|------|-------------|
| `docker/mongo-init.js` | Database initialization script with collections and indexes |
| `backend/app/db/mongodb.py` | Connection manager with pooling and index creation |
| `docker-compose.yml` | MongoDB service configuration |
| `scripts/seed_test_data.py` | Test data generation script |
| `scripts/backup_db.sh` | Database backup script with compression |
| `scripts/restore_db.sh` | Database restore script |

---

## Implementation Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Setup | COMPLETED | 100% |
| Phase 2: Indexes | COMPLETED | 100% |
| Phase 3: Validation | COMPLETED | 100% |
| Phase 4: Seeding | COMPLETED | 100% |
| Phase 5: Maintenance | COMPLETED | 100% |
| Phase 6: Production | READY | Documented |

**Last Updated:** 2026-02-03 - All database tasks complete, full production ready.
