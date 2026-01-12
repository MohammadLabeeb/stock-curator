"""
Tests for security utilities including log sanitization.
"""

import pytest
from src.utils.helpers import sanitize_log_message


class TestSanitizeLogMessage:
    """Test cases for log message sanitization."""

    def test_sanitize_bearer_token(self):
        """Test that Bearer tokens are redacted."""
        message = "Authorization: Bearer abc123xyz456token789"
        result = sanitize_log_message(message)
        assert "Bearer [REDACTED]" in result
        assert "abc123xyz456token789" not in result

    def test_sanitize_api_key(self):
        """Test that API keys are redacted."""
        message = 'api_key="sk-1234567890abcdefghij"'
        result = sanitize_log_message(message)
        assert "api_key=[REDACTED]" in result
        assert "sk-1234567890abcdefghij" not in result

    def test_sanitize_token_in_json(self):
        """Test that tokens in JSON format are redacted."""
        message = '{"token": "xyz1234567890abcdeftoken"}'
        result = sanitize_log_message(message)
        assert "token=[REDACTED]" in result
        assert "xyz1234567890abcdeftoken" not in result

    def test_sanitize_secret(self):
        """Test that secrets are redacted."""
        message = 'secret=mysecretvalue123456'
        result = sanitize_log_message(message)
        assert "secret=[REDACTED]" in result
        # Short secrets (less than 8 chars) may not be redacted
        assert "mysecretvalue123456" not in result

    def test_sanitize_password(self):
        """Test that passwords are redacted."""
        message = 'password="mypassword123"'
        result = sanitize_log_message(message)
        assert "password=[REDACTED]" in result
        assert "mypassword123" not in result

    def test_sanitize_x_api_key_header(self):
        """Test that x-api-key headers are redacted."""
        message = "x-api-key: abc123xyz789"
        result = sanitize_log_message(message)
        assert "x-api-key: [REDACTED]" in result
        assert "abc123xyz789" not in result

    def test_sanitize_google_api_key(self):
        """Test that Google API keys are redacted."""
        message = "AIzaSyDxKL5vX9Y2Z3AbCdEfGhIjKlMnOpQrStU"
        result = sanitize_log_message(message)
        assert "[GOOGLE_API_KEY_REDACTED]" in result
        assert "AIzaSyDxKL5vX9Y2Z3AbCdEfGhIjKlMnOpQrStU" not in result

    def test_sanitize_generic_secret_key(self):
        """Test that generic secret keys are redacted."""
        message = "sk-1234567890abcdefghijklmnop"
        result = sanitize_log_message(message)
        assert "[SECRET_KEY_REDACTED]" in result
        assert "sk-1234567890abcdefghijklmnop" not in result

    def test_truncate_long_message(self):
        """Test that long messages are truncated."""
        long_message = "A" * 1000
        result = sanitize_log_message(long_message, max_length=100)
        assert len(result) < len(long_message)
        assert "truncated" in result
        assert "900 chars hidden" in result

    def test_normal_message_unchanged(self):
        """Test that normal messages without secrets pass through."""
        message = "This is a normal log message"
        result = sanitize_log_message(message)
        assert result == message

    def test_multiple_secrets_in_one_message(self):
        """Test that multiple secrets in one message are all redacted."""
        message = 'Authorization: Bearer token123456789 and api_key="key456789012" and secret="secret789012345"'
        result = sanitize_log_message(message)
        assert "Bearer [REDACTED]" in result
        assert "api_key=[REDACTED]" in result
        assert "secret=[REDACTED]" in result
        assert "token123456789" not in result
        assert "key456789012" not in result
        assert "secret789012345" not in result

    def test_case_insensitive_matching(self):
        """Test that pattern matching works for various capitalizations."""
        message = 'API_KEY="MyKey123456789012" and Token="MyToken12345678901"'
        result = sanitize_log_message(message)
        assert "=[REDACTED]" in result
        assert "MyKey123456789012" not in result
        assert "MyToken12345678901" not in result

    def test_non_string_input(self):
        """Test that non-string inputs are converted to string and sanitized."""
        message = {"api_key": "secret12345678901234"}
        result = sanitize_log_message(message)
        assert isinstance(result, str)
        # When dict is converted to string, it becomes {'api_key': 'secret...'}
        # The pattern should still catch and redact it
        assert "secret12345678901234" not in result or "api_key=[REDACTED]" in result

    def test_empty_message(self):
        """Test that empty messages are handled."""
        result = sanitize_log_message("")
        assert result == ""

    def test_none_input(self):
        """Test that None input is handled."""
        result = sanitize_log_message(None)
        assert result == "None"
