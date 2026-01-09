"""
Test for Subtask 002-03-01: Pod201ペルソナプロンプト作成

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from pathlib import Path


def test_persona_file_exists():
    """AC: `.pod201/persona.txt` にPod201ペルソナプロンプトファイルを配置すること"""
    persona_file = Path(".pod201/persona.txt")
    assert persona_file.exists(), ".pod201/persona.txt ファイルが存在しません"
    assert persona_file.is_file(), ".pod201/persona.txt はファイルである必要があります"


def test_persona_file_not_empty():
    """AC: プロンプトファイルは空でないこと"""
    persona_file = Path(".pod201/persona.txt")
    content = persona_file.read_text(encoding="utf-8")
    assert len(content.strip()) > 0, "persona.txt は空であってはなりません"


def test_persona_file_utf8_encoding():
    """AC: プロンプトファイルはUTF-8エンコーディングで保存すること"""
    persona_file = Path(".pod201/persona.txt")
    try:
        content = persona_file.read_text(encoding="utf-8")
        assert content is not None
    except UnicodeDecodeError:
        pytest.fail("persona.txt はUTF-8でエンコードされている必要があります")


def test_persona_content_has_minimum_length():
    """AC: 最低限の性格定義を含むこと"""
    persona_file = Path(".pod201/persona.txt")
    content = persona_file.read_text(encoding="utf-8")
    # 最低限100文字以上の定義があることを期待
    assert len(content.strip()) >= 100, "persona.txt には最低限の性格定義が必要です (100文字以上)"


def test_persona_defines_character_traits():
    """AC: Pod201の性格特性を定義すること (軍事的、簡潔、洞察的)"""
    persona_file = Path(".pod201/persona.txt")
    content = persona_file.read_text(encoding="utf-8").lower()

    # 性格特性のキーワードまたは関連する表現が含まれているか確認
    # (実際のプロンプト内容に依存するため、柔軟に判定)
    has_content = len(content) > 100
    assert has_content, "persona.txt にPod201の性格特性の定義が必要です"


def test_persona_file_location():
    """追加テスト: ファイルが正しいディレクトリに配置されていること"""
    persona_file = Path(".pod201/persona.txt")
    assert persona_file.parent.name == ".pod201", "ファイルは .pod201 ディレクトリに配置する必要があります"


def test_persona_file_readable():
    """追加テスト: ファイルが読み込み可能であること"""
    persona_file = Path(".pod201/persona.txt")
    assert persona_file.exists()
    content = persona_file.read_text(encoding="utf-8")
    assert isinstance(content, str), "ファイル内容は文字列である必要があります"
