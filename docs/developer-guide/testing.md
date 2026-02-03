# Testing Guide

This guide covers testing strategies, tools, and best practices for Sentimatrix Studio.

## Testing Stack

### Backend
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: Async HTTP client for API testing
- **mongomock**: MongoDB mocking
- **fakeredis**: Redis mocking
- **coverage**: Code coverage

### Frontend
- **Jest**: Test framework
- **React Testing Library**: Component testing
- **Playwright**: End-to-end testing
- **MSW**: API mocking

## Backend Testing

### Setup

Install test dependencies:

```bash
cd backend
pip install -r requirements-test.txt
```

Configure pytest in `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
```

### Test Structure

```
backend/tests/
├── conftest.py           # Shared fixtures
├── api/
│   ├── test_auth.py      # Auth endpoint tests
│   ├── test_projects.py  # Project endpoint tests
│   └── ...
├── services/
│   ├── test_project_service.py
│   └── ...
├── unit/
│   ├── test_validators.py
│   └── ...
└── integration/
    ├── test_scraping.py
    └── ...
```

### Fixtures

Create shared fixtures in `conftest.py`:

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.core.database import get_db

@pytest.fixture
def mongodb():
    """Create mock MongoDB client."""
    client = AsyncMongoMockClient()
    return client.sentimatrix_test

@pytest.fixture
async def client(mongodb):
    """Create test HTTP client."""
    async def override_get_db():
        return mongodb

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }

@pytest.fixture
async def authenticated_user(client, test_user_data):
    """Create and authenticate a test user."""
    # Register
    await client.post("/api/v1/auth/register", json=test_user_data)

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Writing Tests

#### Unit Tests

Test individual functions in isolation:

```python
# tests/unit/test_validators.py
import pytest
from app.core.validators import validate_email, validate_password

class TestEmailValidation:
    def test_valid_email(self):
        assert validate_email("user@example.com") == "user@example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(ValueError, match="Invalid email"):
            validate_email("userexample.com")

    def test_invalid_email_empty(self):
        with pytest.raises(ValueError, match="Email is required"):
            validate_email("")

class TestPasswordValidation:
    def test_valid_password(self):
        result = validate_password("SecurePass123!")
        assert result == "SecurePass123!"

    def test_password_too_short(self):
        with pytest.raises(ValueError, match="at least 8 characters"):
            validate_password("Short1!")

    def test_password_no_uppercase(self):
        with pytest.raises(ValueError, match="uppercase"):
            validate_password("lowercase123!")
```

#### API Tests

Test endpoints with HTTP client:

```python
# tests/api/test_projects.py
import pytest
from httpx import AsyncClient

class TestProjects:
    @pytest.mark.asyncio
    async def test_create_project(
        self,
        client: AsyncClient,
        authenticated_user: dict,
    ):
        """Test creating a project."""
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "description": "A test project",
                "preset": "standard",
            },
            headers=authenticated_user,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["status"] == "active"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_project_duplicate_name(
        self,
        client: AsyncClient,
        authenticated_user: dict,
    ):
        """Test creating project with duplicate name fails."""
        # Create first project
        await client.post(
            "/api/v1/projects",
            json={"name": "Duplicate", "preset": "standard"},
            headers=authenticated_user,
        )

        # Try to create second with same name
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Duplicate", "preset": "standard"},
            headers=authenticated_user,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_list_projects_pagination(
        self,
        client: AsyncClient,
        authenticated_user: dict,
    ):
        """Test project list pagination."""
        # Create multiple projects
        for i in range(25):
            await client.post(
                "/api/v1/projects",
                json={"name": f"Project {i}", "preset": "standard"},
                headers=authenticated_user,
            )

        # Get first page
        response = await client.get(
            "/api/v1/projects?page=1&per_page=10",
            headers=authenticated_user,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["pages"] == 3
```

#### Service Tests

Test business logic:

```python
# tests/services/test_project_service.py
import pytest
from app.services.project_service import ProjectService
from app.models.project import ProjectCreate

class TestProjectService:
    @pytest.fixture
    def service(self, mongodb):
        return ProjectService(mongodb)

    @pytest.mark.asyncio
    async def test_create_project(self, service):
        """Test creating a project via service."""
        data = ProjectCreate(
            name="Test Project",
            preset="standard",
        )

        project = await service.create(
            user_id="507f1f77bcf86cd799439011",
            data=data,
        )

        assert project.name == "Test Project"
        assert project.config is not None

    @pytest.mark.asyncio
    async def test_get_project_statistics(self, service, mongodb):
        """Test project statistics calculation."""
        # Insert test data
        await mongodb.results.insert_many([
            {"project_id": "proj1", "sentiment": "positive", "score": 0.8},
            {"project_id": "proj1", "sentiment": "positive", "score": 0.6},
            {"project_id": "proj1", "sentiment": "negative", "score": -0.4},
        ])

        stats = await service.get_statistics("proj1")

        assert stats["total_results"] == 3
        assert stats["positive_count"] == 2
        assert stats["negative_count"] == 1
        assert stats["average_sentiment"] == pytest.approx(0.33, rel=0.1)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific file
pytest tests/api/test_projects.py

# Run specific test
pytest tests/api/test_projects.py::TestProjects::test_create_project

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "slow"

# Run in parallel
pytest -n auto
```

## Frontend Testing

### Setup

Install test dependencies:

```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

Configure Jest in `jest.config.js`:

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/e2e/'],
};
```

### Component Tests

Test React components:

```tsx
// src/components/ui/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByText('Disabled')).toBeDisabled();
  });

  it('shows loading spinner when loading', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
```

### Hook Tests

Test custom hooks:

```tsx
// src/hooks/__tests__/useProjects.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProjects } from '../useProjects';

const wrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useProjects', () => {
  it('fetches projects successfully', async () => {
    const { result } = renderHook(() => useProjects(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
  });
});
```

### API Mocking with MSW

Mock API calls:

```tsx
// src/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/projects', (req, res, ctx) => {
    return res(
      ctx.json({
        items: [
          { id: '1', name: 'Project 1', status: 'active' },
          { id: '2', name: 'Project 2', status: 'active' },
        ],
        total: 2,
      })
    );
  }),

  rest.post('/api/v1/projects', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({
        id: '3',
        ...body,
        status: 'active',
        created_at: new Date().toISOString(),
      })
    );
  }),
];
```

## End-to-End Testing

### Playwright Setup

Configure Playwright in `e2e/playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E Tests

Write end-to-end tests:

```typescript
// e2e/tests/projects.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Projects', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('can create a new project', async ({ page }) => {
    await page.goto('/projects');
    await page.click('text=Create Project');

    // Fill form
    await page.fill('[name="name"]', 'E2E Test Project');
    await page.selectOption('[name="preset"]', 'standard');
    await page.click('text=Create');

    // Verify creation
    await expect(page).toHaveURL(/\/projects\/.+/);
    await expect(page.locator('h1')).toContainText('E2E Test Project');
  });

  test('can add a target to project', async ({ page }) => {
    await page.goto('/projects/test-project-id');
    await page.click('text=Add Target');

    await page.fill('[name="url"]', 'https://amazon.com/dp/B123456');
    await page.click('text=Save');

    await expect(page.locator('.target-list')).toContainText('amazon.com');
  });

  test('can run a scrape job', async ({ page }) => {
    await page.goto('/projects/test-project-id');
    await page.click('text=Run Scrape');

    // Wait for job to start
    await expect(page.locator('.job-status')).toContainText('Running');

    // Wait for completion (with timeout)
    await expect(page.locator('.job-status')).toContainText('Completed', {
      timeout: 60000,
    });
  });
});
```

### Running E2E Tests

```bash
# Run all E2E tests
npx playwright test

# Run with UI mode
npx playwright test --ui

# Run specific file
npx playwright test tests/projects.spec.ts

# Run in headed mode
npx playwright test --headed

# Generate test report
npx playwright show-report
```

## Test Coverage

### Backend Coverage

```bash
# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Frontend Coverage

```bash
# Run with coverage
npm test -- --coverage

# View report
open coverage/lcov-report/index.html
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Best Practices

1. **Test isolation**: Each test should be independent
2. **Descriptive names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests with AAA pattern
4. **Mock external services**: Don't make real API calls in unit tests
5. **Test edge cases**: Include error paths and boundary conditions
6. **Keep tests fast**: Slow tests discourage running them
7. **Maintain coverage**: Aim for 80%+ coverage on critical paths
8. **Review test failures**: Don't ignore flaky tests
