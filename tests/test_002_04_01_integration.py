"""
Test for Subtask 002-04-01: コンポーネント統合実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
from unittest.mock import Mock, patch
import pytest
from src.resonance_archive_system import ResonanceArchiveSystem


def test_system_class_exists():
    """AC: ResonanceArchiveSystemクラスを提供すること"""
    # Should be able to instantiate with mocked dependencies
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    assert system is not None
    assert hasattr(system, 'indexer')
    assert hasattr(system, 'watcher')
    assert hasattr(system, 'pipeline')


def test_initialize_method_exists():
    """AC: 初期化処理を実装すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    assert hasattr(system, 'initialize')
    assert callable(system.initialize)


def test_initialize_calls_indexer():
    """AC: 初期化処理でChromaDBIndexerのindex_vault()を呼び出すこと"""
    mock_indexer = Mock()
    mock_indexer.index_vault = Mock(return_value={'indexed': 100})
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    result = system.initialize()

    mock_indexer.index_vault.assert_called_once()
    assert result is not None


def test_start_monitoring_method_exists():
    """AC: 監視開始処理を実装すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    assert hasattr(system, 'start_monitoring')
    assert callable(system.start_monitoring)


def test_start_monitoring_starts_watcher():
    """AC: 監視開始処理でFileWatcherを起動すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_watcher.start = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    system.start_monitoring()

    mock_watcher.start.assert_called_once()


def test_search_method_exists():
    """AC: 手動検索処理を実装すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    assert hasattr(system, 'search')
    assert callable(system.search)


def test_search_returns_report():
    """AC: 手動検索処理でPod201レポートを生成して返すこと"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()
    mock_pipeline.generate = Mock(return_value="報告：検索結果を分析した。")

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    result = system.search("test query")

    assert result is not None
    assert isinstance(result, str)
    mock_pipeline.generate.assert_called_once()


def test_get_status_method_exists():
    """AC: ステータス確認処理を実装すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    assert hasattr(system, 'get_status')
    assert callable(system.get_status)


def test_get_status_returns_system_state():
    """AC: ステータス確認処理でシステム状態を返すこと"""
    mock_indexer = Mock()
    mock_indexer.get_collection_count = Mock(return_value=100)
    mock_watcher = Mock()
    mock_watcher.is_running = Mock(return_value=True)
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    status = system.get_status()

    assert status is not None
    assert isinstance(status, dict)
    assert 'indexed_count' in status or 'monitoring' in status


def test_shutdown_method_exists():
    """AC: 終了処理を実装すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    assert hasattr(system, 'shutdown')
    assert callable(system.shutdown)


def test_shutdown_stops_watcher():
    """AC: 終了処理でFileWatcherを停止すること"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_watcher.stop = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    system.shutdown()

    mock_watcher.stop.assert_called_once()


def test_error_handling_in_initialize():
    """AC: エラーハンドリングを実装すること - 初期化エラー"""
    mock_indexer = Mock()
    mock_indexer.index_vault = Mock(side_effect=Exception("Index error"))
    mock_watcher = Mock()
    mock_pipeline = Mock()

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    # Should handle error gracefully, not crash
    result = system.initialize()

    # Should return error info or False
    assert result is not None


def test_error_handling_in_search():
    """AC: エラーハンドリングを実装すること - 検索エラー"""
    mock_indexer = Mock()
    mock_watcher = Mock()
    mock_pipeline = Mock()
    mock_pipeline.generate = Mock(side_effect=Exception("Search error"))

    system = ResonanceArchiveSystem(
        indexer=mock_indexer,
        watcher=mock_watcher,
        pipeline=mock_pipeline
    )

    # Should handle error gracefully, return error message
    result = system.search("test query")

    assert result is not None
    assert isinstance(result, str)
    assert "エラー" in result or "失敗" in result or "error" in result.lower()
