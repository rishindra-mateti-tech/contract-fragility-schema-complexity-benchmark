# Stage C Human Review Sampling Plan (PLAN-001)

## 1. Executive Summary

This plan specifies the stratified sampling strategy used to select task instances for independent human validation.
From the complete suite of 300 Release 1 tasks, a representative sample of 90 tasks (30% sampling ratio) is drawn to evaluate construct validity, clarity, and solvability.

## 2. Stratification Matrix and Allocations

The 90-task sample is evenly stratified across the primary benchmark categories:

| Category | Population ($N=300$) | Sample ($n=90$) | Sampling Fraction (%) | Stratification Dimensions |
| :--- | :---: | :---: | :---: | :--- |
| `ARGUMENT_CONSTRUCTION` | 100 | 30 | 30.0% | Stratified across 5 mutation families and 3 complexity strata |
| `TOOL_SELECTION` | 100 | 30 | 30.0% | Stratified across candidate set sizes (3, 5, 9) and positional indices |
| `ABSTENTION` | 100 | 30 | 30.0% | Stratified across 4 failure patterns and candidate counts |
| **Total Benchmark Sample** | **300** | **90** | **30.0%** | **Comprehensive multi-dimensional stratification** |

## 3. Sample Size Statistical Justification

1. **Power for Inter-Rater Agreement**:
   With $n = 90$ items and dual independent reviews ($K = 2$), the sample provides $>90\%$ statistical power to distinguish substantial agreement (Cohen's $\kappa \ge 0.70$) from moderate or poor agreement ($\kappa < 0.50$) at a two-sided significance level of $\alpha = 0.05$.
2. **Ambiguity Rate Precision**:
   A sample of $n = 90$ yields a standard error of $\le 0.045$ for estimated task ambiguity rates, ensuring narrow 95% Wilson confidence intervals around quality proportions.

## 4. Current Status
All 90 items have been compiled into blinded packages under `data_stage_c/reviewer_packages/`.
Assignment records in `results_stage_c/HUMAN_REVIEW_ASSIGNMENT_TEMPLATE.csv` remain blank pending onboarding of independent evaluators.
