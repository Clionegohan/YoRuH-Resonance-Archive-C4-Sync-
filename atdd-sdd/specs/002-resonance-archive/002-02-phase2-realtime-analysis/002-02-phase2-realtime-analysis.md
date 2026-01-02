---
id: "002-02"
epic_id: "002"
epic_title: "Resonance Archive システム構築"
title: "Phase 2 - Real-time Resonance Analysis"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
---

# Story: Phase 2 - Real-time Resonance Analysis（即時共鳴分析）

## 親EPIC

[002: Resonance Archive システム構築](../002-resonance-archive.md)

## 前提Story

- [002-01: Phase 1 - Archive Synchronization](../002-01-phase1-archive-sync/002-01-phase1-archive-sync.md) が完了していること

## ユーザーストーリー

**ペルソナ**: 開発者（C4）
**目的**: 日記ファイルを監視し、"よしなに"タイミングで類似検索を実行する
**価値**: 執筆中にリアルタイムで過去ログとの共鳴を発見できる
**理由**: 執筆の流れを邪魔せず、適切なタイミングで示唆を得たい

> 開発者として、日記ファイルを監視し、"よしなに"タイミングで類似検索を実行して、執筆中にリアルタイムで過去ログとの共鳴を発見したい。なぜなら執筆の流れを邪魔せず、適切なタイミングで示唆を得たいから。

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** 当日の日記ファイル（`01_diary/YYYY/YYYY-MM-dd.md`）をWatchdogで監視すること

- [ ] **WHEN** ファイルが保存された際
      **GIVEN** マルチシグナル判定で確信度が0.6以上の場合
      **THEN** システムは解析を実行すること

- [ ] **THE SYSTEM SHALL** 構造的シグナル（段落区切り、水平線、文末）を検知すること

- [ ] **THE SYSTEM SHALL** 時間シグナル（long_pause, medium_pause）を検知すること

- [ ] **THE SYSTEM SHALL** 差分シグナル（追加文字数）を検知すること

- [ ] **THE SYSTEM SHALL** 複数シグナルから確信度スコアを計算すること

- [ ] **WHEN** トリガー条件を満たした場合
      **THEN** システムは2秒のデバウンス後に解析を実行すること

- [ ] **THE SYSTEM SHALL** ChromaDBでLevel 1検索（summary, top_k=5）とLevel 2検索（chunk, top_k=10）を実行すること

- [ ] **THE SYSTEM SHALL** 検索結果を統合し、上位3件を抽出すること

## 関連Subtask

- [002-02-01: Watchdogファイル監視実装](./002-02-01-watchdog-watcher.md)
- [002-02-02: 構造的シグナル検知実装](./002-02-02-structural-signals.md)
- [002-02-03: 時間・差分シグナル検知実装](./002-02-03-timing-delta-signals.md)
- [002-02-04: 確信度スコアリング実装](./002-02-04-confidence-scoring.md)
- [002-02-05: 差分抽出とベクトル化](./002-02-05-diff-extraction.md)
- [002-02-06: ChromaDB類似検索実装](./002-02-06-similarity-search.md)
- [002-02-07: マルチレベル検索統合](./002-02-07-multilevel-integration.md)

## 技術的制約

- Watchdog 3.0.0+
- 確信度閾値: 0.6（調整可能）
- デバウンス時間: 2秒（調整可能）

## 備考

このStoryはユーザー体験の核心部分です。"よしなに"タイミングの精度が重要です。
