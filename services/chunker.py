"""Document chunking service for splitting documents into manageable pieces."""

import logging
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Splits documents into chunks with overlap for better retrieval."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        length_function: str = "character"
    ):
        """
        Initialize the document chunker.

        Args:
            chunk_size: Target size for each chunk in characters.
            chunk_overlap: Number of characters to overlap between chunks.
            length_function: Method to measure text length.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

        logger.info(
            f"DocumentChunker initialized: chunk_size={chunk_size}, "
            f"overlap={chunk_overlap}"
        )

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: The full text to split.

        Returns:
            List of text chunks.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to chunk_text")
            return []

        chunks = self.text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")

        return chunks

    def chunk_with_metadata(
        self,
        text: str,
        source: str = "unknown"
    ) -> List[Tuple[str, dict]]:
        """
        Split text into chunks with metadata.

        Args:
            text: The full text to split.
            source: Source document name.

        Returns:
            List of (chunk_text, metadata) tuples.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to chunk_with_metadata")
            return []

        chunks = self.text_splitter.split_text(text)

        chunks_with_metadata = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            }
            chunks_with_metadata.append((chunk, metadata))

        logger.info(
            f"Split '{source}' into {len(chunks)} chunks with metadata"
        )

        return chunks_with_metadata

    def estimate_chunks(self, text: str) -> dict:
        """
        Estimate how many chunks a text will produce.

        Args:
            text: The text to estimate.

        Returns:
            Dictionary with estimation details.
        """
        if not text or not text.strip():
            return {"estimated_chunks": 0, "total_chars": 0}

        total_chars = len(text)
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        estimated_chunks = max(1, total_chars // effective_chunk_size)

        return {
            "estimated_chunks": estimated_chunks,
            "total_chars": total_chars,
            "chunk_size": self.chunk_size,
            "overlap": self.chunk_overlap
        }
