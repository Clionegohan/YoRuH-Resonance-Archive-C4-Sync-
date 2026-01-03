"""
Test for Subtask 002-01-04: Vaultスキャン実装

このテストはAcceptance Criteriaから導出されています。
"""
import os
import pytest
from src.phase1_archive_sync.vault_scanner import VaultScanner


@pytest.fixture
def vault_root():
    """実際のVaultルートパス"""
    return "/Users/chiba_haruta/obsidian_repo/my-vault/"


def test_vault_scanner_initialization(vault_root):
    """AC: Vaultルートを再帰的にスキャンすること - 初期化確認"""
    scanner = VaultScanner(vault_root)
    assert scanner.vault_root == vault_root
    assert os.path.exists(scanner.vault_root)


def test_scan_returns_file_list(vault_root):
    """AC: スキャン結果としてファイルパスのリストを返すこと"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    assert isinstance(files, list)
    assert len(files) > 0
    # すべての要素がファイルパスの文字列であること
    for file in files:
        assert isinstance(file, str)
        assert file.endswith('.md')


def test_include_pattern_diary(vault_root):
    """AC: INCLUDEパターン（01_diary/**/*.md）に一致するファイルを抽出すること"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # 01_diary配下のファイルが含まれていることを確認
    diary_files = [f for f in files if '01_diary' in f]
    assert len(diary_files) > 0

    # すべて.mdファイルであることを確認
    for file in diary_files:
        assert file.endswith('.md')


def test_include_pattern_notes(vault_root):
    """AC: INCLUDEパターン（02_notes/**/*.md）に一致するファイルを抽出すること"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # 02_notes配下のファイルが含まれていることを確認
    notes_files = [f for f in files if '02_notes' in f]
    assert len(notes_files) > 0

    # すべて.mdファイルであることを確認
    for file in notes_files:
        assert file.endswith('.md')


def test_include_pattern_works(vault_root):
    """AC: INCLUDEパターン（07_works/**/*.md）に一致するファイルを抽出すること"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # 07_works配下のファイルが含まれていることを確認
    works_files = [f for f in files if '07_works' in f]
    assert len(works_files) > 0

    # すべて.mdファイルであることを確認
    for file in works_files:
        assert file.endswith('.md')


def test_exclude_pattern_templates(vault_root):
    """AC: EXCLUDEパターン（00_templates/**/*）に一致するファイルを除外すること"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # 00_templates配下のファイルが含まれていないことを確認
    template_files = [f for f in files if '00_templates' in f]
    assert len(template_files) == 0


def test_exclude_pattern_obsidian(vault_root):
    """AC: EXCLUDEパターン（.obsidian/**/*）に一致するファイルを除外すること"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # .obsidian配下のファイルが含まれていないことを確認
    obsidian_files = [f for f in files if '.obsidian' in f]
    assert len(obsidian_files) == 0


def test_exclude_pattern_git(vault_root):
    """AC: EXCLUDEパターン（.git/**/*等の隠しファイル）に一致するファイルを除外すること"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # .git配下のファイルが含まれていないことを確認
    git_files = [f for f in files if '/.git/' in f]
    assert len(git_files) == 0


def test_recursive_scan(vault_root):
    """AC: Vaultルートを再帰的にスキャンすること - サブディレクトリ内のファイルも取得"""
    scanner = VaultScanner(vault_root)
    files = scanner.scan()

    # サブディレクトリ内のファイルが含まれているか確認（2階層以上深いファイル）
    deep_files = [f for f in files if f.count(os.sep) >= vault_root.count(os.sep) + 2]
    assert len(deep_files) > 0
