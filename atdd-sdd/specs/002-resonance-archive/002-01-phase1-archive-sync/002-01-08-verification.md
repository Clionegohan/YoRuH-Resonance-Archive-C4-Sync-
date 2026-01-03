---
id: "002-01-08"
epic_id: "002"
story_id: "002-01"
title: "インデックス構築の検証"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: インデックス構築の検証

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## 前提Subtask

- [002-01-07: ChromaDBインデックス化実装](./002-01-07-chromadb-indexer.md) が完了していること

## ユーザーストーリー

> 開発者として、Phase 1全体が正しく動作することを検証して、Phase 2に進む準備を整えたい。なぜなら基盤が安定していることを確認したいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** 全ファイルがスキャンされ、ベクトル化されること

- [ ] **THE SYSTEM SHALL** 初回インデックス化が5分以内に完了すること（M4 Pro環境）

- [ ] **THE SYSTEM SHALL** 生成されたベクトル数をターミナルに表示すること

- [ ] **WHEN** テスト用クエリで検索した場合
      **THEN** システムは類似ベクトルを返すこと

- [ ] **THE SYSTEM SHALL** メモリ使用量が4GB以内であること
