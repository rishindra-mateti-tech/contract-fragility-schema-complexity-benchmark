"""Stage C Statistical Analysis Plan Engine.

Implements statistical testing utilities for benchmark evaluation:
- McNemar's test for paired binary proportions across matched contract pairs.
- Benjamini-Hochberg False Discovery Rate (FDR) multiple testing correction.
- Wilson score confidence intervals for binomial proportions.
- Standardized numerator/denominator reporting formatters.
"""

from typing import Any, Dict, List, Tuple
import math


class StageCStatisticalPlan:
    """Statistical evaluation routines for Stage C experimental hypotheses."""

    @staticmethod
    def format_ratio(numerator: int, denominator: int) -> str:
        """Formats exact count and percentage string: e.g. '85/100 (85.0%)'."""
        if denominator == 0:
            return "0/0 (0.0%)"
        pct = (numerator / denominator) * 100.0
        return f"{numerator}/{denominator} ({pct:.1f}%)"

    @staticmethod
    def wilson_score_interval(
        successes: int,
        trials: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculates Wilson score interval for a binomial proportion."""
        if trials == 0:
            return 0.0, 0.0

        # Normal critical value approximation (z=1.96 for 95%)
        z = 1.95996 if confidence == 0.95 else 2.57583
        p = successes / trials
        denominator = 1.0 + (z ** 2) / trials
        center = (p + (z ** 2) / (2 * trials)) / denominator
        margin = (z / denominator) * math.sqrt((p * (1 - p) / trials) + (z ** 2) / (4 * (trials ** 2)))

        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)
        return round(lower, 4), round(upper, 4)

    @staticmethod
    def mcnemar_test(
        b_mut_fail_baseline_success: int,
        c_mut_success_baseline_fail: int
    ) -> Tuple[float, float]:
        """Calculates McNemar chi-square test with continuity correction.
        
        b: Baseline succeeded, Mutation failed.
        c: Baseline failed, Mutation succeeded.
        Returns: (chi2_statistic, p_value_approximation)
        """
        total_discordant = b_mut_fail_baseline_success + c_mut_success_baseline_fail
        if total_discordant == 0:
            return 0.0, 1.0

        # Edwards continuity correction
        numerator = max(0.0, abs(b_mut_fail_baseline_success - c_mut_success_baseline_fail) - 1.0) ** 2
        chi2 = numerator / total_discordant

        # 1 degree of freedom p-value approximation via chi-square survival function
        # Using upper incomplete gamma / standard normal approximation
        p_val = math.erfc(math.sqrt(chi2 / 2.0))
        return round(chi2, 4), round(max(0.0, min(1.0, p_val)), 6)

    @staticmethod
    def benjamini_hochberg_correction(
        p_values: List[float],
        alpha: float = 0.05
    ) -> List[Tuple[float, float, bool]]:
        """Applies Benjamini-Hochberg procedure to control False Discovery Rate.
        
        Returns list of tuples: (original_p, adjusted_p, is_significant)
        """
        m = len(p_values)
        if m == 0:
            return []

        # Pair with original indices
        indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
        adjusted = [0.0] * m

        # Compute adjusted p-values from largest to smallest
        running_min = 1.0
        for rank_idx in range(m - 1, -1, -1):
            orig_idx, p = indexed_p[rank_idx]
            rank = rank_idx + 1
            adj_p = min(1.0, (p * m) / rank)
            running_min = min(running_min, adj_p)
            adjusted[orig_idx] = running_min

        results = []
        for i, p in enumerate(p_values):
            adj = adjusted[i]
            sig = adj <= alpha
            results.append((round(p, 6), round(adj, 6), sig))

        return results
