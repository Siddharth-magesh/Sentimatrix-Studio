# Developer Guide: Getting Started

This guide will help you set up a local development environment for Sentimatrix Studio.

## Prerequisites

### Required Software

- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend runtime
- **MongoDB 6.0+**: Primary database
- **Redis 7.0+**: Caching and job queue
- **Git**: Version control

### Optional

- **Docker & Docker Compose**: Containerized setup
- **Poetry**: Python dependency management (recommended)
- **pnpm**: Fast Node.js package manager (recommended)

## Quick Setup with Docker

The fastest way to get started:

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

## Manual Setup

### 1. Clone Repository

```bash
git clone https://github.com/sentimatrix/sentimatrix-studio.git
cd sentimatrix-studio
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or with Poetry (recommended)
poetry install

# Copy environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sentimatrix_studio

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-32-byte-encryption-key

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: LLM API Keys (for testing)
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key
```

Start the backend:

```bash
# Development with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Poetry
poetry run uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Or with pnpm (recommended)
pnpm install

# Copy environment file
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

Start the frontend:

```bash
# Development
npm run dev

# Or with pnpm
pnpm dev
```

### 4. Database Setup

**MongoDB:**

```bash
# Start MongoDB
mongod --dbpath /path/to/data

# Or with Docker
docker run -d -p 27017:27017 --name mongodb mongo:6
```

**Redis:**

```bash
# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 --name redis redis:7
```

## Project Structure

```
sentimatrix-studio/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   │   └── v1/        # Version 1 endpoints
│   │   ├── core/          # Core utilities
│   │   │   ├── config.py  # Configuration
│   │   │   ├── security.py # Auth & encryption
│   │   │   ├── database.py # MongoDB connection
│   │   │   └── cache.py   # Redis caching
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic
│   │   ├── workers/       # Background jobs
│   │   └── main.py        # FastAPI application
│   ├── tests/             # Test suite
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── services/      # API clients
│   │   └── stores/        # State management
│   ├── public/            # Static assets
│   └── package.json
├── docs/                  # Documentation
├── docker-compose.yml
└── README.md
```

## Development Workflow

### Running Tests

**Backend:**

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_projects.py

# Run specific test
pytest tests/api/test_projects.py::TestProjects::test_create_project
```

**Frontend:**

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

### Code Quality

**Backend:**

```bash
# Linting
ruff check app/

# Formatting
black app/

# Type checking
mypy app/
```

**Frontend:**

```bash
# Linting
npm run lint

# Formatting
npm run format

# Type checking
npm run type-check
```

### Database Migrations

We use Alembic for database schema migrations:

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## IDE Setup

### VS Code

Recommended extensions:

- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- MongoDB for VS Code

Workspace settings (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm / WebStorm

1. Mark `backend/app` as Sources Root
2. Mark `frontend/src` as Sources Root
3. Configure Python interpreter to use venv
4. Enable ESLint integration

## Troubleshooting

### MongoDB connection failed

- Verify MongoDB is running: `mongosh`
- Check connection URL in `.env`
- Ensure port 27017 is not blocked

### Redis connection failed

- Verify Redis is running: `redis-cli ping`
- Check Redis URL in `.env`
- Ensure port 6379 is not blocked

### Import errors

- Verify virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version`

### Frontend build errors

- Delete `node_modules` and reinstall
- Clear Next.js cache: `rm -rf .next`
- Check Node version: `node --version`

## Next Steps

- [Architecture Overview](./architecture.md)
- [API Development](./api-development.md)
- [Frontend Development](./frontend-development.md)
- [Testing Guide](./testing.md)
- [Deployment Guide](./deployment.md)
