"""
Test for Subtask 002-01-03: ChromaDB初期化と永続化設定

このテストはAcceptance Criteriaから導出されています。
"""
import os
import shutil
import pytest
from src.phase1_archive_sync.chromadb_indexer import ChromaDBIndexer


@pytest.fixture
def clean_chromadb():
    """テスト前後でChromaDBをクリーンアップ"""
    db_path = "./.chroma_db_test"
    # テスト前: クリーンアップ
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    yield db_path

    # テスト後: クリーンアップ
    if os.path.exists(db_path):
        shutil.rmtree(db_path)


def test_chromadb_directory_created(clean_chromadb):
    """AC: ./.chroma_db/ディレクトリが作成されること"""
    indexer = ChromaDBIndexer(persist_directory=clean_chromadb)
    assert os.path.exists(clean_chromadb)
    assert os.path.isdir(clean_chromadb)


def test_chromadb_client_initialized(clean_chromadb):
    """AC: ChromaDBクライアントが初期化されること"""
    indexer = ChromaDBIndexer(persist_directory=clean_chromadb)
    assert indexer.client is not None


def test_collection_created(clean_chromadb):
    """AC: resonance_archiveコレクションが作成されること"""
    indexer = ChromaDBIndexer(persist_directory=clean_chromadb)
    assert indexer.collection is not None
    assert indexer.collection.name == "resonance_archive"


def test_metadata_schema(clean_chromadb):
    """AC: コレクションのメタデータスキーマが適切に定義されること"""
    indexer = ChromaDBIndexer(persist_directory=clean_chromadb)

    # テスト用ベクトル挿入（summaryタイプ）
    test_vector_summary = [0.1] * 1024  # mxbai-embed-largeは1024次元
    indexer.add_vector(
        id="test_summary_1",
        vector=test_vector_summary,
        metadata={
            "type": "summary",
            "file": "test/summary.md",
            "date": "2026-01-03",
            "char_count": 2500
        }
    )

    # テスト用ベクトル挿入（chunkタイプ）
    test_vector_chunk = [0.2] * 1024
    indexer.add_vector(
        id="test_chunk_1",
        vector=test_vector_chunk,
        metadata={
            "type": "chunk",
            "file": "test/chunk.md",
            "date": "2026-01-03",
            "chunk_index": 0
        }
    )

    # メタデータが正しく保存されているか確認
    result = indexer.collection.get(ids=["test_summary_1"])
    assert result["metadatas"][0]["type"] == "summary"
    assert result["metadatas"][0]["file"] == "test/summary.md"
    assert result["metadatas"][0]["date"] == "2026-01-03"
    assert result["metadatas"][0]["char_count"] == 2500


def test_vector_persistence(clean_chromadb):
    """AC: テスト用ベクトルを挿入した場合、システムはベクトルを永続化すること"""
    indexer = ChromaDBIndexer(persist_directory=clean_chromadb)

    # テスト用ベクトル挿入
    test_vector = [0.1] * 1024
    indexer.add_vector(
        id="test_persist_1",
        vector=test_vector,
        metadata={"type": "chunk", "file": "test.md", "date": "2026-01-03", "chunk_index": 0}
    )

    # 検索で取得確認
    results = indexer.search(query_vector=test_vector, top_k=1)
    assert len(results) > 0
    assert results[0]["id"] == "test_persist_1"


def test_vector_persistence_after_restart(clean_chromadb):
    """AC: システムを再起動した場合、以前に挿入したベクトルが取得できること"""
    # 最初のインスタンス: ベクトル挿入
    indexer1 = ChromaDBIndexer(persist_directory=clean_chromadb)
    test_vector = [0.3] * 1024
    indexer1.add_vector(
        id="test_restart_1",
        vector=test_vector,
        metadata={"type": "chunk", "file": "restart_test.md", "date": "2026-01-03", "chunk_index": 0}
    )

    # インスタンスを破棄（システム再起動をシミュレート）
    del indexer1

    # 新しいインスタンス: 永続化されたデータを読み込み
    indexer2 = ChromaDBIndexer(persist_directory=clean_chromadb)

    # 以前のベクトルが取得できるか確認
    result = indexer2.collection.get(ids=["test_restart_1"])
    assert len(result["ids"]) == 1
    assert result["ids"][0] == "test_restart_1"
    assert result["metadatas"][0]["file"] == "restart_test.md"
