# Local Development

## Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB 6.0+ (local or Docker)
- Git

## Quick Start

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
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
```

### 3. Configure Environment

Edit `backend/.env`:

```bash
# Application
APP_NAME=sentimatrix-studio
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=sentimatrix_studio_dev

# JWT
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000

# Sentimatrix
SENTIMATRIX_LOG_LEVEL=INFO
```

### 4. Start MongoDB

Using Docker:

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:6.0
```

Or install MongoDB locally.

### 5. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend available at: http://localhost:8000

API documentation: http://localhost:8000/docs

### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local
```

### 7. Configure Frontend Environment

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/v1
```

### 8. Run Frontend

```bash
cd frontend
npm run dev
```

Frontend available at: http://localhost:3000

---

## Project Structure

```
sentimatrix-studio/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── auth/             # Authentication
│   │   ├── users/            # User management
│   │   ├── projects/         # Projects
│   │   ├── scrapers/         # Scraper config
│   │   ├── analysis/         # Analysis
│   │   ├── results/          # Results
│   │   ├── webhooks/         # Webhooks
│   │   └── core/             # Core utilities
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Utilities
│   │   ├── stores/           # Zustand stores
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── .env.example
└── docs/
```

---

## Development Workflow

### Running Tests

Backend:

```bash
cd backend
pytest                        # All tests
pytest -v                     # Verbose
pytest tests/unit/            # Unit tests only
pytest --cov=app              # With coverage
```

Frontend:

```bash
cd frontend
npm test                      # Run tests
npm run test:watch            # Watch mode
npm run test:coverage         # With coverage
```

### Code Formatting

Backend:

```bash
cd backend
ruff check .                  # Lint
ruff format .                 # Format
mypy app                      # Type check
```

Frontend:

```bash
cd frontend
npm run lint                  # ESLint
npm run format                # Prettier
npm run typecheck             # TypeScript check
```

### Database Migrations

Create indexes:

```bash
cd backend
python -m app.db.init_indexes
```

Seed data:

```bash
python -m app.db.seed
```

---

## Common Tasks

### Create Admin User

```bash
cd backend
python -m app.cli create-admin --email admin@example.com --password AdminPass123
```

### Reset Database

```bash
# Drop and recreate
python -m app.cli reset-db --confirm
```

### Generate API Client

```bash
cd frontend
npm run generate-api          # Generate from OpenAPI spec
```

---

## Troubleshooting

### MongoDB Connection Failed

```
Error: Connection refused to localhost:27017
```

Solution:
- Ensure MongoDB is running
- Check if port 27017 is available
- Verify MONGODB_URI in .env

### CORS Errors

```
Error: CORS policy blocked
```

Solution:
- Add frontend URL to CORS_ORIGINS in backend .env
- Restart backend after changes

### Module Not Found

```
ModuleNotFoundError: No module named 'app'
```

Solution:
- Ensure virtual environment is activated
- Run `pip install -e .` in backend directory

### Port Already in Use

```
Error: Address already in use
```

Solution:
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

---

## VS Code Setup

Recommended extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss"
  ]
}
```

Settings:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[typescript][typescriptreact]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```
