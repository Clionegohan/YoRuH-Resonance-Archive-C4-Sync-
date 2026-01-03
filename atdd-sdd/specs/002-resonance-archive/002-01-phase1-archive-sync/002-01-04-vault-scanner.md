---
id: "002-01-04"
epic_id: "002"
story_id: "002-01"
title: "Vaultスキャン実装"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
completed_at: null
---

# Subtask: Vaultスキャン実装

## 親Story

[002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync.md)

## 前提Subtask

- [002-01-01: プロジェクト基盤セットアップ](./002-01-01-project-setup.md) が完了していること

## ユーザーストーリー

> 開発者として、Vault全体をスキャンし、INCLUDE/EXCLUDEパターンを適用して対象ファイルリストを生成したい。なぜなら正確な対象ファイルのみをベクトル化したいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** Vaultルート（`/Users/chiba_haruta/obsidian_repo/my-vault/`）を再帰的にスキャンすること

- [ ] **THE SYSTEM SHALL** INCLUDEパターン（`01_diary/**/*.md`, `02_notes/**/*.md`, `07_works/**/*.md`）に一致するファイルを抽出すること

- [ ] **THE SYSTEM SHALL** EXCLUDEパターン（`00_templates/**/*`, `.obsidian/**/*`, etc.）に一致するファイルを除外すること

- [ ] **THE SYSTEM SHALL** スキャン結果としてファイルパスのリストを返すこと
