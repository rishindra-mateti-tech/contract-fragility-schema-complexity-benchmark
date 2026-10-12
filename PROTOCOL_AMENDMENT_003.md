# PROTOCOL_AMENDMENT_003: Source-Faithful Representation and Scoring of Finite Object Unions in Stage B

**Date:** October 12, 2026  
**Reference:** `PROTOCOL.md`, `STAGE_B_EXTRACTION_SPEC.md` (Section 3.3, Section 7), `UNION_VALIDATION_TEST_PLAN.md`  
**Status:** RATIFIED  
**Target Corpus:** Stage B Canonical Real-Source Benchmark  

---

## 1. Context & Motivation

A comprehensive static pre-screen audit of frozen Stage B raw API specifications (`results_stage_b/pre_extraction_candidate_audit.json`) revealed that standard, high-value real-world operations in developer platforms (GitHub `issues/create`) and payments (Stripe `PostRefunds`, `PostCustomers`, `PostPaymentIntents`) define finite, object-level `oneOf` and `anyOf` schema variants:
- GitHub `issues/create` defines `labels.items` as a union between a simple label string and a structured label object (`{id, name, description, color}`).
- Stripe's OpenAPI 3.0 specification systematically represents unsetting/clearing of nested objects (`metadata`, `address`, `payment_method_options`) via `anyOf: [{"type": "object", ...}, {"type": "string", "enum": [""]}]`.

Under the initial frozen Section 3.3 specification, `oneOf` and `anyOf` compositions were restricted strictly to primitive scalar choices (e.g. `string | integer`), with all other union structures marked `EXCLUDE_PENDING`. 

This Amendment establishes a rigorous, non-lossy canonical eligibility framework to permit **source-faithful, finite object-level unions** without resorting to heuristic pruning, arbitrary branch dropping, or synthetic flattening.

---

## 2. Canonical Eligibility & Invariants for Finite Object Unions

To qualify for canonical inclusion under this amendment, object-level union structures must adhere strictly to the following invariants:

1. **Verbatim Branch Preservation**:
   - Every original union branch must be preserved verbatim and in source order.
   - Absolutely **no branch dropping**, selective pruning, flattening, conversion to generic untyped objects (`{}` or `{"type": "object"}`), or heuristic simplification is permitted.
2. **Discriminator Preservation**:
   - Upstream `discriminator` metadata (including `propertyName` and explicit `mapping` dictionaries) must be preserved verbatim in the derived contract.
3. **Branch-Level Lineage Traceability**:
   - Each variant branch within an object union must receive an explicit, machine-verifiable entry in `canonical_field_lineage.jsonl` recording its branch index, exact upstream source JSON Pointer, and branch-level cryptographic SHA-256 hash.
4. **Finite, Non-Cyclic Recursion Bound (MAX_RECURSION_DEPTH = 5 Unaltered)**:
   - The union structure must have finite branch cardinality and zero cyclic references.
   - **Crucial Invariant:** Ratification of Amendment 003 strictly **does not alter** the frozen rule `MAX_RECURSION_DEPTH = 5`. Any union-bearing candidate exceeding depth 5 remains disqualified and excluded (`EXCLUDE_PENDING`).
5. **Strict Protocol vs. Provider Separation**:
   - If a downstream inference provider, hosted API proxy, or model tool-calling interface cannot ingest or correctly parse the preserved JSON Schema union, this failure must be recorded strictly as a **downstream provider-interface limitation**.
   - Under no circumstances may the canonical schema be mutated, flattened, or stripped to accommodate provider-specific constraints.

---

## 3. Source-Faithful Validation & Scoring Framework

1. **Structural Validation Rule**:
   - A model-generated tool call payload is structurally valid under an object-union contract if and only if it validates cleanly against **at least one complete original variant branch** according to standard JSON Schema Draft-07 validation rules.
2. **Branch-Aware Semantic Scoring**:
   - Semantic correctness scoring must evaluate model arguments against the specific branch selected by the model. 
   - A model call that provides a valid scalar label name (Branch 0) is scored against scalar semantics; a call providing a structured label dictionary (Branch 1) is scored against object semantics.
3. **Stratified Reporting & Empirical Isolation**:
   - In benchmark result tables and regression analyses, union-bearing operations must be reported **both as stratified sub-cohorts and in pooled views**, enabling explicit measurement of whether polymorphic union boundaries amplify model fragility relative to monomorphic contracts.
4. **Pre-Implementation Test Requirement**:
   - Dedicated union-preservation validation specifications are established in `UNION_VALIDATION_TEST_PLAN.md`. All validation tests must pass before canonical extraction execution.

---

## 4. Ratification Scope & Operation Classifications

1. **Ratification Action**:
   - Amendment 003 is formally ratified as of October 12, 2026.
2. **Admitted Operation (`PROVISIONAL_CANONICAL_CANDIDATE_FAITHFUL_UNION`)**:
   - **Stripe `PostRefunds`** (`#/paths/~1v1~1refunds/post`): Admitted under ratified Amendment 003. It has observed recursion depth 3 ($\le 5$), zero cycles, zero binary fields, and its sole non-monomorphic structure is the finite `metadata` object/string `anyOf`.
3. **Permanently Excluded Operations Due to Depth Limits (`EXCLUDE_PENDING`)**:
   - **GitHub `issues/create`** (observed depth 6): Excluded under Section 2.2 / Section 3.2 depth limit ($6 > 5$).
   - **Stripe `PostCustomers`** (observed depth 6): Excluded under Section 2.2 / Section 3.2 depth limit ($6 > 5$).
   - **Stripe `PostPaymentIntents`** (observed depth 9): Excluded under Section 2.2 / Section 3.2 depth limit ($9 > 5$).
   - Amendment 003 provides no waiver for recursion depth limits.
4. **Stage A Absolute Invariance**:
   - This amendment applies solely to Stage B empirical expansion. Stage A schemas, results, manifests, scripts, paper tables, and audits remain 100% frozen and untouched.
