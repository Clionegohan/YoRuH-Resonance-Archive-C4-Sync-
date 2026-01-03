"""
ChromaDB Indexer for Resonance Archive System.

This module provides a wrapper around ChromaDB for vector storage and retrieval.
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


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
