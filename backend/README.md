# Sentimatrix Studio - Backend

FastAPI backend for Sentimatrix Studio, a no-code web platform for sentiment analysis.

## Requirements

- Python 3.10+
- MongoDB 6.0+
- Redis 7.0+

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
```

## Running

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the script
studio
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_auth.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API route handlers
│   ├── core/            # Config, security, database
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   └── workers/         # Background job workers
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── Dockerfile           # Container configuration
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `MONGODB_URL` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT signing key
