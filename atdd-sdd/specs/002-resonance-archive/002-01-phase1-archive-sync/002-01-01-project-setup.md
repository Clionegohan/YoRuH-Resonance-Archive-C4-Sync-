---
id: "002-01-01"
epic_id: "002"
story_id: "002-01"
epic_title: "Resonance Archive システム構築"
story_title: "Phase 1 - Archive Synchronization"
title: "プロジェクト基盤セットアップ"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: プロジェクト基盤セットアップ

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## ユーザーストーリー

**ペルソナ**: 開発者
**目的**: プロジェクトの基盤となるディレクトリ構造と設定ファイルを作成する
**価値**: 統一された構造で開発を開始できる
**理由**: 後続の実装をスムーズに進めたい

> 開発者として、プロジェクトの基盤となるディレクトリ構造と設定ファイルを作成して、統一された構造で開発を開始したい。なぜなら後続の実装をスムーズに進めたいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** 以下のディレクトリ構造が作成されていること：
  - `src/phase1_archive_sync/`
  - `src/phase2_realtime_analysis/`
  - `src/phase3_pod_report/`
  - `src/utils/`
  - `tests/__dev__/`
  - `tests/fixtures/`

- [ ] **THE SYSTEM SHALL** `requirements.txt`が存在し、以下の依存関係が定義されていること：
  - `ollama>=0.1.0`
  - `chromadb>=0.4.0`
  - `watchdog>=3.0.0`
  - `python-dotenv>=1.0.0`
  - `pydantic>=2.0.0`
  - `pytest>=7.4.0`
  - `pytest-cov>=4.1.0`

- [ ] **THE SYSTEM SHALL** `.env.example`が存在し、必要な環境変数のテンプレートが定義されていること

- [ ] **THE SYSTEM SHALL** `.gitignore`が更新され、以下が除外されていること：
  - `.chroma_db/`
  - `.pod201/logs/`
  - `.env`
  - `__pycache__/`
  - `*.pyc`

## 実装メモ

### ディレクトリ構造

```
YoRuH_Archive/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── phase1_archive_sync/
│   │   └── __init__.py
│   ├── phase2_realtime_analysis/
│   │   └── __init__.py
│   ├── phase3_pod_report/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── __dev__/
│   └── fixtures/
│       └── sample_vault/
├── .env.example
├── requirements.txt
└── .gitignore
```

### .env.example テンプレート

```bash
# Vault Paths
VAULT_ROOT=/Users/chiba_haruta/obsidian_repo/my-vault
DIARY_PATH=01_diary
WATCH_PATTERN={YYYY}/{YYYY-MM-dd}.md

# ChromaDB
CHROMA_DB_PATH=./.chroma_db
CHROMA_COLLECTION_NAME=resonance_archive

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_GENERATION_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large

# Pod201
POD201_CONFIG_DIR=./.pod201
POD201_PERSONALITY_FILE=./.pod201/pod201_personality.txt
POD201_LOG_ENABLED=true

# Trigger Settings
TRIGGER_CONFIDENCE_THRESHOLD=0.6
TRIGGER_DEBOUNCE_SECONDS=2.0
TRIGGER_MIN_CHAR_COUNT=50
```

## テストケース（ACから導出）

```python
import os
import pytest

def test_directory_structure_exists():
    """ディレクトリ構造が作成されている"""
    assert os.path.exists("src/phase1_archive_sync")
    assert os.path.exists("src/phase2_realtime_analysis")
    assert os.path.exists("src/phase3_pod_report")
    assert os.path.exists("src/utils")
    assert os.path.exists("tests/__dev__")
    assert os.path.exists("tests/fixtures")

def test_requirements_txt_exists():
    """requirements.txtが存在する"""
    assert os.path.exists("requirements.txt")

    with open("requirements.txt") as f:
        content = f.read()
        assert "ollama" in content
        assert "chromadb" in content
        assert "watchdog" in content
        assert "pydantic" in content

def test_env_example_exists():
    """.env.exampleが存在する"""
    assert os.path.exists(".env.example")

    with open(".env.example") as f:
        content = f.read()
        assert "VAULT_ROOT" in content
        assert "CHROMA_DB_PATH" in content
        assert "OLLAMA_BASE_URL" in content

def test_gitignore_updated():
    """.gitignoreが更新されている"""
    assert os.path.exists(".gitignore")

    with open(".gitignore") as f:
        content = f.read()
        assert ".chroma_db/" in content
        assert ".env" in content
        assert "__pycache__/" in content
```

## 完了確認

- 確認日:
- 確認者:
- 備考:

## 参照ドキュメント

- [APP_SPECIFICATION.md](../../../docs/APP_SPECIFICATION.md)
- [プロジェクトREADME](../../../../../README.md)
