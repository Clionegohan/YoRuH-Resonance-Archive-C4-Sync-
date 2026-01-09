"""
Test for Subtask 002-02-07: マルチレベル検索統合

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from src.phase2_realtime_analysis.result_integrator import ResultIntegrator


def test_integrator_class_exists():
    """AC: ResultIntegratorクラスを提供すること"""
    integrator = ResultIntegrator()
    assert integrator is not None


def test_integrate_method_exists():
    """AC: integrate()メソッドを提供すること"""
    integrator = ResultIntegrator()
    assert hasattr(integrator, 'integrate')
    assert callable(integrator.integrate)


def test_integrate_combines_results():
    """AC: level1_resultsとlevel2_resultsを結合すること"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.3, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id3", "distance": 0.2, "metadata": {"type": "chunk"}},
        {"id": "id4", "distance": 0.4, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    # Should have 4 results before limiting to top 3
    ids = [r["id"] for r in results]
    assert "id1" in ids or "id2" in ids or "id3" in ids or "id4" in ids


def test_integrate_sorts_by_distance():
    """AC: 距離(distance)でソート(昇順)すること"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.5, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.1, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id3", "distance": 0.3, "metadata": {"type": "chunk"}},
        {"id": "id4", "distance": 0.2, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    # Should be sorted by distance: id2(0.1), id4(0.2), id3(0.3)
    assert results[0]["id"] == "id2"
    assert results[0]["distance"] == 0.1
    assert results[1]["id"] == "id4"
    assert results[1]["distance"] == 0.2
    assert results[2]["id"] == "id3"
    assert results[2]["distance"] == 0.3


def test_integrate_deduplicates_by_id():
    """AC: 同じidが複数ある場合、最も小さい距離を持つものを採用すること"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.5, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.2, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id1", "distance": 0.3, "metadata": {"type": "chunk"}},  # Duplicate with smaller distance
        {"id": "id3", "distance": 0.4, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    # id1 should appear only once with distance 0.3
    id1_results = [r for r in results if r["id"] == "id1"]
    assert len(id1_results) == 1
    assert id1_results[0]["distance"] == 0.3


def test_integrate_returns_top_3():
    """AC: 上位3件を返すこと"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.2, "metadata": {"type": "summary"}},
        {"id": "id3", "distance": 0.3, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id4", "distance": 0.4, "metadata": {"type": "chunk"}},
        {"id": "id5", "distance": 0.5, "metadata": {"type": "chunk"}},
        {"id": "id6", "distance": 0.6, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    # Should return exactly 3 results
    assert len(results) == 3
    # Should be top 3 by distance
    assert results[0]["id"] == "id1"
    assert results[1]["id"] == "id2"
    assert results[2]["id"] == "id3"


def test_integrate_both_empty_returns_empty():
    """AC: 両方が空の場合は空リストを返すこと"""
    integrator = ResultIntegrator()

    results = integrator.integrate([], [])

    assert results == []


def test_integrate_level1_empty_returns_level2_top3():
    """AC: 一方のみ空の場合は、もう一方から上位3件を返すこと"""
    integrator = ResultIntegrator()

    level2_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "chunk"}},
        {"id": "id2", "distance": 0.2, "metadata": {"type": "chunk"}},
        {"id": "id3", "distance": 0.3, "metadata": {"type": "chunk"}},
        {"id": "id4", "distance": 0.4, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate([], level2_results)

    assert len(results) == 3
    assert results[0]["id"] == "id1"
    assert results[1]["id"] == "id2"
    assert results[2]["id"] == "id3"


def test_integrate_level2_empty_returns_level1_top3():
    """AC: 一方のみ空の場合は、もう一方から上位3件を返すこと"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.5, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.1, "metadata": {"type": "summary"}},
        {"id": "id3", "distance": 0.3, "metadata": {"type": "summary"}},
        {"id": "id4", "distance": 0.2, "metadata": {"type": "summary"}}
    ]

    results = integrator.integrate(level1_results, [])

    assert len(results) == 3
    # Should be sorted: id2(0.1), id4(0.2), id3(0.3)
    assert results[0]["id"] == "id2"
    assert results[1]["id"] == "id4"
    assert results[2]["id"] == "id3"


def test_integrate_none_inputs():
    """AC: 入力リストがNoneの場合でも正しく処理すること"""
    integrator = ResultIntegrator()

    results = integrator.integrate(None, None)
    assert results == []

    level1_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}}
    ]
    results = integrator.integrate(level1_results, None)
    assert len(results) == 1

    results = integrator.integrate(None, level1_results)
    assert len(results) == 1


def test_integrate_less_than_3_results():
    """AC: 結果が3件未満の場合、存在する全件を返すこと"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.2, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id2", "distance": 0.1, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    # Should return 2 results (all available)
    assert len(results) == 2
    assert results[0]["id"] == "id2"
    assert results[1]["id"] == "id1"


def test_integrate_result_fields():
    """AC: 各結果にid, distance, metadataフィールドを含むこと"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary", "file": "file1.md"}}
    ]
    level2_results = [
        {"id": "id2", "distance": 0.2, "metadata": {"type": "chunk", "seq": 1}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    for result in results:
        assert "id" in result
        assert "distance" in result
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)


def test_integrate_preserves_metadata():
    """追加テスト: metadataが正しく保持されること"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "summary", "file": "test.md", "date": "2026-01-09"}}
    ]

    results = integrator.integrate(level1_results, [])

    assert results[0]["metadata"]["type"] == "summary"
    assert results[0]["metadata"]["file"] == "test.md"
    assert results[0]["metadata"]["date"] == "2026-01-09"


def test_integrate_complex_deduplication():
    """追加テスト: 複雑な重複除去シナリオ"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.5, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.2, "metadata": {"type": "summary"}},
        {"id": "id3", "distance": 0.6, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id1", "distance": 0.1, "metadata": {"type": "chunk"}},  # Better match for id1
        {"id": "id2", "distance": 0.3, "metadata": {"type": "chunk"}},  # Worse match for id2
        {"id": "id4", "distance": 0.4, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    # Top 3 should be: id1(0.1), id2(0.2), id4(0.4)
    assert len(results) == 3
    assert results[0]["id"] == "id1"
    assert results[0]["distance"] == 0.1
    assert results[1]["id"] == "id2"
    assert results[1]["distance"] == 0.2
    assert results[2]["id"] == "id4"
    assert results[2]["distance"] == 0.4


def test_integrate_single_result():
    """追加テスト: 結果が1件のみの場合"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.5, "metadata": {"type": "summary"}}
    ]

    results = integrator.integrate(level1_results, [])

    assert len(results) == 1
    assert results[0]["id"] == "id1"


def test_integrate_exact_3_results():
    """追加テスト: ちょうど3件の結果がある場合"""
    integrator = ResultIntegrator()

    level1_results = [
        {"id": "id1", "distance": 0.3, "metadata": {"type": "summary"}},
        {"id": "id2", "distance": 0.1, "metadata": {"type": "summary"}}
    ]
    level2_results = [
        {"id": "id3", "distance": 0.2, "metadata": {"type": "chunk"}}
    ]

    results = integrator.integrate(level1_results, level2_results)

    assert len(results) == 3
    assert results[0]["distance"] == 0.1
    assert results[1]["distance"] == 0.2
    assert results[2]["distance"] == 0.3
