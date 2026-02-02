# Sentimatrix Studio Documentation

Sentimatrix Studio is a no-code web platform for sentiment analysis and social media monitoring. Users can configure scrapers, LLM providers, and analysis pipelines through an intuitive UI without writing any code.

## Documentation Structure

```
docs/
├── README.md                    # This file
├── architecture/                # System architecture and design
│   ├── overview.md             # High-level architecture
│   ├── components.md           # Component breakdown
│   ├── data-flow.md            # Data flow diagrams
│   └── security.md             # Security architecture
├── api/                        # Backend API documentation
│   ├── overview.md             # API design principles
│   ├── authentication.md       # Auth endpoints
│   ├── users.md                # User management
│   ├── projects.md             # Project endpoints
│   ├── scrapers.md             # Scraper configuration
│   ├── analysis.md             # Analysis endpoints
│   └── webhooks.md             # Webhook integrations
├── frontend/                   # Frontend documentation
│   ├── overview.md             # Frontend architecture
│   ├── components.md           # UI components
│   ├── pages.md                # Page structure
│   ├── state-management.md     # State management
│   └── styling.md              # Design system
├── database/                   # Database documentation
│   ├── schema.md               # MongoDB schema design
│   ├── collections.md          # Collection definitions
│   ├── indexes.md              # Index strategies
│   └── migrations.md           # Data migrations
├── deployment/                 # Deployment documentation
│   ├── local.md                # Local development
│   ├── docker.md               # Docker deployment
│   ├── production.md           # Production deployment
│   └── monitoring.md           # Monitoring and logging
├── guides/                     # User and developer guides
│   ├── quickstart.md           # Getting started
│   ├── configuration.md        # Configuration guide
│   ├── presets.md              # Configuration presets
│   └── troubleshooting.md      # Common issues
└── tasks/                      # Task tracking
    ├── overview.md             # Project status
    ├── backend.md              # Backend tasks
    ├── frontend.md             # Frontend tasks
    ├── database.md             # Database tasks
    ├── testing.md              # Testing tasks
    ├── deployment.md           # Deployment tasks
    └── documentation.md        # Documentation tasks
```

## Quick Links

- [Architecture Overview](architecture/overview.md)
- [API Documentation](api/overview.md)
- [Frontend Guide](frontend/overview.md)
- [Database Schema](database/schema.md)
- [Deployment Guide](deployment/local.md)
- [Task Tracking](tasks/overview.md)

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.10+) |
| Frontend | Next.js 14 (React, TypeScript) |
| Database | MongoDB |
| Authentication | JWT + OAuth2 |
| Core Library | Sentimatrix |
| Styling | Tailwind CSS |
| State | Zustand |
| Charts | Recharts |

## Version

- Documentation Version: 1.0.0
- Target Release: v0.1.0
