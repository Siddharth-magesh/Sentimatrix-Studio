"""Custom validators and validation utilities."""

import re
from typing import Any
from urllib.parse import urlparse

from pydantic import field_validator, model_validator
from pydantic_core import PydanticCustomError


def validate_url(url: str, allowed_schemes: list[str] | None = None) -> str:
    """
    Validate URL format and scheme.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (default: http, https)

    Returns:
        Validated URL

    Raises:
        ValueError if invalid
    """
    if not url:
        raise ValueError("URL is required")

    allowed_schemes = allowed_schemes or ["http", "https"]

    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            raise ValueError("URL must include a scheme (http:// or https://)")

        if parsed.scheme.lower() not in allowed_schemes:
            raise ValueError(f"URL scheme must be one of: {', '.join(allowed_schemes)}")

        if not parsed.netloc:
            raise ValueError("URL must include a domain")

        # Reconstruct to normalize
        return url

    except Exception as e:
        if "URL" in str(e):
            raise
        raise ValueError(f"Invalid URL format: {e}")


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email to validate

    Returns:
        Validated and normalized email

    Raises:
        ValueError if invalid
    """
    if not email:
        raise ValueError("Email is required")

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise ValueError("Invalid email format")

    # Normalize
    return email.lower().strip()


def validate_password(password: str, min_length: int = 8) -> str:
    """
    Validate password strength.

    Requirements:
    - Minimum length
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Args:
        password: Password to validate
        min_length: Minimum password length

    Returns:
        Validated password

    Raises:
        ValueError if invalid
    """
    if not password:
        raise ValueError("Password is required")

    if len(password) < min_length:
        raise ValueError(f"Password must be at least {min_length} characters")

    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")

    return password


def validate_mongodb_object_id(value: str) -> str:
    """
    Validate MongoDB ObjectId format.

    Args:
        value: Value to validate

    Returns:
        Validated value

    Raises:
        ValueError if invalid
    """
    if not value:
        raise ValueError("ID is required")

    if not re.match(r'^[a-fA-F0-9]{24}$', value):
        raise ValueError("Invalid ID format")

    return value


def validate_cron_expression(expr: str) -> str:
    """
    Validate cron expression format (basic validation).

    Args:
        expr: Cron expression to validate

    Returns:
        Validated expression

    Raises:
        ValueError if invalid
    """
    if not expr:
        raise ValueError("Cron expression is required")

    parts = expr.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have 5 parts (minute hour day month weekday)")

    return expr


def validate_timezone(tz: str) -> str:
    """
    Validate timezone string.

    Args:
        tz: Timezone to validate

    Returns:
        Validated timezone

    Raises:
        ValueError if invalid
    """
    try:
        import pytz
        pytz.timezone(tz)
        return tz
    except Exception:
        raise ValueError(f"Invalid timezone: {tz}")


def validate_hex_color(color: str) -> str:
    """
    Validate hex color format.

    Args:
        color: Color to validate

    Returns:
        Validated color

    Raises:
        ValueError if invalid
    """
    if not color:
        raise ValueError("Color is required")

    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
        raise ValueError("Invalid hex color format (expected #RGB or #RRGGBB)")

    return color.upper()


def validate_slug(slug: str) -> str:
    """
    Validate URL-safe slug.

    Args:
        slug: Slug to validate

    Returns:
        Validated slug

    Raises:
        ValueError if invalid
    """
    if not slug:
        raise ValueError("Slug is required")

    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")

    if len(slug) > 100:
        raise ValueError("Slug must be 100 characters or less")

    return slug


def sanitize_html(html: str, allowed_tags: list[str] | None = None) -> str:
    """
    Sanitize HTML content by removing dangerous tags.

    Args:
        html: HTML to sanitize
        allowed_tags: List of allowed HTML tags

    Returns:
        Sanitized HTML
    """
    import html as html_module

    if not html:
        return ""

    # Escape HTML entities
    sanitized = html_module.escape(html)

    return sanitized


def validate_json_field(value: Any, max_depth: int = 5) -> Any:
    """
    Validate JSON field to prevent deeply nested objects.

    Args:
        value: Value to validate
        max_depth: Maximum nesting depth

    Returns:
        Validated value

    Raises:
        ValueError if too deeply nested
    """
    def check_depth(obj: Any, current_depth: int = 0) -> None:
        if current_depth > max_depth:
            raise ValueError(f"JSON nesting exceeds maximum depth of {max_depth}")

        if isinstance(obj, dict):
            for v in obj.values():
                check_depth(v, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, current_depth + 1)

    check_depth(value)
    return value


# Pydantic field validators for common use cases
def url_validator(allowed_schemes: list[str] | None = None):
    """Create a Pydantic field validator for URLs."""
    def validator(cls, v):
        return validate_url(v, allowed_schemes)
    return field_validator("url", mode="after")(validator)


def email_validator():
    """Create a Pydantic field validator for emails."""
    def validator(cls, v):
        return validate_email(v)
    return field_validator("email", mode="after")(validator)


def password_validator(min_length: int = 8):
    """Create a Pydantic field validator for passwords."""
    def validator(cls, v):
        return validate_password(v, min_length)
    return field_validator("password", mode="after")(validator)


def object_id_validator(*fields: str):
    """Create a Pydantic field validator for MongoDB ObjectIds."""
    def validator(cls, v):
        return validate_mongodb_object_id(v)
    return field_validator(*fields, mode="after")(validator)
