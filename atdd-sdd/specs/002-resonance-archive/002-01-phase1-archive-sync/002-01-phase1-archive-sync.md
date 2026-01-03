---
id: "002-01"
epic_id: "002"
epic_title: "Resonance Archive システム構築"
title: "Phase 1 - Archive Synchronization"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
---

# Story: Phase 1 - Archive Synchronization（記憶同期）

## 親EPIC

[002: Resonance Archive システム構築](../002-resonance-archive.md)

## ユーザーストーリー

**ペルソナ**: 開発者（C4）
**目的**: Vault全体をスキャンし、マルチレベル・ベクトル化してChromaDBに永続化する
**価値**: 過去52.4MBのメモ資産を検索可能な形で記憶できる
**理由**: リアルタイム解析の基盤となる「記憶」を構築したい

> 開発者として、Vault全体をスキャンし、マルチレベル・ベクトル化してChromaDBに永続化して、過去52.4MBのメモ資産を検索可能な形で記憶したい。なぜならリアルタイム解析の基盤となる「記憶」を構築したいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** Vault全体（01_diary, 02_notes, 07_works）をスキャンし、全`.md`ファイルを取得すること

- [ ] **THE SYSTEM SHALL** テンプレートファイル（00_templates）および除外パターンに一致するファイルを検索対象から除外すること

- [ ] **WHEN** ファイルのテキスト長が2000文字を超える場合
      **THEN** システムはLLM（llama3.1）を用いて500〜800字に要約すること
      **AND** 要約テキストをLevel 1ベクトルとして生成すること

- [ ] **THE SYSTEM SHALL** 全ファイルのテキストを段落・文単位で分割し、最大250文字のチャンクを生成すること

- [ ] **THE SYSTEM SHALL** 各チャンクをmxbai-embed-largeを用いてベクトル化し、Level 2ベクトルとして生成すること

- [ ] **THE SYSTEM SHALL** 生成した全ベクトル（Level 1 + Level 2）をメタデータ付きでChromaDBに永続化すること

- [ ] **THE SYSTEM SHALL** 初回インデックス化を5分以内に完了すること（M4 Pro環境）

- [ ] **THE SYSTEM SHALL** インデックス化完了時、生成されたベクトル数をターミナルに表示すること

## 関連Subtask

- [002-01-01: プロジェクト基盤セットアップ](./002-01-01-project-setup.md)
- [002-01-02: Ollama環境構築とモデル準備](./002-01-02-ollama-setup.md)
- [002-01-03: ChromaDB初期化と永続化設定](./002-01-03-chromadb-init.md)
- [002-01-04: Vaultスキャン実装](./002-01-04-vault-scanner.md)
- [002-01-05: セマンティック分割実装](./002-01-05-semantic-splitter.md)
- [002-01-06: マルチレベルベクトル化実装](./002-01-06-multilevel-vectorizer.md)
- [002-01-07: ChromaDBインデックス化実装](./002-01-07-chromadb-indexer.md)
- [002-01-08: インデックス構築の検証](./002-01-08-verification.md)

## 技術的制約

- Ollama必須（llama3.1:8b, mxbai-embed-large）
- ChromaDB v0.4.0+
- Python 3.11+
- M4 Pro Neural Engine活用

## 備考

このStoryは全システムの基盤となるため、最初に完了させる必要があります。
後続のStory（002-02, 002-03）はこのStoryの完了を前提としています。
