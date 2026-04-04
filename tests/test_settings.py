"""Tests for configuration settings."""

import os
from unittest.mock import patch

from config.settings import get_gemini_api_key, validate_api_key


class TestGetGeminiApiKey:
    """Test Gemini API key retrieval."""

    def test_get_api_key_from_env(self):
        """Test getting API key from environment variable."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key_12345"}):
            result = get_gemini_api_key()
            assert result == "test_api_key_12345"

    def test_get_api_key_placeholder_returns_none(self):
        """Test that placeholder API key returns None."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "your_api_key_here"}):
            result = get_gemini_api_key()
            assert result is None

    def test_get_api_key_not_set(self):
        """Test when API key is not set in environment."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing GEMINI_API_KEY
            os.environ.pop("GEMINI_API_KEY", None)
            result = get_gemini_api_key()
            # Should return None if not in env or secrets
            assert result is None or result == "your_api_key_here"


class TestValidateApiKey:
    """Test API key validation."""

    def test_valid_api_key(self):
        """Test validation of a valid API key."""
        assert validate_api_key("AIzaSyD_valid_api_key_1234567890") is True

    def test_short_api_key(self):
        """Test validation of a too-short API key."""
        assert validate_api_key("short") is False

    def test_none_api_key(self):
        """Test validation of None API key."""
        assert validate_api_key(None) is False

    def test_empty_api_key(self):
        """Test validation of empty API key."""
        assert validate_api_key("") is False

    def test_placeholder_api_key(self):
        """Test validation of placeholder API key."""
        # Placeholder is longer than 20 chars but should still be caught by length check
        placeholder = "your_api_key_here"
        assert validate_api_key(placeholder) is False  # Less than 20 chars
