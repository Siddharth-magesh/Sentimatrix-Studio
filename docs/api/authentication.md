# Authentication API

## Overview

Sentimatrix Studio uses JWT-based authentication with access and refresh tokens.

## Endpoints

### Register

Create a new user account.

```http
POST /v1/auth/register
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe",
  "company": "Acme Inc"
}
```

**Validation Rules:**

| Field | Rules |
|-------|-------|
| email | Valid email format, unique |
| password | Min 8 chars, uppercase, lowercase, number |
| name | 1-100 characters |
| company | Optional, max 100 characters |

**Response (201):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_abc123",
      "email": "user@example.com",
      "name": "John Doe",
      "company": "Acme Inc",
      "created_at": "2026-02-02T12:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Cookies Set:**

```
Set-Cookie: refresh_token=<token>; HttpOnly; Secure; SameSite=Strict; Path=/v1/auth; Max-Age=604800
```

**Errors:**

| Code | Description |
|------|-------------|
| 400 | Validation error |
| 409 | Email already exists |

---

### Login

Authenticate with email and password.

```http
POST /v1/auth/login
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_abc123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 401 | Invalid credentials |
| 429 | Too many attempts |

---

### Logout

Invalidate current session.

```http
POST /v1/auth/logout
Authorization: Bearer <access_token>
```

**Response (204):**

No content. Refresh token cookie is cleared.

---

### Refresh Token

Get new access token using refresh token.

```http
POST /v1/auth/refresh
Cookie: refresh_token=<token>
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 401 | Invalid or expired refresh token |

---

### Forgot Password

Request password reset email.

```http
POST /v1/auth/forgot-password
```

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "message": "If the email exists, a reset link has been sent"
  }
}
```

Note: Always returns success to prevent email enumeration.

---

### Reset Password

Reset password using token from email.

```http
POST /v1/auth/reset-password
```

**Request Body:**

```json
{
  "token": "reset_token_from_email",
  "password": "NewSecurePass123"
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "message": "Password reset successful"
  }
}
```

**Errors:**

| Code | Description |
|------|-------------|
| 400 | Invalid or expired token |

---

### OAuth Login

Initiate OAuth flow.

```http
GET /v1/auth/oauth/{provider}
```

**Supported Providers:**

- `google`
- `github`

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| redirect_uri | Optional custom redirect URI |

**Response (302):**

Redirects to OAuth provider authorization page.

---

### OAuth Callback

Handle OAuth provider callback.

```http
GET /v1/auth/oauth/{provider}/callback
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| code | Authorization code from provider |
| state | State parameter for CSRF protection |

**Response (302):**

Redirects to frontend with tokens in URL fragment:

```
https://studio.sentimatrix.dev/auth/callback#access_token=...&token_type=bearer
```

**Errors:**

| Code | Description |
|------|-------------|
| 400 | Invalid state or code |
| 401 | OAuth authentication failed |

---

## Token Structure

### Access Token Claims

```json
{
  "sub": "usr_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "roles": ["user"],
  "iat": 1706875200,
  "exp": 1706876100,
  "jti": "tok_xyz789"
}
```

### Refresh Token Claims

```json
{
  "sub": "usr_abc123",
  "type": "refresh",
  "iat": 1706875200,
  "exp": 1707480000,
  "jti": "ref_xyz789"
}
```

## Security Considerations

### Rate Limiting

Authentication endpoints have strict rate limits:

| Endpoint | Limit | Window | Lockout |
|----------|-------|--------|---------|
| `/login` | 5 | 1 minute | 15 minutes |
| `/register` | 3 | 1 minute | 30 minutes |
| `/forgot-password` | 3 | 1 hour | - |

### Token Storage

| Token Type | Storage | Lifetime |
|------------|---------|----------|
| Access Token | Memory only | 15 minutes |
| Refresh Token | HTTP-only cookie | 7 days |

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Maximum 128 characters

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_INVALID_CREDENTIALS | Email or password incorrect |
| AUTH_USER_EXISTS | Email already registered |
| AUTH_TOKEN_EXPIRED | Token has expired |
| AUTH_TOKEN_INVALID | Token is malformed or invalid |
| AUTH_RATE_LIMITED | Too many authentication attempts |
| AUTH_ACCOUNT_LOCKED | Account temporarily locked |
| AUTH_PASSWORD_WEAK | Password does not meet requirements |
