---
id: "002-03-02"
title: "Ollama LLMクライアント実装"
status: "completed"
---

# Subtask: Ollama LLMクライアント実装

## Acceptance Criteria

- [x] **THE SYSTEM SHALL** Pod201ReportGeneratorクラスを提供すること

- [x] **THE SYSTEM SHALL** generate_report()メソッドを提供すること
  - 入力: 検索結果リスト（List[Dict]）
  - 出力: Pod201スタイルのレポートテキスト（str）

- [x] **THE SYSTEM SHALL** `.pod201/persona.txt` からPod201ペルソナプロンプトを読み込むこと

- [x] **THE SYSTEM SHALL** OllamaClientを使用してllama3.1:8bモデルでテキスト生成を行うこと

- [x] **THE SYSTEM SHALL** システムプロンプトとしてPod201ペルソナを使用すること

- [x] **THE SYSTEM SHALL** 生成エラー時にNoneを返すこと

- [x] **THE SYSTEM SHALL** 空の検索結果の場合は適切なメッセージを生成すること

