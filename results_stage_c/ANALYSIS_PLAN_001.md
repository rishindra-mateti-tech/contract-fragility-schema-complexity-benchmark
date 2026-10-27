# Stage C Analysis Plan Specification (PLAN-001)

## 1. Executive Summary

This document specifies the pre-registered analysis plan for empirical evaluation on the Stage C synthetic benchmark.
The benchmark is structured to isolate the effects of controlled schema complexity variations on LLM tool-invocation reliability.
In accordance with scientific integrity guidelines, this document establishes all primary and secondary endpoints, hypothesis tests, and subgroup stratifications prior to executing model inference.

Current empirical benchmark status: `NO_EMPIRICAL_RESULTS_PRESENT`.

## 2. Pre-Registered Endpoints

### 2.1 Primary Endpoints
1. **Execution Success Rate (ESR)**:
   - Defined as the proportion of tasks where the candidate model invocation is classified as `EXACT_MATCH`, `SEMANTIC_EQUIVALENT`, or `CORRECT_ABSTENTION`.
   - Denominator: Total tasks evaluated in the relevant category ($N=100$ per category, $N=300$ overall).
2. **Tool Selection Accuracy (TSA)**:
   - Evaluated specifically on Category 2 (`TOOL_SELECTION`).
   - Defined as the proportion of tasks where the candidate model selects the designated target tool amidst distractors.

### 2.2 Secondary Endpoints
1. **Schema Compliance Rate (SCR)**:
   - Defined as the proportion of non-abstention tasks where the emitted arguments validate successfully against the active Draft-07 JSON Schema.
2. **Mean Slot F1 Score**:
   - The harmonic mean of slot precision and slot recall across recovered latent intent slots.
3. **Abstention Accuracy (AA)**:
   - Evaluated on Category 3 (`ABSTENTION`).
   - Proportion of unfulfillable requests correctly met with non-execution or explicit abstention.

## 3. Pre-Planned Hypothesis Comparisons

Statistical comparisons will assess pairwise performance differentials between the unperturbed baseline (`CANONICAL`) and each perturbed mutation family:

1. **Hypothesis 1 (Structural Nesting Fragility)**:
   - Null Hypothesis $H_{0,1}$: $\text{ESR}_{\text{NESTED}} = \text{ESR}_{\text{CANONICAL}}$
   - Alternative Hypothesis $H_{1,1}$: $\text{ESR}_{\text{NESTED}} < \text{ESR}_{\text{CANONICAL}}$
2. **Hypothesis 2 (Optional Parameter Bloat Susceptibility)**:
   - Null Hypothesis $H_{0,2}$: $\text{ESR}_{\text{BLOAT}} = \text{ESR}_{\text{CANONICAL}}$
   - Alternative Hypothesis $H_{1,2}$: $\text{ESR}_{\text{BLOAT}} < \text{ESR}_{\text{CANONICAL}}$
3. **Hypothesis 3 (Identifier Ambiguity Sensitivity)**:
   - Null Hypothesis $H_{0,3}$: $\text{ESR}_{\text{AMBIGUOUS}} = \text{ESR}_{\text{CANONICAL}}$
   - Alternative Hypothesis $H_{1,3}$: $\text{ESR}_{\text{AMBIGUOUS}} < \text{ESR}_{\text{CANONICAL}}$
4. **Hypothesis 4 (Distractor Surface Interference)**:
   - Null Hypothesis $H_{0,4}$: $\text{TSA}_{\text{DISTRACTORS}} = 1.0$ (or ceiling)
   - Alternative Hypothesis $H_{1,4}$: Increasing distractor count (2 vs 4 vs 8) monotonically degrades tool selection accuracy.

## 4. Stratified Subgroup Analyses

Pre-registered subgroup stratifications include:
1. **Complexity Strata**:
   - Stratum 1: `SIMPLE_FLAT` (scalar properties only)
   - Stratum 2: `MEDIUM_ARRAYS_ENUMS` (arrays and categorical constraints)
   - Stratum 3: `NESTED_OBJECTS_SURFACES` (multi-level nested containers)
2. **Domain Clusters**:
   - `data_management`
   - `communications`
   - `analytics_metrics`
   - `access_governance`
   - `workflow_orchestration`

## 5. Handling Missing Data and Malformed Invocations

- **Fail-Closed Rule**: Any unparseable string, malformed JSON, network timeout, or schema failure is treated as an execution failure ($0.0$).
- **No Selective Exclusion**: All 300 registered task instances form the invariant evaluation denominator. No task instance may be omitted post-hoc.
- **Reporting Invariant**: All results must report raw numerator/denominator counts alongside percentages.

## 6. Current Status Declaration

This analysis plan governs future experimental runs.
No LLM or API execution has taken place, and no empirical performance claims are asserted at this time.
All result manifests remain in the state `NO_EMPIRICAL_RESULTS_PRESENT`.
