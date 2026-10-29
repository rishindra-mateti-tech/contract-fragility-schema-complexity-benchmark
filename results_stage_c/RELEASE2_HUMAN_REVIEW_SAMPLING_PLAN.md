# Stage C Release 2 Human Review Sampling Plan

## 1. Objective and Pre-registration

This document defines the stratified sampling plan for the independent blinded human review of Stage C Release 2 tasks.
To establish construct validity without experimental bias, a stratified representative sample of 90 tasks is selected from the 300 compiled Release 2 tasks.

- **Independent Review State (Pending Execution)**: `NO_INDEPENDENT_HUMAN_REVIEW_RESULTS_PRESENT` (independent review is not conducted)
- **Total Sample Size Target**: 90 tasks
- **Reviewers per Task**: Minimum 2 independent reviewers
- **Inter-Rater Agreement Threshold**: Cohen's kappa $\ge 0.70$
- **Author Reconciliation Mode**: Blinding strictly enforced; reconciliation performed post-submission.

## 2. Stratification Matrix

The 90 tasks are sampled across three equal category partitions:

| Evaluation Category | Target Sample Size | Strata Covered | Mutation Families Covered |
| :--- | :---: | :--- | :--- |
| **Argument Construction** | 30 | Flat, Medium, Nested | Canonical, Nested Hierarchy, Optionality Bloat, Ambiguous Identifiers |
| **Tool Selection** | 30 | Flat, Medium, Nested | Distractor Set Complexity (candidate sizes 3, 5, 9) |
| **Abstention** | 30 | Flat, Medium, Nested | Missing Parameters, Out-of-Domain, Contradictory Bounds, Ambiguous Requests |
| **Total Sample** | **90** | **Balanced across all strata** | **All controlled transformation families** |

## 3. Strict Blinding Invariants

Every item delivered to human evaluators is stripped of:
1. True category labels (e.g. `ARGUMENT_CONSTRUCTION`, `TOOL_SELECTION`, `ABSTENTION`).
2. Gold tool names and target selections.
3. Gold argument values and parameter mappings.
4. Mutation family identifiers and baseline contract codes.
5. Paired group identifiers (`paired_group_id`).
6. Internal prompt seeds and generator metadata.

## 4. Calibration Qualification Phase

Prior to reviewing the blinded evaluation sample, reviewers must complete a 5-item qualification packet (`qualification_review_packet.json`).
Reviewers must achieve $\ge 80\%$ agreement with established ground truth on qualification items before accessing evaluation packets.
