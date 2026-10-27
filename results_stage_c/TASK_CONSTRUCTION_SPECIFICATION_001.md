# Stage C Task Construction Specification (SPEC-001)

## 1. Executive Summary

This specification defines the construction protocol, validation criteria, and adversarial safeguards governing the Stage C benchmark task suite.
The task suite comprises 300 standardized evaluation instances systematically divided across three functional categories:
1. `ARGUMENT_CONSTRUCTION` (100 instances)
2. `TOOL_SELECTION` (100 instances)
3. `ABSTENTION` (100 instances)

All instances are generated deterministically from frozen synthetic base contracts and mutation manifests.

## 2. Epistemic Scope and Leakage Prevention

To ensure construct validity and prevent spurious performance inflation:
1. **No Gold Parameter Leakage**: User prompts are phrased using natural intent descriptions without verbatim serialization of raw JSON argument dictionaries.
2. **Positional Neutrality**: In multi-tool contexts (`TOOL_SELECTION`), tool declarations are sorted lexicographically by tool name rather than placing the target tool at index zero.
3. **Draft-07 Conformance**: Every available tool schema declared in a task instance strictly complies with JSON Schema Draft-07 and enforces `additionalProperties: false`.
4. **Offline Reproducibility**: Task instances are persisted as standalone JSON records under `data_stage_c/task_instances/` accompanied by SHA-256 integrity digests in `results_stage_c/TASK_SET_MANIFEST.json`.

## 3. Task Category Specifications

### 3.1 Category 1: ARGUMENT_CONSTRUCTION
- **Target Count**: 100 task instances.
- **Objective**: Assess model precision in formatting structured JSON arguments under varied schema complexities (canonical flat, nested containers, optional bloat, and ambiguous alias names).
- **Environment**: Exactly one tool declaration provided (the target tool).
- **Evaluation Criteria**:
  - Exact match against projected argument schema (`EXACT_MATCH`).
  - Strict compliance with JSON Schema constraints (`additionalProperties: false`, required fields, types).
  - Full recovery of latent intent slots through the inverse codec.

### 3.2 Category 2: TOOL_SELECTION
- **Target Count**: 100 task instances.
- **Objective**: Measure discrimination capability when multiple candidate tool schemas are presented concurrently.
- **Environment**: Multiple tool declarations presented (the target tool plus 2, 4, or 8 distractors from same-domain and cross-domain contract pools).
- **Evaluation Criteria**:
  - Tool selection correctness: the model must select the specific tool capable of fulfilling the user request.
  - Selecting an incorrect tool triggers `TOOL_SELECTION_ERROR`.
  - Upon selecting the correct tool, argument construction is evaluated identically to Category 1.

### 3.3 Category 3: ABSTENTION
- **Target Count**: 100 task instances.
- **Objective**: Evaluate model capability to refrain from invoking tools when a user request cannot be safely, completely, or legitimately fulfilled.
- **Environment**: Relevant tool definitions are provided, but the request exhibits one of four explicit failure modes:
  1. `MISSING_MANDATORY_PARAMETERS`: The user requests an action but omits mandatory parameters (e.g., requesting record creation without providing the required primary key or record payload).
  2. `OUT_OF_DOMAIN_UNSUPPORTED`: The user requests an unfulfillable operation that falls outside the declared capabilities of the tools (e.g., requesting raw disk partition deletion or hardware reboot).
  3. `CONTRADICTORY_BOUNDS`: The request demands values that directly violate parameter schema constraints (e.g., negative record limits or impossible timestamp intervals).
  4. `AMBIGUOUS_ACTION_REQUEST`: The instruction is entirely underspecified or internally contradictory with no actionable parameters.
- **Evaluation Criteria**:
  - Model must NOT call any tool, or must explicitly emit an abstention token (`CORRECT_ABSTENTION`).
  - Any invocation of a tool in an abstention task constitutes an unjustified action, classified as `FALSE_EXECUTION_UNWARRANTED`.

## 4. Task Instance Schema

Each task instance is stored in `data_stage_c/task_instances/{task_id}.json` adhering to the following schema:
- `task_id` (str): Unique task identifier (e.g., `TASK_SYNTH_AC_001`).
- `category` (str): One of `ARGUMENT_CONSTRUCTION`, `TOOL_SELECTION`, `ABSTENTION`.
- `base_contract_id` (str): Identifier of the underlying synthetic base contract.
- `mutation_id` (str): Identifier of the active mutation applied.
- `user_prompt` (str): User instruction delivered to the model.
- `expected_tool_name` (Optional[str]): Target tool name (null for abstention).
- `expected_arguments` (Optional[Dict]): Ground-truth argument dictionary (null for abstention).
- `expected_latent_intent` (Optional[Dict]): Serialized `LatentIntent` (null for abstention).
- `available_tools` (List[Dict]): List of available tools with schemas.
- `oracle_config` (Dict): Configuration parameters for `StageCSemanticOracle`.
- `provenance_statement` (str): `"SYNTHETIC_STAGE_C_GOLD_TASK_INSTANCE"`.

## 5. Verification Matrix and Manifest

The manifest `results_stage_c/TASK_SET_MANIFEST.json` catalogs:
- Total task count: 300 instances.
- Category breakdown: exactly 100 Argument Construction, 100 Tool Selection, 100 Abstention.
- SHA-256 hash for every task file to guarantee immutability.
