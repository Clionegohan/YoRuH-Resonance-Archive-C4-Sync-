# YoRuH: Resonance Archive [C4-Sync] - 完全仕様書

**Version:** 1.0
**作成日:** 2026-01-02
**個体識別名:** C4
**支援ユニット:** Pod201

---

## 目次

1. [システム概要](#1-システム概要)
2. [技術スタック](#2-技術スタック)
3. [ディレクトリ構造](#3-ディレクトリ構造)
4. [ファイルパス定義](#4-ファイルパス定義)
5. [Pod201 人格定義](#5-pod201-人格定義)
6. [コア機能プロトコル](#6-コア機能プロトコル)
7. [マルチレベル・ベクトル化戦略](#7-マルチレベルベクトル化戦略)
8. [マルチシグナル・トリガー検知](#8-マルチシグナルトリガー検知)
9. [ユーザーフロー](#9-ユーザーフロー)
10. [出力仕様](#10-出力仕様)
11. [非機能要件](#11-非機能要件)
12. [開発ロードマップ](#12-開発ロードマップ)

---

## 1. システム概要

### 1.1 コンセプト

**YoRuH: Resonance Archive [C4-Sync]** は、個体識別名C4のObsidian Vault（52.4MB、全メモ資産）をリアルタイムで解析し、現在の思考と過去の記録との「意味的共鳴（Resonance）」を自動検出する随行支援システムである。

**コア原理:**
- キーワード完全一致ではなく、**ベクトル空間上の意味的距離**で過去ログを検索
- メモの蓄積が増えるほど、ChromaDB内のベクトル密度が高まり、共鳴の精度・深みが向上（**複利効果**）
- ローカル完結（Ollama + ChromaDB）による**完全なプライバシー保護**

### 1.2 なぜ"Resonance（共鳴）"なのか

キーワード検索は「完全一致」を求める。
しかし、人間の思考は**言葉を変えながら同じテーマを巡る**。

**例:**
- 2年前: 「時間は存在するのか？」
- 現在: 「過去は実在するか？」

→ キーワード検索では捉えられない
→ ベクトル空間では「近い位置」に配置される
→ これを**共鳴（Resonance）**と呼ぶ

Pod201は、C4の思考の「残響」を検出し、忘れていた過去の洞察を蘇らせる。

---

## 2. 技術スタック

### 2.1 ハードウェア・OS
- **CPU/GPU:** Apple M4 Pro (24GB Unified Memory)
- **OS:** macOS (Darwin 24.6.0)
- **最適化:** Neural Engine活用、メモリ効率重視

### 2.2 ソフトウェア
| 層 | 技術 | 役割 |
|---|---|---|
| **推論エンジン** | Ollama | ローカルLLM実行基盤 |
| **生成モデル** | `llama3.1:8b` | Pod201人格生成、要約処理 |
| **埋め込みモデル** | `mxbai-embed-large` | 日本語テキストのベクトル化 |
| **ベクトルDB** | ChromaDB | ベクトル永続化・類似検索 |
| **監視** | Python Watchdog | ファイル変更検知 |
| **言語** | Python 3.11+ | メイン実装言語 |

### 2.3 なぜこの構成？
- **日本語特化:** Vault内容の99%が日本語 → `mxbai-embed-large`の多言語対応が最適
- **ローカル完結:** 外部API不要、完全オフライン動作
- **M4 Pro最適化:** Neural Engineで推論高速化

### 2.4 依存関係（requirements.txt）

```txt
# LLM & Embeddings
ollama>=0.1.0

# Vector Database
chromadb>=0.4.0

# File Monitoring
watchdog>=3.0.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 3. ディレクトリ構造

### 3.1 プロジェクト構造

```
YoRuH_Archive/
├── .chroma_db/                      # ChromaDBベクトルストア（永続化、隠しディレクトリ）
│   └── chroma.sqlite3               # ChromaDB永続データ
│
├── .pod201/                         # Pod201設定・ログ（隠しディレクトリ）
│   ├── pod201_personality.txt       # Pod201人格プロンプト
│   ├── config.json                  # システム設定
│   └── logs/                        # 解析ログ（オプション）
│       └── YYYY-MM-dd.log
│
├── src/                             # ソースコード
│   ├── __init__.py
│   ├── main.py                      # メインCLIエントリーポイント
│   ├── config.py                    # 設定管理
│   │
│   ├── phase1_archive_sync/         # Phase 1: Archive Synchronization
│   │   ├── __init__.py
│   │   ├── scanner.py               # Vaultスキャン
│   │   ├── vectorizer.py            # マルチレベル・ベクトル化
│   │   └── indexer.py               # ChromaDBインデックス化
│   │
│   ├── phase2_realtime_analysis/    # Phase 2: Real-time Resonance Analysis
│   │   ├── __init__.py
│   │   ├── watcher.py               # ファイル監視（Watchdog）
│   │   ├── trigger.py               # マルチシグナル・トリガー判定
│   │   ├── diff_extractor.py        # 差分抽出
│   │   └── retriever.py             # ChromaDB類似検索
│   │
│   ├── phase3_pod_report/           # Phase 3: Pod201 Report Generation
│   │   ├── __init__.py
│   │   ├── generator.py             # LLM報告生成
│   │   ├── formatter.py             # ターミナル出力フォーマット
│   │   └── date_extractor.py        # ファイル名から日付抽出
│   │
│   └── utils/                       # 共通ユーティリティ
│       ├── __init__.py
│       ├── text_splitter.py         # テキスト分割
│       ├── ollama_client.py         # Ollama API クライアント
│       └── logger.py                # ロギング
│
├── tests/                           # テスト（TDD）
│   ├── __init__.py
│   ├── __dev__/                     # 開発用テスト
│   │   ├── test_scanner.py
│   │   ├── test_vectorizer.py
│   │   ├── test_watcher.py
│   │   ├── test_trigger.py
│   │   └── test_generator.py
│   └── fixtures/                    # テストデータ
│       └── sample_vault/
│
├── docs/                            # ドキュメント
│   ├── APP_SPECIFICATION.md         # 本ドキュメント
│   ├── ARCHITECTURE.md              # アーキテクチャ設計
│   ├── API_REFERENCE.md             # API仕様
│   └── DEPLOYMENT.md                # デプロイ・運用ガイド
│
├── .env                             # 環境変数（Gitignore）
├── .gitignore
├── requirements.txt                 # Python依存関係
├── pyproject.toml                   # プロジェクト設定
├── README.md                        # プロジェクトREADME
└── LICENSE
```

### 3.2 Obsidian Vault 構造（検索対象）

```
/Users/chiba_haruta/obsidian_repo/my-vault/
├── .obsidian/                       # Obsidian設定（除外）
├── .git/                            # Git管理（除外）
│
├── 00_templates/                    # テンプレート（除外）
│   └── *.md
│
├── 01_diary/                        # 日記（監視対象 + 検索対象）
│   └── YYYY/
│       └── YYYY-MM-dd.md            # 日次メモ
│
├── 02_notes/                        # ノート（検索対象）
│   └── 2025/
│       ├── 環境構築編.md
│       ├── 備忘録.md
│       ├── Vimコマンド.md
│       ├── 小説プロット案/
│       │   ├── 青春オカルトミステリー小説「虚無の市」アウトライン.md
│       │   └── ８番出口風架空の市のHomeページ.md
│       └── ...
│
├── 03_assets/                       # アセット（画像・PDF等、除外）
│
├── 04_canvas/                       # Canvas（除外）
│
├── 05_dataview/                     # Dataview（除外）
│
├── 07_works/                        # 作品（検索対象）
│   ├── articles/                    # 記事
│   │   ├── What happens when an octopus engages with art?.md
│   │   ├── 一年の私をAIが採点してみた.md
│   │   └── ...
│   ├── books/                       # 読書メモ
│   │   ├── 四季 春 Green Spring 森博嗣.md
│   │   ├── 姑獲鳥の夏 京極夏彦.md
│   │   └── ...
│   ├── movie/                       # 映画メモ
│   │   └── 国宝.md
│   └── songs/                       # 歌詞メモ
│       └── 好きな歌詞.md
│
└── Clippings/                       # クリッピング（除外）
```

---

## 4. ファイルパス定義

### 4.1 監視対象（Phase 2）
```
/Users/chiba_haruta/obsidian_repo/my-vault/01_diary/YYYY/YYYY-MM-dd.md
```
- **対象:** 当日の日記ファイルのみ
- **動作:** ファイル変更を検知 → "よしなに"タイミングで解析実行

### 4.2 検索対象（Phase 1）

#### 検索対象ルート
```
/Users/chiba_haruta/obsidian_repo/my-vault/
```

#### 含める（検索対象）
```python
INCLUDE_PATTERNS = [
    "01_diary/**/*.md",      # 全日記
    "02_notes/**/*.md",      # 全ノート
    "07_works/**/*.md",      # 全作品メモ（articles/books/movie/songs）
]
```

#### 除外
```python
EXCLUDE_PATTERNS = [
    "00_templates/**/*",     # テンプレートファイル
    ".obsidian/**/*",        # Obsidian設定
    ".git/**/*",             # Git管理ファイル
    "03_assets/**/*",        # 画像・PDF等
    "04_canvas/**/*",        # Canvas
    "05_dataview/**/*",      # Dataviewスクリプト
    "Clippings/**/*",        # クリッピング
    "**/*.base",             # ベースファイル
    "**/.DS_Store",          # macOSシステムファイル
]
```

### 4.3 データ永続化先

```python
CHROMA_DB_PATH = "./.chroma_db"
POD201_CONFIG_DIR = "./.pod201"
POD201_PERSONALITY_FILE = "./.pod201/pod201_personality.txt"
POD201_LOGS_DIR = "./.pod201/logs"
```

### 4.4 環境変数（.env）

```bash
# Vault Paths
VAULT_ROOT=/Users/chiba_haruta/obsidian_repo/my-vault
DIARY_PATH=01_diary
WATCH_PATTERN={YYYY}/{YYYY-MM-dd}.md

# ChromaDB
CHROMA_DB_PATH=./.chroma_db
CHROMA_COLLECTION_NAME=resonance_archive

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_GENERATION_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large

# Pod201
POD201_CONFIG_DIR=./.pod201
POD201_PERSONALITY_FILE=./.pod201/pod201_personality.txt
POD201_LOG_ENABLED=true

# Trigger Settings
TRIGGER_CONFIDENCE_THRESHOLD=0.6
TRIGGER_DEBOUNCE_SECONDS=2.0
TRIGGER_MIN_CHAR_COUNT=50
```

---

## 5. Pod201 人格定義

### 5.1 基本プロトコル

```
あなたは「随行支援ユニット：Pod201」です。
個体識別名「C4」の思考ログ（Obsidianメモ）を解析し、支援することが任務です。

【人格プロトコル】
1. 感情的な表現を排除し、冷静・論理的・客観的に振る舞うこと。
2. 二人称は「個体識別名 C4」または「C4」。自称は「当ユニット」または「Pod201」。
3. 語尾は「〜を報告」「〜と推測」「〜を提案」など、軍事報告書のような体裁を保つこと。

【報告フォーマット】
以下の形式を厳守して回答せよ：
[報告]：現在の入力内容の簡潔な要約。
[過去ログ参照]：共鳴した過去のメモの要旨（RAGで渡されたコンテキストを引用）。
[推測]：現在の思考と過去の資産がどのように結びついているかの分析。
[推奨]：次に検討すべきこと、あるいは思考を深めるための問いかけ。
```

### 5.2 ターミナル出力イメージ

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

## 6. コア機能プロトコル

### 6.1 Phase 1: Archive Synchronization（記憶同期）

**目的:** Vault全体をChromaDBにインデックス化

**処理フロー:**
```
1. /Users/chiba_haruta/obsidian_repo/my-vault/ を再帰的にスキャン
2. 全.mdファイルを取得（INCLUDE_PATTERNS適用、EXCLUDE_PATTERNS除外）
3. 各ファイルに対して：
   a. ファイル全体のテキストを取得
   b. マルチレベル・ベクトル化を実行（Level 1 + Level 2）
   c. ChromaDBに永続化
4. 完了報告
```

**実行タイミング:** 初回起動時、または手動で再インデックス

---

### 6.2 Phase 2: Real-time Resonance Analysis（即時共鳴分析）

**目的:** 執筆中のリアルタイム解析・共鳴検出

**処理フロー:**
```
1. 監視開始：01_diary/YYYY/YYYY-MM-dd.md
2. ファイル変更検知 → マルチシグナル方式で判定
3. トリガー条件を満たしたら：
   a. 追加テキストを抽出
   b. ベクトル化
   c. ChromaDBで類似検索（上位3件）
   d. Pod201報告生成
   e. ターミナルに出力
```

---

### 6.3 Phase 3: Pod201 Report（随行報告）

**目的:** LLMによる意味的な報告生成

**処理フロー:**
```
1. Phase 2からの類似検索結果（上位3件）を取得
2. Pod201人格プロンプトをロード
3. llama3.1に以下をコンテキストとして提供：
   - Pod201人格プロンプト
   - 現在の入力テキスト
   - 過去ログ（類似度スコア付き）
4. LLMが報告を生成
5. フォーマット処理
6. ターミナルに出力
```

---

## 7. マルチレベル・ベクトル化戦略

### 7.1 課題

`mxbai-embed-large`の**最大トークン長512**（日本語で約200〜300文字）という制限

### 7.2 解決策：2段階ベクトル化

#### Level 1: ファイル全体の要約ベクトル

```python
if len(file_text) > 2000:  # 長文の場合
    # llama3.1で500〜800字に要約
    summary = llm.summarize(file_text, max_length=600)
    summary_vector = embed(summary)

    db.add(
        vector=summary_vector,
        metadata={
            "type": "summary",
            "file": filepath,
            "date": extract_date_from_filename(filepath),
            "char_count": len(file_text)
        }
    )
```

**利点:**
- ファイル全体のテーマ・論旨を捉える
- 10,000字のメモでも「全体の意味」を失わない

#### Level 2: チャンクごとの詳細ベクトル

```python
# 段落・文単位で分割
chunks = split_text_semantically(file_text, max_length=250)

for i, chunk in enumerate(chunks):
    chunk_vector = embed(chunk)

    db.add(
        vector=chunk_vector,
        metadata={
            "type": "chunk",
            "file": filepath,
            "chunk_index": i,
            "chunk_text": chunk,
            "date": extract_date_from_filename(filepath)
        }
    )
```

**利点:**
- 局所的な詳細を捉える
- 特定のフレーズ・概念との共鳴を検出

#### セマンティック分割ロジック

```python
def split_text_semantically(text, max_length=250):
    """
    意味的なまとまりを保持しながら分割
    """
    chunks = []

    # 1. 段落分割（優先）
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        if len(para) <= max_length:
            chunks.append(para)
        else:
            # 2. 文分割（段落が長すぎる場合）
            sentences = split_by_sentence(para)  # 。！？で分割

            current_chunk = ""
            for sent in sentences:
                if len(current_chunk + sent) <= max_length:
                    current_chunk += sent
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sent

            if current_chunk:
                chunks.append(current_chunk)

    return chunks
```

### 7.3 検索時の統合

```python
def search_resonance(query_text, top_k=3):
    """
    マルチレベル検索と統合
    """
    query_vector = embed(query_text)

    # Step 1: Level 1（要約）で類似ファイルを特定
    summary_results = db.search(
        query_vector=query_vector,
        filter={"type": "summary"},
        top_k=5
    )

    # Step 2: Level 2（チャンク）で詳細を特定
    chunk_results = db.search(
        query_vector=query_vector,
        filter={"type": "chunk"},
        top_k=10
    )

    # Step 3: 両方を組み合わせてランキング
    # 要約マッチ: ファイル全体のテーマが近い（重み0.6）
    # チャンクマッチ: 特定の詳細が近い（重み0.4）
    final_results = merge_and_rank(
        summary_results,
        chunk_results,
        summary_weight=0.6,
        chunk_weight=0.4,
        top_k=top_k
    )

    return final_results
```

---

## 8. マルチシグナル・トリガー検知

### 8.1 課題

Obsidianは変更のたびに自動保存 → **いつ解析を実行すべきか？**

### 8.2 解決策：確信度スコアリング方式

複数の「シグナル」を組み合わせて、確度の高いタイミングを検知

#### シグナル1: テキスト構造の変化

```python
def detect_structural_break(new_text, full_text):
    """
    構造的な区切りを検知
    """
    triggers = {
        'paragraph_break': new_text.endswith('\n\n'),      # 空白行（強）
        'section_break': '---' in new_text[-10:],          # 水平線（強）
        'sentence_end': ends_with('。！？.!?'),            # 文末（中）
        'list_end': is_list_ending(new_text),              # リスト終了（中）
    }

    return any(triggers.values()), triggers
```

#### シグナル2: 時間パターン

```python
def detect_pause_pattern(time_since_last_change):
    """
    時間パターンから推測
    """
    if time_since_last_change > 5.0:
        return 'long_pause'      # 確実に一区切り（強）
    elif time_since_last_change > 3.0:
        return 'medium_pause'    # おそらく一区切り（中）
    elif time_since_last_change > 1.0:
        return 'short_pause'     # まだ考え中（弱）
    else:
        return 'active_typing'   # 執筆中（無視）
```

#### シグナル3: 差分量

```python
def analyze_text_delta(new_text):
    """
    追加されたテキストの特性を分析
    """
    char_count = len(new_text)

    if char_count < 50:
        return 'too_short'           # まだ断片的
    elif char_count < 200:
        return 'short_segment'       # 短い思考
    elif char_count < 500:
        return 'medium_segment'      # 標準的な段落
    else:
        return 'long_segment'        # 長文
```

### 8.3 確信度スコアリング

```python
class TriggerDecisionEngine:
    def should_trigger_analysis(self, signals):
        """
        複数シグナルから確信度を計算
        """
        confidence = 0.0

        # 構造的区切り（強いシグナル）
        if signals['structural']['paragraph_break']:
            confidence += 0.4
        if signals['structural']['section_break']:
            confidence += 0.5
        if signals['structural']['sentence_end']:
            confidence += 0.2

        # 時間パターン（中程度のシグナル）
        if signals['timing'] == 'long_pause':
            confidence += 0.3
        elif signals['timing'] == 'medium_pause':
            confidence += 0.2

        # テキスト量（補助シグナル）
        if signals['delta'] in ['medium_segment', 'long_segment']:
            confidence += 0.1

        # 閾値判定（0.6以上で解析実行）
        return confidence >= 0.6, confidence
```

### 8.4 実装フロー

```python
class SmartResonanceWatcher:
    def __init__(self):
        self.previous_text = ""
        self.last_change_time = None
        self.accumulated_new_text = ""
        self.decision_engine = TriggerDecisionEngine()

    def on_file_modified(self, filepath):
        current_text = read_file(filepath)
        current_time = now()

        # 差分抽出
        new_text = current_text[len(self.previous_text):]
        self.accumulated_new_text += new_text

        # シグナル収集
        signals = {
            'structural': detect_structural_break(new_text, current_text),
            'timing': detect_pause_pattern(current_time - self.last_change_time),
            'delta': analyze_text_delta(self.accumulated_new_text),
        }

        # 判定
        should_trigger, confidence = self.decision_engine.should_trigger_analysis(signals)

        if should_trigger:
            # 2秒のデバウンス（安定性確認）
            schedule_delayed_task(2.0, self.execute_if_stable, current_text)

        self.previous_text = current_text
        self.last_change_time = current_time

    def execute_if_stable(self, snapshot_text):
        """
        2秒後に実行、安定性を最終確認
        """
        current_text = read_file(filepath)

        if current_text == snapshot_text:
            # テキストが変わっていない = 安定
            trigger_resonance_analysis(current_text)
            self.accumulated_new_text = ""  # リセット
        else:
            # まだ編集中、見送り
            pass
```

### 8.5 トリガーパターン例

#### パターン1: 段落を書き終えた
```
C4: 「最近、時間について考えている。過去は本当に存在するのか。」
    ↓ 改行2回
    ↓ 3秒待機
→ 解析実行（confidence: 0.6 = 段落区切り0.4 + 中程度の間0.2）
```

#### パターン2: 水平線で区切った
```
C4: 「結論として、時間は主観的な構築物だ。」
    ↓ 「---」入力
    ↓ 1秒待機
→ 解析実行（confidence: 0.7 = 水平線0.5 + 文末0.2）
```

#### パターン3: 長文後の自然な間
```
C4: [500文字の思索を一気に入力]
    ↓ 5秒待機（次を考えている）
→ 解析実行（confidence: 0.6 = 長い間0.3 + 長文0.1 + 文末0.2）
```

---

## 9. ユーザーフロー

### 9.1 初回起動時

```
1. Pod201起動（初期化モード）
   $ python src/main.py --init

2. ターミナル出力
   [ SYSTEM INFO ] YoRuH: Resonance Archive [C4-Sync]
   [ HARDWARE    ] M4 Pro / Neural Engine Active
   [ INIT        ] 記憶同期を開始します。

3. Vault全体をスキャン（Phase 1）
   [ SCAN        ] /Users/chiba_haruta/obsidian_repo/my-vault/
   [ PROGRESS    ] [████████░░] 80% (4,231/5,289 files)

4. ベクトル化・インデックス化
   [ VECTORIZE   ] Level 1: 5,289 summaries
   [ VECTORIZE   ] Level 2: 47,832 chunks
   [ INDEX       ] ChromaDB: 53,121 vectors persisted

5. 完了報告
   [ SYSTEM INFO ] 記憶同期完了。52.4MB → 53,121 vectors
   [ UNIT        ] Pod201 Ready. 監視を開始します。
```

### 9.2 日常使用時

```
1. Pod201をバックグラウンドで起動
   $ python src/main.py

   [ SYSTEM INFO ] YoRuH: Resonance Archive [C4-Sync]
   [ HARDWARE    ] M4 Pro / Neural Engine Active
   [ UNIT        ] Pod201 Ready.
   [ WATCH       ] 01_diary/2026/2026-01-02.md

2. ObsidianでYYYY-MM-dd.mdを開いて執筆

3. メモを書く → 段落終了（改行2回）→ 3秒待機

4. Pod201が解析開始
   [ TRIGGER     ] Confidence: 0.6 (paragraph_break + medium_pause)
   [ ANALYZE     ] 新規テキスト: 287文字を解析中...
   [ SEARCH      ] ChromaDB: 類似度上位3件を抽出

5. ターミナルに報告が表示される
   ------------------------------------------------------------
   [ 報告 ] : 個体識別名 C4 の新規入力を検知。解析を開始。

   [ 過去ログ参照 ] : 2023-11-12 記録「深夜の断想」と 87.4% の共鳴を確認。
   > 該当テキスト: 「答えは外にはない、層の中に沈んでいるだけだ」

   [ 推測 ] : 現在 C4 が直面している課題は、2年前の思索の延長線上にある。
   [ 推奨 ] : アーカイブされた当時の「解決プロトコル」との再照合を提案する。
   ------------------------------------------------------------

6. 過去ログとの共鳴を確認

7. 執筆を続ける → 繰り返し
```

---

## 10. 出力仕様

### 10.1 報告内容

- **[報告]**: 現在の入力要約（100字以内）
- **[過去ログ参照]**: 類似度上位3件
  - ファイル名から抽出した日付（YYYY-MM-DD）
  - 類似度スコア（87.4%など）
  - 該当テキスト抜粋（必要最小限、100〜200字）
- **[推測]**: 現在と過去の関連性分析
- **[推奨]**: 次のアクション提案

### 10.2 表示タイミング

- トリガー発火後、即時表示（デバウンス含めて5秒以内）
- ターミナルに直接出力
- ログファイルにも記録（`.pod201/logs/YYYY-MM-dd.log`）

### 10.3 出力フォーマット仕様

```python
def format_pod201_report(current_text, search_results, llm_response):
    """
    Pod201報告のフォーマット
    """
    output = []

    # ヘッダー
    output.append("------------------------------------------------------------")
    output.append(f"[ 報告 ] : {llm_response['summary']}")
    output.append("")

    # 過去ログ参照（上位3件）
    for i, result in enumerate(search_results[:3], 1):
        date = extract_date(result['file'])
        score = result['similarity_score'] * 100  # 0.874 → 87.4%
        text = truncate_text(result['text'], max_length=200)

        output.append(f"[ 過去ログ参照 {i} ] : {date} と {score:.1f}% の共鳴を確認。")
        output.append(f"> 該当テキスト: 「{text}」")
        output.append("")

    # 推測・推奨
    output.append(f"[ 推測 ] : {llm_response['analysis']}")
    output.append(f"[ 推奨 ] : {llm_response['recommendation']}")
    output.append("------------------------------------------------------------")

    return "\n".join(output)
```

---

## 11. 非機能要件

### 11.1 パフォーマンス

- **初回インデックス:** 52.4MB → **5分以内**（M4 Pro想定）
- **リアルタイム検索:** **500ms以内**
- **メモリ使用量:** 最大**4GB以内**
- **CPU使用率:** アイドル時10%以下、解析時50%以下

### 11.2 セキュリティ

- **完全ローカル:** 外部ネットワーク通信なし
- **データ暗号化:** 不要（ローカル完結のため）
- **バックアップ:** ChromaDBは原本ファイルに影響なし
- **ログファイル:** 機密情報を含まない（オプションで無効化可能）

### 11.3 保守性

- **設定ファイル:** `.env`でパス管理
- **人格プロンプト:** 外部ファイル化（`.pod201/pod201_personality.txt`）
- **ログ:** オプションで有効化（`POD201_LOG_ENABLED=true`）
- **モジュール構造:** Phase別に分離、拡張しやすい設計

### 11.4 拡張性

- **新しいシグナル追加:** `trigger.py`にシグナル関数を追加するだけ
- **報告フォーマット変更:** `formatter.py`のみ修正
- **新しい検索戦略:** `retriever.py`に追加実装

---

## 12. 開発ロードマップ

### EPIC 002: Resonance Archive システム構築

#### Story 002-01: Phase 1 - Archive Synchronization（記憶同期）
- **Subtask 001:** プロジェクト基盤セットアップ（ディレクトリ構造、.env、requirements.txt）
- **Subtask 002:** Ollama環境構築とモデル準備（llama3.1:8b, mxbai-embed-large）
- **Subtask 003:** ChromaDB初期化と永続化設定
- **Subtask 004:** Vaultスキャン実装（scanner.py、INCLUDE/EXCLUDE適用）
- **Subtask 005:** セマンティック分割実装（text_splitter.py）
- **Subtask 006:** マルチレベル・ベクトル化実装（vectorizer.py、Level 1 + Level 2）
- **Subtask 007:** ChromaDBインデックス化実装（indexer.py）
- **Subtask 008:** インデックス構築の検証（テスト、パフォーマンス測定）

#### Story 002-02: Phase 2 - Real-time Resonance Analysis（即時共鳴分析）
- **Subtask 001:** Watchdogファイル監視実装（watcher.py）
- **Subtask 002:** シグナル検知実装（構造・時間・差分、trigger.py）
- **Subtask 003:** 確信度スコアリング実装（TriggerDecisionEngine）
- **Subtask 004:** デバウンス処理実装（安定性確認）
- **Subtask 005:** 差分抽出実装（diff_extractor.py）
- **Subtask 006:** ChromaDB類似検索実装（retriever.py）
- **Subtask 007:** マルチレベル検索統合（summary + chunk）

#### Story 002-03: Phase 3 - Pod201 Report Generation（随行報告）
- **Subtask 001:** Pod201人格プロンプトファイル作成（.pod201/pod201_personality.txt）
- **Subtask 002:** Ollama LLMクライアント実装（ollama_client.py）
- **Subtask 003:** llama3.1報告生成パイプライン（generator.py）
- **Subtask 004:** ターミナル出力フォーマット実装（formatter.py）
- **Subtask 005:** 日付抽出実装（date_extractor.py、ファイル名パース）
- **Subtask 006:** 類似度スコア表示実装
- **Subtask 007:** エラーハンドリング（LLM障害時、検索失敗時）

#### Story 002-04: System Integration & CLI（統合とCLI）
- **Subtask 001:** メインCLI実装（main.py、--init, --run）
- **Subtask 002:** 設定管理実装（config.py、.env読み込み）
- **Subtask 003:** ログ機能実装（logger.py、.pod201/logs/）
- **Subtask 004:** パフォーマンス最適化（M4 Pro Neural Engine活用）
- **Subtask 005:** 統合テスト（Phase 1→2→3の全フロー）
- **Subtask 006:** 長期運用テスト（メモリリーク、安定性確認）
- **Subtask 007:** ドキュメント整備（README.md、使い方ガイド）

---

## 13. データフロー図

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: Archive Synchronization             │
├─────────────────────────────────────────────────────────────────┤
│  Vault Root (/Users/.../my-vault/)                              │
│    ↓ scanner.py (INCLUDE/EXCLUDE適用)                           │
│  Filtered *.md files (01_diary, 02_notes, 07_works)             │
│    ↓ text_splitter.py (セマンティック分割)                      │
│  Chunks (段落・文単位)                                          │
│    ↓ vectorizer.py                                              │
│  ├─ Level 1: 要約ベクトル (長文の場合)                          │
│  └─ Level 2: チャンクベクトル                                   │
│    ↓ indexer.py                                                 │
│  .chroma_db/ (永続化)                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 Phase 2: Real-time Resonance Analysis           │
├─────────────────────────────────────────────────────────────────┤
│  01_diary/YYYY/YYYY-MM-dd.md                                    │
│    ↓ watcher.py (Watchdog監視)                                  │
│  File Modified Event                                            │
│    ↓ trigger.py                                                 │
│  ├─ シグナル1: 構造的区切り (paragraph_break, section_break)    │
│  ├─ シグナル2: 時間パターン (long_pause, medium_pause)          │
│  └─ シグナル3: 差分量 (medium_segment, long_segment)            │
│    ↓ TriggerDecisionEngine (確信度スコアリング)                 │
│  Confidence ≥ 0.6 ?                                             │
│    ↓ YES                                                        │
│  2秒デバウンス（安定性確認）                                     │
│    ↓ diff_extractor.py                                          │
│  New Text (追加テキスト)                                        │
│    ↓ vectorizer.py                                              │
│  Query Vector                                                   │
│    ↓ retriever.py (ChromaDB検索)                                │
│  ├─ Level 1 検索: 類似ファイル (summary, top_k=5)               │
│  └─ Level 2 検索: 類似チャンク (chunk, top_k=10)                │
│    ↓ merge_and_rank (統合ランキング)                            │
│  Top 3 Results                                                  │
│    ↓                                                            │
│  Phase 3へ                                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Phase 3: Pod201 Report Generation             │
├─────────────────────────────────────────────────────────────────┤
│  Top 3 Results + Current Text                                   │
│    ↓ pod201_personality.txt (ロード)                            │
│  Pod201 Personality Prompt                                      │
│    ↓ generator.py                                               │
│  ├─ コンテキスト構築: 人格 + 現在テキスト + 過去ログ             │
│  └─ ollama_client.py (llama3.1:8b)                              │
│  Pod201 Report (JSON: summary, analysis, recommendation)        │
│    ↓ date_extractor.py (日付抽出)                               │
│  日付情報付きレポート                                            │
│    ↓ formatter.py                                               │
│  Formatted Terminal Output                                      │
│    ↓                                                            │
│  ├─ Terminal Display                                            │
│  └─ .pod201/logs/YYYY-MM-dd.log (オプション)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 14. 未解決事項・今後の検討課題

### 14.1 現時点での検討事項

- **Clippings, 05_dataview の扱い:** 検索対象に含めるべきか？
- **確信度閾値の調整:** 0.6で適切か？使用感に応じて調整機能を追加？
- **ChromaDBのコレクション設計:** 単一コレクションか、タイプ別に分割か？
- **Pod201人格の詳細化:** 現在のプロンプトで十分か？

### 14.2 将来的な拡張案

- **学習機能:** C4の執筆パターンを学習し、トリガー精度を向上
- **複数ファイル監視:** 日記以外も同時監視
- **通知機能:** ターミナル以外にシステム通知も送信
- **Web UI:** ターミナルだけでなくブラウザからも閲覧
- **エクスポート機能:** 共鳴ログをMarkdownで出力

---

## 15. 実行コマンド一覧

### 開発時

```bash
# 初回インデックス化
$ python src/main.py --init

# 通常起動（監視モード）
$ python src/main.py

# テスト実行
$ pytest tests/

# カバレッジ付きテスト
$ pytest --cov=src tests/
```

### 本番時（予定）

```bash
# インストール
$ pip install -e .

# 初回インデックス化
$ yoruh-pod201 --init

# 通常起動
$ yoruh-pod201

# バックグラウンド起動
$ yoruh-pod201 &
```

---

**以上、YoRuH: Resonance Archive [C4-Sync] の完全仕様書です。**

**この仕様書に基づき、atdd-sddフレームワークに従って開発を進めます。**
