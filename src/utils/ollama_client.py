"""
Ollama API client for text generation and embeddings.

This module provides a simple interface to interact with Ollama API.
"""
import requests
from typing import List, Dict, Any, Optional


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.

        Args:
            base_url: Base URL of Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url

    def is_available(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            True if Ollama is running, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models.

        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except requests.exceptions.RequestException:
            return []

    def generate(self, model: str, prompt: str, stream: bool = False) -> Optional[str]:
        """
        Generate text using specified model.

        Args:
            model: Model name (e.g., "llama3.1:8b")
            prompt: Input prompt text
            stream: Whether to stream the response (default: False)

        Returns:
            Generated text or None if error
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException:
            return None

    def embed(self, model: str, text: str) -> Optional[List[float]]:
        """
        Generate embeddings for text.

        Args:
            model: Embedding model name (e.g., "mxbai-embed-large")
            text: Input text to embed

        Returns:
            Vector (list of floats) or None if error
        """
        try:
            payload = {
                "model": model,
                "input": text
            }
            response = requests.post(
                f"{self.base_url}/api/embed",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            embeddings = data.get("embeddings", [])
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            return None
        except requests.exceptions.RequestException:
            return None
