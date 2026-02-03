# Architecture Overview

This document describes the architecture of Sentimatrix Studio, including system components, data flow, and design decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Browser   │  │  Mobile App │  │   External Integrations │  │
│  │  (Next.js)  │  │   (Future)  │  │     (Webhooks, API)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                     │  │
│  │  • REST API Endpoints                                      │  │
│  │  • WebSocket Connections                                   │  │
│  │  • Authentication Middleware                               │  │
│  │  • Rate Limiting                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Service Layer  │ │   Job Queue     │ │  External APIs  │
│                 │ │                 │ │                 │
│ • ProjectService│ │ • Redis Queue   │ │ • LLM Providers │
│ • ScrapeService │ │ • Worker Pool   │ │ • Scraping APIs │
│ • AnalysisServ. │ │ • Job Scheduler │ │ • Webhooks      │
│ • WebhookServ.  │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │
          └─────────┬─────────┘
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                               │
│  ┌─────────────────────┐        ┌─────────────────────────────┐ │
│  │      MongoDB        │        │          Redis              │ │
│  │                     │        │                             │ │
│  │ • Users             │        │ • Session Cache             │ │
│  │ • Projects          │        │ • API Response Cache        │ │
│  │ • Targets           │        │ • Rate Limit Counters       │ │
│  │ • Results           │        │ • Job Queue                 │ │
│  │ • Schedules         │        │ • Real-time Pub/Sub         │ │
│  │ • Webhooks          │        │                             │ │
│  └─────────────────────┘        └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js)

The frontend is a Next.js 14 application with:

- **App Router**: File-based routing with layouts
- **React Server Components**: Server-side rendering where possible
- **Client Components**: Interactive UI elements
- **Zustand**: Lightweight state management
- **React Query**: Server state and caching
- **Tailwind CSS**: Utility-first styling

Key directories:

```
frontend/src/
├── app/                    # Next.js app router pages
│   ├── (auth)/            # Auth layout group
│   ├── (dashboard)/       # Dashboard layout group
│   └── api/               # API routes (BFF pattern)
├── components/
│   ├── ui/                # Base UI components
│   ├── forms/             # Form components
│   └── features/          # Feature-specific components
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities and helpers
├── services/              # API client services
└── stores/                # Zustand stores
```

### Backend (FastAPI)

The backend is a FastAPI application with:

- **Async/Await**: Full async support for I/O operations
- **Dependency Injection**: Clean, testable architecture
- **Pydantic**: Data validation and serialization
- **Motor**: Async MongoDB driver
- **ARQ**: Redis-based job queue

Key directories:

```
backend/app/
├── api/
│   └── v1/
│       ├── endpoints/     # Route handlers
│       └── deps.py        # Dependency injection
├── core/
│   ├── config.py          # Settings management
│   ├── security.py        # Auth, encryption
│   ├── database.py        # MongoDB connection
│   ├── cache.py           # Redis caching
│   └── rate_limit.py      # Rate limiting
├── models/
│   ├── user.py            # User schemas
│   ├── project.py         # Project schemas
│   └── ...                # Other schemas
├── services/
│   ├── project_service.py
│   ├── scrape_service.py
│   └── ...
└── workers/
    ├── scrape_worker.py   # Scraping jobs
    └── analysis_worker.py # Analysis jobs
```

### Database (MongoDB)

MongoDB stores all persistent data with these collections:

```
sentimatrix_studio/
├── users                  # User accounts
├── projects               # Project configurations
├── targets                # Scrape targets (URLs)
├── scrape_jobs            # Job history and status
├── results                # Scraped and analyzed content
├── schedules              # Scheduled job configurations
├── webhooks               # Webhook configurations
├── webhook_deliveries     # Webhook delivery logs
└── api_keys               # Encrypted API keys
```

**Indexing Strategy:**

- User queries: Index on `email`, `_id`
- Project queries: Index on `user_id`, `created_at`
- Results queries: Compound index on `project_id`, `created_at`, `sentiment`
- Jobs: Index on `project_id`, `status`, `created_at`

### Cache (Redis)

Redis handles:

1. **Session Storage**: JWT token blacklist
2. **API Caching**: Response caching with TTL
3. **Rate Limiting**: Token bucket counters
4. **Job Queue**: ARQ-based task queue
5. **Real-time**: Pub/sub for live updates

Key patterns:

```
cache:response:{user_id}:{endpoint}:{params_hash}
rate_limit:{user_id}:{endpoint}
session:blacklist:{token_id}
job:status:{job_id}
pubsub:user:{user_id}
```

## Data Flow

### Scrape Job Flow

```
1. User clicks "Run Scrape"
       │
       ▼
2. API creates ScrapeJob document (status: pending)
       │
       ▼
3. Job added to Redis queue
       │
       ▼
4. Worker picks up job
       │
       ├──▶ 5a. Update status: running
       │
       ▼
5. Worker scrapes each target
       │
       ├──▶ 5b. Save raw results
       │
       ▼
6. Send results to LLM for analysis
       │
       ├──▶ 6a. Save analyzed results
       │
       ▼
7. Update job status: completed
       │
       ├──▶ 7a. Trigger webhooks
       │
       ▼
8. Update project statistics
```

### Authentication Flow

```
1. User submits credentials
       │
       ▼
2. Validate against stored hash
       │
       ▼
3. Generate JWT access + refresh tokens
       │
       ▼
4. Return tokens to client
       │
       ▼
5. Client stores tokens
       │
       ▼
6. Subsequent requests include Authorization header
       │
       ▼
7. Middleware validates JWT
       │
       ├──▶ Valid: Process request
       │
       └──▶ Invalid/Expired: Return 401
```

## Security Architecture

### Authentication

- **JWT-based**: Stateless authentication
- **Access tokens**: Short-lived (30 min)
- **Refresh tokens**: Longer-lived (7 days)
- **Token blacklisting**: For logout/revocation

### Authorization

- **Role-based**: Admin, User roles
- **Resource ownership**: Users can only access their data
- **Team sharing**: Business plans can share projects

### Encryption

- **API Keys**: AES-256 encryption at rest
- **Passwords**: bcrypt hashing with salt
- **Transport**: TLS 1.3 for all connections
- **Secrets**: Environment variable injection

### Rate Limiting

Three tiers of rate limiting:

1. **Global**: 1000 req/min per IP
2. **Auth**: 10 login attempts per 15 min
3. **API**: 100 req/min per user

## Scalability Considerations

### Horizontal Scaling

- **Stateless API**: Can run multiple instances
- **Database**: MongoDB replica sets
- **Cache**: Redis cluster mode
- **Workers**: Multiple worker processes

### Vertical Scaling

- **Worker concurrency**: Configurable per instance
- **Connection pools**: Tunable limits
- **Memory caching**: In-process caching for hot data

### Performance Optimizations

- **Connection pooling**: Reuse database connections
- **Query optimization**: Proper indexing and projections
- **Response caching**: TTL-based caching for read endpoints
- **Pagination**: Cursor-based for large result sets
- **Streaming**: WebSocket for real-time updates

## Technology Decisions

### Why FastAPI?

- Native async support
- Automatic OpenAPI documentation
- Type hints and validation with Pydantic
- High performance (Starlette/Uvicorn)

### Why MongoDB?

- Flexible schema for varied content
- Good performance for document-based queries
- Easy horizontal scaling
- Rich aggregation framework

### Why Redis?

- Fast in-memory operations
- Built-in pub/sub for real-time
- Excellent for rate limiting
- Good job queue options (ARQ)

### Why Next.js?

- React with server-side rendering
- File-based routing
- API routes for BFF pattern
- Great developer experience

## Future Architecture Considerations

- **Microservices**: Split scraping into separate service
- **Event sourcing**: For audit logging and replay
- **GraphQL**: Alternative API for complex queries
- **Kubernetes**: Container orchestration for production
- **CDC**: Change data capture for analytics
