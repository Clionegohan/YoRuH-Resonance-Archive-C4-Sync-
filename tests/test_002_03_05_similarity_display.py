"""
Test for Subtask 002-03-05: 類似度スコア表示実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from src.phase3_pod_report.pod201_report_generator import Pod201ReportGenerator


def test_calculate_similarity_percentage_method_exists():
    """AC: _calculate_similarity_percentage()メソッドを提供すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        assert hasattr(generator, '_calculate_similarity_percentage')
        assert callable(generator._calculate_similarity_percentage)


def test_calculate_similarity_percentage_formula():
    """AC: 変換式 similarity = (1 - distance) * 100"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Test exact formula
        assert generator._calculate_similarity_percentage(0.0) == 100  # Perfect match
        assert generator._calculate_similarity_percentage(0.2) == 80
        assert generator._calculate_similarity_percentage(0.5) == 50
        assert generator._calculate_similarity_percentage(1.0) == 0   # No similarity


def test_calculate_similarity_percentage_range():
    """AC: 結果は0-100%の範囲"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Test various distances in valid range
        for distance in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
            similarity = generator._calculate_similarity_percentage(distance)
            assert 0 <= similarity <= 100, f"Similarity {similarity} out of range for distance {distance}"


def test_calculate_similarity_percentage_handles_out_of_range():
    """AC: distance値の範囲外を適切に処理（負数→0%, 1.0超過→0%）"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Negative values should clip to 0%
        assert generator._calculate_similarity_percentage(-0.5) == 0
        assert generator._calculate_similarity_percentage(-1.0) == 0

        # Values > 1.0 should clip to 0%
        assert generator._calculate_similarity_percentage(1.5) == 0
        assert generator._calculate_similarity_percentage(2.0) == 0


def test_format_similarity_bar_method_exists():
    """AC: _format_similarity_bar()メソッドを実装すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        assert hasattr(generator, '_format_similarity_bar')
        assert callable(generator._format_similarity_bar)


def test_format_similarity_bar_structure():
    """AC: Unicodeブロック文字（█, ░）を使用、バー長10文字"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Test 80% similarity
        bar = generator._format_similarity_bar(80)
        assert bar == "[████████░░]", f"Expected [████████░░] but got {bar}"

        # Test 0% similarity
        bar = generator._format_similarity_bar(0)
        assert bar == "[░░░░░░░░░░]", f"Expected [░░░░░░░░░░] but got {bar}"

        # Test 100% similarity
        bar = generator._format_similarity_bar(100)
        assert bar == "[██████████]", f"Expected [██████████] but got {bar}"


def test_format_similarity_bar_various_percentages():
    """追加テスト: 様々なパーセンテージでのバー表示"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        test_cases = [
            (10, "[█░░░░░░░░░]"),
            (25, "[██░░░░░░░░]"),   # 2.5 → 2
            (50, "[█████░░░░░]"),
            (75, "[███████░░░]"),   # 7.5 → 7
            (90, "[█████████░]"),
        ]

        for percentage, expected_bar in test_cases:
            bar = generator._format_similarity_bar(percentage)
            assert bar == expected_bar, f"For {percentage}%, expected {expected_bar} but got {bar}"


def test_format_search_results_includes_similarity_display():
    """AC: 類似度スコアを数値とビジュアルで併記すること"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.2, "metadata": {"type": "summary"}}
        ]

        result = generator._format_search_results(search_results)

        # Should include similarity bar
        assert "[████████░░]" in result, "Should include visual similarity bar"

        # Should include percentage (80% for distance 0.2)
        assert "80%" in result, "Should include percentage"

        # Should include distance value with 4-digit precision
        assert "0.2000" in result, "Should include distance with 4-digit precision"

        # Format: "類似度: [████████░░] 80% (distance: 0.2000)"
        assert "類似度:" in result, "Should include '類似度:' label"


def test_format_search_results_replaces_old_distance_format():
    """AC: 既存の「類似度距離: 0.1234」を新フォーマットに置換"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.3, "metadata": {"type": "summary"}}
        ]

        result = generator._format_search_results(search_results)

        # Old format should NOT exist
        assert "類似度距離:" not in result, "Old format '類似度距離:' should be removed"

        # New format should exist
        assert "類似度:" in result and "[" in result and "]" in result, "New format should exist"


def test_format_search_results_multiple_results_with_similarity():
    """追加テスト: 複数の検索結果それぞれに類似度バーを表示"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        search_results = [
            {"id": "id1", "distance": 0.1, "metadata": {"type": "summary"}},  # 90%
            {"id": "id2", "distance": 0.5, "metadata": {"type": "chunk"}},    # 50%
            {"id": "id3", "distance": 0.8, "metadata": {"type": "summary"}},  # 20%
        ]

        result = generator._format_search_results(search_results)

        # Should include all three bars
        assert "[█████████░]" in result, "Should include 90% bar"
        assert "[█████░░░░░]" in result, "Should include 50% bar"
        assert "[██░░░░░░░░]" in result, "Should include 20% bar"

        # Should include all percentages
        assert "90%" in result
        assert "50%" in result
        assert "20%" in result


def test_similarity_calculation_integration():
    """追加テスト: distance→similarity変換の統合テスト"""
    persona_content = "報告：Pod201"

    with patch("builtins.open", mock_open(read_data=persona_content)):
        mock_ollama = Mock()
        generator = Pod201ReportGenerator(ollama_client=mock_ollama)

        # Verify the entire flow: distance → percentage → bar
        distance = 0.35
        percentage = generator._calculate_similarity_percentage(distance)
        bar = generator._format_similarity_bar(percentage)

        assert percentage == 65  # (1 - 0.35) * 100 = 65
        assert bar == "[██████░░░░]"  # 6.5 → 6 filled blocks
