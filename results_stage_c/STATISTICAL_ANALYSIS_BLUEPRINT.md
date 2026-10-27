# Stage C Statistical Analysis Blueprint

## 1. Experimental Design and Statistical Framework

This document outlines the statistical testing procedures and reporting standards for the Stage C benchmark.
Because each base contract is evaluated under both an unperturbed canonical baseline and controlled mutation operators, the evaluation is fundamentally a paired within-contract design.
Analyzing paired binary performance (success versus failure) requires exact non-parametric matched-pair tests rather than independent-sample tests.

Current empirical benchmark status: `NO_EMPIRICAL_RESULTS_PRESENT`.

## 2. Hypothesis Testing Methodology

### 2.1 Paired Binary Proportions: McNemar's Test
For comparing performance on identical contract tasks between a mutation family $M_i$ and the baseline $M_0$:
- Let $b$ be the count of task instances where the baseline succeeded and the mutation failed.
- Let $c$ be the count of task instances where the baseline failed and the mutation succeeded.
- Test statistic with Edwards continuity correction:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$
  with 1 degree of freedom.
- Null Hypothesis $H_0$: The marginal probabilities of success are identical ($p_b = p_c$).
- Significance threshold: $\alpha = 0.05$.

### 2.2 Confidence Intervals for Proportions
All binomial accuracy and rate estimates must report 95% confidence intervals computed via the Wilson score method:
$$p_w = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = 1.96$. This method provides superior coverage properties near boundary values ($0.0$ and $1.0$) compared to normal approximations.

### 2.3 Multiplicity Control: Benjamini-Hochberg Procedure
When testing multiple mutation families, complexity strata, and task categories simultaneously, family-wise False Discovery Rate (FDR) will be controlled at $q = 0.05$ using the Benjamini-Hochberg procedure:
1. Sort raw $p$-values: $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$.
2. Compute adjusted critical value: $p_{(k)} \le \frac{k}{m} \cdot q$.
3. Declare significance for all tests up to the largest $k$ satisfying the inequality.

## 3. Power Analysis and Sample Size Rationale

The benchmark fixes sample sizes at:
- $N = 100$ instances for Argument Construction.
- $N = 100$ instances for Tool Selection.
- $N = 100$ instances for Abstention.
- Total task suite: $N = 300$ instances.

Power calculations for McNemar's test show that with $N = 100$ paired observations:
- At $\alpha = 0.05$ (two-tailed), the test achieves $>80\%$ power to detect an absolute performance drop of 15% (e.g., baseline success rate 85% versus mutated success rate 70%), assuming a discordant pair proportion of 25%.
- This sample size is sufficient to identify medium-to-large schema fragility effects across model families.

## 4. Denominator Reporting Standard

To guarantee full transparency:
1. Percentages alone are strictly prohibited in reporting.
2. Every accuracy metric must be presented as: `Numerator / Denominator (Percentage%) [95% CI]`.
   Example: `82/100 (82.0%) [73.3%, 88.3%]`.
3. The denominator must reflect the complete pre-registered task population ($N = 100$ or $N = 300$). Selective omission of failed or timed-out tasks is forbidden.
