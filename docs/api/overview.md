# API Overview

## Introduction

Sentimatrix Studio exposes a RESTful API built with FastAPI. All endpoints follow REST conventions and return JSON responses.

## Base URL

```
Production: https://api.studio.sentimatrix.dev/v1
Development: http://localhost:8000/v1
```

## Authentication

All API endpoints (except auth) require a valid JWT token.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Refresh

Access tokens expire after 15 minutes. Use the refresh endpoint to obtain new tokens:

```http
POST /v1/auth/refresh
Cookie: refresh_token=<token>
```

## API Conventions

### Request Format

```http
POST /v1/projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description"
}
```

### Response Format

**Success Response:**

```json
{
  "success": true,
  "data": {
    "id": "proj_123",
    "name": "My Project"
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

**Error Response:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "name",
        "message": "Name is required"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (delete) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Pagination

List endpoints support pagination:

```http
GET /v1/projects?page=1&limit=20
```

Response includes pagination metadata:

```json
{
  "success": true,
  "data": [...],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Filtering

List endpoints support filtering:

```http
GET /v1/results?project_id=proj_123&sentiment=positive&date_from=2026-01-01
```

### Sorting

List endpoints support sorting:

```http
GET /v1/projects?sort=-created_at,name
```

- Prefix with `-` for descending order
- Multiple fields separated by commas

## API Endpoints Summary

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout |
| POST | `/auth/refresh` | Refresh tokens |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password |
| GET | `/auth/oauth/{provider}` | OAuth login |
| GET | `/auth/oauth/{provider}/callback` | OAuth callback |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user |
| PUT | `/users/me` | Update current user |
| DELETE | `/users/me` | Delete account |
| PUT | `/users/me/password` | Change password |
| GET | `/users/me/api-keys` | List API keys |
| POST | `/users/me/api-keys` | Create API key |
| DELETE | `/users/me/api-keys/{id}` | Delete API key |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List projects |
| POST | `/projects` | Create project |
| GET | `/projects/{id}` | Get project |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |
| GET | `/projects/{id}/stats` | Get project statistics |

### Scrapers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/scrapers/platforms` | List available platforms |
| GET | `/scrapers/commercial` | List commercial providers |
| POST | `/scrapers/validate` | Validate scraper config |
| POST | `/scrape/run` | Execute scrape job |
| GET | `/scrape/jobs` | List scrape jobs |
| GET | `/scrape/jobs/{id}` | Get job status |
| POST | `/scrape/jobs/{id}/cancel` | Cancel job |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analysis/run` | Run analysis |
| GET | `/analysis/jobs` | List analysis jobs |
| GET | `/analysis/jobs/{id}` | Get job status |

### Results

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/results` | List results |
| GET | `/results/{id}` | Get result detail |
| GET | `/results/aggregate` | Get aggregated stats |
| POST | `/results/export` | Export results |

### LLM Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/llm/providers` | List LLM providers |
| POST | `/llm/validate` | Validate LLM config |
| POST | `/llm/test` | Test LLM connection |

### Presets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/presets` | List presets |
| GET | `/presets/{id}` | Get preset |
| POST | `/presets` | Create custom preset |
| DELETE | `/presets/{id}` | Delete custom preset |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhooks` | List webhooks |
| POST | `/webhooks` | Create webhook |
| PUT | `/webhooks/{id}` | Update webhook |
| DELETE | `/webhooks/{id}` | Delete webhook |
| POST | `/webhooks/{id}/test` | Test webhook |

## Rate Limits

| Endpoint Type | Requests | Window |
|---------------|----------|--------|
| Authentication | 5 | 1 minute |
| General API | 100 | 1 minute |
| Scraping | 10 | 1 minute |
| Export | 5 | 1 minute |

Rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

## WebSocket API

### Connection

```
wss://api.studio.sentimatrix.dev/v1/ws?token=<access_token>
```

### Events

See [webhooks.md](webhooks.md) for WebSocket event documentation.

## OpenAPI Documentation

Interactive API documentation available at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
