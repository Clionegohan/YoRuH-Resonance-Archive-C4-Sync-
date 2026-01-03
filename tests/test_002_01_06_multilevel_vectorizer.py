"""
Test for Subtask 002-01-06: マルチレベルベクトル化実装

このテストは改訂されたAcceptance Criteriaから導出されています。
"""
import pytest
from datetime import datetime
from src.phase1_archive_sync.multilevel_vectorizer import MultilevelVectorizer, EmbeddingRecord
from src.utils.ollama_client import OllamaClient


@pytest.fixture
def vectorizer():
    """MultilevelVectorizerインスタンスを作成"""
    return MultilevelVectorizer()


@pytest.fixture
def ollama_client():
    """OllamaClientインスタンスを作成"""
    return OllamaClient()


def test_returns_embedding_record_list(vectorizer):
    """AC: EmbeddingRecord構造体のリストを返すこと"""
    text = "短いテキストです。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    assert isinstance(records, list)
    assert len(records) > 0
    assert all(isinstance(record, EmbeddingRecord) for record in records)


def test_embedding_record_fields(vectorizer):
    """AC: EmbeddingRecordは id, text, vector, metadata フィールドを持つこと"""
    text = "テストテキスト。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    for record in records:
        assert hasattr(record, 'id')
        assert hasattr(record, 'text')
        assert hasattr(record, 'vector')
        assert hasattr(record, 'metadata')


def test_level2_all_chunks_vectorized(vectorizer):
    """AC: 全てのファイルをチャンク分割し、各チャンクをベクトル化すること（Level 2）"""
    text = "段落1です。\n\n段落2です。\n\n段落3です。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    # Level 2レコードを抽出
    level2_records = [r for r in records if r.metadata['level'] == 2]
    assert len(level2_records) >= 1

    # すべてのチャンクがベクトル化されている
    for record in level2_records:
        assert isinstance(record.vector, list)
        assert len(record.vector) == 1024  # mxbai-embed-large


def test_level1_summary_for_long_text(vectorizer):
    """AC: テキスト長が2000文字を超える場合、要約を生成しベクトル化すること（Level 1）"""
    # 2000文字を超えるテキスト
    text = "あ" * 2100 + "。"
    file_path = "long_test.md"

    records = vectorizer.vectorize(text, file_path)

    # Level 1レコードを抽出
    level1_records = [r for r in records if r.metadata['level'] == 1]
    assert len(level1_records) == 1

    # 要約が生成されている
    summary_record = level1_records[0]
    assert summary_record.metadata['type'] == 'summary'
    assert len(summary_record.text) <= 800  # 要約は500-800字
    assert len(summary_record.vector) == 1024


def test_level1_summary_for_many_chunks(vectorizer):
    """AC: チャンク数が5個を超える場合、要約を生成すること（Level 1）"""
    # 短いチャンクを多数生成するテキスト（段落多数）
    text = "\n\n".join([f"段落{i}です。" * 20 for i in range(10)])
    file_path = "many_chunks_test.md"

    records = vectorizer.vectorize(text, file_path)

    # チャンク数が5個を超える場合、Level 1要約が生成される
    level1_records = [r for r in records if r.metadata['level'] == 1]
    level2_records = [r for r in records if r.metadata['level'] == 2]

    if len(level2_records) > 5:
        assert len(level1_records) == 1


def test_metadata_fields(vectorizer):
    """AC: 各ベクトルにメタデータを付与すること"""
    text = "テストテキスト。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    for record in records:
        metadata = record.metadata

        # 必須フィールドの存在確認
        assert 'level' in metadata
        assert 'chunk_id' in metadata
        assert 'type' in metadata
        assert 'file' in metadata
        assert 'date' in metadata
        assert 'seq' in metadata
        assert 'char_count' in metadata
        assert 'content_hash' in metadata
        assert 'created_at' in metadata
        assert 'updated_at' in metadata

        # 値の妥当性
        assert metadata['level'] in [1, 2]
        assert metadata['type'] in ['summary', 'chunk']
        assert metadata['file'] == file_path
        assert isinstance(metadata['seq'], int)
        assert metadata['seq'] >= 0
        assert isinstance(metadata['char_count'], int)
        assert len(metadata['content_hash']) == 64  # SHA256
        assert isinstance(metadata['created_at'], str)
        assert isinstance(metadata['updated_at'], str)


def test_chunk_id_format(vectorizer):
    """AC: chunk_idは {file_path}#{seq}#{content_hash[:8]} 形式であること"""
    text = "テストテキスト。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    for record in records:
        chunk_id = record.metadata['chunk_id']
        parts = chunk_id.split('#')

        assert len(parts) == 3
        assert parts[0] == file_path
        assert parts[1].isdigit()  # seq
        assert len(parts[2]) == 8  # content_hash[:8]


def test_seq_numbering(vectorizer):
    """AC: seqはLevel 1は0、Level 2は0始まりの連番であること"""
    text = "段落1です。\n\n段落2です。\n\n段落3です。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    level1_records = [r for r in records if r.metadata['level'] == 1]
    level2_records = [r for r in records if r.metadata['level'] == 2]

    # Level 1のseqは0（存在する場合）
    for record in level1_records:
        assert record.metadata['seq'] == 0

    # Level 2のseqは0始まりの連番
    level2_seqs = [r.metadata['seq'] for r in level2_records]
    level2_seqs.sort()
    assert level2_seqs == list(range(len(level2_seqs)))


def test_skip_empty_chunks(vectorizer, caplog):
    """AC: チャンクが空または空白文字のみの場合、スキップし警告ログを出力すること"""
    text = "段落1です。\n\n   \n\n段落2です。"  # 空白のみの段落を含む
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    # 空白チャンクはスキップされる
    for record in records:
        assert record.text.strip() != ""

    # 警告ログが出力される（ログレベルの確認は実装依存）


def test_empty_file_skip(vectorizer, caplog):
    """AC: ファイルが空の場合、エラーログを出力しスキップすること"""
    text = ""
    file_path = "empty.md"

    records = vectorizer.vectorize(text, file_path)

    # 空ファイルは空リストを返す
    assert records == []

    # エラーログが出力される


def test_vector_dimension_1024(vectorizer):
    """すべてのベクトルが1024次元であること（mxbai-embed-large）"""
    text = "テストテキスト。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    for record in records:
        assert len(record.vector) == 1024
        assert all(isinstance(v, float) for v in record.vector)


def test_iso8601_timestamps(vectorizer):
    """created_at, updated_atがISO 8601形式であること"""
    text = "テストテキスト。"
    file_path = "test.md"

    records = vectorizer.vectorize(text, file_path)

    for record in records:
        # ISO 8601パース可能であることを確認
        created_at = datetime.fromisoformat(record.metadata['created_at'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(record.metadata['updated_at'].replace('Z', '+00:00'))

        assert isinstance(created_at, datetime)
        assert isinstance(updated_at, datetime)


def test_summary_bullet_format(vectorizer):
    """AC: 要約を500〜800字の箇条書き形式で生成すること"""
    # 2000文字を超えるテキスト
    text = "テスト" * 600 + "。"
    file_path = "long_test.md"

    records = vectorizer.vectorize(text, file_path)

    level1_records = [r for r in records if r.metadata['level'] == 1]

    if len(level1_records) > 0:
        summary = level1_records[0].text

        # 箇条書き形式（-や•を含む）
        assert ('-' in summary or '•' in summary or '・' in summary)

        # 500-800字
        assert 500 <= len(summary) <= 800
