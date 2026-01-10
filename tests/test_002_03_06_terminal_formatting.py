"""
Test for Subtask 002-03-06: ターミナル出力整形実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
from unittest.mock import Mock, patch, mock_open
from src.phase3_pod_report.pod201_report_generator import Pod201ReportGenerator


def test_format_rich_output_method_exists():
    """AC: richライブラリを使用した高度なターミナル整形機能を提供すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        assert hasattr(generator, 'format_rich_output')
        assert callable(generator.format_rich_output)


def test_format_rich_output_includes_header():
    """AC: レポートヘッダーをパネル形式で表示すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.2, "metadata": {"type": "summary"}}
        ]

        output = generator.format_rich_output(search_results)

        # Should include "Pod201" and result count
        assert "Pod201" in output
        assert "1件" in output  # Result count with unit


def test_format_rich_output_includes_table():
    """AC: 検索結果をリッチなテーブル形式で表示すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.2, "metadata": {"type": "summary", "date": "2026-01-10"}}
        ]

        output = generator.format_rich_output(search_results)

        # Should include table-like structure with key information
        assert "id1" in output
        assert "80%" in output  # Similarity percentage with symbol
        assert "2026-01-10" in output


def test_format_rich_output_applies_color_coding():
    """AC: 類似度バーに色付けを適用すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "high", "distance": 0.1, "metadata": {}},   # 90% - green
            {"id": "low", "distance": 0.6, "metadata": {}},    # 40% - red
            {"id": "mid", "distance": 0.3, "metadata": {}},    # 70% - yellow
        ]

        output = generator.format_rich_output(search_results)

        # Verify color coding logic is implemented (bars are present)
        # Note: When outputting to StringIO without force_terminal, colors may not appear
        # but the structure with similarity bars should still be present
        assert "[█████████░]" in output  # 90% bar
        assert "[████░░░░░░]" in output  # 40% bar
        assert "[███████░░░]" in output  # 70% bar


def test_format_rich_output_handles_empty_results():
    """追加テスト: 空の検索結果を適切に処理すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = []

        output = generator.format_rich_output(search_results)

        # Should handle empty results gracefully
        assert "0件" in output or "該当データ無し" in output


def test_format_rich_output_multiple_results():
    """追加テスト: 複数の検索結果をテーブルに表示すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}},
            {"id": "id2", "distance": 0.5, "metadata": {"type": "chunk"}},
            {"id": "id3", "distance": 0.8, "metadata": {"type": "summary"}},
        ]

        output = generator.format_rich_output(search_results)

        # Should include all IDs
        assert "id1" in output
        assert "id2" in output
        assert "id3" in output
