---
id: "002-01-06"
epic_id: "002"
story_id: "002-01"
title: "マルチレベルベクトル化実装"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: マルチレベルベクトル化実装

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## 前提Subtask

- [002-01-02: Ollama環境構築とモデル準備](./002-01-02-ollama-setup.md) が完了していること
- [002-01-05: セマンティック分割実装](./002-01-05-semantic-splitter.md) が完了していること

## ユーザーストーリー

> 開発者として、ファイル全体の要約ベクトル（Level 1）とチャンクベクトル（Level 2）を生成して、全体のテーマと局所的な詳細の両方を捉えたい。なぜなら長文メモでも意味を失わず検索したいから。

## Acceptance Criteria

- [ ] **WHEN** ファイルのテキスト長が2000文字を超える場合
      **THEN** システムはllama3.1を用いて500〜800字に要約すること
      **AND** 要約をmxbai-embed-largeでベクトル化すること（Level 1）

- [ ] **THE SYSTEM SHALL** 全てのファイルをチャンク分割し、各チャンクをベクトル化すること（Level 2）

- [ ] **THE SYSTEM SHALL** 各ベクトルにメタデータ（`type`, `file`, `date`, etc.）を付与すること

- [ ] **THE SYSTEM SHALL** ベクトルとメタデータのタプルリストを返すこと
