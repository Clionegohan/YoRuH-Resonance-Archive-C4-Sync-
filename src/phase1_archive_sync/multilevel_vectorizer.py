"""
Multilevel Vectorizer for Resonance Archive System.

This module generates two-level vectors:
- Level 1: Document-wide summary vector
- Level 2: Chunk-level detail vectors
"""
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import time

from src.phase1_archive_sync.semantic_splitter import SemanticSplitter
from src.utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingRecord:
    """Represents an embedding record with metadata."""
    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultilevelVectorizer:
    """Generates multi-level embeddings for documents."""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        semantic_splitter: Optional[SemanticSplitter] = None,
        summary_threshold_chars: int = 2000,
        summary_threshold_chunks: int = 5
    ):
        """
        Initialize MultilevelVectorizer.

        Args:
            ollama_client: OllamaClient instance (default: create new)
            semantic_splitter: SemanticSplitter instance (default: create new)
            summary_threshold_chars: Minimum chars to trigger summary (default: 2000)
            summary_threshold_chunks: Minimum chunks to trigger summary (default: 5)
        """
        self.ollama_client = ollama_client or OllamaClient()
        self.semantic_splitter = semantic_splitter or SemanticSplitter()
        self.summary_threshold_chars = summary_threshold_chars
        self.summary_threshold_chunks = summary_threshold_chunks

    def vectorize(self, text: str, file_path: str) -> List[EmbeddingRecord]:
        """
        Generate multi-level embeddings for text.

        Args:
            text: Input text to vectorize
            file_path: File path (relative to vault root)

        Returns:
            List of EmbeddingRecord objects
        """
        # Handle empty files
        if not text or not text.strip():
            logger.error(f"Empty file: {file_path}")
            return []

        records = []
        current_time = datetime.now(timezone.utc).isoformat()

        try:
            # Level 2: Chunk-level vectors
            chunks = self.semantic_splitter.split(text)
            level2_records = []

            for chunk in chunks:
                # Skip empty chunks
                if not chunk.text.strip():
                    logger.warning(f"Skipping empty chunk in {file_path}")
                    continue

                # Vectorize chunk with retry
                vector = self._vectorize_with_retry(chunk.text)
                if vector is None:
                    logger.error(f"Failed to vectorize chunk in {file_path}")
                    continue

                # Generate metadata
                content_hash = self._compute_hash(chunk.text)
                chunk_id = f"{file_path}#{chunk.seq}#{content_hash[:8]}"

                metadata = {
                    'level': 2,
                    'chunk_id': chunk_id,
                    'type': 'chunk',
                    'file': file_path,
                    'date': self._extract_date_from_path(file_path),
                    'seq': chunk.seq,
                    'char_count': len(chunk.text),
                    'content_hash': content_hash,
                    'created_at': current_time,
                    'updated_at': current_time
                }

                record = EmbeddingRecord(
                    id=chunk_id,
                    text=chunk.text,
                    vector=vector,
                    metadata=metadata
                )
                level2_records.append(record)

            records.extend(level2_records)

            # Level 1: Summary vector (if needed)
            if self._should_generate_summary(text, len(level2_records)):
                summary_record = self._generate_summary_record(
                    text, file_path, current_time
                )
                if summary_record:
                    records.insert(0, summary_record)  # Insert at beginning

            return records

        except Exception as e:
            logger.error(f"Error vectorizing {file_path}: {e}")
            return []

    def _should_generate_summary(self, text: str, chunk_count: int) -> bool:
        """
        Determine if summary should be generated.

        Args:
            text: Input text
            chunk_count: Number of chunks

        Returns:
            True if summary should be generated
        """
        return (
            len(text) > self.summary_threshold_chars or
            chunk_count > self.summary_threshold_chunks
        )

    def _generate_summary_record(
        self,
        text: str,
        file_path: str,
        current_time: str
    ) -> Optional[EmbeddingRecord]:
        """
        Generate Level 1 summary record.

        Args:
            text: Input text
            file_path: File path
            current_time: Current timestamp

        Returns:
            EmbeddingRecord or None if failed
        """
        try:
            # Generate summary using LLM
            summary = self._generate_summary(text)
            if not summary:
                logger.error(f"Failed to generate summary for {file_path}")
                return None

            # Vectorize summary with retry
            vector = self._vectorize_with_retry(summary)
            if vector is None:
                logger.error(f"Failed to vectorize summary for {file_path}")
                return None

            # Generate metadata
            content_hash = self._compute_hash(summary)
            chunk_id = f"{file_path}#0#{content_hash[:8]}"

            metadata = {
                'level': 1,
                'chunk_id': chunk_id,
                'type': 'summary',
                'file': file_path,
                'date': self._extract_date_from_path(file_path),
                'seq': 0,
                'char_count': len(summary),
                'content_hash': content_hash,
                'created_at': current_time,
                'updated_at': current_time
            }

            return EmbeddingRecord(
                id=chunk_id,
                text=summary,
                vector=vector,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error generating summary record for {file_path}: {e}")
            return None

    def _generate_summary(self, text: str) -> Optional[str]:
        """
        Generate summary using LLM.

        Args:
            text: Input text

        Returns:
            Summary text (500-800 chars, bullet format) or None
        """
        prompt = f"""以下のテキストを500〜800字の箇条書き形式で要約してください。

要約時に必ず保持すべき要素：
- 固有名詞（人名、組織名、プロジェクト名等）
- 日付・時刻情報
- 数値データ（統計、ID、バージョン番号等）
- 決定事項・アクションアイテム
- 例外条件・制約事項

形式：
- 箇条書き（-で開始）
- 500〜800字

テキスト：
{text}

要約："""

        try:
            summary = self.ollama_client.generate(
                model="llama3.1:8b",
                prompt=prompt
            )
            return summary.strip() if summary else None

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return None

    def _vectorize_with_retry(
        self,
        text: str,
        max_retries: int = 3
    ) -> Optional[List[float]]:
        """
        Vectorize text with retry logic.

        Args:
            text: Text to vectorize
            max_retries: Maximum retry attempts (default: 3)

        Returns:
            Vector or None if failed
        """
        for attempt in range(max_retries):
            try:
                vector = self.ollama_client.embed(
                    model="mxbai-embed-large",
                    text=text
                )
                if vector and len(vector) == 1024:
                    return vector

                logger.warning(f"Invalid vector dimension (attempt {attempt + 1}/{max_retries})")

            except Exception as e:
                logger.warning(f"Vectorization attempt {attempt + 1}/{max_retries} failed: {e}")

            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

        logger.error(f"Vectorization failed after {max_retries} attempts")
        return None

    def _compute_hash(self, text: str) -> str:
        """
        Compute SHA256 hash of text.

        Args:
            text: Input text

        Returns:
            Hex digest of SHA256 hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _extract_date_from_path(self, file_path: str) -> str:
        """
        Extract date from file path.

        Args:
            file_path: File path

        Returns:
            Date string (YYYY-MM-DD) or empty string
        """
        # Try to extract date from filename (e.g., 2026-01-03.md)
        import re
        match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path)
        if match:
            return match.group(1)

        # Return empty string if no date found
        return ""
