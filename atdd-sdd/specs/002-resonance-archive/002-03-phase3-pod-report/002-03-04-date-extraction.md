---
id: "002-03-04"
title: "日付情報抽出実装"
status: "in_progress"
---

# Subtask: 日付情報抽出実装

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** Pod201ReportGeneratorに日付情報抽出機能を追加すること

- [ ] **THE SYSTEM SHALL** _extract_date()メソッドを提供すること
  - メタデータから日付情報を抽出
  - file, date, created_at等のキーから日付を検出
  - 日付が見つからない場合はNoneを返す

- [ ] **THE SYSTEM SHALL** 複数の日付フォーマットに対応すること
  - YYYY-MM-DD形式（例: "2026-01-10"）
  - ファイルパス内の日付（例: "01_diary/2026/2026-01-10.md"）

- [ ] **THE SYSTEM SHALL** 抽出した日付情報をレポートプロンプトに含めること

- [ ] **THE SYSTEM SHALL** 日付情報がない場合でもレポート生成を継続すること

