# Security Architecture

## Overview

Sentimatrix Studio implements defense-in-depth security measures to protect user data, API credentials, and system integrity.

## Authentication

### JWT Token Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Token Architecture                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Access Token                    Refresh Token               │
│  ┌────────────────────┐         ┌────────────────────┐      │
│  │ Lifetime: 15 min   │         │ Lifetime: 7 days   │      │
│  │ Storage: Memory    │         │ Storage: HTTP-only │      │
│  │ Contains: user_id, │         │          cookie    │      │
│  │   email, roles     │         │ Contains: token_id │      │
│  └────────────────────┘         └────────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Token Claims

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "roles": ["user"],
  "iat": 1234567890,
  "exp": 1234568790,
  "jti": "unique_token_id"
}
```

### Password Security

| Aspect | Implementation |
|--------|----------------|
| Hashing | bcrypt with cost factor 12 |
| Minimum Length | 8 characters |
| Requirements | Uppercase, lowercase, number |
| Breach Check | HaveIBeenPwned API (optional) |

### OAuth2 Integration

Supported providers:
- Google
- GitHub

OAuth flow:
1. User clicks OAuth provider button
2. Redirect to provider authorization page
3. Provider redirects back with authorization code
4. Backend exchanges code for tokens
5. Fetch user profile from provider
6. Create or link user account
7. Issue JWT tokens

## Authorization

### Role-Based Access Control (RBAC)

| Role | Description | Permissions |
|------|-------------|-------------|
| `user` | Standard user | Own projects, own results |
| `admin` | Administrator | All projects, user management |
| `readonly` | Read-only access | View only, no modifications |

### Resource-Level Permissions

```python
# Permission check example
async def check_project_access(user_id: str, project_id: str) -> bool:
    project = await get_project(project_id)
    return (
        project.owner_id == user_id or
        user_id in project.collaborators or
        user.role == "admin"
    )
```

## API Security

### Rate Limiting

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 5 requests | 1 minute |
| API (authenticated) | 100 requests | 1 minute |
| Scraping | 10 requests | 1 minute |
| Export | 5 requests | 1 minute |

### Input Validation

All inputs are validated using Pydantic models:

```python
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    targets: List[HttpUrl] = Field(..., max_items=50)

    @validator("name")
    def sanitize_name(cls, v):
        return bleach.clean(v)
```

### CORS Configuration

```python
CORS_CONFIG = {
    "allow_origins": [
        "https://studio.sentimatrix.dev",
        "http://localhost:3000",  # Development only
    ],
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Authorization", "Content-Type"],
    "allow_credentials": True,
    "max_age": 600,
}
```

## Data Protection

### API Key Encryption

User-provided API keys (OpenAI, Groq, etc.) are encrypted at rest:

```
┌─────────────────────────────────────────────────────────────┐
│                  API Key Storage                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Input          Encryption           MongoDB            │
│  ┌──────────┐       ┌──────────┐        ┌──────────────┐    │
│  │ sk-abc123│ ────> │ AES-256  │ ────>  │ encrypted:   │    │
│  │          │       │ GCM      │        │ 0x7f3a...    │    │
│  └──────────┘       └──────────┘        │ nonce: ...   │    │
│                                          │ tag: ...     │    │
│                                          └──────────────┘    │
│                                                              │
│  Key derivation: PBKDF2 from master secret                  │
│  Master secret: Environment variable (never in code)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Sensitive Data Handling

| Data Type | Storage | Encryption | Logging |
|-----------|---------|------------|---------|
| Passwords | Hashed | bcrypt | Never logged |
| API Keys | Encrypted | AES-256-GCM | Never logged |
| JWT Tokens | Memory/Cookie | Signed | Token ID only |
| User PII | MongoDB | At rest (Atlas) | Masked |

### Data Retention

| Data Type | Retention | Deletion |
|-----------|-----------|----------|
| Scraping Results | 90 days default | On request |
| Analysis Data | 90 days default | On request |
| Audit Logs | 1 year | Automatic |
| Deleted Accounts | 30 days grace | Permanent |

## Security Headers

```python
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; ...",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
```

## Audit Logging

### Logged Events

| Event Category | Events |
|----------------|--------|
| Authentication | Login, logout, failed login, password change |
| Authorization | Permission denied, role change |
| Data Access | Export, bulk download |
| Configuration | API key change, project settings change |
| Admin Actions | User management, system configuration |

### Log Format

```json
{
  "timestamp": "2026-02-02T12:00:00Z",
  "event_type": "auth.login",
  "user_id": "user_123",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "metadata": {
    "method": "password"
  }
}
```

## Vulnerability Prevention

### OWASP Top 10 Mitigations

| Vulnerability | Mitigation |
|---------------|------------|
| Injection | Parameterized queries, Pydantic validation |
| Broken Auth | JWT with refresh, rate limiting |
| Sensitive Data | Encryption at rest, HTTPS only |
| XXE | JSON-only APIs, no XML parsing |
| Broken Access Control | RBAC, resource-level checks |
| Security Misconfiguration | Hardened defaults, security headers |
| XSS | React auto-escaping, CSP |
| Insecure Deserialization | Pydantic validation, no pickle |
| Known Vulnerabilities | Dependency scanning, updates |
| Insufficient Logging | Comprehensive audit logging |

### Dependency Security

```bash
# Regular security scans
pip-audit
safety check
npm audit

# CI/CD integration
- Run on every PR
- Block merge on critical vulnerabilities
```

## Incident Response

### Security Contact

Report security vulnerabilities to: security@sentimatrix.dev

### Response Timeline

| Severity | Response Time | Resolution Target |
|----------|---------------|-------------------|
| Critical | 4 hours | 24 hours |
| High | 24 hours | 7 days |
| Medium | 72 hours | 30 days |
| Low | 1 week | 90 days |

## Compliance Considerations

### GDPR

- User data export endpoint
- Account deletion endpoint
- Consent management
- Data processing records

### SOC 2 (Future)

- Access controls documented
- Encryption standards
- Audit logging
- Incident response procedures
