# Stage C Mutation Operator Specification (SPEC-001)

## 1. Overview and Theoretical Scope

This specification details the formal semantics, transformation rules, and reversibility invariants for the five controlled mutation operator families utilized in the Stage C benchmark.
The goal of controlled schema mutation is to isolate how specific dimensions of schema complexity influence large language model (LLM) tool-use reliability across Argument Construction, Tool Selection, and Abstention tasks.

All transformations are deterministic, parameterized, and reproducible from the master seed (42).

## 2. Invariant Transformation Principles

Every mutation operator must strictly adhere to the following invariants:
1. **Schema Specification Invariant**: The transformed schema must strictly validate as valid Draft-07 JSON Schema.
2. **Additional Properties Invariant**: All object definitions, both root and nested containers, must retain `additionalProperties: false`.
3. **Semantic Intent Preservation**: Transformations in argument structure (nesting, aliasing) must preserve a mathematically reversible projection to the underlying canonical `LatentIntent`.
4. **Deterministic Reproducibility**: Given a base contract and mutation parameters, the compiler produces bit-for-bit identical schemas and mappings.

## 3. Mutation Operator Families

### 3.1 Family 1: CANONICAL (Identity Baseline)
- **Operator Code**: `CANONICAL`
- **Objective**: Establishes the unperturbed performance baseline for each base contract.
- **Transformation Mechanics**:
  - The parameter schema, required list, properties, and descriptions are preserved without alteration.
  - The mapping specification defines identity projections: `path(x) = x`.
- **Epistemic Role**: Serves as the experimental control group ($M_0$) against which all perturbed variants ($M_i$) are comparatively evaluated.

### 3.2 Family 2: NESTED_HIERARCHY
- **Operator Code**: `NESTED_HIERARCHY`
- **Objective**: Evaluates model susceptibility to structural depth, hierarchical boundaries, and containerized parameter organizations.
- **Transformation Mechanics**:
  - Subsets of top-level properties are encapsulated within an intermediate object container (e.g., `payload_parameters`).
  - Container objects are typed as `object`, enforce `additionalProperties: false`, and declare nested `required` arrays.
  - Forward mapping maps slot $s$ to path `container.s`.
  - Backward mapping maps path `container.s` to slot $s$.
- **Hypothesis**: Hierarchical nesting increases argument construction errors due to boundary traversal failures and path-flattening tendencies.

### 3.3 Family 3: OPTIONALITY_BLOAT
- **Operator Code**: `OPTIONALITY_BLOAT`
- **Objective**: Evaluates model precision and hallucination susceptibility when encountering extraneous optional fields and default values.
- **Transformation Mechanics**:
  - Injects controlled optional parameters (e.g., `client_request_id`, `dry_run`, `trace_context`, `timeout_ms`) into the schema properties.
  - Injected parameters are strictly optional (omitted from `required`).
  - Canonical required properties and existing optional properties remain intact.
- **Hypothesis**: High parameter optionality leads to spurious parameter hallucination or omission of essential payload elements.

### 3.4 Family 4: AMBIGUOUS_IDENTIFIERS
- **Operator Code**: `AMBIGUOUS_IDENTIFIERS`
- **Objective**: Evaluates robustness against semantic ambiguity and lexical naming variations.
- **Transformation Mechanics**:
  - Parameter identifiers are systematically replaced with semantically near-synonyms via a deterministic alias registry (e.g., `key` -> `entry_identifier`, `user_id` -> `account_identifier`).
  - Descriptions and type constraints remain preserved.
  - Bidirectional alias mapping tracks every name substitution.
- **Hypothesis**: Ambiguous identifiers degrade argument construction accuracy when prompt terminology does not mirror schema keys verbatim.

### 3.5 Family 5: DISTRACTOR_SET_COMPLEXITY
- **Operator Code**: `DISTRACTOR_SET_COMPLEXITY`
- **Objective**: Measures tool selection accuracy and discrimination capacity under increasing candidate surface complexity.
- **Transformation Mechanics**:
  - The target contract schema remains unchanged.
  - A controlled set of distractor tool definitions is injected into the tool environment (varying candidate count: 2, 4, 8 distractors).
  - Distractors are drawn systematically from same-domain and cross-domain synthetic base contracts.
- **Hypothesis**: Semantic proximity between candidate tool signatures substantially elevates misclassification rates in multi-tool contexts.

## 4. Reversibility and Verification Matrix

| Mutation Family | Reversible Mapping | Schema Valid | Target Changed | Distractor Injected |
| :--- | :---: | :---: | :---: | :---: |
| `CANONICAL` | Yes (Identity) | Draft-07 | No | No |
| `NESTED_HIERARCHY` | Yes (Path Proj) | Draft-07 | Yes (Depth +1) | No |
| `OPTIONALITY_BLOAT` | Yes (Filter Bloat)| Draft-07 | Yes (Props +3/5) | No |
| `AMBIGUOUS_IDENTIFIERS` | Yes (Alias Map) | Draft-07 | Yes (Renamed) | No |
| `DISTRACTOR_SET_COMPLEXITY`| Yes (Identity) | Draft-07 | No | Yes (2/4/8 tools)|

## 5. Storage and Registry Layout

1. Compiled individual mutation records: `data_stage_c/mutation_manifests/{mutation_id}.json`
2. Master mutation registry index: `results_stage_c/MUTATION_REGISTRY.json`
3. Each record contains full schema, forward/backward mappings, distractor lists, and recalculated complexity metrics.
