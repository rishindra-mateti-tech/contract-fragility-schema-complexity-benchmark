# Stage C Release 2 Changelog (from Release 1)

## 1. Architectural Overview and Immutability Notice

This changelog documents all structural and methodological differences between Release 1 and Release 2.
Release 1 is preserved intact in `data_stage_c/` and serves as immutable historical diagnostic evidence. Release 2 is generated independently in `data_stage_c_release2/`.

## 2. Itemized Changelog

### A. Paired Experimental Design Tracking
- **Release 1**: Tasks generated from the same base contract shared latent intent hashes, but lacked an explicit pairing schema attribute. The Release 1 audit flagged 100 tasks as `INTENT_CONFLICT`.
- **Release 2**: Every task includes an explicit `paired_group_id`. Shared intents across mutation variants are recognized as intentional controlled experimental pairings rather than conflicting tasks.

### B. User Prompt Naturalization and Leakage Elimination
- **Release 1**:
  - Argument Construction prompts explicitly quoted the target tool name (`Please execute the {tool_name} operation...`), creating 100 `TOOL_NAME_EXACT_LEAK` findings.
  - Parameter values were formatted via literal schema key assignments (`Specific parameters required: {key} set to {value}`), triggering 166 `FIELD_NAME_EXACT_LEAK` findings.
- **Release 2**:
  - Argument Construction prompts completely omit tool names. The tool declaration is provided solely within the single available tool schema payload.
  - Prompts are rephrased into conversational English sentences describing the desired values without quoting programmatic snake_case keys.

### C. Elimination of Intra-Cell Duplicate Prompts
- **Release 1**: Generating 100 tasks by modulo cycling over 40 contracts caused tasks 41 through 100 to repeat identical prompt text within the same category and mutation family, producing 180 `DUPLICATE_PROMPTS` findings.
- **Release 2**: Every task instance uses distinct prompt seeds, diversified argument values, and varied template frames. Duplicate prompts within the same experimental cell are reduced to zero.

### D. Audit Rule Recalibration for Synthetic Schemas
- **Release 1**: The leakage audit rule checked top-level keys of `expected_arguments`. On `NESTED_HIERARCHY` mutations, the synthetic wrapper object `payload_parameters` was flagged as a missing user value in 25 tasks (`CONSTRUCTION_OMITTED_GOLD_VALUE`).
- **Release 2**: The leakage auditor traverses nested schema structures and verifies underlying leaf values rather than synthetic schema wrapper identifiers.

### E. Distractor Ambiguity Remediation in Abstention
- **Release 1**: In 3 abstention tasks (`TASK_SYNTH_AB_001`, `041`, `081`), candidate tool `synth_create_key_value` had all required parameters mentioned in the user prompt, creating genuine semantic ambiguity.
- **Release 2**: Candidate tool selection for abstention tasks enforces strict negative filtering, ensuring no candidate tool can have all its required properties satisfied by the user prompt.

### F. Task Metadata Schema Expansion
- **Release 1 Task Record**: Contained 11 fields (`task_id`, `category`, `base_contract_id`, `mutation_id`, `mutation_family`, `user_prompt`, `expected_tool_name`, `expected_arguments`, `expected_latent_intent`, `available_tools`, `oracle_config`).
- **Release 2 Task Record**: Expands to 18 fields by adding:
  - `paired_group_id`: Unique identifier for the semantic paired group.
  - `prompt_template_id`: Template frame identifier.
  - `prompt_seed`: Deterministic seed used for prompt rendering.
  - `target_position`: Integer index of target tool in candidate list.
  - `task_sha256`: Cryptographic digest of complete task instance.
  - `schema_sha256`: Cryptographic digest of available tool schemas.
  - `prompt_sha256`: Cryptographic digest of user prompt text.
  - `release_marker`: Set to `"RELEASE_2_PENDING_HUMAN_VALIDATION"`.
