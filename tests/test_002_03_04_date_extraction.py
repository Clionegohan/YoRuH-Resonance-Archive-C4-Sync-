"""
Test for Subtask 002-03-04: 日付情報抽出実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from src.phase3_pod_report.pod201_report_generator import Pod201ReportGenerator


def test_extract_date_method_exists():
    """AC: _extract_date()メソッドを提供すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        assert hasattr(generator, '_extract_date')
        assert callable(generator._extract_date)


def test_extract_date_from_date_key():
    """AC: メタデータのdateキーから日付を抽出"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        metadata = {"date": "2026-01-10", "type": "summary"}
        date = generator._extract_date(metadata)

        assert date == "2026-01-10"


def test_extract_date_from_file_path():
    """AC: ファイルパス内の日付を抽出（YYYY-MM-DD形式）"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        metadata = {"file": "01_diary/2026/2026-01-10.md", "type": "summary"}
        date = generator._extract_date(metadata)

        assert date == "2026-01-10"


def test_extract_date_from_created_at():
    """AC: created_atキーから日付を抽出"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        metadata = {"created_at": "2026-01-09", "type": "chunk"}
        date = generator._extract_date(metadata)

        assert date == "2026-01-09"


def test_extract_date_returns_none_when_no_date():
    """AC: 日付が見つからない場合はNoneを返す"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        metadata = {"type": "summary", "seq": 1}
        date = generator._extract_date(metadata)

        assert date is None


def test_extract_date_priority():
    """追加テスト: 複数の日付キーがある場合の優先順位（date > created_at > file）"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        metadata = {
            "date": "2026-01-10",
            "created_at": "2026-01-09",
            "file": "01_diary/2026/2026-01-08.md"
        }
        date = generator._extract_date(metadata)

        # dateキーが最優先
        assert date == "2026-01-10"


def test_generate_report_includes_date_info():
    """AC: 抽出した日付情報をレポートプロンプトに含めること"""
    persona_content = "報告：Pod201"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary", "date": "2026-01-10"}}
    ]

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：2026-01-10のデータを分析"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        _ = generator.generate_report(search_results)

        # Verify that date info is included in the prompt
        call_args = mock_ollama.generate.call_args
        prompt = call_args[1]["prompt"]

        # Date should appear somewhere in the prompt
        assert "2026-01-10" in prompt or "date" in prompt.lower()


def test_generate_report_continues_without_date():
    """AC: 日付情報がない場合でもレポート生成を継続すること"""
    persona_content = "報告：Pod201"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}}
    ]

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：データ分析完了"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        result = generator.generate_report(search_results)

        # Should still generate report even without date
        assert result == "報告：データ分析完了"
        mock_ollama.generate.assert_called_once()


def test_extract_date_from_complex_file_path():
    """追加テスト: 複雑なファイルパスから日付を抽出"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Different file path patterns
        test_cases = [
            ("01_diary/2026/2026-01-10.md", "2026-01-10"),
            ("02_notes/2025-12-25_memo.md", "2025-12-25"),
            ("07_works/project_2026-01-05.txt", "2026-01-05"),
        ]

        for file_path, expected_date in test_cases:
            metadata = {"file": file_path}
            date = generator._extract_date(metadata)
            assert date == expected_date, f"Failed for {file_path}"


def test_extract_date_handles_invalid_format():
    """追加テスト: 無効な日付フォーマットの処理"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        metadata = {"file": "notes/invalid-date.md", "type": "summary"}
        date = generator._extract_date(metadata)

        # Should return None for invalid format
        assert date is None
