---
id: "002-01-06"
epic_id: "002"
story_id: "002-01"
title: "マルチレベルベクトル化実装"
status: "pending"
created_at: "2026-01-02"
updated_at: "2026-01-03"
completed_at: null
revision_notes: "仕様改訂: 要約品質要件追加、メタデータ拡充、EmbeddingRecord構造体追加、エラーハンドリング明確化"
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

### Level 1: 文書全体ベクトル（要約ベース）

- [ ] **WHEN** ファイルのテキスト長が2000文字を超える、またはチャンク数が5個を超える場合
      **THEN** システムはllama3.1を用いて要約を生成すること

- [ ] **THE SYSTEM SHALL** 要約生成時に以下の要素を必ず保持すること：
  - 固有名詞（人名、組織名、プロジェクト名等）
  - 日付・時刻情報
  - 数値データ（統計、ID、バージョン番号等）
  - 決定事項・アクションアイテム
  - 例外条件・制約事項

- [ ] **THE SYSTEM SHALL** 要約を500〜800字の箇条書き形式で生成すること

- [ ] **THE SYSTEM SHALL** 生成された要約をmxbai-embed-largeでベクトル化すること（Level 1）

- [ ] **WHEN** 要約生成が失敗した場合
      **THEN** システムはエラーログを出力し、そのファイルのLevel 1ベクトルをスキップすること

### Level 2: チャンクベクトル（詳細ベース）

- [ ] **THE SYSTEM SHALL** 全てのファイルをチャンク分割（Subtask 002-01-05）し、各チャンクをmxbai-embed-largeでベクトル化すること（Level 2）

- [ ] **WHEN** チャンクが空または空白文字のみの場合
      **THEN** システムはそのチャンクをスキップし、警告ログを出力すること

- [ ] **WHEN** ベクトル化APIが失敗した場合
      **THEN** システムは最大3回リトライし、それでも失敗した場合はエラーログを出力してスキップすること

### メタデータ設計

- [ ] **THE SYSTEM SHALL** 各ベクトルに以下のメタデータを付与すること：
  - `level`: ベクトルレベル（1 or 2）
  - `chunk_id`: 一意識別子（`{file_path}#{seq}#{content_hash[:8]}`形式）
  - `type`: ベクトルタイプ（`"summary"` or `"chunk"`）
  - `file`: Vaultルートからの相対ファイルパス
  - `date`: ファイルの日付（ファイル名またはメタデータから抽出）
  - `seq`: チャンク順序番号（Level 1は0、Level 2は0始まりの連番）
  - `char_count`: 文字数（Level 1: 要約文字数、Level 2: チャンク文字数）
  - `content_hash`: テキストのSHA256ハッシュ（再計算判定用）
  - `created_at`: ベクトル生成日時（ISO 8601形式）
  - `updated_at`: 最終更新日時（ISO 8601形式）

### 返却形式

- [ ] **THE SYSTEM SHALL** `EmbeddingRecord`構造体のリストを返すこと

- [ ] **THE SYSTEM SHALL** `EmbeddingRecord`は以下のフィールドを持つこと：
  - `id`: chunk_id
  - `text`: 元テキスト（要約またはチャンク）
  - `vector`: 1024次元ベクトル（List[float]）
  - `metadata`: 上記メタデータ（Dict[str, Any]）

### エラーハンドリング

- [ ] **WHEN** ファイルが空または読み込み不可の場合
      **THEN** システムはエラーログを出力し、そのファイルをスキップすること

- [ ] **WHEN** 文字化けまたはエンコードエラーが発生した場合
      **THEN** システムは以下の順序でファイル単位のリカバリを試行すること：
      1. UTF-8エンコーディングで再読み込み
      2. 失敗した場合、`errors='ignore'`を使用したlossy読み込みを試行
      3. それでも失敗した場合、警告ログを出力してファイル全体をスキップすること
