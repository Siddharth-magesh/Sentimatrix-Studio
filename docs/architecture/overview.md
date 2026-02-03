# Architecture Overview

## Introduction

Sentimatrix Studio is a full-stack web application that provides a no-code interface for sentiment analysis and social media monitoring. The platform allows users to configure scrapers, LLM providers, and analysis pipelines through an intuitive dashboard.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Sentimatrix Studio                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐  ┌─────────────┐  │
│  │   Frontend   │    │   Backend    │    │   MongoDB   │  │    Redis    │  │
│  │   (Next.js)  │◄──►│  (FastAPI)   │◄──►│  (Database) │  │   (Cache)   │  │
│  └──────────────┘    └──────────────┘    └─────────────┘  └─────────────┘  │
│         │                   │                                               │
│         │         ┌─────────┴─────────────┐                                 │
│         │         ▼                       ▼                                 │
│         │  ┌────────────────┐    ┌────────────────┐                        │
│         │  │  Job Workers   │    │   Scheduler    │                        │
│         │  │ (Background)   │    │  (Cron Jobs)   │                        │
│         │  └────────────────┘    └────────────────┘                        │
│         │         │                       │                                 │
│         │         ▼                       ▼                                 │
│         │  ┌──────────────────────────────────────┐                        │
│         │  │         Sentimatrix Library          │                        │
│         │  │   (Scraping + Analysis Engine)       │                        │
│         │  └──────────────────────────────────────┘                        │
│         │         │                       │                                 │
│         │  ┌──────┴───────┐       ┌──────┴───────┐                        │
│         │  ▼              ▼       ▼              ▼                         │
│         │  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│         │  │  Scrapers  │  │    LLMs    │  │  Webhooks  │                 │
│         │  └────────────┘  └────────────┘  └────────────┘                 │
│         │         │              │                │                        │
│         ▼         ▼              ▼                ▼                        │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                       External Services                               │ │
│  │  Amazon  Steam  YouTube  Reddit  Trustpilot  Yelp  Google Reviews    │ │
│  │  OpenAI  Groq  Anthropic  ScraperAPI  Apify  BrightData  Custom      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend (Next.js 14)

The frontend is built with Next.js 14 using the App Router, providing:

- Server-side rendering for SEO and performance
- React Server Components for optimal loading
- TypeScript for type safety
- Tailwind CSS for styling
- Zustand for client-side state management

**Key Features:**
- Authentication pages (login, register, password reset)
- Dashboard with analytics overview
- Project management interface
- Scraper configuration wizard
- LLM provider configuration
- Real-time analysis results
- Export and reporting tools

### 2. Backend (FastAPI)

The backend is built with FastAPI, providing:

- Async/await support for high concurrency
- Automatic OpenAPI documentation
- Pydantic models for validation
- JWT-based authentication
- Background task processing
- WebSocket support for real-time updates

**Key Features:**
- RESTful API endpoints
- User authentication and authorization
- Project and configuration management
- Scraping job orchestration
- Analysis pipeline execution
- Webhook integrations with HMAC signing
- Scheduled job execution
- Rate limiting (token bucket algorithm)
- Response caching with TTL
- API key encryption (AES-256)

**Core Modules:**
- `app/core/` - Configuration, security, database, caching, rate limiting, validators
- `app/api/` - API route handlers organized by version
- `app/models/` - Pydantic schemas for all entities
- `app/repositories/` - Database access layer
- `app/services/` - Business logic (scraping, analysis, scheduling, webhooks)
- `app/workers/` - Background job processors

### 3. Database (MongoDB)

MongoDB is used for flexible document storage:

- Users and authentication
- Projects and configurations
- Targets (URLs to scrape)
- Scrape jobs and status
- Analysis results
- Schedules
- Webhooks and delivery logs
- Encrypted API keys
- Audit logs

### 4. Cache (Redis)

Redis provides:

- API response caching with TTL
- Rate limit counters (token bucket)
- Session management
- Job queue for background tasks
- Real-time pub/sub for live updates

### 5. Sentimatrix Library

The core Sentimatrix library provides:

- 19 LLM provider integrations
- 15 scraper integrations
- Sentiment and emotion analysis
- Batch processing capabilities
- Caching and rate limiting

## Data Flow

### User Registration Flow

```
User → Frontend → POST /api/auth/register → Backend → MongoDB
                                              │
                                              ▼
                                    Create user document
                                    Generate JWT tokens
                                              │
                                              ▼
                                    Return tokens to frontend
                                    Store in HTTP-only cookies
```

### Scraping Flow

```
User triggers scrape → Frontend → POST /api/scrape/run → Backend
                                                           │
                                                           ▼
                                                   Validate config
                                                   Queue background job
                                                           │
                                                           ▼
                                                   Execute Sentimatrix
                                                   scraper
                                                           │
                                                           ▼
                                                   Store results in MongoDB
                                                   Notify via WebSocket
```

### Analysis Flow

```
Scraping complete → Backend → Execute Sentimatrix analysis
                                        │
                                        ▼
                              Store analysis results
                              Update project stats
                                        │
                                        ▼
                              Notify frontend via WebSocket
                              User sees updated dashboard
```

## Design Principles

### 1. No-Code First

Every feature must be accessible through the UI without requiring users to write code.

### 2. Configuration as Data

All configurations are stored as structured data in MongoDB, enabling:
- Version history
- Easy duplication
- Sharing between users
- Preset templates

### 3. Progressive Complexity

Users start with simple presets and can progressively access more advanced options:
- Starter: Basic presets, limited customization
- Standard: Full configuration access
- Advanced: Custom code snippets, webhooks

### 4. Real-Time Feedback

All long-running operations provide real-time progress updates via WebSockets.

### 5. Defensive Design

- Rate limiting on all endpoints
- Input validation at every layer
- Audit logging for security events
- Graceful error handling

## Scalability Considerations

### Horizontal Scaling

- Stateless backend enables multiple instances
- MongoDB replica sets for database scaling
- Redis cluster for distributed caching
- Load balancing with Traefik or nginx

### Background Processing

- FastAPI BackgroundTasks for simple jobs
- ARQ (Redis-based) for job queue
- Scheduler service for cron-like scheduled tasks
- Worker pool for concurrent job execution

### Caching Strategy

- Redis for API response caching with TTL
- In-memory caching for hot data (LRU)
- MongoDB aggregation pipelines for analytics
- CDN for static assets

## Security Architecture

See [security.md](security.md) for detailed security documentation.

**Key Security Features:**
- JWT tokens with refresh mechanism (30 min access, 7 day refresh)
- Password hashing with bcrypt
- Rate limiting per user/IP (token bucket algorithm)
- Input sanitization and validation
- CORS configuration with allowed origins
- API key encryption at rest (AES-256 with Fernet)
- HMAC-SHA256 webhook payload signing
- Request ID tracking for audit trails

## API Architecture

The API follows RESTful conventions:

**Endpoints:**
- `/api/v1/auth/*` - Authentication (login, register, refresh, logout)
- `/api/v1/projects/*` - Project management
- `/api/v1/projects/{id}/targets/*` - Target management
- `/api/v1/projects/{id}/jobs/*` - Scrape jobs
- `/api/v1/projects/{id}/results/*` - Analysis results
- `/api/v1/schedules/*` - Scheduled jobs
- `/api/v1/webhooks/*` - Webhook management
- `/api/v1/settings/*` - User settings and API keys
- `/api/v1/dashboard/*` - Dashboard statistics

**Response Format:**
- Paginated lists return `{items, total, page, per_page, pages}`
- Single resources return the full object
- Errors return `{detail, code}` with appropriate HTTP status

## Testing Architecture

**Backend Testing:**
- pytest with pytest-asyncio for async tests
- mongomock for database mocking
- fakeredis for cache mocking
- httpx AsyncClient for API testing

**Frontend Testing:**
- Jest with React Testing Library for components
- Playwright for E2E testing
- MSW for API mocking

**Test Organization:**
- `tests/unit/` - Unit tests for models, validators, utilities
- `tests/api/` - API endpoint integration tests
- `tests/integration/` - Service integration tests
- `e2e/tests/` - End-to-end browser tests
