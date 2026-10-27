# Stage C Leakage Detection Policy (POLICY-001)

## 1. Objective and Theoretical Scope

This policy establishes the formal detection criteria, classification standards, and remediation rules for potential prompt leakage and shortcut cues within the Stage C benchmark.
An effective benchmark must ensure that an agent solves a task through semantic understanding and schema adherence rather than exploiting superficial lexical artifacts, prompt-target name sharing, or positional clustering.

This policy enforces transparent, fail-closed auditing. Diagnostic heuristics are explicitly labeled as heuristics and do not substitute for human validation.

## 2. The 14 Pre-Registered Leakage Dimensions

### 2.1 Direct Lexical and Identity Leakage
1. **TOOL_NAME_EXACT_LEAK**:
   - *Definition*: Verbatim target tool name occurs in the natural-language user prompt.
   - *Severity*: CRITICAL/HIGH in Tool Selection (bypasses selection construct); MEDIUM in Argument Construction.
   - *Classification*: `INVALID` for selection tasks; `REQUIRES_HUMAN_REVIEW` for single-tool construction.
   - *Remediation*: Replace tool name with functional domain description.

2. **TOOL_NAME_SUBSTRING_LEAK**:
   - *Definition*: Sub-word stem or normalized token of the target tool (e.g., 'cache' for 'set_cache_entry') occurs in the prompt.
   - *Severity*: MEDIUM.
   - *Classification*: `REQUIRES_HUMAN_REVIEW`.
   - *Remediation*: Paraphrase using alternative domain terminology.

3. **FIELD_NAME_EXACT_LEAK**:
   - *Definition*: Schema parameter keys occur verbatim in the prompt.
   - *Distinction Invariant*: Common domain words (e.g., 'user', 'value', 'message', 'limit') are classified as `UNAVOIDABLE_DOMAIN_WORD`. Specialized technical keys (e.g., 'ttl_seconds', 'client_request_id', 'entry_identifier') are classified as `SHORTCUT_LEAK`.
   - *Classification*: `REQUIRES_HUMAN_REVIEW`.

4. **MUTATION_LABEL_LEAK**:
   - *Definition*: Internal benchmark mutation names (e.g., 'canonical', 'nested', 'bloat', 'ambiguous') appear in the prompt.
   - *Severity*: HIGH.
   - *Classification*: `INVALID`.
   - *Remediation*: Remove benchmark-internal labels from model-facing prompts.

5. **GOLD_VALUE_VERBATIM_COPY**:
   - *Definition*: Raw JSON argument serialization copied verbatim into the prompt.
   - *Severity*: CRITICAL.
   - *Classification*: `INVALID`.
   - *Remediation*: Paraphrase into conversational prose.

### 2.2 Distractor and Multi-Tool Environment Cues
6. **DISTRACTOR_LEXICAL_CONTRAST**:
   - *Definition*: Target tool description length or style diverges sharply from distractors (ratio > 3.0 or < 0.33).
   - *Severity*: LOW.
   - *Classification*: `REQUIRES_HUMAN_REVIEW`.
   - *Remediation*: Calibrate distractor descriptions to match target verbosity.

7. **POSITIONAL_BIAS**:
   - *Definition*: Target tool appearing at a non-uniform or fixed index position (e.g., index 0 clustering > 50%).
   - *Severity*: MEDIUM.
   - *Classification*: `REQUIRES_HUMAN_REVIEW`.
   - *Remediation*: Deterministically sort candidate tools or randomize order.

8. **DUPLICATE_PROMPTS**:
   - *Definition*: Multiple task instances sharing verbatim identical prompt strings.
   - *Severity*: MEDIUM.
   - *Classification*: `REQUIRES_HUMAN_REVIEW`.
   - *Remediation*: Introduce syntactic and stylistic phrasing variations.

9. **INTENT_CONFLICT**:
   - *Definition*: Identical latent intent hash mapped to conflicting expected gold argument payloads.
   - *Severity*: CRITICAL.
   - *Classification*: `INVALID`.
   - *Remediation*: Distinct intents must map to distinct semantic objectives.

10. **ABSTENTION_VALID_TOOL_LEAK**:
    - *Definition*: An abstention task where the prompt accidentally satisfies all required parameters of an available tool.
    - *Severity*: HIGH.
    - *Classification*: `AMBIGUOUS`.
    - *Remediation*: Explicitly invalidate or omit mandatory parameters.

11. **SELECTION_MULTIPLE_VALID_TOOLS**:
    - *Definition*: Multiple candidate tools share identical required-parameter signatures and descriptions.
    - *Severity*: HIGH.
    - *Classification*: `AMBIGUOUS`.
    - *Remediation*: Introduce distinguishing parameter boundaries or remove colliding tool.

12. **CONSTRUCTION_OMITTED_GOLD_VALUE**:
    - *Definition*: A required gold argument parameter is completely omitted from the user prompt.
    - *Severity*: HIGH.
    - *Classification*: `INVALID`.
    - *Remediation*: Provide all required parameter values in prompt or declare parameter as optional.

13. **PROMPT_FAMILY_WORDING_LEAK**:
    - *Definition*: Phrasing that informs the model whether to generate nested or flat structures (e.g., 'use the nested container').
    - *Severity*: HIGH.
    - *Classification*: `INVALID`.
    - *Remediation*: Restrict prompt strictly to business intent.

14. **METADATA_PAYLOAD_LEAK**:
    - *Definition*: Internal task IDs, seeds, hashes, or provenance tags appearing in prompt text.
    - *Severity*: CRITICAL.
    - *Classification*: `INVALID`.
    - *Remediation*: Strip internal metadata headers.

## 3. Remediation and Versioning Protocol

1. **Immutability of Historical Releases**:
   - Release 1 task artifacts (`data_stage_c/task_instances/`) must NEVER be modified in place.
   - Historical audit findings must remain transparently documented in `results_stage_c/TASK_LEAKAGE_AUDIT_RELEASE1.md`.
2. **Release 2 Generation Requirement**:
   - Any remediation of tasks flagged as `INVALID` or `AMBIGUOUS` must be generated into a dedicated, versioned workspace: `data_stage_c_release2/`.
   - Release 2 must undergo an identical automated leakage audit prior to human review gating.
