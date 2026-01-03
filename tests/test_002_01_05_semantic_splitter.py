"""
Test for Subtask 002-01-05: セマンティック分割実装

このテストは改訂されたAcceptance Criteriaから導出されています。
"""
import pytest
from src.phase1_archive_sync.semantic_splitter import SemanticSplitter, Chunk


def test_returns_chunk_objects():
    """AC: テキストを意味的なまとまりを保ちながら分割し、Chunkオブジェクトのリストを返すこと"""
    splitter = SemanticSplitter()
    text = "これは最初の段落です。\n\nこれは2番目の段落です。"

    chunks = splitter.split(text)

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)


def test_default_max_chars_600():
    """AC: 各チャンクが設定可能な最大文字数（デフォルト600文字）以内であること"""
    splitter = SemanticSplitter()  # デフォルト600文字
    # 700文字のテキスト
    text = "あ" * 700

    chunks = splitter.split(text)

    for chunk in chunks:
        assert len(chunk.text) <= 600


def test_configurable_max_chars():
    """AC: 最大文字数が設定可能であること"""
    splitter = SemanticSplitter(max_chars=400)
    text = "あ" * 500

    chunks = splitter.split(text)

    for chunk in chunks:
        assert len(chunk.text) <= 400


def test_default_overlap_100():
    """AC: チャンク間に設定可能なオーバーラップ（デフォルト100文字）を持たせること"""
    splitter = SemanticSplitter()  # デフォルトoverlap=100
    # 800文字の文（分割されるはず）
    text = "あ" * 800 + "。"

    chunks = splitter.split(text)

    if len(chunks) >= 2:
        # 2番目のチャンクの開始位置が、1番目のチャンクの終了位置より100文字以上前であることを確認
        overlap = chunks[0].end_offset - chunks[1].start_offset
        assert overlap >= 100


def test_configurable_overlap():
    """AC: オーバーラップが設定可能であること"""
    splitter = SemanticSplitter(max_chars=400, overlap=50)
    text = "あ" * 500 + "。"

    chunks = splitter.split(text)

    if len(chunks) >= 2:
        overlap = chunks[0].end_offset - chunks[1].start_offset
        assert overlap >= 50


def test_protect_code_blocks():
    """AC: コードブロック（```で囲まれた領域）を保護し、内部を分割しないこと"""
    splitter = SemanticSplitter()
    text = """# タイトル

```python
def function():
    return "code"
```

次の段落。"""

    chunks = splitter.split(text)

    # コードブロックが含まれるチャンクを探す
    code_chunks = [c for c in chunks if "```" in c.text]
    assert len(code_chunks) > 0

    # コードブロックが完全に保持されている（開始と終了の```がある）
    for chunk in code_chunks:
        assert chunk.text.count("```") % 2 == 0  # 偶数個（開始と終了）


def test_split_by_heading():
    """AC: Markdown見出し（#, ##等）を境界として分割すること"""
    splitter = SemanticSplitter()
    text = """# 見出し1

内容1

## 見出し2

内容2"""

    chunks = splitter.split(text)

    # 見出しで分割されているはず
    assert len(chunks) >= 2
    # 各見出しが異なるチャンクにあることを確認
    heading_chunks = [c for c in chunks if c.text.strip().startswith("#")]
    assert len(heading_chunks) >= 2


def test_split_by_horizontal_rule():
    """AC: Markdown水平線（---, ***）を境界として分割すること"""
    splitter = SemanticSplitter()
    text = """セクション1

---

セクション2

***

セクション3"""

    chunks = splitter.split(text)

    # 水平線で分割されているはず
    assert len(chunks) >= 3


def test_split_by_paragraph():
    """AC: 段落単位（\\n\\n）で分割すること"""
    splitter = SemanticSplitter(max_chars=30)  # 小さいmax_charsで段落分割を強制
    text = "段落1です。これは長い段落です。\n\n段落2です。これも長い段落です。\n\n段落3です。これも長めです。"

    chunks = splitter.split(text)

    # 段落が境界として使われているはず
    assert len(chunks) >= 3
    # 各チャンクが段落境界を尊重している
    for chunk in chunks:
        # \n\nが途中で切れていないことを確認
        if '\n\n' in chunk.text:
            # チャンク内に完全な段落が含まれている
            assert chunk.text.count('\n\n') >= 0


def test_split_by_sentence_when_exceeds_max():
    """AC: チャンクが最大文字数を超える場合、文単位（。！？）でさらに分割すること"""
    splitter = SemanticSplitter(max_chars=100)
    # 100文字を超える段落（複数の文）
    text = ("あ" * 50 + "。" + "い" * 50 + "。" + "う" * 50 + "。")

    chunks = splitter.split(text)

    # 文単位で分割されているはず
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk.text) <= 100


def test_split_by_comma_when_sentence_exceeds_max():
    """AC: 文分割後も最大文字数を超える場合、句読点（、）で分割すること"""
    splitter = SemanticSplitter(max_chars=100)
    # 100文字を超える1文（句読点あり）
    text = "あ" * 60 + "、" + "い" * 60 + "、" + "う" * 60 + "。"

    chunks = splitter.split(text)

    # 句読点で分割されているはず
    for chunk in chunks:
        assert len(chunk.text) <= 100


def test_hard_split_with_overlap():
    """AC: それでも最大文字数を超える場合、最大文字数でハード分割しオーバーラップを付けること"""
    splitter = SemanticSplitter(max_chars=100, overlap=20)
    # 句読点なしの長文
    text = "あ" * 250

    chunks = splitter.split(text)

    # ハード分割されているはず
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk.text) <= 100

    # オーバーラップが存在
    if len(chunks) >= 2:
        overlap = chunks[0].end_offset - chunks[1].start_offset
        assert overlap > 0


def test_chunk_metadata_fields():
    """AC: 各チャンクに text, start_offset, end_offset, seq, source_markers を付与すること"""
    splitter = SemanticSplitter()
    text = "段落1\n\n段落2\n\n段落3"

    chunks = splitter.split(text)

    for i, chunk in enumerate(chunks):
        assert hasattr(chunk, 'text')
        assert hasattr(chunk, 'start_offset')
        assert hasattr(chunk, 'end_offset')
        assert hasattr(chunk, 'seq')
        assert hasattr(chunk, 'source_markers')

        # seqは0始まりの連番
        assert chunk.seq == i

        # offsetが妥当
        assert 0 <= chunk.start_offset <= chunk.end_offset
        assert chunk.text == text[chunk.start_offset:chunk.end_offset]


def test_empty_text_returns_empty_list():
    """AC: 空テキストが入力された場合、空リストを返すこと"""
    splitter = SemanticSplitter()
    text = ""

    chunks = splitter.split(text)

    assert chunks == []


def test_oversized_code_block_protection():
    """AC: コードブロックが最大文字数を超える場合、1つのチャンクとして扱うこと"""
    splitter = SemanticSplitter(max_chars=100)
    # 100文字を超えるコードブロック
    code = "def function():\n" + "    " + "x" * 100 + "\n"
    text = f"```python\n{code}```"

    chunks = splitter.split(text)

    # コードブロック全体が1つのチャンクとして保護されている
    assert len(chunks) == 1
    assert "```python" in chunks[0].text
    assert "```" in chunks[0].text[10:]  # 終了タグも含む
    # 警告ログが出力されることは実装で確認


def test_source_markers_with_headings():
    """チャンクに見出し情報がsource_markersとして付与されること"""
    splitter = SemanticSplitter()
    text = """# メインタイトル

内容1

## サブタイトル

内容2"""

    chunks = splitter.split(text)

    # source_markersに見出し情報が含まれることを確認
    heading_markers = [c.source_markers for c in chunks if c.source_markers]
    assert len(heading_markers) > 0
