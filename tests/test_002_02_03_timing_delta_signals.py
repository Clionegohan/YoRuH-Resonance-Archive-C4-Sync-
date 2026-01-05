"""
Test for Subtask 002-02-03: 時間・差分シグナル検知実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
import time
from src.phase2_realtime_analysis.timing_delta_signal_detector import (
    TimingDeltaSignalDetector,
    TimingSignal,
    DeltaSignal
)


def test_detector_class_exists():
    """AC: TimingDeltaSignalDetectorクラスを提供すること"""
    detector = TimingDeltaSignalDetector()
    assert detector is not None


def test_detect_method_exists():
    """AC: detect()メソッドを提供すること"""
    detector = TimingDeltaSignalDetector()
    assert hasattr(detector, 'detect')
    assert callable(detector.detect)


def test_detect_long_pause():
    """AC: 前回保存から5分以上経過した場合、type="long_pause"のシグナルを検知すること"""
    detector = TimingDeltaSignalDetector()

    previous_timestamp = time.time() - 301  # 5分1秒前
    current_timestamp = time.time()

    signals = detector.detect(
        previous_text="Previous content",
        previous_timestamp=previous_timestamp,
        current_text="Previous content\nNew content",
        current_timestamp=current_timestamp
    )

    # Should detect long_pause
    timing_signals = [s for s in signals if isinstance(s, TimingSignal)]
    long_pauses = [s for s in timing_signals if s.type == "long_pause"]

    assert len(long_pauses) == 1
    assert long_pauses[0].elapsed_seconds >= 300


def test_detect_medium_pause():
    """AC: 前回保存から2分以上5分未満経過した場合、type="medium_pause"のシグナルを検知すること"""
    detector = TimingDeltaSignalDetector()

    previous_timestamp = time.time() - 150  # 2分30秒前
    current_timestamp = time.time()

    signals = detector.detect(
        previous_text="Previous content",
        previous_timestamp=previous_timestamp,
        current_text="Previous content\nNew content",
        current_timestamp=current_timestamp
    )

    # Should detect medium_pause
    timing_signals = [s for s in signals if isinstance(s, TimingSignal)]
    medium_pauses = [s for s in timing_signals if s.type == "medium_pause"]

    assert len(medium_pauses) == 1
    assert 120 <= medium_pauses[0].elapsed_seconds < 300


def test_no_timing_signal_for_short_interval():
    """AC: 前回保存から2分未満の場合、時間シグナルは検知しないこと"""
    detector = TimingDeltaSignalDetector()

    previous_timestamp = time.time() - 60  # 1分前
    current_timestamp = time.time()

    signals = detector.detect(
        previous_text="Previous content",
        previous_timestamp=previous_timestamp,
        current_text="Previous content\nNew content",
        current_timestamp=current_timestamp
    )

    # Should not detect timing signals
    timing_signals = [s for s in signals if isinstance(s, TimingSignal)]
    assert len(timing_signals) == 0


def test_detect_large_delta():
    """AC: 追加文字数が100文字以上の場合、type="large_delta"のシグナルを検知すること"""
    detector = TimingDeltaSignalDetector()

    previous_text = "Short text"
    current_text = previous_text + ("a" * 150)  # 150文字追加

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    # Should detect large_delta
    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    large_deltas = [s for s in delta_signals if s.type == "large_delta"]

    assert len(large_deltas) == 1
    assert large_deltas[0].char_delta >= 100


def test_detect_medium_delta():
    """AC: 追加文字数が30文字以上100文字未満の場合、type="medium_delta"のシグナルを検知すること"""
    detector = TimingDeltaSignalDetector()

    previous_text = "Short text"
    current_text = previous_text + ("a" * 50)  # 50文字追加

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    # Should detect medium_delta
    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    medium_deltas = [s for s in delta_signals if s.type == "medium_delta"]

    assert len(medium_deltas) == 1
    assert 30 <= medium_deltas[0].char_delta < 100


def test_detect_small_delta():
    """AC: 追加文字数が10文字以上30文字未満の場合、type="small_delta"のシグナルを検知すること"""
    detector = TimingDeltaSignalDetector()

    previous_text = "Short text"
    current_text = previous_text + ("a" * 20)  # 20文字追加

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    # Should detect small_delta
    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    small_deltas = [s for s in delta_signals if s.type == "small_delta"]

    assert len(small_deltas) == 1
    assert 10 <= small_deltas[0].char_delta < 30


def test_no_delta_signal_for_small_change():
    """AC: 追加文字数が10文字未満の場合、差分シグナルは検知しないこと"""
    detector = TimingDeltaSignalDetector()

    previous_text = "Short text"
    current_text = previous_text + "abc"  # 3文字追加

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    # Should not detect delta signals
    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    assert len(delta_signals) == 0


def test_no_delta_signal_for_deletion():
    """AC: テキストが削除された場合（負の差分）、差分シグナルは検知しないこと"""
    detector = TimingDeltaSignalDetector()

    previous_text = "This is a long text with many characters"
    current_text = "Short"  # 削除

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    # Should not detect delta signals
    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    assert len(delta_signals) == 0


def test_timing_signal_contains_required_fields():
    """AC: 各時間シグナルにtype, elapsed_secondsを含むこと"""
    detector = TimingDeltaSignalDetector()

    previous_timestamp = time.time() - 200
    current_timestamp = time.time()

    signals = detector.detect(
        previous_text="Previous",
        previous_timestamp=previous_timestamp,
        current_text="Previous\nNew",
        current_timestamp=current_timestamp
    )

    timing_signals = [s for s in signals if isinstance(s, TimingSignal)]
    assert len(timing_signals) > 0

    signal = timing_signals[0]
    assert hasattr(signal, 'type')
    assert hasattr(signal, 'elapsed_seconds')


def test_delta_signal_contains_required_fields():
    """AC: 各差分シグナルにtype, char_deltaを含むこと"""
    detector = TimingDeltaSignalDetector()

    previous_text = "Short"
    current_text = previous_text + ("a" * 50)

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    assert len(delta_signals) > 0

    signal = delta_signals[0]
    assert hasattr(signal, 'type')
    assert hasattr(signal, 'char_delta')


def test_first_save_no_timing_signal():
    """AC: 前回保存情報がない場合（初回保存）、時間シグナルは検知せず、差分シグナルのみ検知すること"""
    detector = TimingDeltaSignalDetector()

    current_text = "a" * 100  # 100文字

    signals = detector.detect(
        previous_text=None,
        previous_timestamp=None,
        current_text=current_text,
        current_timestamp=time.time()
    )

    # Should not detect timing signals
    timing_signals = [s for s in signals if isinstance(s, TimingSignal)]
    assert len(timing_signals) == 0

    # Should detect delta signal (current_text as new content)
    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    assert len(delta_signals) == 1


def test_delta_calculation():
    """AC: 差分は len(current_text) - len(previous_text) で計算し、正の値のみをシグナル対象とすること"""
    detector = TimingDeltaSignalDetector()

    previous_text = "Hello"  # 5文字
    current_text = previous_text + " World!"  # +7文字 = 12文字

    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    assert len(delta_signals) == 0  # 7文字は10文字未満なので検知しない

    # Test with 15 character addition
    current_text = previous_text + ("a" * 15)  # +15文字
    signals = detector.detect(
        previous_text=previous_text,
        previous_timestamp=time.time() - 10,
        current_text=current_text,
        current_timestamp=time.time()
    )

    delta_signals = [s for s in signals if isinstance(s, DeltaSignal)]
    assert len(delta_signals) == 1
    assert delta_signals[0].char_delta == 15


def test_thresholds_are_configurable():
    """AC: 時間閾値と差分閾値をクラス定数として定義し、将来的に調整可能にすること"""
    # Check that thresholds are defined as class constants
    assert hasattr(TimingDeltaSignalDetector, 'LONG_PAUSE_SECONDS')
    assert hasattr(TimingDeltaSignalDetector, 'MEDIUM_PAUSE_SECONDS')
    assert hasattr(TimingDeltaSignalDetector, 'LARGE_DELTA_CHARS')
    assert hasattr(TimingDeltaSignalDetector, 'MEDIUM_DELTA_CHARS')
    assert hasattr(TimingDeltaSignalDetector, 'SMALL_DELTA_CHARS')

    # Check values
    assert TimingDeltaSignalDetector.LONG_PAUSE_SECONDS == 300  # 5分
    assert TimingDeltaSignalDetector.MEDIUM_PAUSE_SECONDS == 120  # 2分
    assert TimingDeltaSignalDetector.LARGE_DELTA_CHARS == 100
    assert TimingDeltaSignalDetector.MEDIUM_DELTA_CHARS == 30
    assert TimingDeltaSignalDetector.SMALL_DELTA_CHARS == 10
