"""
Test for Subtask 002-03-02: Ollama LLMクライアント実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from src.phase3_pod_report.pod201_report_generator import Pod201ReportGenerator


def test_generator_class_exists():
    """AC: Pod201ReportGeneratorクラスを提供すること"""
    mock_ollama = Mock()
    generator = Pod201ReportGenerator(ollama_client=mock_ollama)
    assert generator is not None


def test_generate_report_method_exists():
    """AC: generate_report()メソッドを提供すること"""
    mock_ollama = Mock()
    generator = Pod201ReportGenerator(ollama_client=mock_ollama)
    assert hasattr(generator, 'generate_report')
    assert callable(generator.generate_report)


def test_loads_persona_from_file():
    """AC: `.pod201/persona.txt` からPod201ペルソナプロンプトを読み込むこと"""
    persona_content = "報告：Pod201ペルソナテスト"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        assert generator.persona_prompt == persona_content


def test_uses_ollama_client_for_generation():
    """AC: OllamaClientを使用してllama3.1:8bモデルでテキスト生成を行うこと"""
    persona_content = "報告：Pod201ペルソナ"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary", "file": "test.md"}}
    ]

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：レポート生成完了"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        result = generator.generate_report(search_results)

        # Verify OllamaClient.generate was called
        mock_ollama.generate.assert_called_once()
        call_args = mock_ollama.generate.call_args

        # Verify model is llama3.1:8b
        assert call_args[1]["model"] == "llama3.1:8b"


def test_uses_persona_as_system_prompt():
    """AC: システムプロンプトとしてPod201ペルソナを使用すること"""
    persona_content = "報告：Pod201ペルソナ定義"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}}
    ]

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：テスト"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        _ = generator.generate_report(search_results)

        # Verify persona is included in the prompt
        call_args = mock_ollama.generate.call_args
        prompt = call_args[1]["prompt"]
        assert persona_content in prompt


def test_returns_generated_report():
    """AC: generate_report()は生成されたレポートテキストを返すこと"""
    persona_content = "報告：Pod201"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}}
    ]
    expected_report = "報告：レポート生成完了。類似検索結果を分析。"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = expected_report

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        result = generator.generate_report(search_results)

        assert result == expected_report


def test_returns_none_on_generation_error():
    """AC: 生成エラー時にNoneを返すこと"""
    persona_content = "報告：Pod201"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}}
    ]

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = None  # Simulate error

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        result = generator.generate_report(search_results)

        assert result is None


def test_handles_empty_search_results():
    """AC: 空の検索結果の場合は適切なメッセージを生成すること"""
    persona_content = "報告：Pod201"
    search_results = []

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：該当データ無し。検索結果は空。"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        result = generator.generate_report(search_results)

        # Should still generate a report (Pod style message)
        assert result is not None
        mock_ollama.generate.assert_called_once()


def test_ollama_client_injection():
    """追加テスト: OllamaClientがコンストラクタで注入されること"""
    mock_ollama = Mock()

    with patch("builtins.open", mock_open(read_data="persona")):
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        assert generator.ollama_client is mock_ollama


def test_formats_search_results_in_prompt():
    """追加テスト: 検索結果がプロンプトに適切にフォーマットされること"""
    persona_content = "報告：Pod201"
    search_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary", "file": "test1.md"}},
        {"id": "id2", "distance": 0.2, "metadata": {"type": "chunk", "seq": 1}}
    ]

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        mock_ollama.generate.return_value = "報告：完了"

        generator = Pod201ReportGenerator(ollama_client=mock_ollama)
        _ = generator.generate_report(search_results)

        # Verify search results are formatted in prompt
        call_args = mock_ollama.generate.call_args
        prompt = call_args[1]["prompt"]

        # Check that result info appears in prompt
        assert "id1" in prompt or "test1.md" in prompt


def test_persona_file_not_found_raises_error():
    """追加テスト: ペルソナファイルが存在しない場合はエラー"""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        mock_ollama = Mock()

        with pytest.raises(FileNotFoundError):
            Pod201ReportGenerator(ollama_client=mock_ollama)
