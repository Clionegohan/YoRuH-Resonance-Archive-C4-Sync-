"""
Test for Subtask 002-03-03: レポート生成パイプライン実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from unittest.mock import Mock
from src.phase3_pod_report.report_pipeline import ReportPipeline


def test_pipeline_class_exists():
    """AC: ReportPipelineクラスを提供すること"""
    mock_integrator = Mock()
    mock_generator = Mock()
    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    assert pipeline is not None


def test_generate_method_exists():
    """AC: generate()メソッドを提供すること"""
    mock_integrator = Mock()
    mock_generator = Mock()
    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    assert hasattr(pipeline, 'generate')
    assert callable(pipeline.generate)


def test_uses_result_integrator():
    """AC: ResultIntegratorを使用して検索結果を統合すること"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    level2_results = [{"id": "id2", "distance": 0.2, "metadata": {}}]

    # Setup integrator to return integrated results
    integrated_results = [
        {"id": "id1", "distance": 0.1, "metadata": {}},
        {"id": "id2", "distance": 0.2, "metadata": {}}
    ]
    mock_integrator.integrate.return_value = integrated_results
    mock_generator.generate_report.return_value = "報告：レポート完了"

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    _ = pipeline.generate(level1_results, level2_results)

    # Verify integrator was called with both result sets
    mock_integrator.integrate.assert_called_once_with(level1_results, level2_results)


def test_uses_pod201_report_generator():
    """AC: Pod201ReportGeneratorを使用してレポートを生成すること"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    level2_results = [{"id": "id2", "distance": 0.2, "metadata": {}}]

    integrated_results = [
        {"id": "id1", "distance": 0.1, "metadata": {}}
    ]
    mock_integrator.integrate.return_value = integrated_results
    mock_generator.generate_report.return_value = "報告：分析完了"

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    _ = pipeline.generate(level1_results, level2_results)

    # Verify generator was called with integrated results
    mock_generator.generate_report.assert_called_once_with(integrated_results)


def test_returns_generated_report():
    """AC: generate()は生成されたレポートテキストを返すこと"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    level2_results = []

    integrated_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    expected_report = "報告：検索完了。類似度スコア0.1。"

    mock_integrator.integrate.return_value = integrated_results
    mock_generator.generate_report.return_value = expected_report

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    result = pipeline.generate(level1_results, level2_results)

    assert result == expected_report


def test_returns_none_on_integration_failure():
    """AC: 統合失敗時にNoneを返すこと"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    level2_results = []

    # Simulate integration failure
    mock_integrator.integrate.side_effect = Exception("Integration error")

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    result = pipeline.generate(level1_results, level2_results)

    assert result is None


def test_returns_none_on_generation_failure():
    """AC: レポート生成失敗時にNoneを返すこと"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    level2_results = []

    integrated_results = [{"id": "id1", "distance": 0.1, "metadata": {}}]
    mock_integrator.integrate.return_value = integrated_results
    # Simulate generation failure (return None)
    mock_generator.generate_report.return_value = None

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    result = pipeline.generate(level1_results, level2_results)

    assert result is None


def test_handles_empty_search_results():
    """AC: 空の検索結果（両方とも空）の場合でも適切に処理すること"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = []
    level2_results = []

    # Integrator returns empty list
    mock_integrator.integrate.return_value = []
    # Generator should still be called and produce a message
    mock_generator.generate_report.return_value = "報告：検索結果無し。"

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    result = pipeline.generate(level1_results, level2_results)

    # Should still call both components
    mock_integrator.integrate.assert_called_once()
    mock_generator.generate_report.assert_called_once()
    assert result == "報告：検索結果無し。"


def test_integrator_injection():
    """追加テスト: ResultIntegratorがコンストラクタで注入されること"""
    mock_integrator = Mock()
    mock_generator = Mock()

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )

    assert pipeline.result_integrator is mock_integrator


def test_generator_injection():
    """追加テスト: Pod201ReportGeneratorがコンストラクタで注入されること"""
    mock_integrator = Mock()
    mock_generator = Mock()

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )

    assert pipeline.report_generator is mock_generator


def test_pipeline_integration_flow():
    """追加テスト: パイプライン全体のフローが正しく実行されること"""
    mock_integrator = Mock()
    mock_generator = Mock()

    level1_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.3, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id3", "distance": 0.2, "metadata": {"type": "chunk"}}
    ]

    # Top 3: id1(0.1), id3(0.2), id2(0.3)
    integrated_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}},
        {"id": "id3", "distance": 0.2, "metadata": {"type": "chunk"}},
        {"id": "id2", "distance": 0.3, "metadata": {"type": "summary"}}
    ]

    mock_integrator.integrate.return_value = integrated_results
    mock_generator.generate_report.return_value = "報告：分析完了。上位3件を検出。"

    pipeline = ReportPipeline(
        result_integrator=mock_integrator,
        report_generator=mock_generator
    )
    result = pipeline.generate(level1_results, level2_results)

    # Verify the flow
    assert mock_integrator.integrate.call_count == 1
    assert mock_generator.generate_report.call_count == 1
    assert result == "報告：分析完了。上位3件を検出。"
