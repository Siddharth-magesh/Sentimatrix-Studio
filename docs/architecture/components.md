# Component Breakdown

## Backend Components

### 1. Authentication Module

**Location:** `backend/app/auth/`

| Component | Description |
|-----------|-------------|
| `router.py` | Authentication endpoints (login, register, refresh, logout) |
| `service.py` | Business logic for authentication |
| `models.py` | Pydantic models for auth requests/responses |
| `jwt.py` | JWT token generation and validation |
| `oauth.py` | OAuth2 provider integrations (Google, GitHub) |
| `dependencies.py` | FastAPI dependencies for auth |

### 2. User Management Module

**Location:** `backend/app/users/`

| Component | Description |
|-----------|-------------|
| `router.py` | User CRUD endpoints |
| `service.py` | User management business logic |
| `models.py` | User Pydantic models |
| `repository.py` | MongoDB operations for users |

### 3. Project Module

**Location:** `backend/app/projects/`

| Component | Description |
|-----------|-------------|
| `router.py` | Project CRUD endpoints |
| `service.py` | Project management logic |
| `models.py` | Project Pydantic models |
| `repository.py` | MongoDB operations for projects |

### 4. Scraper Configuration Module

**Location:** `backend/app/scrapers/`

| Component | Description |
|-----------|-------------|
| `router.py` | Scraper configuration endpoints |
| `service.py` | Scraper orchestration logic |
| `models.py` | Scraper configuration models |
| `executor.py` | Sentimatrix scraper execution |
| `scheduler.py` | Scheduled scraping jobs |

### 5. Analysis Module

**Location:** `backend/app/analysis/`

| Component | Description |
|-----------|-------------|
| `router.py` | Analysis endpoints |
| `service.py` | Analysis pipeline orchestration |
| `models.py` | Analysis configuration models |
| `executor.py` | Sentimatrix analysis execution |

### 6. LLM Configuration Module

**Location:** `backend/app/llm/`

| Component | Description |
|-----------|-------------|
| `router.py` | LLM configuration endpoints |
| `service.py` | LLM provider management |
| `models.py` | LLM configuration models |
| `providers.py` | Provider availability checks |

### 7. Results Module

**Location:** `backend/app/results/`

| Component | Description |
|-----------|-------------|
| `router.py` | Results retrieval endpoints |
| `service.py` | Results aggregation logic |
| `models.py` | Results data models |
| `export.py` | Export to CSV, JSON, Excel |

### 8. Webhooks Module

**Location:** `backend/app/webhooks/`

| Component | Description |
|-----------|-------------|
| `router.py` | Webhook management endpoints |
| `service.py` | Webhook delivery logic |
| `models.py` | Webhook configuration models |

### 9. Core Module

**Location:** `backend/app/core/`

| Component | Description |
|-----------|-------------|
| `config.py` | Application configuration |
| `database.py` | MongoDB connection management |
| `exceptions.py` | Custom exception classes |
| `middleware.py` | Request/response middleware |
| `security.py` | Security utilities |
| `logging.py` | Structured logging setup |

---

## Frontend Components

### 1. Layout Components

**Location:** `frontend/src/components/layout/`

| Component | Description |
|-----------|-------------|
| `Header.tsx` | Navigation header with user menu |
| `Sidebar.tsx` | Main navigation sidebar |
| `Footer.tsx` | Application footer |
| `MainLayout.tsx` | Primary layout wrapper |
| `AuthLayout.tsx` | Layout for auth pages |

### 2. Authentication Components

**Location:** `frontend/src/components/auth/`

| Component | Description |
|-----------|-------------|
| `LoginForm.tsx` | Login form with validation |
| `RegisterForm.tsx` | Multi-step registration form |
| `ForgotPasswordForm.tsx` | Password reset request |
| `ResetPasswordForm.tsx` | Password reset form |
| `OAuthButtons.tsx` | Social login buttons |

### 3. Dashboard Components

**Location:** `frontend/src/components/dashboard/`

| Component | Description |
|-----------|-------------|
| `StatsCards.tsx` | Overview statistics cards |
| `SentimentChart.tsx` | Sentiment distribution chart |
| `TrendChart.tsx` | Sentiment over time chart |
| `RecentActivity.tsx` | Recent scraping activity |
| `QuickActions.tsx` | Quick action buttons |

### 4. Project Components

**Location:** `frontend/src/components/projects/`

| Component | Description |
|-----------|-------------|
| `ProjectList.tsx` | Project listing with filters |
| `ProjectCard.tsx` | Individual project card |
| `ProjectForm.tsx` | Create/edit project form |
| `ProjectDetails.tsx` | Project detail view |

### 5. Configuration Components

**Location:** `frontend/src/components/config/`

| Component | Description |
|-----------|-------------|
| `PresetSelector.tsx` | Configuration preset selection |
| `ScraperConfig.tsx` | Scraper configuration form |
| `LLMConfig.tsx` | LLM provider configuration |
| `ScheduleConfig.tsx` | Scraping schedule setup |
| `TargetConfig.tsx` | Target URL configuration |
| `LimitConfig.tsx` | Rate limiting configuration |

### 6. Results Components

**Location:** `frontend/src/components/results/`

| Component | Description |
|-----------|-------------|
| `ResultsTable.tsx` | Tabular results view |
| `ResultsChart.tsx` | Visual results charts |
| `SentimentBreakdown.tsx` | Detailed sentiment analysis |
| `EmotionBreakdown.tsx` | Emotion analysis view |
| `ExportDialog.tsx` | Export options dialog |

### 7. Common Components

**Location:** `frontend/src/components/common/`

| Component | Description |
|-----------|-------------|
| `Button.tsx` | Styled button component |
| `Input.tsx` | Form input component |
| `Select.tsx` | Dropdown select component |
| `Modal.tsx` | Modal dialog component |
| `Card.tsx` | Card container component |
| `Table.tsx` | Data table component |
| `Loading.tsx` | Loading indicators |
| `ErrorBoundary.tsx` | Error boundary wrapper |

### 8. Form Components

**Location:** `frontend/src/components/forms/`

| Component | Description |
|-----------|-------------|
| `FormField.tsx` | Form field wrapper with label |
| `FormError.tsx` | Form error display |
| `FormSection.tsx` | Form section grouping |
| `Stepper.tsx` | Multi-step form stepper |

---

## Page Structure

### Authentication Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | `LoginPage.tsx` | User login |
| `/register` | `RegisterPage.tsx` | User registration |
| `/forgot-password` | `ForgotPasswordPage.tsx` | Password reset request |
| `/reset-password` | `ResetPasswordPage.tsx` | Password reset |

### Dashboard Pages

| Route | Page | Description |
|-------|------|-------------|
| `/dashboard` | `DashboardPage.tsx` | Main dashboard |
| `/dashboard/analytics` | `AnalyticsPage.tsx` | Detailed analytics |

### Project Pages

| Route | Page | Description |
|-------|------|-------------|
| `/projects` | `ProjectsPage.tsx` | Project listing |
| `/projects/new` | `NewProjectPage.tsx` | Create project |
| `/projects/[id]` | `ProjectDetailPage.tsx` | Project details |
| `/projects/[id]/edit` | `EditProjectPage.tsx` | Edit project |
| `/projects/[id]/results` | `ProjectResultsPage.tsx` | Project results |

### Configuration Pages

| Route | Page | Description |
|-------|------|-------------|
| `/config/scrapers` | `ScrapersPage.tsx` | Scraper management |
| `/config/llm` | `LLMPage.tsx` | LLM configuration |
| `/config/presets` | `PresetsPage.tsx` | Preset management |

### Settings Pages

| Route | Page | Description |
|-------|------|-------------|
| `/settings` | `SettingsPage.tsx` | User settings |
| `/settings/api-keys` | `APIKeysPage.tsx` | API key management |
| `/settings/webhooks` | `WebhooksPage.tsx` | Webhook configuration |
| `/settings/billing` | `BillingPage.tsx` | Usage and billing |
