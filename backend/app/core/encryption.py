"""Encryption utilities for sensitive data like API keys."""

import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import get_settings


def _derive_key(secret: str, salt: bytes) -> bytes:
    """Derive a Fernet key from the secret and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    return key


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key using Fernet symmetric encryption.

    Returns a string in format: salt:encrypted_data (both base64 encoded)
    """
    settings = get_settings()

    # Generate a random salt
    salt = secrets.token_bytes(16)

    # Derive key from secret
    key = _derive_key(settings.secret_key, salt)
    fernet = Fernet(key)

    # Encrypt the API key
    encrypted_data = fernet.encrypt(api_key.encode())

    # Combine salt and encrypted data
    combined = base64.urlsafe_b64encode(salt).decode() + ":" + encrypted_data.decode()
    return combined


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_key: String in format salt:encrypted_data

    Returns:
        The decrypted API key
    """
    settings = get_settings()

    # Split salt and encrypted data
    parts = encrypted_key.split(":")
    if len(parts) != 2:
        raise ValueError("Invalid encrypted key format")

    salt = base64.urlsafe_b64decode(parts[0])
    encrypted_data = parts[1].encode()

    # Derive key from secret
    key = _derive_key(settings.secret_key, salt)
    fernet = Fernet(key)

    # Decrypt
    decrypted = fernet.decrypt(encrypted_data)
    return decrypted.decode()


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display, showing only first and last few characters.

    Args:
        api_key: The full API key
        visible_chars: Number of characters to show at start and end

    Returns:
        Masked key like "sk-ab...xy"
    """
    if len(api_key) <= visible_chars * 2:
        return "*" * len(api_key)

    prefix = api_key[:visible_chars]
    suffix = api_key[-visible_chars:]
    return f"{prefix}...{suffix}"


def hash_api_key(api_key: str) -> str:
    """
    Create a hash of an API key for comparison/lookup.

    This allows checking if a key already exists without storing
    or comparing the full encrypted key.
    """
    settings = get_settings()

    # Use HMAC with the secret key
    combined = f"{settings.secret_key}:{api_key}".encode()
    return hashlib.sha256(combined).hexdigest()
