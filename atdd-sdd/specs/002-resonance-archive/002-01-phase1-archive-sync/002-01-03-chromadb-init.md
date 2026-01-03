---
id: "002-01-03"
epic_id: "002"
story_id: "002-01"
title: "ChromaDB初期化と永続化設定"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: ChromaDB初期化と永続化設定

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## 前提Subtask

- [002-01-01: プロジェクト基盤セットアップ](./002-01-01-project-setup.md) が完了していること

## ユーザーストーリー

**ペルソナ**: 開発者
**目的**: ChromaDBを初期化し、ベクトル永続化の準備をする
**価値**: ベクトルを永続的に保存できる
**理由**: システム再起動後もベクトルを保持したい

> 開発者として、ChromaDBを初期化し、ベクトル永続化の準備をして、ベクトルを永続的に保存したい。なぜならシステム再起動後もベクトルを保持したいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** `./.chroma_db/`ディレクトリが作成されること

- [ ] **THE SYSTEM SHALL** ChromaDBクライアントが初期化されること

- [ ] **THE SYSTEM SHALL** `resonance_archive`コレクションが作成されること

- [ ] **THE SYSTEM SHALL** コレクションのメタデータスキーマが以下を含むこと：
  - `type`: "summary" | "chunk"
  - `file`: ファイルパス
  - `date`: 日付（YYYY-MM-DD）
  - `char_count`: 文字数（summaryのみ）
  - `chunk_index`: チャンク番号（chunkのみ）

- [ ] **WHEN** テスト用ベクトルを挿入した場合
      **THEN** システムはベクトルを永続化すること

- [ ] **WHEN** システムを再起動した場合
      **THEN** 以前に挿入したベクトルが取得できること

## テストケース

```python
def test_chromadb_initialization():
    """ChromaDBが初期化できる"""
    from src.phase1_archive_sync.indexer import ChromaDBIndexer

    indexer = ChromaDBIndexer()
    assert indexer.client is not None
    assert indexer.collection is not None

def test_vector_persistence():
    """ベクトルが永続化される"""
    from src.phase1_archive_sync.indexer import ChromaDBIndexer

    indexer = ChromaDBIndexer()

    # テスト用ベクトル挿入
    indexer.add_vector(
        vector=[0.1] * 768,
        metadata={"type": "chunk", "file": "test.md"}
    )

    # 取得確認
    results = indexer.search(query_vector=[0.1] * 768, top_k=1)
    assert len(results) > 0
```
