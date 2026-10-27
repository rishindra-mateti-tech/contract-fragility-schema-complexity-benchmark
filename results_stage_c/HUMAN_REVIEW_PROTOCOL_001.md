# Stage C Human Review Protocol (PROTOCOL-001)

## 1. Scope and Scientific Objective

This protocol specifies the qualification, task presentation, response capture, and quality standards governing human validation of the Stage C benchmark task suite.
The purpose of independent human review is to empirically verify that benchmark task prompts are natural, unambiguous, free from unintended shortcut cues, and soluble by human experts given only the declared tool schemas.

Current Status: `NO_HUMAN_REVIEW_RESULTS_PRESENT`. Author self-inspection does not constitute independent review and independent review remains pending.

## 2. Reviewer Qualification Criteria

To qualify for participation, reviewers must satisfy the following prerequisite criteria:
1. **Technical Literacy**: Practical experience working with JSON, REST APIs, or structured RPC specifications.
2. **Schema Comprehension**: Demonstrated familiarity with JSON Schema Draft-07 validation rules, including types, required properties, and `additionalProperties: false`.
3. **Qualification Packet Completion**: Reviewers must independently complete the 5 qualification calibration items in `results_stage_c/HUMAN_REVIEW_QUALIFICATION_PACKET.md` with at least 80% consensus agreement prior to receiving benchmark assignment batches.
4. **Independence Invariant**: Reviewers must not be co-authors of the benchmark generation engine or have prior access to gold answer keys.

## 3. Reviewer Workflow and Presentation Environment

Reviewers interact strictly through the offline local reviewer application (`review_app/`):
- All items are presented in randomized order.
- Each item displays:
  - Natural-language user prompt.
  - Candidate tool signatures and parameter schemas.
  - Standardized review instructions.
- Reviewers never see gold tool names, gold arguments, mutation family labels, or benchmark internal IDs.
- For each item, reviewers submit:
  - Selected tool name (or explicit abstention).
  - Constructed argument dictionary (JSON).
  - Confidence rating on a 1 (low) to 5 (high) Likert scale.
  - Ambiguity flag (`is_ambiguous`).
  - Optional rationale or commentary.

## 4. Response Standardization and Submission

All reviews are exported as hash-verified JSON submission bundles conforming to `results_stage_c/HUMAN_REVIEW_RESULTS_SCHEMA.json`.
No internet connectivity, cloud analytics, or external telemetry is permitted during review sessions.
