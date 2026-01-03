"""
Test for Subtask 002-01-07: ChromaDBインデックス化実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
import tempfile
import shutil
from src.phase1_archive_sync.chromadb_indexer import ChromaDBIndexer
from src.phase1_archive_sync.multilevel_vectorizer import EmbeddingRecord


@pytest.fixture
def temp_db_dir():
    """一時的なDBディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def indexer(temp_db_dir):
    """ChromaDBIndexerインスタンスを作成"""
    return ChromaDBIndexer(persist_directory=temp_db_dir)


@pytest.fixture
def sample_embedding_records():
    """テスト用のEmbeddingRecordリストを作成"""
    records = []
    for i in range(5):
        record = EmbeddingRecord(
            id=f"test.md#{i}#abcd1234",
            text=f"Test chunk {i}",
            vector=[0.1 * (i + 1)] * 1024,  # Slightly different vectors
            metadata={
                'level': 2,
                'chunk_id': f"test.md#{i}#abcd1234",
                'type': 'chunk',
                'file': 'test.md',
                'date': '2026-01-03',
                'seq': i,
                'char_count': 100,
                'content_hash': f'abcd123{i}' * 8,
                'created_at': '2026-01-03T00:00:00Z',
                'updated_at': '2026-01-03T00:00:00Z'
            }
        )
        records.append(record)
    return records


def test_add_vectors_batch_method_exists(indexer):
    """AC: バッチ処理でChromaDBに挿入すること - メソッドが存在すること"""
    assert hasattr(indexer, 'add_vectors_batch')
    assert callable(indexer.add_vectors_batch)


def test_add_vectors_batch_accepts_embedding_records(indexer, sample_embedding_records):
    """AC: バッチ処理でChromaDBに挿入すること - EmbeddingRecordリストを受け取ること"""
    result = indexer.add_vectors_batch(sample_embedding_records)

    # Should return result dictionary
    assert isinstance(result, dict)
    assert 'success' in result
    assert 'failed' in result
    assert 'errors' in result


def test_add_vectors_batch_returns_success_count(indexer, sample_embedding_records):
    """AC: バッチ処理 - 成功件数を返すこと"""
    result = indexer.add_vectors_batch(sample_embedding_records)

    assert result['success'] == len(sample_embedding_records)
    assert result['failed'] == 0
    assert len(result['errors']) == 0


def test_add_vectors_batch_stores_all_vectors(indexer, sample_embedding_records):
    """AC: バッチ処理でChromaDBに挿入すること - 全てのベクトルが保存されること"""
    indexer.add_vectors_batch(sample_embedding_records)

    # Verify all vectors are stored
    collection = indexer.collection
    stored_count = collection.count()
    assert stored_count == len(sample_embedding_records)


def test_add_vectors_batch_preserves_metadata(indexer, sample_embedding_records):
    """AC: 挿入時にメタデータを付与すること - 全てのメタデータが保存されること"""
    indexer.add_vectors_batch(sample_embedding_records)

    # Verify metadata is preserved by querying
    for record in sample_embedding_records:
        results = indexer.search(query_vector=record.vector, top_k=1)
        assert len(results) > 0
        stored_metadata = results[0]['metadata']

        # Check all metadata fields are preserved
        for key, value in record.metadata.items():
            assert key in stored_metadata
            assert stored_metadata[key] == value


def test_add_vectors_batch_handles_empty_list(indexer):
    """AC: エラーハンドリング - 空リストを処理できること"""
    result = indexer.add_vectors_batch([])

    assert result['success'] == 0
    assert result['failed'] == 0
    assert len(result['errors']) == 0


def test_add_vectors_batch_validates_vector_dimension(indexer):
    """AC: エラーハンドリング - ベクトル次元を検証すること（1024次元）"""
    invalid_record = EmbeddingRecord(
        id="invalid#0#12345678",
        text="Invalid vector",
        vector=[0.1] * 512,  # Wrong dimension (should be 1024)
        metadata={'type': 'chunk', 'file': 'test.md', 'level': 2, 'chunk_id': 'invalid#0#12345678',
                  'date': '2026-01-03', 'seq': 0, 'char_count': 100, 'content_hash': '12345678' * 8,
                  'created_at': '2026-01-03T00:00:00Z', 'updated_at': '2026-01-03T00:00:00Z'}
    )

    result = indexer.add_vectors_batch([invalid_record])

    # Should mark as failed, not raise exception
    assert result['success'] == 0
    assert result['failed'] == 1
    assert len(result['errors']) > 0
    assert 'dimension' in result['errors'][0].lower() or '1024' in result['errors'][0]


def test_add_vectors_batch_partial_failure_continues(indexer, sample_embedding_records):
    """AC: エラーハンドリング - 部分的失敗でも処理続行すること"""
    # Mix valid and invalid records
    invalid_record = EmbeddingRecord(
        id="invalid#0#12345678",
        text="Invalid vector",
        vector=[0.1] * 512,  # Wrong dimension
        metadata={'type': 'chunk', 'file': 'test.md', 'level': 2, 'chunk_id': 'invalid#0#12345678',
                  'date': '2026-01-03', 'seq': 0, 'char_count': 100, 'content_hash': '12345678' * 8,
                  'created_at': '2026-01-03T00:00:00Z', 'updated_at': '2026-01-03T00:00:00Z'}
    )

    mixed_records = sample_embedding_records[:2] + [invalid_record] + sample_embedding_records[2:]

    result = indexer.add_vectors_batch(mixed_records)

    # Should continue processing valid records
    assert result['success'] == len(sample_embedding_records)
    assert result['failed'] == 1
    assert len(result['errors']) == 1


def test_add_vectors_batch_with_custom_batch_size(indexer, sample_embedding_records):
    """AC: バッチ処理 - batch_sizeパラメータを受け取ること"""
    # Should accept batch_size parameter
    result = indexer.add_vectors_batch(sample_embedding_records, batch_size=2)

    assert result['success'] == len(sample_embedding_records)

    # Verify all vectors are still stored
    stored_count = indexer.collection.count()
    assert stored_count == len(sample_embedding_records)


def test_add_vectors_batch_default_batch_size_100(indexer):
    """AC: バッチ処理 - デフォルトバッチサイズは100であること"""
    # Create 150 records to test batching
    large_batch = []
    for i in range(150):
        record = EmbeddingRecord(
            id=f"large#{i}#abcd1234",
            text=f"Large batch {i}",
            vector=[0.01 * (i + 1)] * 1024,
            metadata={
                'level': 2,
                'chunk_id': f"large#{i}#abcd1234",
                'type': 'chunk',
                'file': 'large.md',
                'date': '2026-01-03',
                'seq': i,
                'char_count': 100,
                'content_hash': f'large{i:03d}' * 8,
                'created_at': '2026-01-03T00:00:00Z',
                'updated_at': '2026-01-03T00:00:00Z'
            }
        )
        large_batch.append(record)

    result = indexer.add_vectors_batch(large_batch)

    assert result['success'] == 150
    assert indexer.collection.count() == 150


def test_add_vectors_batch_shows_progress_when_enabled(indexer, sample_embedding_records, capsys):
    """AC: 進捗を表示すること - show_progress=Trueで進捗バーが表示されること"""
    indexer.add_vectors_batch(sample_embedding_records, show_progress=True)

    # Check that progress output was produced
    captured = capsys.readouterr()
    # tqdm writes to stderr by default
    assert len(captured.err) > 0


def test_add_vectors_batch_no_progress_when_disabled(indexer, sample_embedding_records, capsys):
    """AC: 進捗を表示すること - show_progress=Falseで進捗バーを非表示にできること"""
    indexer.add_vectors_batch(sample_embedding_records, show_progress=False)

    # Should not show progress
    captured = capsys.readouterr()
    # No tqdm output expected
    assert 'it/s' not in captured.err and '%' not in captured.err


def test_add_vectors_batch_persists_data(temp_db_dir, sample_embedding_records):
    """AC: バッチ処理 - データが永続化されること"""
    # Create indexer and add vectors
    indexer1 = ChromaDBIndexer(persist_directory=temp_db_dir)
    indexer1.add_vectors_batch(sample_embedding_records)

    # Create new indexer instance (simulating restart)
    indexer2 = ChromaDBIndexer(persist_directory=temp_db_dir)

    # Verify data persisted
    stored_count = indexer2.collection.count()
    assert stored_count == len(sample_embedding_records)
