# Stage C Construct Validity Protocol (PROTOCOL-001)

## 1. Protocol Identification and Epistemic Objective

This protocol governs the construct-validity verification, leakage auditing, distractor calibration, and human-validation architecture for the Stage C controlled mutation benchmark.
Before any large language model (LLM) is evaluated on Stage C task instances, the benchmark must establish that the observed test performance will genuinely reflect the intended construct rather than methodological shortcuts, prompt leakage, distractor triviality, or positional confounding.

Current Benchmark State: `MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION`.

## 2. Theoretical Construct Operationalization

### 2.1 Target Construct Definition
The benchmark measures:
"Ability to map a natural-language request to an appropriate structured tool invocation under controlled schema-surface transformations."

### 2.2 Operationalized Construct Dimensions
1. **Argument Construction**: Translating user-specified entities, quantities, and flags into schema-compliant parameter objects adhering to JSON Schema Draft-07 syntax, types, and boundary rules (`additionalProperties: false`).
2. **Tool Selection**: Discriminating the uniquely capable tool from a set of distractors exhibiting controlled degrees of semantic and lexical proximity.
3. **Abstention**: Correctly recognizing when an instruction is unfulfillable, ambiguous, out of operational scope, or lacking mandatory inputs, and refraining from executing an invalid tool call.
4. **Surface Robustness**: Maintaining execution integrity across controlled structural perturbations (nesting, optional parameter bloat, and ambiguous identifier renaming).

### 2.3 Excluded Non-Constructs
The benchmark explicitly does not measure:
- Real-world production API availability, transport-layer latency, or wire serialization.
- Endpoint execution success, database mutation, or third-party service reliability.
- Software engineering coding proficiency beyond parameter payload construction.
- Encyclopedic knowledge, world trivia, or domain memorization.
- Business value or practical utility of the tool operations.
- Subjective stylistic preferences or conversational tone.

## 3. Pre-Registered Audit Dimensions

### 3.1 Task Leakage and Shortcut Dimensions
The audit engine (`src/audit_stage_c_task_leakage.py`) evaluates 14 distinct leakage pathways:
1. `TOOL_NAME_EXACT_LEAK`: Verbatim target tool name in prompt text.
2. `TOOL_NAME_SUBSTRING_LEAK`: Target tool stem or normalized alias in prompt text.
3. `FIELD_NAME_EXACT_LEAK`: Schema parameter keys copied verbatim into prompt.
4. `MUTATION_LABEL_LEAK`: Explicit mention of mutation family names (e.g., "nested", "bloat", "alias") in prompt text.
5. `GOLD_VALUE_VERBATIM_COPY`: Raw JSON values unparaphrased in prompt text.
6. `DISTRACTOR_LEXICAL_CONTRAST`: Distractors differing so radically in length or domain that target identity is trivially obvious.
7. `POSITIONAL_BIAS`: Target tool appearing at a non-random or fixed index position across tasks.
8. `DUPLICATE_PROMPTS`: Repeated or near-identical prompts across distinct tasks.
9. `INTENT_CONFLICT`: Identical latent intents mapped to contradictory gold parameters.
10. `ABSTENTION_VALID_TOOL_LEAK`: An abstention task accidentally possessing a validly executable tool.
11. `SELECTION_MULTIPLE_VALID_TOOLS`: A selection task containing more than one equally valid tool candidate.
12. `CONSTRUCTION_OMITTED_GOLD_VALUE`: Prompt failing to specify a required semantic value present in gold arguments.
13. `PROMPT_FAMILY_WORDING_LEAK`: Prompt phrasing that signals whether the underlying contract is canonical or mutated.
14. `METADATA_PAYLOAD_LEAK`: Task metadata, hashes, or internal IDs leaking into model-facing payloads.

### 3.2 Distractor Quality and Task Ambiguity Dimensions
Evaluated on Category 2 (Tool Selection) and Category 3 (Abstention):
- **Lexical Similarity**: Jaccard and edit-distance metrics between target and candidate tool names and descriptions.
- **Semantic Field Overlap**: Proportion of shared property names and types across candidate tools.
- **Signature Collision**: Identical required property sets causing ambiguity between distinct tools.
- **Candidate Set Size**: Balance across 3, 5, and 9 candidate tool environments.
- **Positional Uniformity**: Target tool placement distribution across candidate list indices.
- **Accidental Duplication**: Co-occurrence of identical tool signatures within the same candidate set.

### 3.3 Corpus Balance and Diversity Dimensions
Evaluated across all 300 task instances:
- Equal category balance (100 AC, 100 TS, 100 AB).
- Stratum distribution across base contracts (Simple Flat, Medium Arrays/Enums, Nested Objects).
- Mutation family parity (Canonical, Nested Hierarchy, Optionality Bloat, Ambiguous Identifiers, Distractor Set Complexity).
- Structural metric distributions: nesting depth, field count, required ratio.
- Lexical diversity: vocabulary entropy and template duplication avoidance.

## 4. Task Classification Taxonomy

Audit findings classify tasks into one of four mutually exclusive quality states:
1. `CLEAR`: Non-leaky, unambiguous, well-formed task instance ready for evaluation.
2. `REQUIRES_HUMAN_REVIEW`: Borderline semantic overlap or natural domain vocabulary requiring independent human verification.
3. `AMBIGUOUS`: Conflicting or underspecified task definition where multiple interpretations exist.
4. `INVALID`: Confirmed leakage, missing mandatory gold parameter, or signature collision. Tasks in this state cannot be used for model evaluation.

## 5. Blind Human-Review Sampling Plan

1. **Sample Size**: A stratified sample of at least 90 task instances (minimum 30% of the 300-task suite).
2. **Stratification Variables**:
   - Task Category: 30 Argument Construction, 30 Tool Selection, 30 Abstention.
   - Mutation Family: Proportional representation across all 5 families.
   - Complexity Stratum: Balanced across Flat, Medium, and Nested strata.
   - Audit Status: Stratified inclusion of CLEAR, REQUIRES_HUMAN_REVIEW, and AMBIGUOUS items.
3. **Blinding Invariants**:
   - Strip all gold tool names, gold arguments, mutation family labels, base contract IDs, and author notes.
   - Assign pseudo-random blind IDs (`BLIND_TASK_XXX`) decoupled from original identifiers.
   - Deliver via an offline local reviewer application with zero network telemetry.

## 6. Reviewer Agreement and Adjudication Protocol

1. **Reviewer Multiplicity**: Every sampled task must receive independent reviews from at least two qualified reviewers ($K \ge 2$).
2. **Agreement Metrics**:
   - Tool Selection / Abstention: Cohen's kappa ($\kappa$) and raw percentage agreement.
   - Argument Construction: Field-level exact match and F1 agreement.
3. **Adjudication Mechanism**:
   - Any discordant task where reviewers disagree triggers an adjudication queue.
   - A third independent senior adjudicator resolves discrepancies.
   - If consensus cannot be achieved, the task is marked `INVALID` and excluded.
4. **Current Status**: `NO_HUMAN_REVIEW_RESULTS_PRESENT`. Author self-review shall never be characterized as independent validation.

## 7. Model-Execution Release Gates

Twelve mandatory verification gates must all evaluate to `PASS` before model evaluation can proceed:
1. Synthetic Base Corpus Reproducibility (`PASS`).
2. Mutation Registry Reproducibility (`PASS`).
3. Task Suite Reproducibility (`PASS`).
4. Task Leakage Audit Complete (`PASS`).
5. Distractor Quality Audit Complete (`PASS`).
6. Corpus Balance Audit Complete (`PASS`).
7. Zero Unresolved `INVALID` Tasks in Evaluation Set (`PENDING REVIEW`).
8. Blinded Human-Review Package Built (`PASS`).
9. Dual Independent Human Reviews Completed on Pre-Registered Sample (`PENDING HUMAN REVIEW`).
10. Inter-Rater Agreement Thresholds Satisfied ($\kappa \ge 0.70$) (`PENDING HUMAN REVIEW`).
11. Disagreements Adjudicated and Logged (`PENDING HUMAN REVIEW`).
12. Final Benchmark Task Suite Frozen and Hashed (`PENDING HUMAN REVIEW`).

Until all twelve gates pass, model execution is strictly forbidden.
