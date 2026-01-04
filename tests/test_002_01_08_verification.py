"""
Test for Subtask 002-01-08: インデックス構築の検証

このテストは承認されたAcceptance Criteriaから導出されています。
統合テスト: Phase 1全体のパイプライン検証
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from scripts.build_index import build_index


@pytest.fixture
def temp_vault():
    """テスト用の小規模Vaultを作成（実際の構造に合わせる）"""
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir)

    # Create test directory structure (actual Vault structure)
    # 01_diary/2026/2026-01-01.md
    diary_2026 = vault_path / "01_diary" / "2026"
    diary_2026.mkdir(parents=True)

    # 02_notes/2026/category/note.md
    notes_2026 = vault_path / "02_notes" / "2026" / "tech"
    notes_2026.mkdir(parents=True)

    # 07_works/project/task.md
    works_project = vault_path / "07_works" / "project_a"
    works_project.mkdir(parents=True)

    # 00_templates (should be excluded)
    templates = vault_path / "00_templates"
    templates.mkdir()

    # Create test markdown files
    # File 1: Diary entry (short)
    (diary_2026 / "2026-01-01.md").write_text(
        "# 2026年1月1日の日記\n\n今日は新年です。\n\n良い一年になりますように。"
    )

    # File 2: Long note (Level 1 + Level 2)
    long_text = "# 長い技術ノート\n\n" + "\n\n".join([f"段落{i}です。" * 50 for i in range(10)])
    (notes_2026 / "long_note.md").write_text(long_text)

    # File 3: Another diary entry
    (diary_2026 / "2026-01-02.md").write_text(
        "# 2026年1月2日\n\n" + "今日のメモ。\n\n" * 20
    )

    # File 4: Work note
    (works_project / "task_001.md").write_text(
        "# タスク001\n\nプロジェクトAの進捗。\n\n完了予定: 2026-01-15"
    )

    # File 5: Template (should be excluded)
    (templates / "template.md").write_text(
        "This should be excluded from indexing"
    )

    yield str(vault_path)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db_dir():
    """一時的なDBディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_build_index_function_exists():
    """AC: build_index関数が存在すること"""
    assert callable(build_index)


def test_build_index_scans_all_files(temp_vault, temp_db_dir):
    """AC: 全ファイルがスキャンされ、ベクトル化されること"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=False
    )

    # 4 files should be scanned (excluding templates)
    assert result['files_scanned'] == 4
    assert result['files_processed'] == 4


def test_build_index_generates_vectors(temp_vault, temp_db_dir):
    """AC: 生成されたベクトル数が返されること"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=False
    )

    # Should have vectors generated
    assert result['vectors_generated'] > 0
    assert result['level1_count'] >= 0  # May or may not have summaries
    assert result['level2_count'] > 0  # Should always have chunks

    # Total should match
    assert result['vectors_generated'] == result['level1_count'] + result['level2_count']


def test_build_index_returns_statistics(temp_vault, temp_db_dir):
    """AC: 統計情報を返すこと"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=False
    )

    # Check all required fields
    assert 'files_scanned' in result
    assert 'files_processed' in result
    assert 'vectors_generated' in result
    assert 'level1_count' in result
    assert 'level2_count' in result
    assert 'elapsed_time' in result
    assert 'memory_peak_mb' in result

    # Check types
    assert isinstance(result['files_scanned'], int)
    assert isinstance(result['files_processed'], int)
    assert isinstance(result['vectors_generated'], int)
    assert isinstance(result['level1_count'], int)
    assert isinstance(result['level2_count'], int)
    assert isinstance(result['elapsed_time'], float)
    assert isinstance(result['memory_peak_mb'], float)


def test_build_index_measures_time(temp_vault, temp_db_dir):
    """AC: 処理時間を計測すること"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=False
    )

    # Should take some time but not too long
    assert result['elapsed_time'] > 0
    assert result['elapsed_time'] < 300  # Should finish within 5 minutes for test data


def test_build_index_measures_memory(temp_vault, temp_db_dir):
    """AC: メモリ使用量を計測すること（4GB以内）"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=False
    )

    # Memory should be measured
    assert result['memory_peak_mb'] > 0

    # Should be within 4GB limit
    assert result['memory_peak_mb'] < 4096


def test_build_index_enables_search(temp_vault, temp_db_dir):
    """AC: テスト用クエリで検索した場合、類似ベクトルを返すこと"""
    # Build index first
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=False
    )

    assert result['vectors_generated'] > 0

    # Test search functionality
    from src.phase1_archive_sync.chromadb_indexer import ChromaDBIndexer
    from src.utils.ollama_client import OllamaClient

    indexer = ChromaDBIndexer(persist_directory=temp_db_dir)
    ollama = OllamaClient()

    # Create query vector
    query_text = "新年"
    query_vector = ollama.embed(model="mxbai-embed-large", text=query_text)

    # Search
    results = indexer.search(query_vector=query_vector, top_k=3)

    # Should return results
    assert len(results) > 0
    assert 'id' in results[0]
    assert 'metadata' in results[0]


def test_build_index_handles_errors_gracefully(temp_db_dir):
    """AC: エラーハンドリング - 存在しないVaultパスでもクラッシュしないこと"""
    result = build_index(
        vault_root="/nonexistent/path",
        db_path=temp_db_dir,
        show_progress=False
    )

    # Should return zero counts but not crash
    assert result['files_scanned'] == 0
    assert result['files_processed'] == 0
    assert result['vectors_generated'] == 0


def test_build_index_with_progress_display(temp_vault, temp_db_dir, capsys):
    """AC: 進捗表示が有効な場合、出力が生成されること"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=True
    )

    captured = capsys.readouterr()

    # Should have some output (from tqdm or logging)
    assert len(captured.out) > 0 or len(captured.err) > 0


def test_build_index_prints_statistics(temp_vault, temp_db_dir, capsys):
    """AC: 生成されたベクトル数をターミナルに表示すること"""
    result = build_index(
        vault_root=temp_vault,
        db_path=temp_db_dir,
        show_progress=True
    )

    captured = capsys.readouterr()
    combined_output = captured.out + captured.err

    # Should display statistics
    assert 'vectors' in combined_output.lower() or 'files' in combined_output.lower()
