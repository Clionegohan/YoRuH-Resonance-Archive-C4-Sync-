---
id: "002-01-05"
epic_id: "002"
story_id: "002-01"
title: "セマンティック分割実装"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: セマンティック分割実装

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## 前提Subtask

- [002-01-04: Vaultスキャン実装](./002-01-04-vault-scanner.md) が完了していること

## ユーザーストーリー

> 開発者として、テキストを意味的なまとまりを保ちながら分割して、ベクトル化に適したチャンクを生成したい。なぜなら文脈を失わずにベクトル化したいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** テキストを段落単位（`\n\n`）で分割すること

- [ ] **WHEN** 段落が250文字を超える場合
      **THEN** システムは文単位（`。！？`）でさらに分割すること

- [ ] **THE SYSTEM SHALL** 各チャンクが最大250文字以内であること

- [ ] **THE SYSTEM SHALL** チャンクのリストを返すこと
