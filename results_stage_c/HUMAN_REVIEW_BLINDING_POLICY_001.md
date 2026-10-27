# Stage C Human Review Blinding Policy (POLICY-001)

## 1. Principles of Blinding Integrity

To prevent confirmation bias, halo effects, and benchmark-internal shortcuts during human validation, strict blinding protocols are enforced across all reviewer materials.
Evaluators must assess task prompts and schemas purely from the perspective of an external agent without access to gold labels or experimental hypotheses.

## 2. Masked and Redacted Information

The following metadata elements are strictly stripped from all reviewer packages:
1. **Target Tool Identity**: The designated gold tool name is omitted. All candidate tools are presented in standard schema format.
2. **Gold Arguments**: Ground-truth parameter dictionaries and slot mappings are omitted.
3. **Mutation Family**: Identifiers such as `CANONICAL`, `NESTED_HIERARCHY`, `OPTIONALITY_BLOAT`, `AMBIGUOUS_IDENTIFIERS`, or `DISTRACTOR_SET_COMPLEXITY` are scrubbed.
4. **Base Contract IDs**: Identifiers such as `BASE_SYNTH_001` are omitted.
5. **Generation Seed and Salts**: Master seed (42) and task index numbers are omitted.
6. **Task Identifiers**: Tasks are assigned blind identifiers (`BLIND_TASK_001` through `090`) generated through deterministic pseudo-random shuffling.
7. **Author Notes and Audit Flags**: Heuristic audit scores, collision notes, and ambiguity tags are omitted.

## 3. Server-Side Reconciliation Separation

The mapping between `blind_task_id` and `original_task_id` is maintained exclusively in `data_stage_c/reviewer_packages/author_reconciliation_map.json`.
This key file is stored in server-side storage and is strictly excluded from client-facing reviewer distribution archives.
The local review application server never serves gold parameters or original IDs to the browser DOM.
