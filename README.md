# Sentimatrix Studio

A no-code web platform for sentiment analysis and social media monitoring. Scrape reviews from Amazon, Steam, YouTube, Reddit, and more, then analyze sentiment and emotions using AI-powered models.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

## Features

- **Multi-Platform Scraping** - Collect reviews from Amazon, Steam, YouTube, Reddit, Trustpilot, Yelp, and Google Reviews
- **AI-Powered Analysis** - Sentiment analysis (3 or 5 class) and emotion detection using Groq, OpenAI, or Anthropic
- **No-Code Interface** - Configure scrapers, LLM providers, and analysis pipelines through an intuitive UI
- **Preset Configurations** - Quick setup with Starter, Standard, Advanced, Budget, and Enterprise presets
- **Scheduled Scraping** - Automate data collection with hourly, daily, weekly, or monthly schedules
- **Real-time Webhooks** - Get notified when scrape jobs complete or new results are available
- **Export Options** - Download results as CSV, JSON, or Excel
- **Analytics Dashboard** - Visualize sentiment trends, emotion distributions, and key insights

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | Next.js 14 (React, TypeScript) |
| Database | MongoDB 7.0 |
| Cache/Queue | Redis 7 |
| Authentication | JWT + OAuth2 (Google, GitHub) |
| Core Library | [Sentimatrix](https://github.com/sentimatrix/sentimatrix) |
| Styling | Tailwind CSS |
| State Management | Zustand + React Query |
| Charts | Recharts |
| Testing | pytest, Jest, Playwright |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/sentimatrix/sentimatrix-studio.git
cd sentimatrix-studio

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

#### Required Services

```bash
# MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7

# Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sentimatrix_studio

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (generate secure keys for production)
SECRET_KEY=your-32-character-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-64-character-hex-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: LLM API Keys (users can also add via UI)
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key
```

### LLM Providers

Sentimatrix Studio supports multiple LLM providers:

| Provider | Models | Free Tier |
|----------|--------|-----------|
| **Groq** | LLaMA 3.1 70B/8B, Mixtral | Yes |
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-3.5 | No |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Haiku | No |

Users can add their own API keys via Settings > API Keys.

## Project Structure

```
sentimatrix-studio/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API route handlers
│   │   ├── core/            # Config, security, database
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic
│   │   └── workers/         # Background job workers
│   └── tests/               # Backend tests
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities and API client
│   │   └── stores/          # Zustand stores
│   └── e2e/                 # Playwright E2E tests
├── docs/                    # Documentation
├── docker/                  # Docker configurations
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Local development
└── docker-compose.prod.yml  # Production deployment
```

## Usage

### 1. Create an Account

Register at `http://localhost:3000/auth/register` or login if you already have an account.

### 2. Configure LLM Provider

Go to **Settings > API Keys** and add your LLM provider API key (Groq recommended for free tier).

### 3. Create a Project

1. Click **Create Project** from the dashboard
2. Enter a name and description
3. Choose a preset (Standard recommended) or customize settings
4. Click **Create**

### 4. Add Targets

1. Open your project
2. Go to the **Targets** tab
3. Click **Add Target**
4. Paste URLs (e.g., Amazon product pages, Steam games, YouTube videos)
5. The platform auto-detects the platform type

### 5. Run Analysis

1. Click **Run Scrape** on the project overview
2. Monitor progress in real-time
3. View results in the **Results** tab
4. Export data as CSV, JSON, or Excel

### 6. Automate (Optional)

- **Scheduling**: Set up automated scrapes (hourly, daily, weekly)
- **Webhooks**: Get notified when jobs complete

## API

The REST API is available at `http://localhost:8000/api/v1/`.

### Quick Examples

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=yourpassword"

# List projects
curl http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "preset": "standard"}'
```

### Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Full API Reference**: [docs/api-reference/](docs/api-reference/)

## Testing

### Backend

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tests
pytest tests/api/test_projects.py -v
```

### Frontend

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npx playwright test

# Run E2E with UI
npx playwright test --ui
```

## Deployment

### Docker Production

```bash
# Build and run production containers
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup

For production, ensure you:

1. Generate secure keys for `SECRET_KEY`, `JWT_SECRET_KEY`, and `ENCRYPTION_KEY`
2. Configure proper MongoDB authentication
3. Set up HTTPS with a reverse proxy (Traefik included in prod compose)
4. Configure proper CORS origins
5. Set `DEBUG=false` and `ENVIRONMENT=production`

See [docs/developer-guide/deployment.md](docs/developer-guide/deployment.md) for detailed instructions.

## Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/user-guide/getting-started.md) | Getting started for end users |
| [Developer Guide](docs/developer-guide/getting-started.md) | Development environment setup |
| [API Reference](docs/api-reference/overview.md) | Complete REST API documentation |
| [Architecture](docs/architecture/overview.md) | System architecture and design |
| [Testing](docs/developer-guide/testing.md) | Testing strategies and tools |

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/sentimatrix/studio/issues)
- **Email**: support@sentimatrix.io

## Acknowledgments

- [Sentimatrix](https://github.com/sentimatrix/sentimatrix) - Core sentiment analysis library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
