"""
Test for Subtask 002-02-05: 差分抽出とベクトル化

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from unittest.mock import Mock, patch
from src.phase2_realtime_analysis.diff_extractor import DiffExtractor


def test_extractor_class_exists():
    """AC: DiffExtractorクラスを提供すること"""
    extractor = DiffExtractor()
    assert extractor is not None


def test_extract_diff_method_exists():
    """AC: extract_diff()メソッドを提供すること"""
    extractor = DiffExtractor()
    assert hasattr(extractor, 'extract_diff')
    assert callable(extractor.extract_diff)


def test_vectorize_diff_method_exists():
    """AC: vectorize_diff()メソッドを提供すること"""
    extractor = DiffExtractor()
    assert hasattr(extractor, 'vectorize_diff')
    assert callable(extractor.vectorize_diff)


def test_extract_diff_when_previous_is_none():
    """AC: previous_textがNoneの場合、current_text全体を差分とする"""
    extractor = DiffExtractor()

    current_text = "This is new content"
    diff = extractor.extract_diff(previous_text=None, current_text=current_text)

    assert diff == current_text


def test_extract_diff_when_previous_is_empty():
    """AC: previous_textが空文字列の場合、current_text全体を差分とする"""
    extractor = DiffExtractor()

    current_text = "This is new content"
    diff = extractor.extract_diff(previous_text="", current_text=current_text)

    assert diff == current_text


def test_extract_diff_addition():
    """AC: previous_textが存在する場合、追加部分（current_text[len(previous_text):]）を差分とする"""
    extractor = DiffExtractor()

    previous_text = "Hello"
    current_text = "Hello World"

    diff = extractor.extract_diff(previous_text=previous_text, current_text=current_text)

    assert diff == " World"


def test_extract_diff_large_addition():
    """AC: 大きな追加の場合も正しく差分を抽出すること"""
    extractor = DiffExtractor()

    previous_text = "Initial text.\n\n"
    additional_text = "This is a long paragraph that was added.\nWith multiple lines.\n"
    current_text = previous_text + additional_text

    diff = extractor.extract_diff(previous_text=previous_text, current_text=current_text)

    assert diff == additional_text


def test_extract_diff_deletion_returns_empty():
    """AC: 削除（current_textがprevious_textより短い）の場合、空文字列を返す"""
    extractor = DiffExtractor()

    previous_text = "This is a long text"
    current_text = "Short"

    diff = extractor.extract_diff(previous_text=previous_text, current_text=current_text)

    assert diff == ""


def test_extract_diff_no_change_returns_empty():
    """追加テスト: 変更がない場合、空文字列を返す"""
    extractor = DiffExtractor()

    text = "Same text"
    diff = extractor.extract_diff(previous_text=text, current_text=text)

    assert diff == ""


def test_vectorize_diff_returns_vector():
    """AC: vectorize_diff()は1024次元ベクトルを返すこと"""
    mock_client = Mock()
    mock_client.embed.return_value = [0.1] * 1024

    extractor = DiffExtractor(ollama_client=mock_client)

    diff_text = "This is diff text"
    vector = extractor.vectorize_diff(diff_text)

    assert vector is not None
    assert len(vector) == 1024
    mock_client.embed.assert_called_once_with(
        model="mxbai-embed-large",
        text=diff_text
    )


def test_vectorize_diff_empty_text_returns_none():
    """AC: 差分テキストが空の場合、vectorize_diff()はNoneを返すこと"""
    extractor = DiffExtractor()

    vector = extractor.vectorize_diff("")

    assert vector is None


def test_vectorize_diff_whitespace_only_returns_none():
    """追加テスト: 空白のみの場合、Noneを返すこと"""
    extractor = DiffExtractor()

    vector = extractor.vectorize_diff("   \n\t  ")

    assert vector is None


def test_vectorize_diff_retry_on_failure():
    """AC: リトライロジック実装（最大3回、exponential backoff）"""
    mock_client = Mock()
    # 1回目と2回目は失敗、3回目で成功
    mock_client.embed.side_effect = [
        Exception("Network error"),
        Exception("Timeout"),
        [0.1] * 1024
    ]

    extractor = DiffExtractor(ollama_client=mock_client)

    vector = extractor.vectorize_diff("Test text")

    assert vector is not None
    assert len(vector) == 1024
    assert mock_client.embed.call_count == 3


def test_vectorize_diff_returns_none_after_max_retries():
    """AC: ベクトル化に失敗した場合、エラーログを出力しNoneを返すこと"""
    mock_client = Mock()
    # すべて失敗
    mock_client.embed.side_effect = Exception("Persistent error")

    extractor = DiffExtractor(ollama_client=mock_client)

    with patch('src.phase2_realtime_analysis.diff_extractor.logger') as mock_logger:
        vector = extractor.vectorize_diff("Test text")

        assert vector is None
        assert mock_client.embed.call_count == 3  # 最大リトライ回数
        # エラーログが出力されること
        assert mock_logger.error.called


def test_vectorize_diff_invalid_dimension_retries():
    """追加テスト: 無効な次元のベクトルの場合、リトライすること"""
    mock_client = Mock()
    # 無効な次元、その後成功
    mock_client.embed.side_effect = [
        [0.1] * 512,  # 無効な次元
        [0.1] * 1024  # 正しい次元
    ]

    extractor = DiffExtractor(ollama_client=mock_client)

    with patch('src.phase2_realtime_analysis.diff_extractor.logger') as mock_logger:
        vector = extractor.vectorize_diff("Test text")

        assert vector is not None
        assert len(vector) == 1024
        assert mock_client.embed.call_count == 2
        # 警告ログが出力されること
        assert mock_logger.warning.called


def test_vectorize_diff_exponential_backoff():
    """AC: exponential backoffでリトライすること"""
    mock_client = Mock()
    mock_client.embed.side_effect = [
        Exception("Error 1"),
        Exception("Error 2"),
        [0.1] * 1024
    ]

    extractor = DiffExtractor(ollama_client=mock_client)

    import time
    with patch('time.sleep') as mock_sleep:
        vector = extractor.vectorize_diff("Test text")

        assert vector is not None
        # 2回のリトライで2回のsleep（1秒、2秒）
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1


def test_extract_and_vectorize_integration():
    """統合テスト: 差分抽出とベクトル化の一連の流れ"""
    mock_client = Mock()
    mock_client.embed.return_value = [0.5] * 1024

    extractor = DiffExtractor(ollama_client=mock_client)

    previous_text = "Initial content"
    current_text = "Initial content\nNew paragraph added"

    # 差分抽出
    diff = extractor.extract_diff(previous_text=previous_text, current_text=current_text)
    assert diff == "\nNew paragraph added"

    # ベクトル化
    vector = extractor.vectorize_diff(diff)
    assert vector is not None
    assert len(vector) == 1024


def test_ollama_client_default_initialization():
    """追加テスト: OllamaClientがデフォルトで初期化されること"""
    extractor = DiffExtractor()
    assert extractor.ollama_client is not None


def test_ollama_client_custom_initialization():
    """追加テスト: カスタムOllamaClientを受け取れること"""
    custom_client = Mock()
    extractor = DiffExtractor(ollama_client=custom_client)
    assert extractor.ollama_client is custom_client
