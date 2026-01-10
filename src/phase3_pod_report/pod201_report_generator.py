"""
Pod201 Report Generator for Resonance Archive System.

Generates Pod201-style reports from similarity search results using LLM.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class Pod201ReportGenerator:
    """Generates Pod201-style reports from search results using Ollama LLM."""

    def __init__(self, ollama_client):
        """
        Initialize Pod201ReportGenerator.

        Args:
            ollama_client: OllamaClient instance for LLM generation

        Raises:
            FileNotFoundError: If .pod201/persona.txt does not exist
        """
        self.ollama_client = ollama_client
        self.persona_prompt = self._load_persona()

    def _load_persona(self) -> str:
        """
        Load Pod201 persona prompt from file.

        Returns:
            Persona prompt text

        Raises:
            FileNotFoundError: If .pod201/persona.txt does not exist
        """
        persona_path = Path(".pod201/persona.txt")
        with open(persona_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_report(
        self,
        search_results: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Generate Pod201-style report from search results.

        Args:
            search_results: List of similarity search result dictionaries
                            Each dict contains: id, distance, metadata

        Returns:
            Generated Pod201-style report text, or None if generation fails

        Implementation:
            - Formats search results into a structured prompt
            - Includes Pod201 persona as system context
            - Uses llama3.1:8b model for generation
            - Returns None on error
        """
        # Format search results for the prompt
        results_text = self._format_search_results(search_results)

        # Construct full prompt with persona and results
        full_prompt = f"""{self.persona_prompt}

---

## 任務ブリーフィング
以下の類似検索結果を分析し、Pod201ペルソナでレポートを生成せよ。

{results_text}

## 指示
- 接頭語ラベル（報告/分析/提案等）を使用すること
- だ・である調の断定形を使用すること
- 簡潔に核心的な洞察を提供すること
- 一人称「当機」、二人称「随行対象」を使用すること
"""

        # Call Ollama LLM
        try:
            report = self.ollama_client.generate(
                model="llama3.1:8b",
                prompt=full_prompt
            )
            return report
        except Exception:
            return None

    def _extract_date(self, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Extract date information from metadata.

        Args:
            metadata: Metadata dictionary from search result

        Returns:
            Date string (YYYY-MM-DD format) or None if not found

        Implementation:
            - Priority: date > created_at > file (path extraction)
            - Supports YYYY-MM-DD format
            - Extracts from file paths using regex
            - Validates dates using datetime.strptime
        """
        def validate_date(date_str: str) -> Optional[str]:
            """Validate date string using datetime parsing."""
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except (ValueError, TypeError):
                return None

        # Priority 1: Check 'date' key
        if "date" in metadata:
            validated = validate_date(metadata["date"])
            if validated:
                return validated

        # Priority 2: Check 'created_at' key
        if "created_at" in metadata:
            validated = validate_date(metadata["created_at"])
            if validated:
                return validated

        # Priority 3: Extract from 'file' path
        if "file" in metadata:
            file_value = metadata["file"]
            # Guard against non-string/bytes types
            if isinstance(file_value, (str, bytes)):
                file_path = file_value if isinstance(file_value, str) else file_value.decode('utf-8', errors='ignore')
                # Match YYYY-MM-DD pattern in file path
                match = re.search(r'\d{4}-\d{2}-\d{2}', file_path)
                if match:
                    validated = validate_date(match.group(0))
                    if validated:
                        return validated

        return None

    def _format_search_results(
        self,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Format search results into readable text.

        Args:
            search_results: List of search result dictionaries

        Returns:
            Formatted text representation of results
        """
        if not search_results:
            return "検索結果: 0件（該当データ無し）"

        formatted_lines = []
        formatted_lines.append(f"検索結果: {len(search_results)}件\n")

        for i, result in enumerate(search_results, 1):
            result_id = result.get("id", "unknown")
            distance = result.get("distance", 0.0)
            metadata = result.get("metadata", {})

            formatted_lines.append(f"[{i}] ID: {result_id}")
            formatted_lines.append(f"    類似度距離: {distance:.4f}")

            # Extract and display date if available
            date = self._extract_date(metadata)
            if date:
                formatted_lines.append(f"    日付: {date}")

            # Add other metadata information
            for key, value in metadata.items():
                if key not in ["date", "created_at", "file"]:  # Skip - file used only for date extraction, not for display
                    formatted_lines.append(f"    {key}: {value}")

            formatted_lines.append("")  # Empty line between results

        return "\n".join(formatted_lines)
