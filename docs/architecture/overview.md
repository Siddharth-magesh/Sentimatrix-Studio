# Architecture Overview

## Introduction

Sentimatrix Studio is a full-stack web application that provides a no-code interface for sentiment analysis and social media monitoring. The platform allows users to configure scrapers, LLM providers, and analysis pipelines through an intuitive dashboard.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Sentimatrix Studio                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   Frontend   │    │   Backend    │    │       Database           │  │
│  │   (Next.js)  │◄──►│  (FastAPI)   │◄──►│       (MongoDB)          │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│         │                   │                        │                   │
│         │                   ▼                        │                   │
│         │            ┌──────────────┐                │                   │
│         │            │  Sentimatrix │                │                   │
│         │            │    Library   │                │                   │
│         │            └──────────────┘                │                   │
│         │                   │                        │                   │
│         │         ┌─────────┴─────────┐              │                   │
│         │         ▼                   ▼              │                   │
│         │  ┌────────────┐    ┌────────────┐         │                   │
│         │  │  Scrapers  │    │    LLMs    │         │                   │
│         │  └────────────┘    └────────────┘         │                   │
│         │         │                   │              │                   │
│         ▼         ▼                   ▼              ▼                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    External Services                              │  │
│  │  Amazon  Steam  YouTube  Reddit  IMDB  OpenAI  Groq  Anthropic   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
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
- Webhook integrations

### 3. Database (MongoDB)

MongoDB is used for flexible document storage:

- Users and authentication
- Projects and configurations
- Scraping results
- Analysis data
- Audit logs

### 4. Sentimatrix Library

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
- Redis for session storage and caching (future)

### Background Processing

- FastAPI BackgroundTasks for simple jobs
- Celery with Redis for complex workflows (future)

### Caching Strategy

- In-memory caching for frequently accessed data
- MongoDB aggregation pipelines for analytics
- CDN for static assets

## Security Architecture

See [security.md](security.md) for detailed security documentation.

**Key Security Features:**
- JWT tokens with refresh mechanism
- Password hashing with bcrypt
- Rate limiting per user/IP
- Input sanitization
- CORS configuration
- API key encryption at rest
