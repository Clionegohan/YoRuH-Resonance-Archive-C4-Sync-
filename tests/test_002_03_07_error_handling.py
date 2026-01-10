"""
Test for Subtask 002-03-07: エラーハンドリング実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import logging
from unittest.mock import Mock, patch, mock_open
from src.phase3_pod_report.pod201_report_generator import Pod201ReportGenerator


def test_llm_error_logging(caplog):
    """AC: LLM生成失敗時にエラーログを記録すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        # Simulate LLM generation error
        mock_ollama.generate.side_effect = ConnectionError("Connection failed")

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        with caplog.at_level(logging.ERROR):
            result = generator.generate_report([])

        # Should log the error
        assert len(caplog.records) > 0
        assert any("LLM" in record.message or "生成" in record.message for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)


def test_llm_error_fallback_report():
    """AC: LLM生成失敗時にフォールバックレポートを返すこと"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.side_effect = Exception("LLM error")

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.2, "metadata": {"type": "summary"}}
        ]

        result = generator.generate_report(search_results)

        # Should return a fallback report, not None
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

        # Should include warning message
        assert "警告" in result or "失敗" in result or "エラー" in result

        # Should include search results
        assert "id1" in result


def test_connection_error_handling():
    """AC: Ollama接続エラーを適切に処理すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.side_effect = ConnectionError("Cannot connect to Ollama")

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        result = generator.generate_report([])

        # Should return fallback report
        assert result is not None
        assert isinstance(result, str)

        # Should mention connection error
        assert "接続" in result or "エラー" in result


def test_empty_llm_response_handling():
    """AC: LLMレスポンスが空/Noneの場合にフォールバックすること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()

        # Test various invalid responses
        invalid_responses = [None, "", "   ", "\n\n"]

        for invalid_response in invalid_responses:
            mock_ollama.generate.return_value = invalid_response

            generator = Pod201ReportGenerator(ollama_client=mock_ollama)

            search_results = [{"id": "test", "distance": 0.1, "metadata": {}}]
            result = generator.generate_report(search_results)

            # Should return fallback report
            assert result is not None, f"Failed for response: {repr(invalid_response)}"
            assert isinstance(result, str)
            assert len(result.strip()) > 0


def test_persona_file_not_found_fallback():
    """AC: ペルソナファイル読み込み失敗時にデフォルトペルソナを使用すること"""
    with patch("builtins.open", side_effect=FileNotFoundError("Persona file not found")):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "テスト報告"

        # Should not raise exception, use default persona instead
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Should have some default persona
        assert generator.persona_prompt is not None
        assert isinstance(generator.persona_prompt, str)
        assert len(generator.persona_prompt) > 0


def test_generate_report_always_returns_string():
    """AC: 全エラーケースで有効なレポート文字列を返すこと"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()

        # Test various error scenarios
        error_scenarios = [
            ConnectionError("Connection failed"),
            TimeoutError("Timeout"),
            ValueError("Invalid value"),
            RuntimeError("Runtime error"),
        ]

        for error in error_scenarios:
            mock_ollama.generate.side_effect = error

            generator = Pod201ReportGenerator(ollama_client=mock_ollama)
            result = generator.generate_report([])

            # Should ALWAYS return a valid string, never None
            assert result is not None, f"Returned None for {type(error).__name__}"
            assert isinstance(result, str), f"Not a string for {type(error).__name__}"
            assert len(result) > 0, f"Empty string for {type(error).__name__}"


def test_successful_generation_still_works():
    """追加テスト: 正常系が引き続き動作すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：類似検索結果を分析した。"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
        result = generator.generate_report(search_results)

        # Should return LLM-generated report
        assert result == "報告：類似検索結果を分析した。"
