# Stage C Release 2 Design Specification

## 1. Executive Summary and Methodological Decoupling

Stage C Release 2 establishes a remediated, production-grade synthetic benchmark foundation for investigating how controlled schema-complexity mutations affect large language model (LLM) tool-use reliability.
Release 1 is preserved intact in `data_stage_c/` as immutable historical diagnostic evidence. Release 2 is created separately in `data_stage_c_release2/` and incorporates the findings from `results_stage_c/RELEASE1_FINDING_ADJUDICATION.md`.

The primary design principle of Release 2 is: **eliminate superficial shortcuts and unintended duplication without destroying the controlled experimental comparison**.

## 2. Paired-Group Experimental Architecture

1. **Explicit Paired Group Tracking**:
   - In Release 1, evaluating the same user goal across multiple schema variants triggered false positive "intent conflict" warnings.
   - Release 2 introduces a mandatory `paired_group_id` attribute for every task instance.
   - Tasks that share a `paired_group_id` share an identical underlying `LatentIntent` (same semantic intent and slots), but systematically vary:
     - The schema mutation family (`CANONICAL`, `NESTED_HIERARCHY`, `OPTIONALITY_BLOAT`, `AMBIGUOUS_IDENTIFIERS`, `DISTRACTOR_SET_COMPLEXITY`), or
     - The evaluation category (`ARGUMENT_CONSTRUCTION` vs `TOOL_SELECTION`).
   - This design isolates schema surface complexity as the sole independent variable while holding semantic intent constant.

2. **Intra-Cell Uniqueness Invariant**:
   - Two tasks may share a prompt only if they test distinct experimental conditions (e.g. comparing how a model handles the identical prompt under a flat schema vs a nested schema).
   - Within the same experimental cell (same task category, same mutation family, and same complexity stratum), duplicate prompts are strictly prohibited.

## 3. Task Category Protocols and Formatting Rules

### A. Argument Construction Tasks (`ARGUMENT_CONSTRUCTION`)
1. **Single Tool Exposure**: Exactly one tool schema is provided in `available_tools`.
2. **Tool-Name Omission from User Request**: The natural-language user prompt must never explicitly quote or mention the tool name. The tool identity is defined exclusively by the schema payload.
3. **Natural Language Argument Description**: Parameter requirements must be expressed through natural conversational language rather than programmatic key-value dumps (e.g. "set the cache timeout to 3600 seconds and enable overwrite" rather than `ttl_seconds set to 3600, overwrite set to True`).
4. **Complete Semantic Grounding**: Every non-inferable semantic value required by the gold invocation must be present in the user prompt. Structural wrappers introduced by mutations (e.g. `payload_parameters`) must be inferred by the model from schema definitions.

### B. Tool Selection Tasks (`TOOL_SELECTION`)
1. **Multiple Tool Candidates**: Each task presents between 3 and 9 candidate tools in `available_tools`.
2. **Target Name Masking**: The target tool name must never appear in the user prompt.
3. **Plausible Distractors**: Distractors are drawn from the same or related functional domains, sharing thematic vocabulary while having distinct parameter requirements or operational goals.
4. **Deterministic Positional Uniformity**: The target tool position within the candidate list is randomized deterministically from the prompt seed and balanced across candidate indices.
5. **No Parameter Shortcut Dumps**: Selection prompts describe the operational goal without listing verbatim parameter names, preventing models from selecting tools through lexical overlap with schema keys.

### C. Abstention Tasks (`ABSTENTION`)
1. **No Valid Tool Match**: Candidate tools are presented, but no candidate satisfies the user request.
2. **Abstention Keyword Blacklist**: Prompts must never include artificial abstention cues such as "none of these tools", "unavailable", "cannot fulfill", or "unsupported". The request must read as a natural user request for which no valid tool exists in the environment.
3. **Collision Verification**: Candidate toolsets must be verified against the prompt to ensure no candidate tool has all its required parameters satisfied by the user request.

## 4. Prompt Diversity and Template Architecture

1. **Multi-Frame Template Library**:
   - Each domain utilizes a diversified library of phrasing frames (e.g. imperative, contextual, conversational, and declarative request templates).
   - Phrasing frames decouple semantic values from field identifiers.
2. **Deterministic Seed Derivation**:
   - Prompt generation is parameterized by a deterministic seed derived from `hashlib.sha256(f"{task_id}_{paired_group_id}".encode()).hexdigest()`.
   - Ensures 100% offline reproducibility across all generated tasks.

## 5. Preregistered Release 2 Quality Gates

Before Release 2 can be packaged for blinded human review:
1. `UNRESOLVED_INVALID_TASKS == 0`: Zero tasks classified as `INVALID`.
2. `UNADJUDICATED_AMBIGUITY == 0`: Zero unadjudicated ambiguous items in selection or abstention.
3. `INTRA_CELL_DUPLICATES == 0`: Zero duplicate prompts within any experimental cell.
4. `TARGET_POSITION_SKEW <= 0.15`: Uniform target tool distribution across selection candidates.
5. `OPERATIONAL_STATE`: Programmatically frozen as `MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION`.
