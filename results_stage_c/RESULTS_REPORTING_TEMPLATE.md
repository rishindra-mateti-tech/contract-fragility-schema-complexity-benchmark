# Stage C Empirical Results Reporting Template

## 1. Experimental Protocol and Metadata Block

Every future empirical evaluation report must begin with the following standardized metadata block:

- **Benchmark Stage**: Stage C Synthetic Controlled Mutation Benchmark
- **Evaluation Status**: `NO_EMPIRICAL_RESULTS_PRESENT` (Infrastructure ready, inference pending)
- **Model Identifier**: `[MODEL_NAME_AND_VERSION]`
- **Inference Temperature**: `0.0`
- **Sampling Top-p**: `1.0`
- **Evaluation Date**: `[YYYY-MM-DD]`
- **Master Seed**: `42`
- **Total Task Suite Size**: `300` instances

## 2. Overall Primary Results Summary

| Metric | Category | Numerator / Denominator | Rate (%) | 95% Wilson CI |
| :--- | :--- | :---: | :---: | :---: |
| Execution Success Rate (ESR) | Overall (All Tasks) | [PENDING] / 300 | [PENDING]% | [[PENDING]%, [PENDING]%] |
| Execution Success Rate (ESR) | Argument Construction | [PENDING] / 100 | [PENDING]% | [[PENDING]%, [PENDING]%] |
| Tool Selection Accuracy (TSA) | Tool Selection | [PENDING] / 100 | [PENDING]% | [[PENDING]%, [PENDING]%] |
| Abstention Accuracy (AA) | Abstention | [PENDING] / 100 | [PENDING]% | [[PENDING]%, [PENDING]%] |
| Schema Compliance Rate (SCR) | Overall Non-Abstain | [PENDING] / 200 | [PENDING]% | [[PENDING]%, [PENDING]%] |
| Mean Slot F1 Score | Overall Non-Abstain | - | [PENDING] | [[PENDING], [PENDING]] |

## 3. Controlled Mutation Family Breakdown

Impact of controlled schema transformations compared against canonical baseline:

| Mutation Family | Sample Size ($N$) | Success Count | Success Rate (%) | McNemar $\chi^2$ vs Baseline | Raw $p$-value | BH Adjusted $p$ | Significant ($\alpha=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `CANONICAL` (Baseline) | 100 | [PENDING] | [PENDING]% | Reference | Reference | Reference | - |
| `NESTED_HIERARCHY` | 100 | [PENDING] | [PENDING]% | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| `OPTIONALITY_BLOAT` | 100 | [PENDING] | [PENDING]% | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| `AMBIGUOUS_IDENTIFIERS` | 100 | [PENDING] | [PENDING]% | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| `DISTRACTOR_SET_COMPLEXITY` | 100 | [PENDING] | [PENDING]% | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

## 4. Complexity Strata Performance

Performance stratified across base schema structural complexity levels:

| Complexity Stratum | Task Count | Success Count | Success Rate (%) | 95% Wilson CI | Mean Slot F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `SIMPLE_FLAT` | [PENDING] | [PENDING] | [PENDING]% | [[PENDING]%, [PENDING]%] | [PENDING] |
| `MEDIUM_ARRAYS_ENUMS` | [PENDING] | [PENDING] | [PENDING]% | [[PENDING]%, [PENDING]%] | [PENDING] |
| `NESTED_OBJECTS_SURFACES` | [PENDING] | [PENDING] | [PENDING]% | [[PENDING]%, [PENDING]%] | [PENDING] |

## 5. Failure Taxonomy Distribution

Distribution of non-successful outcomes across the standardized error hierarchy:

| Failure Classification | Count | Proportion of Failures (%) | Typical Mechanism |
| :--- | :---: | :---: | :--- |
| `SCHEMA_VIOLATION` | [PENDING] | [PENDING]% | Violated type bounds, failed additionalProperties |
| `MISSING_REQUIRED_SLOT` | [PENDING] | [PENDING]% | Omitted mandatory payload argument |
| `VALUE_CORRUPTION` | [PENDING] | [PENDING]% | Hallucinated or mistranslated argument value |
| `HALLUCINATED_SLOT` | [PENDING] | [PENDING]% | Injected unauthorized parameter not in intent |
| `TOOL_SELECTION_ERROR` | [PENDING] | [PENDING]% | Chose distractor tool instead of target tool |
| `FALSE_EXECUTION_UNWARRANTED` | [PENDING] | [PENDING]% | Invoked tool on unfulfillable abstention task |
| `MALFORMED_INVOCATION` | [PENDING] | [PENDING]% | Invalid JSON syntax or unparseable text |
