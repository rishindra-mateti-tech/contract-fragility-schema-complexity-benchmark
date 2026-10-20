# Stage B Empirical Benchmark Execution Prerequisites

**Document Type:** Technical Prerequisite Specification & Execution Governance  
**Document Status:** `ACTIVE_PRECONDITION_POLICY`  
**Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md`  
**Current Enforcement State:** `LIVE_MODEL_EVALUATION_LOCKED` (Prerequisites Incomplete)  

---

## 1. Core Principle and Execution Lock

To prevent wasted API expenditures, unreproducible model calls, and invalid empirical findings, **no live model evaluations or benchmark runs may be executed for Stage B** until all five prerequisite gates are formally cleared and certified by automated tests.

Executing model calls against incomplete canonical contracts or simulated mock harnesses yields scientifically invalid data that cannot be published.

---

## 2. Five Mandatory Prerequisite Gates

### Prerequisite 1: 100% Canonical Extraction Coverage (Gate 3)
- **Mandate:** All 30 active manifest operations across all 10 clusters must be fully extracted into valid JSON Schema Draft-07 contracts.
- **Verification Criteria:**
  * 30/30 canonical contract files present in `data_stage_b/canonical/{cluster_id}/`.
  * `canonical_field_lineage.jsonl` contains 100% bidirectional mappings for all derived properties.
  * `audit_canonical_provenance.py` reports `POTENTIAL_LOSS: 0` and `DROPPED_REQUIRED_FIELDS: 0`.
- **Current Status:** `INCOMPLETE (2/30 extracted: SLOT_GITHUB_01, SLOT_STRIPE_02)`.

### Prerequisite 2: Independent Human Validation (Gate 4)
- **Mandate:** Double-blind external human validation must be executed across the stratified sample plan (14 operations, 28 independent evaluations) with Cohen's kappa $\kappa \ge 0.85$.
- **Verification Criteria:**
  * External reviewer sign-offs committed with cryptographic Git provenance.
  * Target operations elevated to `CANONICAL_FAITHFUL` or `CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY`.
  * Zero author self-certification used to claim independent validation.
- **Current Status:** `INCOMPLETE (0/14 sampled operations reviewed by independent panels)`.

### Prerequisite 3: Hermetic Offline Mock Execution Harness (Gate 6)
- **Mandate:** Deterministic offline mock state machines must be implemented for all 30 operations, eliminating all outbound network calls during benchmark runs.
- **Verification Criteria:**
  * In-memory state fixtures pre-configured for every operation (e.g. repository trees, base/head branches, customer records).
  * State transition validation: mock executors return RFC 7807 problem details or valid JSON responses without touching live web endpoints.
  * Socket-level network sandboxing: runner test suite asserts zero outbound HTTP/HTTPS packets.
- **Current Status:** `NOT_STARTED (Mock requirements partitioned in metadata, but zero mock engines built)`.

### Prerequisite 4: Rigorous Parameter Freezing Protocol (Gate 7)
- **Mandate:** All model evaluation generation parameters must be frozen to enforce determinism.
- **Verification Criteria:**
  * `temperature: 0.0` strictly enforced across all provider calls.
  * `seed: 42` (or provider-specific deterministic seed flags) passed in every payload.
  * Exact model snapshots pinned (e.g. `gpt-4o-2024-08-06`, `claude-3-5-sonnet-20241022`, `gemini-1.5-pro-002`) rather than moving alias tags.
- **Current Status:** `NOT_STARTED`.

### Prerequisite 5: Cost, Quota, and Telemetry Infrastructure (Gate 8)
- **Mandate:** Hard financial budget ceilings and rate-limiting queues must be configured before execution.
- **Verification Criteria:**
  * Pre-execution cost model estimating token expenditure ($N \ge 6,000$ calls $\times$ 1,500 avg tokens = ~9,000,000 tokens).
  * Hard spend limit configured with automatic kill-switch.
  * Full raw response logging (`raw_responses.jsonl`) recording prompt, completion, latency, token count, and raw bytes.
- **Current Status:** `NOT_STARTED`.

---

## 3. Enforcement and Invariant Sanctions

Any benchmark results obtained prior to formal certification of Prerequisites 1 through 3:
1. Are classified as `PREMATURE_AND_INVALID`.
2. Are barred from inclusion in any academic publication, preprint, or release note.
3. Must be purged from the repository results directory.
