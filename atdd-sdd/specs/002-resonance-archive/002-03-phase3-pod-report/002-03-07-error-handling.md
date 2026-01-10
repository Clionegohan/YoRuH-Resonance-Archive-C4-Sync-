---
id: "002-03-07"
title: "エラーハンドリング実装"
status: "pending"
---

# Subtask: エラーハンドリング実装

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** LLM生成失敗時にエラーログを記録すること
  - Pythonの標準loggingモジュールを使用
  - エラーの種類と詳細をログレベルERRORで記録
  - 例外のトレースバックを含める

- [ ] **THE SYSTEM SHALL** LLM生成失敗時にフォールバックレポートを返すこと
  - `_format_search_results()`を使用した検索結果のプレーンテキスト表示
  - エラー通知メッセージを含む（例: "【警告】LLM生成失敗。検索結果を表示します。"）
  - Noneを返さず、常に有効な文字列を返す

- [ ] **THE SYSTEM SHALL** Ollama接続エラーを適切に処理すること
  - 接続エラー（ConnectionError, TimeoutError等）を明示的にキャッチ
  - エラーメッセージに接続失敗の旨を含める
  - フォールバックレポートを返す

- [ ] **THE SYSTEM SHALL** LLMレスポンスが空/Noneの場合にフォールバックすること
  - レスポンスのバリデーション（空文字列、None、空白のみをチェック）
  - 無効なレスポンス時にフォールバックレポートを返す

- [ ] **THE SYSTEM SHALL** ペルソナファイル読み込み失敗時にデフォルトペルソナを使用すること
  - FileNotFoundErrorをキャッチ
  - デフォルトペルソナプロンプト文字列を定義（クラス定数）
  - 初期化時のエラーを記録

- [ ] **THE SYSTEM SHALL** 全エラーケースで有効なレポート文字列を返すこと
  - generate_report()の戻り値型をOptional[str]からstrに変更
  - 全てのパスで非Noneの文字列を保証
  - テストで全エラーケースをカバー

