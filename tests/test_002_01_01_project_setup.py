"""
Test for Subtask 002-01-01: プロジェクト基盤セットアップ

このテストはAcceptance Criteriaから導出されています。
"""
import os
import pytest


def test_directory_structure_exists():
    """AC: ディレクトリ構造が作成されていること"""
    assert os.path.exists("src/phase1_archive_sync")
    assert os.path.exists("src/phase2_realtime_analysis")
    assert os.path.exists("src/phase3_pod_report")
    assert os.path.exists("src/utils")
    assert os.path.exists("tests/__dev__")
    assert os.path.exists("tests/fixtures")


def test_requirements_txt_exists():
    """AC: requirements.txtが存在し、必要な依存関係が定義されていること"""
    assert os.path.exists("requirements.txt")

    with open("requirements.txt") as f:
        content = f.read()
        assert "ollama" in content
        assert "chromadb" in content
        assert "watchdog" in content
        assert "python-dotenv" in content
        assert "pydantic" in content
        assert "pytest" in content


def test_env_example_exists():
    """AC: .env.exampleが存在し、必要な環境変数のテンプレートが定義されていること"""
    assert os.path.exists(".env.example")

    with open(".env.example") as f:
        content = f.read()
        assert "VAULT_ROOT" in content
        assert "CHROMA_DB_PATH" in content
        assert "OLLAMA_BASE_URL" in content
        assert "OLLAMA_GENERATION_MODEL" in content
        assert "OLLAMA_EMBEDDING_MODEL" in content


def test_gitignore_updated():
    """AC: .gitignoreが更新され、必要なパターンが除外されていること"""
    assert os.path.exists(".gitignore")

    with open(".gitignore") as f:
        content = f.read()
        assert ".chroma_db/" in content
        assert ".env" in content
        assert "__pycache__/" in content
        assert "*.pyc" in content
