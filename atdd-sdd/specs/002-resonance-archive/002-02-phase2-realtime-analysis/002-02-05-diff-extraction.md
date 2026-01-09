---
id: "002-02-05"
title: "差分抽出とベクトル化"
status: "completed"
---

# Subtask: 差分抽出とベクトル化

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** DiffExtractorクラスを提供すること

- [ ] **THE SYSTEM SHALL** extract_diff()メソッドで差分テキストを抽出すること
  - previous_text と current_text を入力として受け取る
  - previous_textがNoneの場合、current_text全体を差分とする
  - previous_textが存在する場合、追加部分（current_text[len(previous_text):]）を差分とする
  - 削除（current_textがprevious_textより短い）の場合、空文字列を返す

- [ ] **THE SYSTEM SHALL** vectorize_diff()メソッドで差分テキストをベクトル化すること
  - OllamaClientを使用（mxbai-embed-large）
  - 1024次元ベクトルを返す
  - リトライロジック実装（最大3回、exponential backoff）

- [ ] **THE SYSTEM SHALL** 差分テキストが空の場合、vectorize_diff()はNoneを返すこと

- [ ] **THE SYSTEM SHALL** ベクトル化に失敗した場合、エラーログを出力しNoneを返すこと
