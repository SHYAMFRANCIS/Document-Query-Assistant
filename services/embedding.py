"""Embedding service using Google Gemini for vector representations."""

import logging
from typing import Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages text embeddings using Google Gemini."""

    def __init__(self):
        """Initialize the embedding service."""
        self.embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
        logger.info("EmbeddingService initialized")

    def initialize(self, api_key: str) -> bool:
        """
        Initialize the embeddings model with API key.

        Args:
            api_key: Google Gemini API key.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=api_key,
                task_type="retrieval_document"
            )
            logger.info("Embeddings model initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            self.embeddings = None
            return False

    def get_embeddings(self) -> Optional[GoogleGenerativeAIEmbeddings]:
        """
        Get the embeddings model.

        Returns:
            LangChain embeddings model or None.
        """
        return self.embeddings

    def is_ready(self) -> bool:
        """
        Check if embeddings model is ready.

        Returns:
            True if initialized, False otherwise.
        """
        return self.embeddings is not None
