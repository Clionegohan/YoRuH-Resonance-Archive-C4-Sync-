"""
Test for Subtask 002-02-06: ChromaDB類似検索実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.phase2_realtime_analysis.similarity_searcher import SimilaritySearcher


def test_searcher_class_exists():
    """AC: SimilaritySearcherクラスを提供すること"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    assert searcher is not None


def test_search_level1_method_exists():
    """AC: search_level1()メソッドを提供すること"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    assert hasattr(searcher, 'search_level1')
    assert callable(searcher.search_level1)


def test_search_level2_method_exists():
    """AC: search_level2()メソッドを提供すること"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    assert hasattr(searcher, 'search_level2')
    assert callable(searcher.search_level2)


def test_search_level1_filters_summary():
    """AC: search_level1()はtype="summary"のmetadataフィルタを適用すること"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    # Mock ChromaDB query response
    mock_collection.query.return_value = {
        "ids": [["id1", "id2"]],
        "distances": [[0.1, 0.2]],
        "metadatas": [[{"type": "summary"}, {"type": "summary"}]]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    _ = searcher.search_level1(query_vector)

    # Verify query was called with correct parameters
    mock_collection.query.assert_called_once()
    call_args = mock_collection.query.call_args

    assert call_args[1]["where"] == {"type": "summary"}
    assert call_args[1]["n_results"] == 5


def test_search_level1_returns_results():
    """AC: search_level1()は検索結果リストを返すこと"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    mock_collection.query.return_value = {
        "ids": [["id1", "id2", "id3"]],
        "distances": [[0.1, 0.2, 0.3]],
        "metadatas": [[
            {"type": "summary", "file": "file1.md"},
            {"type": "summary", "file": "file2.md"},
            {"type": "summary", "file": "file3.md"}
        ]]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    results = searcher.search_level1(query_vector)

    assert len(results) == 3
    assert results[0]["id"] == "id1"
    assert results[0]["distance"] == 0.1
    assert results[0]["metadata"]["type"] == "summary"


def test_search_level2_filters_chunk():
    """AC: search_level2()はtype="chunk"のmetadataフィルタを適用すること"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    mock_collection.query.return_value = {
        "ids": [["id1", "id2"]],
        "distances": [[0.1, 0.2]],
        "metadatas": [[{"type": "chunk"}, {"type": "chunk"}]]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    _ = searcher.search_level2(query_vector)

    # Verify query was called with correct parameters
    mock_collection.query.assert_called_once()
    call_args = mock_collection.query.call_args

    assert call_args[1]["where"] == {"type": "chunk"}
    assert call_args[1]["n_results"] == 10


def test_search_level2_returns_results():
    """AC: search_level2()は検索結果リストを返すこと"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    mock_collection.query.return_value = {
        "ids": [["chunk1", "chunk2"]],
        "distances": [[0.15, 0.25]],
        "metadatas": [[
            {"type": "chunk", "seq": 1},
            {"type": "chunk", "seq": 2}
        ]]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    results = searcher.search_level2(query_vector)

    assert len(results) == 2
    assert results[0]["id"] == "chunk1"
    assert results[0]["distance"] == 0.15
    assert results[0]["metadata"]["type"] == "chunk"


def test_search_level1_none_vector_returns_empty():
    """AC: query_vectorがNoneの場合、空リストを返すこと"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)

    results = searcher.search_level1(None)

    assert results == []


def test_search_level1_empty_vector_returns_empty():
    """AC: query_vectorが空の場合、空リストを返すこと"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)

    results = searcher.search_level1([])

    assert results == []


def test_search_level2_none_vector_returns_empty():
    """追加テスト: search_level2()でquery_vectorがNoneの場合、空リストを返すこと"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)

    results = searcher.search_level2(None)

    assert results == []


def test_search_level2_empty_vector_returns_empty():
    """追加テスト: search_level2()でquery_vectorが空の場合、空リストを返すこと"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)

    results = searcher.search_level2([])

    assert results == []


def test_search_level1_handles_error():
    """AC: 検索失敗時、エラーログを出力し空リストを返すこと"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    # Simulate ChromaDB error
    mock_collection.query.side_effect = Exception("ChromaDB error")

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    from unittest.mock import patch
    with patch('src.phase2_realtime_analysis.similarity_searcher.logger') as mock_logger:
        results = searcher.search_level1(query_vector)

        assert results == []
        # Verify error was logged
        assert mock_logger.exception.called


def test_search_level2_handles_error():
    """追加テスト: search_level2()で検索失敗時、エラーログを出力し空リストを返すこと"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    # Simulate ChromaDB error
    mock_collection.query.side_effect = Exception("ChromaDB error")

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    from unittest.mock import patch
    with patch('src.phase2_realtime_analysis.similarity_searcher.logger') as mock_logger:
        results = searcher.search_level2(query_vector)

        assert results == []
        # Verify error was logged
        assert mock_logger.exception.called


def test_search_level1_empty_results():
    """追加テスト: 検索結果が0件の場合、空リストを返すこと"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    # Empty results
    mock_collection.query.return_value = {
        "ids": [[]],
        "distances": [[]],
        "metadatas": [[]]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    results = searcher.search_level1(query_vector)

    assert results == []


def test_search_level2_empty_results():
    """追加テスト: search_level2()で検索結果が0件の場合、空リストを返すこと"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    # Empty results
    mock_collection.query.return_value = {
        "ids": [[]],
        "distances": [[]],
        "metadatas": [[]]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    results = searcher.search_level2(query_vector)

    assert results == []


def test_chromadb_indexer_injection():
    """追加テスト: ChromaDBIndexerがコンストラクタで注入されること"""
    mock_indexer = Mock()
    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)

    assert searcher.chromadb_indexer is mock_indexer


def test_search_level1_top_k_5():
    """追加テスト: Level 1検索はtop_k=5であること"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    mock_collection.query.return_value = {
        "ids": [["id1", "id2", "id3", "id4", "id5"]],
        "distances": [[0.1, 0.2, 0.3, 0.4, 0.5]],
        "metadatas": [[{"type": "summary"}] * 5]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    results = searcher.search_level1(query_vector)

    # Verify n_results=5
    call_args = mock_collection.query.call_args
    assert call_args[1]["n_results"] == 5

    # Verify we get up to 5 results
    assert len(results) == 5


def test_search_level2_top_k_10():
    """追加テスト: Level 2検索はtop_k=10であること"""
    mock_indexer = Mock()
    mock_collection = MagicMock()
    mock_indexer.collection = mock_collection

    mock_collection.query.return_value = {
        "ids": [["id" + str(i) for i in range(10)]],
        "distances": [[0.1 * i for i in range(10)]],
        "metadatas": [[{"type": "chunk"}] * 10]
    }

    searcher = SimilaritySearcher(chromadb_indexer=mock_indexer)
    query_vector = [0.1] * 1024

    results = searcher.search_level2(query_vector)

    # Verify n_results=10
    call_args = mock_collection.query.call_args
    assert call_args[1]["n_results"] == 10

    # Verify we get up to 10 results
    assert len(results) == 10
