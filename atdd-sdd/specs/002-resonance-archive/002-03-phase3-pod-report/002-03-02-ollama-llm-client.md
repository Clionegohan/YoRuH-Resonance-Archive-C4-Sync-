---
id: "002-03-02"
title: "Ollama LLMクライアント実装"
status: "in_progress"
---

# Subtask: Ollama LLMクライアント実装

## Acceptance Criteria

- [ ] **THE SYSTEM SHALL** Pod201ReportGeneratorクラスを提供すること

- [ ] **THE SYSTEM SHALL** generate_report()メソッドを提供すること
  - 入力: 検索結果リスト（List[Dict]）
  - 出力: Pod201スタイルのレポートテキスト（str）

- [ ] **THE SYSTEM SHALL** `.pod201/persona.txt` からPod201ペルソナプロンプトを読み込むこと

- [ ] **THE SYSTEM SHALL** OllamaClientを使用してllama3.1:8bモデルでテキスト生成を行うこと

- [ ] **THE SYSTEM SHALL** システムプロンプトとしてPod201ペルソナを使用すること

- [ ] **THE SYSTEM SHALL** 生成エラー時にNoneを返すこと

- [ ] **THE SYSTEM SHALL** 空の検索結果の場合は適切なメッセージを生成すること

