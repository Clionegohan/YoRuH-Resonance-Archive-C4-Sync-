"""
Test for Subtask 002-02-02: 構造的シグナル検知実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from src.phase2_realtime_analysis.structural_signal_detector import (
    StructuralSignalDetector,
    StructuralSignal
)


def test_detector_class_exists():
    """AC: StructuralSignalDetectorクラスを提供すること"""
    detector = StructuralSignalDetector()
    assert detector is not None


def test_detect_method_exists():
    """AC: detect(text: str)メソッドを提供すること"""
    detector = StructuralSignalDetector()
    assert hasattr(detector, 'detect')
    assert callable(detector.detect)


def test_detect_paragraph_break():
    """AC: 段落区切り（\\n\\n）が含まれる場合、type="paragraph_break"のシグナルを検知すること"""
    detector = StructuralSignalDetector()
    text = "First paragraph.\n\nSecond paragraph."

    signals = detector.detect(text)

    # Should detect paragraph break
    paragraph_breaks = [s for s in signals if s.type == "paragraph_break"]
    assert len(paragraph_breaks) > 0

    # Check first paragraph break
    signal = paragraph_breaks[0]
    assert signal.type == "paragraph_break"
    assert signal.pattern == "\n\n"
    assert signal.position == 16  # After "First paragraph."


def test_detect_horizontal_rule():
    """AC: 水平線（---）が含まれる場合、type="horizontal_rule"のシグナルを検知すること"""
    detector = StructuralSignalDetector()
    text = "Before line.\n---\nAfter line."

    signals = detector.detect(text)

    # Should detect horizontal rule
    horizontal_rules = [s for s in signals if s.type == "horizontal_rule"]
    assert len(horizontal_rules) > 0

    # Check horizontal rule
    signal = horizontal_rules[0]
    assert signal.type == "horizontal_rule"
    assert signal.pattern == "---"
    assert signal.position == 13  # After "Before line.\n"


def test_detect_sentence_end():
    """AC: 文末（。！？）が含まれる場合、type="sentence_end"のシグナルを検知すること"""
    detector = StructuralSignalDetector()
    text = "文章です。次の文！最後？"

    signals = detector.detect(text)

    # Should detect sentence ends
    sentence_ends = [s for s in signals if s.type == "sentence_end"]
    assert len(sentence_ends) == 3

    # Check each sentence end
    assert sentence_ends[0].pattern == "。"
    assert sentence_ends[1].pattern == "！"
    assert sentence_ends[2].pattern == "？"


def test_signal_contains_required_fields():
    """AC: 各シグナルにtype, position, patternを含むこと"""
    detector = StructuralSignalDetector()
    text = "Test.\n\nParagraph."

    signals = detector.detect(text)

    assert len(signals) > 0
    signal = signals[0]

    # Should have required fields
    assert hasattr(signal, 'type')
    assert hasattr(signal, 'position')
    assert hasattr(signal, 'pattern')


def test_detect_multiple_signals():
    """AC: 複数の構造的シグナルが含まれる場合、全てのシグナルを位置順にリストで返すこと"""
    detector = StructuralSignalDetector()
    text = "First sentence。\n\nSecond paragraph.\n---\nThird section！"

    signals = detector.detect(text)

    # Should detect multiple signals
    assert len(signals) >= 4  # 。, \n\n, 。, ---, ！

    # Should be ordered by position
    positions = [s.position for s in signals]
    assert positions == sorted(positions)


def test_empty_text_returns_empty_list():
    """AC: 空文字列が入力された場合、空リストを返すこと"""
    detector = StructuralSignalDetector()
    signals = detector.detect("")

    assert signals == []


def test_no_signals_returns_empty_list():
    """AC: シグナルが見つからない場合、空リストを返すこと"""
    detector = StructuralSignalDetector()
    text = "Simple text without special patterns"

    signals = detector.detect(text)

    assert signals == []


def test_multiple_sentence_end_markers_at_same_position():
    """AC: 同じ位置に複数の文末記号がある場合、最初の文字のみを1つのシグナルとして検知すること"""
    detector = StructuralSignalDetector()
    text = "Really！？"

    signals = detector.detect(text)

    # Should detect only the first marker
    sentence_ends = [s for s in signals if s.type == "sentence_end"]

    # At position 6, only one signal should be detected (！)
    position_6_signals = [s for s in sentence_ends if s.position == 6]
    assert len(position_6_signals) == 1
    assert position_6_signals[0].pattern == "！"


def test_multiple_paragraph_breaks():
    """追加テスト: 複数の段落区切りを検知すること"""
    detector = StructuralSignalDetector()
    text = "Para1.\n\nPara2.\n\nPara3."

    signals = detector.detect(text)

    paragraph_breaks = [s for s in signals if s.type == "paragraph_break"]
    assert len(paragraph_breaks) == 2


def test_horizontal_rule_on_separate_line():
    """追加テスト: 独立行の水平線を検知すること"""
    detector = StructuralSignalDetector()
    text = "Content above.\n\n---\n\nContent below."

    signals = detector.detect(text)

    horizontal_rules = [s for s in signals if s.type == "horizontal_rule"]
    assert len(horizontal_rules) == 1
