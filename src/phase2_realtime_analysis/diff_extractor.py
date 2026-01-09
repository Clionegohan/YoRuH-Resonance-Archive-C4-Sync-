"""
Diff Extractor for Resonance Archive System.

Extracts diff text from file changes and vectorizes it for similarity search.
"""
import logging
import time
from typing import Optional, List
from src.utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class DiffExtractor:
    """Extracts and vectorizes diff text from file changes."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """
        Initialize DiffExtractor.

        Args:
            ollama_client: OllamaClient instance (default: create new)
        """
        self.ollama_client = ollama_client or OllamaClient()

    def extract_diff(
        self,
        previous_text: Optional[str],
        current_text: str
    ) -> str:
        """
        Extract diff text from previous and current text.

        Args:
            previous_text: Previous text (None for first save)
            current_text: Current text

        Returns:
            Diff text (added portion). Empty string if deletion or no change.

        Implementation:
            - If previous_text is None or empty: return current_text
            - If current_text is shorter: return empty string (deletion)
            - Otherwise: return current_text[len(previous_text):]
        """
        # Handle None or empty previous_text
        if not previous_text:
            return current_text

        # Handle deletion or no change
        if len(current_text) <= len(previous_text):
            return ""

        # Extract added portion
        return current_text[len(previous_text):]

    def vectorize_diff(
        self,
        diff_text: str,
        max_retries: int = 3
    ) -> Optional[List[float]]:
        """
        Vectorize diff text using OllamaClient.

        Args:
            diff_text: Diff text to vectorize
            max_retries: Maximum retry attempts (default: 3)

        Returns:
            1024-dimensional vector or None if empty or failed

        Implementation:
            - Return None if diff_text is empty or whitespace-only
            - Use OllamaClient with mxbai-embed-large model
            - Retry up to max_retries with exponential backoff
            - Return None and log error if all retries fail
        """
        # Return None if empty or whitespace-only
        if not diff_text or not diff_text.strip():
            return None

        # Retry with exponential backoff
        for attempt in range(max_retries):
            try:
                vector = self.ollama_client.embed(
                    model="mxbai-embed-large",
                    text=diff_text
                )

                # Validate vector dimension
                if vector and len(vector) == 1024:
                    return vector

                logger.warning(
                    f"Invalid vector dimension: {len(vector) if vector else 0} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

            except Exception as e:
                logger.warning(
                    f"Vectorization attempt {attempt + 1}/{max_retries} failed: {e}"
                )

            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

        # All retries failed
        logger.error(f"Vectorization failed after {max_retries} attempts")
        return None
