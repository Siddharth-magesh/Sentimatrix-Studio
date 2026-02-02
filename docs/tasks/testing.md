# Testing Tasks

## Overview

Testing strategy and tasks for Sentimatrix Studio.

---

## Testing Strategy

| Type | Coverage Target | Tools |
|------|-----------------|-------|
| Unit Tests | 80% | pytest, Jest |
| Integration Tests | Key flows | pytest, Playwright |
| E2E Tests | Critical paths | Playwright |
| Performance Tests | API endpoints | Locust |

---

## Backend Testing

### Unit Tests [P0]

#### Auth Module
- [ ] Test password hashing
- [ ] Test JWT token generation
- [ ] Test JWT token validation
- [ ] Test token refresh logic
- [ ] Test auth dependencies

#### User Module
- [ ] Test user creation
- [ ] Test user validation
- [ ] Test user update
- [ ] Test password change

#### Project Module
- [ ] Test project creation
- [ ] Test project validation
- [ ] Test configuration validation
- [ ] Test project queries

#### Scraper Module
- [ ] Test scraper configuration validation
- [ ] Test platform detection
- [ ] Test URL parsing

#### Analysis Module
- [ ] Test analysis configuration
- [ ] Test result transformation

#### Utility Functions
- [ ] Test encryption utilities
- [ ] Test date utilities
- [ ] Test pagination helpers

### Integration Tests [P1]

#### Auth Flow
- [ ] Test complete registration flow
- [ ] Test complete login flow
- [ ] Test token refresh flow
- [ ] Test logout flow
- [ ] Test password reset flow

#### Project Lifecycle
- [ ] Test project creation with targets
- [ ] Test project update
- [ ] Test project deletion
- [ ] Test cascading deletes

#### Scraping Pipeline
- [ ] Test scrape job creation
- [ ] Test scrape execution (mocked scrapers)
- [ ] Test result storage
- [ ] Test job status updates

#### Analysis Pipeline
- [ ] Test analysis job creation
- [ ] Test analysis execution (mocked LLM)
- [ ] Test result updates

### API Tests [P0]

#### Auth Endpoints
- [ ] POST /auth/register - success
- [ ] POST /auth/register - validation errors
- [ ] POST /auth/register - duplicate email
- [ ] POST /auth/login - success
- [ ] POST /auth/login - invalid credentials
- [ ] POST /auth/refresh - success
- [ ] POST /auth/refresh - expired token

#### User Endpoints
- [ ] GET /users/me - authenticated
- [ ] GET /users/me - unauthenticated
- [ ] PUT /users/me - success
- [ ] PUT /users/me - validation errors

#### Project Endpoints
- [ ] GET /projects - empty list
- [ ] GET /projects - with data
- [ ] GET /projects - pagination
- [ ] POST /projects - success
- [ ] POST /projects - validation errors
- [ ] GET /projects/{id} - found
- [ ] GET /projects/{id} - not found
- [ ] GET /projects/{id} - forbidden
- [ ] PUT /projects/{id} - success
- [ ] DELETE /projects/{id} - success

#### Scraper Endpoints
- [ ] GET /scrapers/platforms
- [ ] GET /scrapers/commercial
- [ ] POST /scrapers/validate - valid
- [ ] POST /scrapers/validate - invalid
- [ ] POST /scrape/run - success
- [ ] POST /scrape/run - rate limited
- [ ] GET /scrape/jobs/{id}

#### Results Endpoints
- [ ] GET /results - pagination
- [ ] GET /results - filters
- [ ] GET /results - search
- [ ] POST /results/export

---

## Frontend Testing

### Component Tests [P0]

#### Common Components
- [ ] Button - all variants
- [ ] Input - states and validation
- [ ] Select - selection behavior
- [ ] Modal - open/close
- [ ] Table - sorting and pagination
- [ ] Loading - all variants

#### Form Components
- [ ] FormField - error display
- [ ] PresetSelector - selection
- [ ] PlatformSelector - multi-select
- [ ] TargetInput - add/remove

#### Chart Components
- [ ] SentimentChart - data rendering
- [ ] EmotionChart - data rendering

### Hook Tests [P1]

- [ ] useAuth - login/logout
- [ ] useProjects - CRUD operations
- [ ] useResults - pagination
- [ ] useWebSocket - connection

### Page Tests [P1]

#### Auth Pages
- [ ] Login - form submission
- [ ] Login - validation errors
- [ ] Register - multi-step flow
- [ ] Register - form validation

#### Dashboard
- [ ] Dashboard - data loading
- [ ] Dashboard - empty state

#### Projects
- [ ] Projects list - display
- [ ] Projects list - filtering
- [ ] Project detail - display
- [ ] Project wizard - flow

---

## E2E Tests [P1]

### Critical Paths

#### Authentication
- [ ] User can register
- [ ] User can login
- [ ] User can logout
- [ ] User can reset password

#### Project Management
- [ ] User can create project
- [ ] User can view project list
- [ ] User can view project details
- [ ] User can edit project
- [ ] User can delete project

#### Scraping
- [ ] User can add target
- [ ] User can trigger scrape
- [ ] User can view scrape progress
- [ ] User can view results

#### Analysis
- [ ] User can run analysis
- [ ] User can view analysis results

#### Export
- [ ] User can export to CSV
- [ ] User can export to JSON

---

## Performance Tests [P2]

### API Performance

- [ ] Auth endpoints < 200ms
- [ ] List endpoints < 500ms
- [ ] Create endpoints < 300ms
- [ ] Aggregate endpoints < 1000ms

### Load Testing

- [ ] 100 concurrent users
- [ ] 1000 requests/minute
- [ ] Sustained load (15 minutes)

---

## Test Configuration

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
```

### jest.config.js

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/.next/'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};
```

### playwright.config.ts

```typescript
export default {
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
};
```

---

## CI Integration

### Test Workflow

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    # Backend tests
    - name: Backend tests
      run: |
        cd backend
        pip install -e ".[dev]"
        pytest --cov=app --cov-report=xml

    # Frontend tests
    - name: Frontend tests
      run: |
        cd frontend
        npm ci
        npm test -- --coverage

    # E2E tests
    - name: E2E tests
      run: |
        docker-compose up -d
        npx playwright test
```

---

## Coverage Requirements

| Module | Target |
|--------|--------|
| Backend Core | 90% |
| Backend API | 85% |
| Frontend Components | 80% |
| Frontend Pages | 70% |
| E2E Flows | 100% critical paths |
