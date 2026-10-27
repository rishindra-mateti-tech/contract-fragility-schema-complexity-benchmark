"""Tests for Stage C Statistical Analysis Plan Engine (Track 6).

Verifies ratio formatting, Wilson score intervals, McNemar test calculations,
and Benjamini-Hochberg FDR adjustments.
"""

import pytest
from src.stage_c_statistical_plan import StageCStatisticalPlan


def test_format_ratio():
    assert StageCStatisticalPlan.format_ratio(85, 100) == "85/100 (85.0%)"
    assert StageCStatisticalPlan.format_ratio(1, 3) == "1/3 (33.3%)"
    assert StageCStatisticalPlan.format_ratio(0, 0) == "0/0 (0.0%)"


def test_wilson_score_interval():
    low, high = StageCStatisticalPlan.wilson_score_interval(85, 100)
    assert 0.76 < low < 0.80
    assert 0.89 < high < 0.93

    low_zero, high_zero = StageCStatisticalPlan.wilson_score_interval(0, 100)
    assert low_zero == 0.0
    assert high_zero > 0.0


def test_mcnemar_test():
    # Symmetric discordance -> chi2 should be 0.0, p_val 1.0
    chi2, p_val = StageCStatisticalPlan.mcnemar_test(10, 10)
    assert chi2 == 0.0
    assert p_val == 1.0

    # Highly asymmetric discordance: baseline 25 successes where mutation failed, mutation 2
    chi2_asym, p_asym = StageCStatisticalPlan.mcnemar_test(25, 2)
    assert chi2_asym > 15.0
    assert p_asym < 0.001


def test_benjamini_hochberg_correction():
    # 4 hypothesis tests: 2 very small p-values, 2 large
    p_vals = [0.001, 0.008, 0.25, 0.70]
    corrected = StageCStatisticalPlan.benjamini_hochberg_correction(p_vals, alpha=0.05)

    assert len(corrected) == 4
    # First test should remain significant
    orig_p, adj_p, is_sig = corrected[0]
    assert is_sig is True
    assert adj_p < 0.05

    # Fourth test should not be significant
    _, adj_p4, is_sig4 = corrected[3]
    assert is_sig4 is False
