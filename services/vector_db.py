"""Vector database service for document storage and retrieval."""

import logging
from typing import Dict, List, Optional, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class VectorDB:
    """FAISS-based vector database for document storage and semantic search."""

    def __init__(self):
        """Initialize the vector database."""
        self.vectorstores: Dict[str, FAISS] = {}
        self.embeddings = None
        logger.info("VectorDB initialized")

    def set_embeddings(self, embeddings):
        """
        Set the embeddings model.

        Args:
            embeddings: LangChain embeddings model.
        """
        self.embeddings = embeddings
        logger.info("Embeddings model set")

    def add_document(
        self,
        doc_id: str,
        chunks: List[Tuple[str, dict]]
    ) -> bool:
        """
        Add a document's chunks to the vector database.

        Args:
            doc_id: Unique identifier for the document.
            chunks: List of (chunk_text, metadata) tuples.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if not self.embeddings:
                logger.error("Embeddings model not set")
                return False

            if not chunks:
                logger.warning(f"No chunks to add for document: {doc_id}")
                return False

            # Create LangChain documents
            documents = [
                Document(page_content=chunk, metadata=metadata)
                for chunk, metadata in chunks
            ]

            # Create or update FAISS index
            if doc_id in self.vectorstores:
                # Update existing index
                self.vectorstores[doc_id].add_documents(documents)
                logger.info(
                    f"Updated {len(documents)} chunks for '{doc_id}'"
                )
            else:
                # Create new index
                self.vectorstores[doc_id] = FAISS.from_documents(
                    documents, self.embeddings
                )
                logger.info(
                    f"Added {len(documents)} chunks for '{doc_id}'"
                )

            return True

        except Exception as e:
            logger.error(f"Failed to add document '{doc_id}': {e}")
            return False

    def search(
        self,
        query: str,
        doc_id: Optional[str] = None,
        k: int = 5
    ) -> List[Tuple[str, float, dict]]:
        """
        Search for relevant chunks.

        Args:
            query: Search query.
            doc_id: Optional document ID to search within.
            k: Number of results to return.

        Returns:
            List of (chunk_text, score, metadata) tuples.
        """
        try:
            if not self.embeddings:
                logger.error("Embeddings model not set")
                return []

            results = []

            if doc_id and doc_id in self.vectorstores:
                # Search within specific document
                docs = self.vectorstores[doc_id].similarity_with_relevance_scores(
                    query, k=k
                )
                for doc, score in docs:
                    results.append((
                        doc.page_content,
                        score,
                        doc.metadata
                    ))
            else:
                # Search across all documents
                for doc_id, vectorstore in self.vectorstores.items():
                    docs = vectorstore.similarity_with_relevance_scores(
                        query, k=k
                    )
                    for doc, score in docs:
                        results.append((
                            doc.page_content,
                            score,
                            doc.metadata
                        ))

                # Sort by score and take top k
                results.sort(key=lambda x: x[1], reverse=True)
                results = results[:k]

            logger.info(
                f"Search returned {len(results)} results for query: "
                f"'{query[:50]}...'"
            )

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def remove_document(self, doc_id: str) -> bool:
        """
        Remove a document from the vector database.

        Args:
            doc_id: Document ID to remove.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if doc_id in self.vectorstores:
                del self.vectorstores[doc_id]
                logger.info(f"Removed document '{doc_id}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove document '{doc_id}': {e}")
            return False

    def clear_all(self) -> None:
        """Clear all documents from the vector database."""
        self.vectorstores.clear()
        logger.info("Cleared all documents from VectorDB")

    def get_stats(self) -> dict:
        """
        Get vector database statistics.

        Returns:
            Dictionary with stats.
        """
        total_docs = len(self.vectorstores)
        total_chunks = sum(
            vs.index.ntotal for vs in self.vectorstores.values()
        )

        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks
        }
