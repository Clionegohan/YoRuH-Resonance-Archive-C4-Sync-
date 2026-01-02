---
id: "002"
title: "Resonance Archive システム構築"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
---

# EPIC: Resonance Archive システム構築

## ユーザーストーリー

**ペルソナ**: 開発者（C4）
**目的**: 過去の膨大なメモアーカイブと現在の思考を「共鳴」させる支援システムを構築する
**価値**: 忘れていた過去の洞察を自動的に蘇らせ、思考の複利効果を最大化できる
**理由**: 52.4MBのメモ資産を有効活用し、執筆の質と深みを向上させたい

> 開発者として、過去の膨大なメモアーカイブと現在の思考を「共鳴」させる支援システムを構築して、忘れていた過去の洞察を自動的に蘇らせたい。なぜなら52.4MBのメモ資産を有効活用し、執筆の質と深みを向上させたいから。

## Acceptance Criteria

### 基本要件

- [ ] **THE SYSTEM SHALL** Vault全体（01_diary, 02_notes, 07_works）をスキャンし、ChromaDBにベクトル化して永続化すること

- [ ] **THE SYSTEM SHALL** 当日の日記ファイル（01_diary/YYYY/YYYY-MM-dd.md）をリアルタイムで監視すること

- [ ] **WHEN** ユーザーがObsidianでメモを書き、一定の条件を満たした際
      **THEN** システムは自動的に解析を開始すること
      **AND** 過去ログとの類似度上位3件を抽出すること

- [ ] **WHEN** 類似ログが検出された際
      **GIVEN** Pod201人格プロンプトが定義されている場合
      **THEN** システムはLLM（llama3.1）を用いて報告を生成すること
      **AND** ターミナルに規定フォーマットで出力すること

### 非機能要件

- [ ] **THE SYSTEM SHALL** 完全ローカル環境で動作し、外部ネットワーク通信を一切行わないこと

- [ ] **THE SYSTEM SHALL** 初回インデックス化を5分以内に完了すること（M4 Pro環境）

- [ ] **THE SYSTEM SHALL** リアルタイム検索を500ms以内に完了すること

- [ ] **THE SYSTEM SHALL** メモリ使用量を最大4GB以内に抑えること

### データ整合性

- [ ] **THE SYSTEM SHALL** ChromaDBのデータがクラッシュしても、Obsidianの原本ファイルに影響を与えないこと

- [ ] **THE SYSTEM SHALL** テンプレートファイル（00_templates）を検索対象から除外すること

## 関連Story

- [002-01: Phase 1 - Archive Synchronization](./002-01-phase1-archive-sync/002-01-phase1-archive-sync.md)
- [002-02: Phase 2 - Real-time Resonance Analysis](./002-02-phase2-realtime-analysis/002-02-phase2-realtime-analysis.md)
- [002-03: Phase 3 - Pod201 Report Generation](./002-03-phase3-pod-report/002-03-phase3-pod-report.md)
- [002-04: System Integration & CLI](./002-04-integration-cli/002-04-integration-cli.md)

## 技術的制約

- Apple M4 Pro (24GB Unified Memory)
- macOS環境
- Ollama必須（llama3.1:8b, mxbai-embed-large）
- ChromaDB v0.4.0+
- Python 3.11+

## 備考

このEPICは3つのPhaseに分かれています：
1. Phase 1: Archive Synchronization（記憶同期）
2. Phase 2: Real-time Resonance Analysis（即時共鳴分析）
3. Phase 3: Pod201 Report Generation（随行報告）

完全ローカル環境で動作し、外部ネットワーク通信を一切行いません。
