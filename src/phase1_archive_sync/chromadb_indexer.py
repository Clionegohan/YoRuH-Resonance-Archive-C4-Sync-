"""
ChromaDB Indexer for Resonance Archive System.

This module provides a wrapper around ChromaDB for vector storage and retrieval.
"""
import logging
import os
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import chromadb
from chromadb.config import Settings
from tqdm import tqdm

if TYPE_CHECKING:
    from src.phase1_archive_sync.multilevel_vectorizer import EmbeddingRecord

logger = logging.getLogger(__name__)


class ChromaDBIndexer:
    """ChromaDB indexer for storing and retrieving semantic vectors."""

    def __init__(self, persist_directory: str = "./.chroma_db"):
        """
        Initialize ChromaDB indexer with persistence.

        Args:
            persist_directory: Directory path for ChromaDB persistence (default: ./.chroma_db)
        """
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client with persistence
        # chromadb 0.3.x uses Settings with persist_directory
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="resonance_archive",
            metadata={"description": "Semantic vectors for Obsidian vault archive"}
        )

    def add_vector(
        self,
        id: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add a vector with metadata to the collection.

        Args:
            id: Unique identifier for the vector
            vector: Embedding vector (1024 dimensions from mxbai-embed-large)
            metadata: Metadata dictionary with fields:
                - type: "summary" or "chunk"
                - file: File path relative to vault root
                - date: ISO format date (YYYY-MM-DD)
                - char_count: Character count (for summary type)
                - chunk_index: Chunk index (for chunk type)
        """
        self.collection.add(
            ids=[id],
            embeddings=[vector],
            metadatas=[metadata]
        )
        # Persist data to disk
        self.client.persist()

    def search(
        self,
        query_vector: List[float],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return (default: 3)

        Returns:
            List of result dictionaries with keys: id, distance, metadata
        """
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
                })

        return formatted_results

    def add_vectors_batch(
        self,
        records: List['EmbeddingRecord'],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Add multiple vectors in batches with progress tracking.

        Args:
            records: List of EmbeddingRecord objects to index
            batch_size: Number of vectors to add per batch (default: 100)
            show_progress: Show tqdm progress bar (default: True)

        Returns:
            Dictionary with keys:
                - success: Number of successfully indexed vectors
                - failed: Number of failed vectors
                - errors: List of error messages
        """
        success_count = 0
        failed_count = 0
        errors = []

        # Handle empty list
        if not records:
            return {
                'success': 0,
                'failed': 0,
                'errors': []
            }

        # Create progress bar
        iterator = tqdm(records, desc="Indexing vectors", disable=not show_progress)

        # Process in batches
        batch_ids = []
        batch_embeddings = []
        batch_metadatas = []

        for record in iterator:
            try:
                # Validate vector dimension
                if len(record.vector) != 1024:
                    error_msg = f"Invalid vector dimension for {record.id}: expected 1024, got {len(record.vector)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    failed_count += 1
                    continue

                # Add to batch
                batch_ids.append(record.id)
                batch_embeddings.append(record.vector)
                batch_metadatas.append(record.metadata)

                # Insert batch when size is reached
                if len(batch_ids) >= batch_size:
                    self._insert_batch(batch_ids, batch_embeddings, batch_metadatas)
                    success_count += len(batch_ids)

                    # Clear batch
                    batch_ids = []
                    batch_embeddings = []
                    batch_metadatas = []

            except Exception as e:
                error_msg = f"Error processing record {record.id}: {e}"
                errors.append(error_msg)
                logger.exception(error_msg)
                failed_count += 1

        # Insert remaining records in final batch
        if batch_ids:
            try:
                self._insert_batch(batch_ids, batch_embeddings, batch_metadatas)
                success_count += len(batch_ids)
            except Exception as e:
                error_msg = f"Error inserting final batch: {e}"
                errors.append(error_msg)
                logger.exception(error_msg)
                failed_count += len(batch_ids)

        return {
            'success': success_count,
            'failed': failed_count,
            'errors': errors
        }

    def _insert_batch(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Insert a batch of vectors into ChromaDB.

        Args:
            ids: List of vector IDs
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
        """
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )
        # Persist data to disk
        self.client.persist()
