"""
Similarity Searcher for Resonance Archive System.

Performs multi-level similarity search against ChromaDB.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SimilaritySearcher:
    """Performs multi-level similarity search using ChromaDB."""

    def __init__(self, chromadb_indexer):
        """
        Initialize SimilaritySearcher.

        Args:
            chromadb_indexer: ChromaDBIndexer instance
        """
        self.chromadb_indexer = chromadb_indexer

    def search_level1(
        self,
        query_vector: Optional[List[float]]
    ) -> List[Dict[str, Any]]:
        """
        Perform Level 1 search (summary) with top_k=5.

        Args:
            query_vector: Query embedding vector (1024 dimensions)

        Returns:
            List of result dictionaries with keys: id, distance, metadata
            Empty list if query_vector is None/empty or search fails

        Implementation:
            - Returns empty list if query_vector is None or empty
            - Queries ChromaDB with where={"type": "summary"}
            - Returns up to 5 results
            - Logs error and returns empty list on failure
        """
        # Validate query_vector
        if not query_vector:
            return []

        try:
            # Query ChromaDB with metadata filter
            results = self.chromadb_indexer.collection.query(
                query_embeddings=[query_vector],
                n_results=5,
                where={"type": "summary"}
            )

            # Format results
            return self._format_results(results)

        except Exception:
            logger.exception("Level 1 search failed")
            return []

    def search_level2(
        self,
        query_vector: Optional[List[float]]
    ) -> List[Dict[str, Any]]:
        """
        Perform Level 2 search (chunk) with top_k=10.

        Args:
            query_vector: Query embedding vector (1024 dimensions)

        Returns:
            List of result dictionaries with keys: id, distance, metadata
            Empty list if query_vector is None/empty or search fails

        Implementation:
            - Returns empty list if query_vector is None or empty
            - Queries ChromaDB with where={"type": "chunk"}
            - Returns up to 10 results
            - Logs error and returns empty list on failure
        """
        # Validate query_vector
        if not query_vector:
            return []

        try:
            # Query ChromaDB with metadata filter
            results = self.chromadb_indexer.collection.query(
                query_embeddings=[query_vector],
                n_results=10,
                where={"type": "chunk"}
            )

            # Format results
            return self._format_results(results)

        except Exception:
            logger.exception("Level 2 search failed")
            return []

    def _format_results(
        self,
        results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format ChromaDB query results into list of dictionaries.

        Args:
            results: ChromaDB query results

        Returns:
            List of formatted result dictionaries
        """
        formatted_results = []

        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
                })

        return formatted_results
