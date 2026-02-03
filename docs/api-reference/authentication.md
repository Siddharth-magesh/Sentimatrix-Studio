# Authentication API

The Authentication API handles user registration, login, and token management.

## Endpoints

### Register User

Create a new user account.

```
POST /api/v1/auth/register
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Min 8 chars, uppercase, lowercase, number |
| `full_name` | string | No | User's full name |

**Response:** `201 Created`

```json
{
  "id": "usr_abc123def456",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `EMAIL_EXISTS` | Email already registered |
| 422 | `VALIDATION_ERROR` | Invalid input data |

---

### Login

Authenticate and receive access tokens.

```
POST /api/v1/auth/login
```

**Request Body:** `application/x-www-form-urlencoded`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | Email address |
| `password` | string | Yes | Password |

**Example:**

```bash
curl -X POST https://api.sentimatrix.io/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!"
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfYWJjMTIz...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfYWJjMTIz...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

| Field | Description |
|-------|-------------|
| `access_token` | JWT for API authentication (30 min expiry) |
| `refresh_token` | Token for refreshing access (7 day expiry) |
| `token_type` | Always "bearer" |
| `expires_in` | Access token lifetime in seconds |

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 401 | `INVALID_CREDENTIALS` | Wrong email or password |
| 403 | `ACCOUNT_DISABLED` | Account has been disabled |
| 429 | `RATE_LIMITED` | Too many login attempts |

---

### Refresh Token

Get a new access token using the refresh token.

```
POST /api/v1/auth/refresh
```

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 401 | `INVALID_TOKEN` | Refresh token is invalid |
| 401 | `TOKEN_EXPIRED` | Refresh token has expired |

---

### Logout

Invalidate the current tokens.

```
POST /api/v1/auth/logout
```

**Headers:**

```
Authorization: Bearer {access_token}
```

**Response:** `204 No Content`

---

### Get Current User

Get the authenticated user's profile.

```
GET /api/v1/auth/me
```

**Headers:**

```
Authorization: Bearer {access_token}
```

**Response:** `200 OK`

```json
{
  "id": "usr_abc123def456",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "settings": {
    "timezone": "UTC",
    "notifications_enabled": true
  }
}
```

---

### Update Profile

Update the current user's profile.

```
PUT /api/v1/auth/me
```

**Headers:**

```
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "full_name": "John Smith",
  "settings": {
    "timezone": "America/New_York",
    "notifications_enabled": false
  }
}
```

**Response:** `200 OK`

Returns the updated user object.

---

### Change Password

Change the current user's password.

```
POST /api/v1/auth/change-password
```

**Headers:**

```
Authorization: Bearer {access_token}
```

**Request Body:**

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Response:** `200 OK`

```json
{
  "message": "Password changed successfully"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `WRONG_PASSWORD` | Current password is incorrect |
| 422 | `WEAK_PASSWORD` | New password doesn't meet requirements |

---

### Request Password Reset

Request a password reset email.

```
POST /api/v1/auth/forgot-password
```

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`

```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

Note: This endpoint always returns success to prevent email enumeration.

---

### Reset Password

Reset password using the token from email.

```
POST /api/v1/auth/reset-password
```

**Request Body:**

```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword789!"
}
```

**Response:** `200 OK`

```json
{
  "message": "Password reset successfully"
}
```

**Errors:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_TOKEN` | Reset token is invalid |
| 400 | `TOKEN_EXPIRED` | Reset token has expired |

---

## Using Authentication

### In API Requests

Include the access token in the Authorization header:

```bash
curl https://api.sentimatrix.io/api/v1/projects \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Refresh Flow

```
1. Make API request with access token
2. If 401 response with "token_expired" code:
   a. Call /auth/refresh with refresh_token
   b. Store new access_token and refresh_token
   c. Retry original request
3. If refresh also fails, redirect to login
```

### JavaScript Example

```javascript
async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${getAccessToken()}`,
    },
  });

  if (response.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      return apiRequest(url, options); // Retry
    }
    // Redirect to login
    window.location.href = '/login';
  }

  return response;
}
```

### Python Example

```python
import requests

class SentimatrixAuth:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None

    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            data={"username": email, "password": password}
        )
        response.raise_for_status()
        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

    def refresh(self):
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        if response.ok:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens["refresh_token"]
            return True
        return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}
```

## Security Best Practices

1. **Store tokens securely**: Use secure storage (httpOnly cookies, secure localStorage)
2. **Use HTTPS**: Never transmit tokens over unencrypted connections
3. **Short token lifetimes**: Access tokens expire in 30 minutes
4. **Refresh token rotation**: Each refresh issues new tokens
5. **Logout everywhere**: Clear all tokens when logging out
