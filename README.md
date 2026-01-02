# YoRuH: Resonance Archive [C4-Sync]

**随行支援ユニット：Pod201プロトコル**

> C4の思考を過去の膨大なアーカイブと「共鳴」させる、ローカル完結型の意味的検索支援システム

---

## 概要

**YoRuH: Resonance Archive** は、Obsidian Vault（52.4MB）をリアルタイムで解析し、現在の思考と過去の記録との「意味的共鳴（Resonance）」を自動検出するシステムです。

### 特徴

- 🔍 **ベクトル検索:** キーワード完全一致ではなく、意味的距離で過去ログを検出
- 🤖 **Pod201:** 冷静・論理的な軍事報告書スタイルのAI支援ユニット
- 🔒 **完全ローカル:** Ollama + ChromaDB、外部ネットワーク通信なし
- ⚡ **リアルタイム:** 執筆中に"よしなに"タイミングで自動解析
- 🧠 **M4 Pro最適化:** Neural Engine活用、高速・低メモリ

---

## 動作イメージ

```
[ SYSTEM INFO ] YoRuH: Resonance Archive [C4-Sync]
[ HARDWARE    ] M4 Pro / Neural Engine Active
[ UNIT        ] Pod201 Ready.
------------------------------------------------------------
[ 報告 ] : 個体識別名 C4 の新規入力を検知。解析を開始。

[ 過去ログ参照 ] : 2023-11-12 記録「深夜の断想」と 87.4% の共鳴を確認。
> 該当テキスト: 「答えは外にはない、層の中に沈んでいるだけだ」

[ 推測 ] : 現在 C4 が直面している課題は、2年前の思索の延長線上にある。
[ 推奨 ] : アーカイブされた当時の「解決プロトコル」との再照合を提案する。
------------------------------------------------------------
```

---

## プロジェクト構造

```
YoRuH_Arcive/
├── atdd-sdd/                        # 仕様駆動開発（ATDD-SDD）
│   ├── specs/                       # 仕様書（EPIC/Story/Subtask）
│   │   └── 002-resonance-archive/   # EPIC 002（これから作成）
│   └── docs/
│       └── APP_SPECIFICATION.md     # 完全仕様書
│
├── src/                             # ソースコード（これから作成）
│   ├── phase1_archive_sync/         # Phase 1: 記憶同期
│   ├── phase2_realtime_analysis/    # Phase 2: 即時共鳴分析
│   ├── phase3_pod_report/           # Phase 3: Pod201報告生成
│   └── utils/                       # 共通ユーティリティ
│
├── .chroma_db/                      # ChromaDBベクトルストア（実行時に生成）
├── .pod201/                         # Pod201設定・ログ（実行時に生成）
├── tests/                           # テスト（TDD）
├── .env                             # 環境変数
├── requirements.txt                 # Python依存関係
└── README.md                        # 本ファイル
```

---

## 技術スタック

| 層 | 技術 | 役割 |
|---|---|---|
| 推論エンジン | Ollama | ローカルLLM実行基盤 |
| 生成モデル | llama3.1:8b | Pod201人格生成、要約処理 |
| 埋め込みモデル | mxbai-embed-large | 日本語テキストのベクトル化 |
| ベクトルDB | ChromaDB | ベクトル永続化・類似検索 |
| 監視 | Python Watchdog | ファイル変更検知 |
| 言語 | Python 3.11+ | メイン実装言語 |

**ハードウェア:** Apple M4 Pro (24GB Unified Memory)

---

## ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [`atdd-sdd/docs/APP_SPECIFICATION.md`](atdd-sdd/docs/APP_SPECIFICATION.md) | **完全仕様書**（技術スタック、アーキテクチャ、全詳細） |
| `atdd-sdd/specs/` | EPIC/Story/Subtask仕様書（これから作成） |
| `atdd-sdd/README.md` | ATDD-SDD開発フレームワークの説明 |

---

## コア機能

### Phase 1: Archive Synchronization（記憶同期）

Vault全体（`01_diary`, `02_notes`, `07_works`）をスキャンし、マルチレベル・ベクトル化：

- **Level 1:** ファイル全体を要約してベクトル化（全体のテーマを捉える）
- **Level 2:** 段落・文単位で分割してベクトル化（局所的な詳細を捉える）

### Phase 2: Real-time Resonance Analysis（即時共鳴分析）

日記ファイル（`01_diary/YYYY/YYYY-MM-dd.md`）を監視し、"よしなに"タイミングで解析：

- **マルチシグナル方式:** 構造的区切り + 時間パターン + 差分量
- **確信度スコアリング:** 複数シグナルから解析タイミングを自動判定

### Phase 3: Pod201 Report（随行報告）

LLM（llama3.1）がPod201人格で報告を生成：

- **[報告]:** 現在の入力要約
- **[過去ログ参照]:** 類似度上位3件（日付・スコア・テキスト抜粋）
- **[推測]:** 現在と過去の関連性分析
- **[推奨]:** 次のアクション提案

---

## 開発方針：ATDD-SDD

このプロジェクトは **ATDD-SDD（仕様駆動開発）** フレームワークに従って開発されます。

### 開発フロー

1. **仕様策定（`/spec` Skill）**
   - EPIC → Story → Subtask の3階層で仕様を定義
   - EARS記法でAcceptance Criteria（AC）を明確化

2. **実装（`spec-workflow`）**
   - TDD厳守：Red → Green → Refactor
   - ACの範囲内のみ実装
   - スコープ外は提案のみ

3. **完了確認**
   - AC全項目チェック
   - ステータス更新

詳細は [`atdd-sdd/README.md`](atdd-sdd/README.md) を参照

---

## クイックスタート（予定）

### 前提条件

- Python 3.11+
- Ollama（インストール済み）
- モデル：`llama3.1:8b`, `mxbai-embed-large`

### インストール

```bash
# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envを編集してVaultパスを設定
```

### 初回セットアップ

```bash
# Vault全体をインデックス化（初回のみ）
python src/main.py --init
```

### 通常起動

```bash
# Pod201を起動（監視モード）
python src/main.py
```

---

## 開発ロードマップ

### EPIC 002: Resonance Archive システム構築

- **Story 002-01:** Phase 1 - Archive Synchronization（記憶同期）
- **Story 002-02:** Phase 2 - Real-time Resonance Analysis（即時共鳴分析）
- **Story 002-03:** Phase 3 - Pod201 Report Generation（随行報告）
- **Story 002-04:** System Integration & CLI（統合とCLI）

詳細は [`atdd-sdd/docs/APP_SPECIFICATION.md`](atdd-sdd/docs/APP_SPECIFICATION.md) の「12. 開発ロードマップ」を参照

---

## ライセンス

MIT

---

**個体識別名 C4 / 支援ユニット Pod201**
