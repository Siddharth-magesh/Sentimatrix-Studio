"""Tests for encryption utilities."""

import pytest

from app.core.encryption import (
    encrypt_api_key,
    decrypt_api_key,
    mask_api_key,
    hash_api_key,
)


class TestEncryption:
    """Test encryption utilities."""

    def test_encrypt_decrypt_api_key(self):
        """Test encrypting and decrypting an API key."""
        original_key = "sk-test-api-key-12345"

        encrypted = encrypt_api_key(original_key)
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == original_key
        assert encrypted != original_key
        assert ":" in encrypted  # Should have salt:data format

    def test_encrypt_produces_different_ciphertext(self):
        """Test that encrypting same key twice produces different ciphertext."""
        api_key = "sk-test-key"

        encrypted1 = encrypt_api_key(api_key)
        encrypted2 = encrypt_api_key(api_key)

        # Different salts should produce different ciphertext
        assert encrypted1 != encrypted2

        # But both should decrypt to same value
        assert decrypt_api_key(encrypted1) == api_key
        assert decrypt_api_key(encrypted2) == api_key

    def test_mask_api_key_default(self):
        """Test masking API key with default parameters."""
        api_key = "sk-1234567890abcdef"

        masked = mask_api_key(api_key)

        assert masked == "sk-1...cdef"
        assert "1234567890" not in masked

    def test_mask_api_key_custom_chars(self):
        """Test masking with custom visible chars."""
        api_key = "sk-1234567890abcdef"

        masked = mask_api_key(api_key, visible_chars=6)

        assert masked == "sk-123...abcdef"

    def test_mask_short_key(self):
        """Test masking a short key."""
        api_key = "short"

        masked = mask_api_key(api_key)

        assert masked == "*****"  # Should be fully masked

    def test_hash_api_key(self):
        """Test hashing an API key."""
        api_key = "sk-test-key"

        hash1 = hash_api_key(api_key)
        hash2 = hash_api_key(api_key)

        # Same key should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_hash_different_keys(self):
        """Test that different keys produce different hashes."""
        hash1 = hash_api_key("key1")
        hash2 = hash_api_key("key2")

        assert hash1 != hash2

    def test_decrypt_invalid_format(self):
        """Test decrypting invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid encrypted key format"):
            decrypt_api_key("invalid-no-colon")

    def test_encrypt_empty_key(self):
        """Test encrypting empty key."""
        encrypted = encrypt_api_key("")
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == ""

    def test_encrypt_long_key(self):
        """Test encrypting a long key."""
        long_key = "x" * 1000

        encrypted = encrypt_api_key(long_key)
        decrypted = decrypt_api_key(encrypted)

        assert decrypted == long_key
