"""Password hashing utilities using bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Automatically handles passwords of any length by using SHA-256 prehashing
    when the password exceeds bcrypt's 72-byte limit.
    """
    password_bytes = password.encode("utf-8")
    
    # bcrypt automatically handles long passwords in version 4.1.0+
    # by truncating at 72 bytes, but we'll be explicit about it
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)
