"""Gemini AI service for document query answering."""

import logging
import time
from typing import Optional, Tuple

import google.generativeai as genai

logger = logging.getLogger(__name__)


def initialize_gemini(api_key: str) -> Optional[genai.GenerativeModel]:
    """
    Initialize and configure the Gemini AI model.

    Args:
        api_key: Google Gemini API key.

    Returns:
        Configured Gemini model or None if initialization fails.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Successfully initialized Gemini model")
        return model
    except Exception as e:
        error_msg = f"Failed to configure Gemini API: {str(e)}"
        logger.error(error_msg)
        return None


def generate_response(
    model: genai.GenerativeModel,
    prompt: str,
    max_retries: int = 3
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate a response from the Gemini model with retry logic.

    Args:
        model: Configured Gemini model instance.
        prompt: The prompt to send to the model.
        max_retries: Maximum number of retry attempts.

    Returns:
        Tuple of (response_text, error_message).
        One of them will be None.
    """
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)

            if response.text:
                return response.text, None
            else:
                error_msg = "Received empty response from Gemini"
                logger.warning(error_msg)
                return None, error_msg

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(f"Attempt {attempt + 1}/{max_retries} - {error_msg}")

            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("Max retries reached")
                return None, error_msg

    return None, "Unexpected error in generate_response"
