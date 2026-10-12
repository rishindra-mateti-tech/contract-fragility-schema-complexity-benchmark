# UNION_VALIDATION_TEST_PLAN: Verification Protocol for Source-Faithful Object Unions

**Version:** 1.0.0  
**Date:** October 12, 2026  
**Reference:** `PROTOCOL_AMENDMENT_003.md`, `STAGE_B_EXTRACTION_SPEC.md` (Sections 3.3, 5, 7)  
**Status:** APPROVED_DESIGN_SPEC (Specification Only — No Implementation Code)  
**Target Operations:** Stage B Faithful-Union Cohort (`Stripe PostRefunds`)  

---

## 1. Objective & Scope

Under ratified `PROTOCOL_AMENDMENT_003.md`, finite source-faithful object unions are permitted in the Stage B canonical real-world benchmark without lossy pruning or artificial flattening. 

This document defines the formal validation test plan and verification protocol that will govern all union-bearing operations prior to admission into `CANONICAL_FAITHFUL`. It specifies test cases, validator invariants, expected fixtures, and failure criteria. In strict accordance with benchmark design rules, this document is a specification only; test code implementation will occur only after the extraction engine architecture is formally authorized.

---

## 2. Core Invariants to be Tested

Every union-bearing canonical contract must satisfy six immutable invariants:

1. **Zero Branch Dropping (Completeness)**:
   All upstream variant branches declared under `oneOf` or `anyOf` must be present in the extracted contract in exact upstream source order.
2. **Zero Heuristic Degradation (Faithfulness)**:
   No union variant may be converted to an untyped container (`{}` or `{"type": "object"}`), stripped of required properties, or pruned of nested definitions.
3. **Branch-Level Cryptographic Lineage**:
   Each union branch must have an independent entry in `canonical_field_lineage.jsonl` with an exact source JSON Pointer and cryptographic hash.
4. **Recursion Depth Bound ($\le 5$)**:
   No branch within the union may cause the operation's maximum recursion depth to exceed the frozen limit `MAX_RECURSION_DEPTH = 5`.
5. **Standard Draft-07 Validator Conformance**:
   Validation of model-generated tool call arguments must execute natively against standard JSON Schema Draft-07 validator rules (e.g., Python `jsonschema` Draft7Validator).
6. **Strict Protocol vs. Provider Separation**:
   If an inference provider API (e.g. OpenAI function calling, Anthropic tool use, Gemini function declarations) rejects or misinterprets an `anyOf`/`oneOf` schema, the canonical contract must remain unmodified. The issue must be logged strictly as a provider interface constraint.

---

## 3. Planned Test Suites & Verification Criteria

### Suite 1: Structural Completeness & Branch Order Verification
- **Target**: `Stripe PostRefunds` (`#/paths/~1v1~1refunds/post`)
- **Inspection Target**: `body.metadata` property schema (`anyOf`)
- **Test Logic**:
  1. Resolve canonical extracted schema for `PostRefunds`.
  2. Inspect `properties.body.properties.metadata`.
  3. Assert `anyOf` exists and contains exactly 2 branches:
     - Branch 0: `{"type": "object", "additionalProperties": {"type": "string"}}` (or equivalent source key-value mapping).
     - Branch 1: `{"type": "string", "enum": [""]}` (representing upstream sentinel clearing).
  4. Assert neither branch is pruned, omitted, or reordered.

### Suite 2: Cryptographic Field Lineage Integrity
- **Target**: `canonical_field_lineage.jsonl`
- **Test Logic**:
  1. Query lineage records for `operation_id == "PostRefunds"`.
  2. Verify existence of branch-level lineage entries:
     - `PostRefunds.body.metadata.anyOf[0]`
     - `PostRefunds.body.metadata.anyOf[1]`
  3. Assert source JSON pointer resolves directly against frozen raw source `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`.
  4. Assert source branch SHA-256 matches computed SHA-256 of extracted branch definition.

### Suite 3: Dual-Branch Payload Validation (Draft-07 Conformance)
- **Target**: Model payload validator
- **Test Logic**:
  1. Instantiate standard JSON Schema Draft-07 validator with the extracted `PostRefunds` contract.
  2. **Valid Object Payload Test**:
     - Provide: `{"body": {"charge": "ch_123", "metadata": {"order_id": "9876", "reason": "damaged"}}}`
     - Assert: Validator returns `is_valid == True`, zero schema errors.
  3. **Valid Sentinel String Payload Test**:
     - Provide: `{"body": {"charge": "ch_123", "metadata": ""}}`
     - Assert: Validator returns `is_valid == True`, zero schema errors.
  4. **Invalid Variant Type Test**:
     - Provide: `{"body": {"charge": "ch_123", "metadata": 12345}}`
     - Assert: Validator returns `is_valid == False` with specific type violation on both branches.

### Suite 4: Semantic Evaluator Multi-Branch Routing
- **Target**: Semantic argument scorer
- **Test Logic**:
  1. Pass test cases with intent requiring dictionary metadata.
  2. Assert model providing Branch 0 dictionary is scored on key-value semantic match.
  3. Pass test cases with intent requiring metadata unsetting.
  4. Assert model providing Branch 1 empty string sentinel is scored on unsetting semantics.
  5. Assert scoring does not penalize models for choosing the valid variant corresponding to the task prompt.

### Suite 5: Depth Limit Enforcement & Rejection of Depth > 5
- **Target**: Depth verification gate across candidate pool
- **Test Logic**:
  1. Assert `PostRefunds` has observed depth 3, passing `depth <= 5`.
  2. Assert `PostCustomers` (observed depth 6) fails Suite 5 and remains `EXCLUDE_PENDING`.
  3. Assert `issues/create` (observed depth 6) fails Suite 5 and remains `EXCLUDE_PENDING`.
  4. Assert `PostPaymentIntents` (observed depth 9) fails Suite 5 and remains `EXCLUDE_PENDING`.
  5. Assert that no candidate with depth > 5 can be assigned `PROVISIONAL_CANONICAL_CANDIDATE_FAITHFUL_UNION`.

### Suite 6: Provider Isolation & Error Categorization
- **Target**: Provider adapter interface
- **Test Logic**:
  1. Feed the union-bearing contract through standard provider formatters (OpenAI, Anthropic, Google).
  2. If a provider API rejects `anyOf` at the top level or nested level:
     - Assert the rejection is captured as `PROVIDER_INTERFACE_INCOMPATIBILITY`.
     - Assert canonical contract hash is NOT altered.
     - Assert no fallback heuristic prunes the schema before downstream evaluation.

---

## 4. Negative & Adversarial Test Scenarios

| Test ID | Adversarial Condition | Expected Enforcement Result |
| :--- | :--- | :--- |
| `NEG-UNION-001` | Extractor prunes sentinel string branch `anyOf[1]` to simplify schema | **FATAL**: Lineage check detects missing branch; build aborts. |
| `NEG-UNION-002` | Extractor replaces `metadata` with untyped `{"type": "object"}` | **FATAL**: Schema diff detects lossy flattening; contract rejected. |
| `NEG-UNION-003` | Candidate declares self-referential recursive union | **FATAL**: Cycle detector trips; operation disqualified to `EXCLUDE_PENDING`. |
| `NEG-UNION-004` | Candidate declares union branch exceeding depth 5 | **FATAL**: Depth checker trips; operation disqualified to `EXCLUDE_PENDING`. |
| `NEG-UNION-005` | Model produces payload matching neither union branch | **VALIDATION_FAILURE**: Payload scored as 0 for structural adherence. |

---

## 5. Execution Pre-requisites & Verification Gate

1. This test plan must be fully satisfied by the future extraction engine before `Stripe PostRefunds` may be evaluated with local mocks or benchmark models.
2. In the current pre-extraction phase, `Stripe PostRefunds` remains provisionally categorized as `PROVISIONAL_CANONICAL_CANDIDATE_FAITHFUL_UNION`.
3. Its ultimate admission to `CANONICAL_FAITHFUL` requires passing all 6 validation suites in automated CI and receiving unanimous sign-off in the manual review audit.
