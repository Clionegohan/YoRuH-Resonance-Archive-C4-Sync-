---
id: "002-01-02"
epic_id: "002"
story_id: "002-01"
title: "Ollama環境構築とモデル準備"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: Ollama環境構築とモデル準備

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## 前提Subtask

- [002-01-01: プロジェクト基盤セットアップ](./002-01-01-project-setup.md) が完了していること

## ユーザーストーリー

**ペルソナ**: 開発者
**目的**: Ollama接続を確認し、必要なモデルを準備する
**価値**: LLM推論とベクトル化が実行可能になる
**理由**: Phase 1の要約生成とベクトル化に必須

> 開発者として、Ollama接続を確認し、必要なモデルを準備して、LLM推論とベクトル化が実行可能にしたい。なぜならPhase 1の要約生成とベクトル化に必須だから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** `http://localhost:11434`でOllamaに接続できること

- [ ] **WHEN** Ollamaに接続できる場合
      **THEN** システムは利用可能なモデルリストを取得すること

- [ ] **THE SYSTEM SHALL** `llama3.1:8b`モデルがダウンロードされていること

- [ ] **THE SYSTEM SHALL** `mxbai-embed-large`モデルがダウンロードされていること

- [ ] **THE SYSTEM SHALL** Ollama APIクライアント（`src/utils/ollama_client.py`）が実装されていること

- [ ] **WHEN** テスト用テキストをllama3.1に送信した場合
      **THEN** システムは応答を受け取ること

- [ ] **WHEN** テスト用テキストをmxbai-embed-largeで埋め込みした場合
      **THEN** システムは768次元のベクトルを受け取ること

## テストケース

```python
def test_ollama_connection():
    """Ollamaに接続できる"""
    from src.utils.ollama_client import OllamaClient

    client = OllamaClient()
    assert client.is_available()

def test_llama31_generation():
    """llama3.1でテキスト生成できる"""
    from src.utils.ollama_client import OllamaClient

    client = OllamaClient()
    response = client.generate(
        model="llama3.1:8b",
        prompt="こんにちは"
    )
    assert response is not None
    assert len(response) > 0

def test_mxbai_embedding():
    """mxbai-embed-largeでベクトル化できる"""
    from src.utils.ollama_client import OllamaClient

    client = OllamaClient()
    vector = client.embed(
        model="mxbai-embed-large",
        text="テストテキスト"
    )
    assert len(vector) == 768
```
