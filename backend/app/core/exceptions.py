"""Custom exception hierarchy for the application."""

from typing import Any


class StudioException(Exception):
    """Base exception for all application exceptions."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


# Authentication Exceptions
class AuthenticationError(StudioException):
    """Base authentication error."""

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    message = "Authentication failed"


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password."""

    error_code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class TokenExpiredError(AuthenticationError):
    """Token has expired."""

    error_code = "TOKEN_EXPIRED"
    message = "Token has expired"


class InvalidTokenError(AuthenticationError):
    """Token is invalid."""

    error_code = "INVALID_TOKEN"
    message = "Invalid token"


class TokenBlacklistedError(AuthenticationError):
    """Token has been blacklisted."""

    error_code = "TOKEN_BLACKLISTED"
    message = "Token has been revoked"


# Authorization Exceptions
class AuthorizationError(StudioException):
    """Base authorization error."""

    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    message = "You do not have permission to perform this action"


class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions."""

    error_code = "INSUFFICIENT_PERMISSIONS"
    message = "Insufficient permissions"


# Resource Exceptions
class NotFoundError(StudioException):
    """Resource not found."""

    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class UserNotFoundError(NotFoundError):
    """User not found."""

    error_code = "USER_NOT_FOUND"
    message = "User not found"


class ProjectNotFoundError(NotFoundError):
    """Project not found."""

    error_code = "PROJECT_NOT_FOUND"
    message = "Project not found"


class TargetNotFoundError(NotFoundError):
    """Target not found."""

    error_code = "TARGET_NOT_FOUND"
    message = "Target not found"


# Validation Exceptions
class ValidationError(StudioException):
    """Validation error."""

    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class DuplicateError(StudioException):
    """Resource already exists."""

    status_code = 409
    error_code = "DUPLICATE_ERROR"
    message = "Resource already exists"


class ConflictError(StudioException):
    """Conflict with current state."""

    status_code = 409
    error_code = "CONFLICT_ERROR"
    message = "Operation conflicts with current state"


class EmailAlreadyExistsError(DuplicateError):
    """Email already registered."""

    error_code = "EMAIL_EXISTS"
    message = "A user with this email already exists"


# Rate Limiting Exceptions
class RateLimitError(StudioException):
    """Rate limit exceeded."""

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please try again later"


# External Service Exceptions
class ExternalServiceError(StudioException):
    """Error communicating with external service."""

    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"
    message = "Error communicating with external service"


class ScraperError(ExternalServiceError):
    """Error during scraping operation."""

    error_code = "SCRAPER_ERROR"
    message = "Scraping operation failed"


class LLMError(ExternalServiceError):
    """Error communicating with LLM provider."""

    error_code = "LLM_ERROR"
    message = "LLM service error"


# Database Exceptions
class DatabaseError(StudioException):
    """Database operation error."""

    status_code = 500
    error_code = "DATABASE_ERROR"
    message = "Database operation failed"
