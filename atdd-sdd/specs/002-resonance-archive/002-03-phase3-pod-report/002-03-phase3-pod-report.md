---
id: "002-03"
epic_id: "002"
epic_title: "Resonance Archive システム構築"
title: "Phase 3 - Pod201 Report Generation"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-02"
---

# Story: Phase 3 - Pod201 Report Generation（Pod201報告生成）

## 親EPIC

[002: Resonance Archive システム構築](../002-resonance-archive.md)

## 前提Story

- [002-02: Phase 2 - Real-time Resonance Analysis](../002-02-phase2-realtime-analysis/002-02-phase2-realtime-analysis.md) が完了していること

## ユーザーストーリー

**ペルソナ**: 開発者（C4）
**目的**: 検索結果をPod201ペルソナで軍事的かつ簡潔なレポートに変換し、ターミナルに出力する
**価値**: 思考を中断せず、過去の洞察を即座に把握できる
**理由**: 執筆フローを維持しながら、核心的な示唆を受け取りたい

> 開発者として、検索結果をPod201ペルソナで軍事的かつ簡潔なレポートに変換し、ターミナルに出力して、思考を中断せず、過去の洞察を即座に把握したい。なぜなら執筆フローを維持しながら、核心的な示唆を受け取りたいから。

## Acceptance Criteria

- [ ] **WHEN** マルチレベル検索で上位3件が抽出された際
      **THEN** システムはPod201ペルソナのプロンプトを読み込むこと
      **AND** LLM（llama3.1）を用いて簡潔レポートを生成すること

- [ ] **THE SYSTEM SHALL** レポートに日付情報、類似度スコア、核心的洞察を含めること

- [ ] **THE SYSTEM SHALL** ターミナル出力を整形し、視認性を確保すること

- [ ] **THE SYSTEM SHALL** 生成エラー時にフォールバック処理（元テキスト抜粋表示）を実行すること

## 関連Subtask

- [002-03-01: Pod201ペルソナプロンプト作成](./002-03-01-pod201-prompt.md)
- [002-03-02: Ollama LLMクライアント実装](./002-03-02-ollama-llm-client.md)
- [002-03-03: レポート生成パイプライン実装](./002-03-03-report-pipeline.md)
- [002-03-04: 日付情報抽出実装](./002-03-04-date-extraction.md)
- [002-03-05: 類似度スコア表示実装](./002-03-05-similarity-display.md)
- [002-03-06: ターミナル出力整形実装](./002-03-06-terminal-formatting.md)
- [002-03-07: エラーハンドリング実装](./002-03-07-error-handling.md)

## 技術的制約

- Ollama llama3.1:8b必須
- Pod201ペルソナプロンプトファイル（`.pod201/persona.txt`）
- rich ライブラリ推奨（ターミナル整形）

## 備考

このStoryはユーザー体験の最終段階です。Pod201の性格（軍事的・簡潔・洞察的）を維持することが重要です。
