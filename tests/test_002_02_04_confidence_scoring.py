"""
Test for Subtask 002-02-04: 確信度スコアリング実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from src.phase2_realtime_analysis.trigger_decision_engine import TriggerDecisionEngine
from src.phase2_realtime_analysis.structural_signal_detector import StructuralSignal
from src.phase2_realtime_analysis.timing_delta_signal_detector import TimingSignal, DeltaSignal


def test_engine_class_exists():
    """AC: TriggerDecisionEngineクラスを提供すること"""
    engine = TriggerDecisionEngine()
    assert engine is not None


def test_calculate_confidence_method_exists():
    """AC: calculate_confidence()メソッドを提供すること"""
    engine = TriggerDecisionEngine()
    assert hasattr(engine, 'calculate_confidence')
    assert callable(engine.calculate_confidence)


def test_should_trigger_method_exists():
    """AC: should_trigger()メソッドを提供すること"""
    engine = TriggerDecisionEngine()
    assert hasattr(engine, 'should_trigger')
    assert callable(engine.should_trigger)


def test_weights_are_defined():
    """AC: 各シグナルの重みを辞書形式で定義すること"""
    assert hasattr(TriggerDecisionEngine, 'WEIGHTS')
    assert isinstance(TriggerDecisionEngine.WEIGHTS, dict)

    # 構造的シグナル
    assert TriggerDecisionEngine.WEIGHTS['paragraph_break'] == 0.2
    assert TriggerDecisionEngine.WEIGHTS['horizontal_rule'] == 0.3
    assert TriggerDecisionEngine.WEIGHTS['sentence_end'] == 0.1

    # 時間シグナル
    assert TriggerDecisionEngine.WEIGHTS['long_pause'] == 0.4
    assert TriggerDecisionEngine.WEIGHTS['medium_pause'] == 0.2

    # 差分シグナル
    assert TriggerDecisionEngine.WEIGHTS['large_delta'] == 0.3
    assert TriggerDecisionEngine.WEIGHTS['medium_delta'] == 0.2
    assert TriggerDecisionEngine.WEIGHTS['small_delta'] == 0.1


def test_calculate_confidence_with_single_signal():
    """AC: 検知された各シグナル種類の重みを加算して確信度スコアを計算すること"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='paragraph_break', position=10, pattern='\n\n')
    ]

    confidence = engine.calculate_confidence(signals)
    assert confidence == 0.2


def test_calculate_confidence_with_multiple_signals():
    """AC: 複数のシグナルの重みを加算すること"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='horizontal_rule', position=10, pattern='---'),
        TimingSignal(type='medium_pause', elapsed_seconds=150),
        DeltaSignal(type='medium_delta', char_delta=50)
    ]

    # 0.3 + 0.2 + 0.2 = 0.7
    confidence = engine.calculate_confidence(signals)
    assert confidence == 0.7


def test_calculate_confidence_deduplicates_same_type():
    """AC: 同じ種類のシグナルが複数ある場合、1つとしてカウントすること"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='sentence_end', position=10, pattern='。'),
        StructuralSignal(type='sentence_end', position=20, pattern='！'),
        StructuralSignal(type='sentence_end', position=30, pattern='？')
    ]

    # 3つあっても1つとしてカウント: 0.1
    confidence = engine.calculate_confidence(signals)
    assert confidence == 0.1


def test_calculate_confidence_max_limit():
    """AC: 確信度スコアの上限を1.0とすること"""
    engine = TriggerDecisionEngine()

    # すべてのシグナルを含める（合計は1.0を超える）
    signals = [
        StructuralSignal(type='paragraph_break', position=10, pattern='\n\n'),
        StructuralSignal(type='horizontal_rule', position=20, pattern='---'),
        StructuralSignal(type='sentence_end', position=30, pattern='。'),
        TimingSignal(type='long_pause', elapsed_seconds=400),
        TimingSignal(type='medium_pause', elapsed_seconds=150),  # 重複、無視される
        DeltaSignal(type='large_delta', char_delta=150),
        DeltaSignal(type='medium_delta', char_delta=50),  # 重複、無視される
        DeltaSignal(type='small_delta', char_delta=15),  # 重複、無視される
    ]

    # 0.2 + 0.3 + 0.1 + 0.4 + 0.3 = 1.3 -> 上限1.0
    confidence = engine.calculate_confidence(signals)
    assert confidence == 1.0


def test_should_trigger_returns_true_when_above_threshold():
    """AC: 確信度スコアが0.6以上の場合、should_trigger()はTrueを返すこと"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='horizontal_rule', position=10, pattern='---'),
        TimingSignal(type='medium_pause', elapsed_seconds=150),
        DeltaSignal(type='medium_delta', char_delta=50)
    ]

    # 0.3 + 0.2 + 0.2 = 0.7 >= 0.6
    should_trigger = engine.should_trigger(signals)
    assert should_trigger is True


def test_should_trigger_returns_false_when_below_threshold():
    """AC: 確信度スコアが0.6未満の場合、should_trigger()はFalseを返すこと"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='sentence_end', position=10, pattern='。'),
        DeltaSignal(type='small_delta', char_delta=15)
    ]

    # 0.1 + 0.1 = 0.2 < 0.6
    should_trigger = engine.should_trigger(signals)
    assert should_trigger is False


def test_should_trigger_at_exact_threshold():
    """AC: 確信度スコアが正確に0.6の場合、Trueを返すこと"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='paragraph_break', position=10, pattern='\n\n'),
        TimingSignal(type='long_pause', elapsed_seconds=400)
    ]

    # 0.2 + 0.4 = 0.6 (境界値)
    should_trigger = engine.should_trigger(signals)
    assert should_trigger is True


def test_confidence_threshold_is_configurable():
    """AC: 確信度閾値をクラス定数として定義し、将来的に調整可能にすること"""
    assert hasattr(TriggerDecisionEngine, 'CONFIDENCE_THRESHOLD')
    assert TriggerDecisionEngine.CONFIDENCE_THRESHOLD == 0.6


def test_empty_signals_returns_zero_confidence():
    """追加テスト: シグナルが空の場合、確信度は0.0を返すこと"""
    engine = TriggerDecisionEngine()

    confidence = engine.calculate_confidence([])
    assert confidence == 0.0


def test_empty_signals_does_not_trigger():
    """追加テスト: シグナルが空の場合、トリガーしないこと"""
    engine = TriggerDecisionEngine()

    should_trigger = engine.should_trigger([])
    assert should_trigger is False


def test_unknown_signal_type_is_ignored():
    """追加テスト: 未知のシグナルタイプは無視されること"""
    engine = TriggerDecisionEngine()

    # 未知のシグナルタイプを含む
    signals = [
        StructuralSignal(type='unknown_signal', position=10, pattern='???'),
        StructuralSignal(type='paragraph_break', position=20, pattern='\n\n')
    ]

    # unknown_signalは無視され、paragraph_breakのみカウント
    confidence = engine.calculate_confidence(signals)
    assert confidence == 0.2


def test_typical_scenario_paragraph_and_pause():
    """実用例: 段落区切り + long_pause = トリガー"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='paragraph_break', position=100, pattern='\n\n'),
        TimingSignal(type='long_pause', elapsed_seconds=350)
    ]

    confidence = engine.calculate_confidence(signals)
    assert confidence == pytest.approx(0.6)
    assert engine.should_trigger(signals) is True


def test_typical_scenario_horizontal_rule_and_delta():
    """実用例: 水平線 + medium_pause + medium_delta = トリガー"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='horizontal_rule', position=50, pattern='---'),
        TimingSignal(type='medium_pause', elapsed_seconds=180),
        DeltaSignal(type='medium_delta', char_delta=60)
    ]

    confidence = engine.calculate_confidence(signals)
    assert confidence == 0.7
    assert engine.should_trigger(signals) is True


def test_typical_scenario_weak_signals_no_trigger():
    """実用例: 弱いシグナルのみ = トリガーせず"""
    engine = TriggerDecisionEngine()

    signals = [
        StructuralSignal(type='sentence_end', position=10, pattern='。'),
        DeltaSignal(type='small_delta', char_delta=15)
    ]

    confidence = engine.calculate_confidence(signals)
    assert confidence == 0.2
    assert engine.should_trigger(signals) is False
