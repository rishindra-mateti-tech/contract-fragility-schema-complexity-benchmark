# Stage C Task Leakage and Shortcut Audit Report (Release 1)

## 1. Executive Summary

- **Benchmark Release**: Release 1 (300 standardized tasks)
- **Audit Date**: 2026-10-27
- **Audited Tasks**: 300
- **Total Diagnostic Findings**: 651
- **Task Quality Classification Distribution**:
  - `CLEAR`: 40
  - `REQUIRES_HUMAN_REVIEW`: 160
  - `AMBIGUOUS`: 0
  - `INVALID`: 100

## 2. Leakage Dimension Findings Breakdown

| Dimension | Description | Finding Count | Typical Severity | Remediation Category |
| :--- | :--- | :---: | :---: | :--- |
| `TOOL_NAME_EXACT_LEAK` | Target tool name verbatim in prompt | 100 | High/Med | MASK_TOOL_NAME |
| `TOOL_NAME_SUBSTRING_LEAK` | Tool stem or normalized token in prompt | 80 | Med/Low | PARAPHRASE_VOCABULARY |
| `FIELD_NAME_EXACT_LEAK` | Schema parameter keys in prompt text | 166 | Medium | PARAPHRASE_VOCABULARY |
| `MUTATION_LABEL_LEAK` | Mutation family name in prompt | 0 | High | PARAPHRASE_VOCABULARY |
| `GOLD_VALUE_VERBATIM_COPY` | Verbatim JSON serialization in prompt | 0 | Critical | MARK_INVALID_REPLACE |
| `DISTRACTOR_LEXICAL_CONTRAST` | Asymmetric tool description length | 0 | Low | ISOLATE_DISTRACTOR |
| `POSITIONAL_BIAS` | Non-uniform target tool position | 0 | Medium | RANDOMIZE_POSITIONS |
| `DUPLICATE_PROMPTS` | Identical prompts across distinct tasks | 180 | Medium | PARAPHRASE_VOCABULARY |
| `INTENT_CONFLICT` | Same intent hash with conflicting gold args | 100 | Critical | MARK_INVALID_REPLACE |
| `ABSTENTION_VALID_TOOL_LEAK` | Abstention prompt providing valid params | 0 | High | MARK_INVALID_REPLACE |
| `SELECTION_MULTIPLE_VALID_TOOLS`| Colliding required-field signatures | 0 | High | ISOLATE_DISTRACTOR |
| `CONSTRUCTION_OMITTED_GOLD_VALUE`| Gold value missing entirely from prompt | 25 | High | MARK_INVALID_REPLACE |
| `PROMPT_FAMILY_WORDING_LEAK` | Prompt exposes schema mutation type | 0 | High | PARAPHRASE_VOCABULARY |
| `METADATA_PAYLOAD_LEAK` | Internal benchmark tokens in prompt | 0 | Critical | PARAPHRASE_VOCABULARY |

## 3. Methodological Observations and Distinction of Domain Vocabulary

1. **Explicit Tool Mentions in Argument Construction**:
   In Category 1 (Argument Construction), prompts explicitly reference the tool name (e.g., 'Please execute the set_cache_entry operation...').
   While this is expected behavior when isolating parameter construction in a single-tool setting, in Category 2 (Tool Selection) referencing the target tool name bypasses the selection construct. The audit flags tool mentions in selection tasks as `INVALID` and in construction tasks as `REQUIRES_HUMAN_REVIEW`.

2. **Field-Name Mentions versus Natural Language**:
   Many parameters (e.g., 'key', 'value', 'user_id', 'status') naturally occur in conversational instructions.
   The audit separates unavoidable common vocabulary from specialized parameter keys, flagging the latter for paraphrasing.

3. **Release 2 Remediation Recommendation**:
   To eliminate all potential shortcut vectors, a versioned Release 2 corpus (`data_stage_c_release2/`) should be created to:
   - Paraphrase field names with natural synonyms.
   - Strip all tool-name tokens from user prompts across all categories.
   - Positionally randomize tool selection candidate lists.
