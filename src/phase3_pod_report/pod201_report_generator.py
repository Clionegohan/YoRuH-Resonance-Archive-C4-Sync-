"""
Pod201 Report Generator for Resonance Archive System.

Generates Pod201-style reports from similarity search results using LLM.
"""
import re
import logging
from datetime import datetime
from io import StringIO
from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Set up logger
logger = logging.getLogger(__name__)


class Pod201ReportGenerator:
    """Generates Pod201-style reports from search results using Ollama LLM."""

    # Default persona prompt when persona.txt is not available
    DEFAULT_PERSONA = """あなたはPod201、知的アーカイブ解析エージェントです。
簡潔で核心的な洞察を提供する、だ・である調の断定形で報告してください。
一人称は「当機」、二人称は「随行対象」を使用してください。
接頭語ラベル（報告/分析/提案等）を使用してください。"""

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
            Persona prompt text (from file or default)

        Note:
            Falls back to DEFAULT_PERSONA if file is not found
        """
        persona_path = Path(".pod201/persona.txt")
        try:
            with open(persona_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(
                f"Persona file not found at {persona_path}. Using default persona."
            )
            return self.DEFAULT_PERSONA

    def generate_report(
        self,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate Pod201-style report from search results.

        Args:
            search_results: List of similarity search result dictionaries
                            Each dict contains: id, distance, metadata

        Returns:
            Generated Pod201-style report text (falls back to plain text on error)

        Implementation:
            - Formats search results into a structured prompt
            - Includes Pod201 persona as system context
            - Uses llama3.1:8b model for generation
            - On error: logs the error and returns fallback report
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

            # Validate response
            if report is None or (isinstance(report, str) and not report.strip()):
                logger.error("LLM returned empty or None response")
                return self._generate_fallback_report(results_text)

            return report

        except ConnectionError as e:
            logger.error(f"Connection error during LLM generation: {e}", exc_info=True)
            return self._generate_fallback_report(results_text, error_type="接続エラー")
        except TimeoutError as e:
            logger.error(f"Timeout during LLM generation: {e}", exc_info=True)
            return self._generate_fallback_report(results_text, error_type="タイムアウト")
        except Exception as e:
            logger.error(f"Error during LLM generation: {e}", exc_info=True)
            return self._generate_fallback_report(results_text)

    def _generate_fallback_report(
        self,
        results_text: str,
        error_type: str = "LLM生成失敗"
    ) -> str:
        """
        Generate fallback report when LLM generation fails.

        Args:
            results_text: Formatted search results text
            error_type: Type of error that occurred

        Returns:
            Fallback report with warning message and search results
        """
        warning_message = f"【警告】{error_type}。検索結果を表示します。\n\n"
        return warning_message + results_text

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

    def _calculate_similarity_percentage(self, distance: float) -> int:
        """
        Calculate similarity percentage from distance value.

        Args:
            distance: Distance value from ChromaDB search (0.0 = perfect match, 1.0 = no similarity)

        Returns:
            Similarity percentage (0-100)

        Implementation:
            - Formula: similarity = (1 - distance) * 100
            - Clamps negative values and values > 1.0 to 0%
            - Returns integer percentage
        """
        # Clamp out-of-range values
        if distance < 0 or distance > 1.0:
            return 0

        # Calculate similarity percentage
        similarity = (1 - distance) * 100
        return round(similarity)

    def _format_similarity_bar(self, percentage: int) -> str:
        """
        Format similarity percentage as a visual progress bar.

        Args:
            percentage: Similarity percentage (0-100)

        Returns:
            Visual bar string like "[████████░░] 80%"

        Implementation:
            - Uses Unicode block characters: █ (filled), ░ (empty)
            - Bar length: 10 characters (10% increments)
            - Format: [bar]
            - Clamps percentage to valid range for defensive coding
        """
        # Clamp to valid range (defensive coding)
        percentage = max(0, min(100, percentage))

        # Calculate number of filled blocks (out of 10)
        filled_blocks = percentage // 10
        empty_blocks = 10 - filled_blocks

        # Build bar string
        bar = "█" * filled_blocks + "░" * empty_blocks
        return f"[{bar}]"

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
            distance = result.get("distance")
            distance = distance if isinstance(distance, (int, float)) else 0.0
            metadata = result.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}

            # Calculate similarity and format visual bar
            similarity_percentage = self._calculate_similarity_percentage(distance)
            similarity_bar = self._format_similarity_bar(similarity_percentage)

            formatted_lines.append(f"[{i}] ID: {result_id}")
            formatted_lines.append(f"    類似度: {similarity_bar} {similarity_percentage}% (distance: {distance:.4f})")

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

    def format_rich_output(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results using Rich library for enhanced terminal output.

        Args:
            search_results: List of search result dictionaries

        Returns:
            Rich-formatted output string with colors, tables, and panels

        Implementation:
            - Uses rich.console.Console for rendering
            - Creates Panel for header with result count
            - Creates Table with columns: ID, Similarity Bar, %, Distance, Date, Metadata
            - Applies color coding: green (≥80%), yellow (50-79%), red (<50%)
            - Captures output to StringIO for string return
        """
        # Create string buffer to capture rich output
        string_buffer = StringIO()
        console = Console(file=string_buffer, width=120)

        # Create header panel
        result_count = len(search_results)
        header_text = f"検索結果: {result_count}件"
        panel = Panel(header_text, title="Pod201 類似検索レポート", border_style="cyan")
        console.print(panel)

        if not search_results:
            console.print("[yellow]検索結果: 0件（該当データ無し）[/yellow]")
            return string_buffer.getvalue()

        # Create results table
        table = Table(title="類似検索結果", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("類似度バー", justify="center")
        table.add_column("%", justify="right", style="bold")
        table.add_column("Distance", justify="right")
        table.add_column("日付", style="dim")
        table.add_column("メタデータ", style="dim")

        for result in search_results:
            result_id = result.get("id", "unknown")
            distance = result.get("distance")
            distance = distance if isinstance(distance, (int, float)) else 0.0
            metadata = result.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}

            # Calculate similarity and format bar
            similarity_percentage = self._calculate_similarity_percentage(distance)
            similarity_bar = self._format_similarity_bar(similarity_percentage)

            # Apply color coding based on similarity
            if similarity_percentage >= 80:
                bar_color = "green"
            elif similarity_percentage >= 50:
                bar_color = "yellow"
            else:
                bar_color = "red"

            colored_bar = f"[{bar_color}]{similarity_bar}[/{bar_color}]"

            # Extract date
            date = self._extract_date(metadata)
            date_str = date if date else "-"

            # Format other metadata
            meta_parts = []
            for key, value in metadata.items():
                if key not in ["date", "created_at", "file"]:
                    meta_parts.append(f"{key}: {value}")
            meta_str = ", ".join(meta_parts) if meta_parts else "-"

            # Add row to table
            table.add_row(
                result_id,
                colored_bar,
                f"{similarity_percentage}%",
                f"{distance:.4f}",
                date_str,
                meta_str
            )

        console.print(table)
        return string_buffer.getvalue()
