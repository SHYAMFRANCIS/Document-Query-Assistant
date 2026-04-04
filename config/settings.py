"""Configuration management for the Document Query Assistant."""

import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


def get_gemini_api_key() -> Optional[str]:
    """
    Get Gemini API key from environment variables or Streamlit secrets.

    Returns:
        The API key if found, None otherwise.
    """
    # Try environment variable first
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        return api_key

    # Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "gemini" in st.secrets:
            api_key = st.secrets["gemini"].get("api_key")
            if api_key and api_key != "your_api_key_here":
                return api_key
    except Exception:
        pass

    return None


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate that the API key is properly configured.

    Args:
        api_key: The API key to validate.

    Returns:
        True if valid, False otherwise.
    """
    return api_key is not None and len(api_key) > 20
