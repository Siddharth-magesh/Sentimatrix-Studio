# Sentimatrix Studio Documentation

Sentimatrix Studio is a no-code web platform for sentiment analysis and social media monitoring. Users can configure scrapers, LLM providers, and analysis pipelines through an intuitive UI without writing any code.

## Documentation Structure

### User Guide

For end users of Sentimatrix Studio:

| Document | Description |
|----------|-------------|
| [Getting Started](./user-guide/getting-started.md) | Quick start guide for new users |
| [Managing Projects](./user-guide/projects.md) | Project configuration and management |
| [LLM Configuration](./user-guide/llm-configuration.md) | Setting up AI providers |
| [Scheduling](./user-guide/scheduling.md) | Automated scrape jobs |
| [Webhooks](./user-guide/webhooks.md) | Real-time notifications |
| [Analytics](./user-guide/analytics.md) | Understanding your data |
| [FAQ](./user-guide/faq.md) | Frequently asked questions |

### Developer Guide

For developers building with or contributing to Sentimatrix Studio:

| Document | Description |
|----------|-------------|
| [Getting Started](./developer-guide/getting-started.md) | Development environment setup |
| [Architecture](./developer-guide/architecture.md) | System architecture overview |
| [API Development](./developer-guide/api-development.md) | Building API endpoints |
| [Testing](./developer-guide/testing.md) | Testing strategies and tools |
| [Deployment](./developer-guide/deployment.md) | Production deployment guide |

### API Reference

Complete REST API documentation:

| Document | Description |
|----------|-------------|
| [Overview](./api-reference/overview.md) | API introduction and basics |
| [Authentication](./api-reference/authentication.md) | Auth endpoints and tokens |
| [Projects](./api-reference/projects.md) | Project management API |
| [Targets](./api-reference/targets.md) | Target (URL) management API |
| [Jobs](./api-reference/jobs.md) | Scrape job management API |
| [Results](./api-reference/results.md) | Results and analytics API |
| [Schedules](./api-reference/schedules.md) | Automated scheduling API |
| [Webhooks](./api-reference/webhooks.md) | Webhook configuration API |
| [Settings](./api-reference/settings.md) | API keys, providers, presets |
| [Billing](./api-reference/billing.md) | Subscription and usage API |

### Technical Documentation

Detailed technical documentation:

| Directory | Description |
|-----------|-------------|
| [architecture/](./architecture/) | System architecture and design |
| [api/](./api/) | Backend API specifications |
| [frontend/](./frontend/) | Frontend architecture |
| [database/](./database/) | Database schema and indexes |
| [deployment/](./deployment/) | Deployment configurations |

## Quick Links

### For Users

| Task | Documentation |
|------|--------------|
| Create first project | [Getting Started](./user-guide/getting-started.md#create-your-first-project) |
| Configure LLM provider | [LLM Configuration](./user-guide/llm-configuration.md) |
| Set up scheduled scrapes | [Scheduling](./user-guide/scheduling.md) |
| Export results | [Analytics](./user-guide/analytics.md#exporting-data) |

### For Developers

| Task | Documentation |
|------|--------------|
| Set up dev environment | [Developer Getting Started](./developer-guide/getting-started.md) |
| Understand architecture | [Architecture Overview](./developer-guide/architecture.md) |
| Write tests | [Testing Guide](./developer-guide/testing.md) |
| Deploy to production | [Deployment Guide](./developer-guide/deployment.md) |

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | Next.js 14 (React, TypeScript) |
| Database | MongoDB |
| Cache | Redis |
| Authentication | JWT + OAuth2 |
| Core Library | Sentimatrix |
| Styling | Tailwind CSS |
| State | Zustand + React Query |
| Charts | Recharts |
| Testing | pytest, Jest, Playwright |

## Getting Help

- **Email Support**: support@sentimatrix.io
- **Community Forum**: forum.sentimatrix.io
- **GitHub Issues**: github.com/sentimatrix/studio/issues

## Version

- Documentation Version: 1.0.0
- Release: v1.0.0
