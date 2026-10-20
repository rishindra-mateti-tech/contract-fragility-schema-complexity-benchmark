# Stage B Reproducibility and Infrastructure Integrity Audit

## 1. Audit Executive Summary

- **Audit Date:** 2026-10-19T23:25:00Z
- **Auditor Role:** AUTHOR_MANUAL_REVIEW
- **Benchmark Phase:** Stage B Research Infrastructure Hardening
- **Repository:** `contract-fragility-schema-complexity-benchmark`
- **Audit Outcome:** PASS (7/7 Integrity Checks Satisfied)
- **Status Invariant Compliance:** STRICT (Zero unauthorized slot extractions; zero claims of `CANONICAL_FAITHFUL`)

---

## 2. Environment and Dependency Verification

The benchmark execution environment enforces pinned dependencies to ensure that tests and extraction routines run identically across development workstations and continuous integration runners.

| Package | Pinned Version | Installed Version | Status |
| :--- | :--- | :--- | :--- |
| `python` | `>= 3.10` | `3.13.2` | VERIFIED |
| `pytest` | `9.1.1` | `9.1.1` | VERIFIED |
| `jsonschema` | `4.25.1` | `4.25.1` | VERIFIED |
| `pyyaml` | `6.0.3` | `6.0.3` | VERIFIED |

---

## 3. Raw Specification Provenance Verification

All 7 pinned raw specifications were cryptographically verified against `data_stage_b/provenance/raw_source_registry.json`. Both file SHA-256 and Git blob SHA match the registered values with zero drift.

| Candidate ID | Cluster ID | Domain | Local File Path | Raw File SHA-256 | Git Blob SHA | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAND-001` | `CLUSTER_GITHUB` | Developer Platforms | `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json` | `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194` | `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d` | VERIFIED |
| `CAND-002` | `CLUSTER_STRIPE` | Payments & Billing | `data_stage_b/raw/CAND-002/097be640e3c544e31e5bb090cfb6389fcf276708.json` | `19614457e5e347ba07e15e8b4e7b8979c52220ea1901a88bb3e81bfb3e15fba2` | `097be640e3c544e31e5bb090cfb6389fcf276708` | VERIFIED |
| `CAND-003` | `CLUSTER_DO` | Cloud Infrastructure | `data_stage_b/raw/CAND-003/f3d64c23f790c6ca7e0c463f82cb3cfc48dc268c.yaml` | `4b18dfa711f18e95738c64bb9c2a8cbf4d707792ec06f7bf308b4ef8471169c9` | `f3d64c23f790c6ca7e0c463f82cb3cfc48dc268c` | VERIFIED |
| `CAND-004` | `CLUSTER_TWILIO` | Telephony & Messaging | `data_stage_b/raw/CAND-004/d8df17945d8b857731737e6da824eb8729ce9bb9.json` | `296a60db2fa9d83dfeb8bb1db4be896f64244247e8b919d7dbe989a647aa5e20` | `d8df17945d8b857731737e6da824eb8729ce9bb9` | VERIFIED |
| `CAND-005` | `CLUSTER_LINE` | Messaging & Bots | `data_stage_b/raw/CAND-005/a9eb8ee2c94c038ee84ea993fefb09f0df1fe746.yaml` | `0297ea4f3c0ce2fdbbe7e85c1815b3a985f5e55e88698bfd9c79fa4340333221` | `a9eb8ee2c94c038ee84ea993fefb09f0df1fe746` | VERIFIED |
| `CAND-006` | `CLUSTER_BOX` | Content & Files | `data_stage_b/raw/CAND-006/d3bc8f278eb1711202ec27027ae3e2646631b0e5.json` | `dff6d31872df03d7f1da260fc900a6f8ff5ff1303867c29633c5e2972ee78e38` | `d3bc8f278eb1711202ec27027ae3e2646631b0e5` | VERIFIED |
| `CAND-007` | `CLUSTER_CHATWOOT` | Customer Support | `data_stage_b/raw/CAND-007/b99480a6b7d2f33c3a45c71d64380eb922c0ff2e.json` | `dbfa16e91ea6b67bc1ca6b86fb3510f01ba333e6c0c20a4b7f94082fb5a473e6` | `b99480a6b7d2f33c3a45c71d64380eb922c0ff2e` | VERIFIED |

---

## 4. Test Suite Execution Summary

The complete pytest test suite was executed across all modules:
- Total tests collected: 163
- Passed: 163
- Failed: 0
- Skipped: 0
- Execution duration: ~134 seconds

### Module Coverage Breakdown
1. `tests/test_audit.py`: Stage A audit tests (1 test)
2. `tests/test_audit_stage_b_prescreen.py`: Stage B candidate prescreen audit (10 tests)
3. `tests/test_mutations.py`: Mutation operator tests (5 tests)
4. `tests/test_rank_stage_b_replacement_candidates.py`: Replacement candidate ranking (10 tests)
5. `tests/test_runner.py`: Runner execution tests (6 tests)
6. `tests/test_scan_stage_b_raw_operation_universe.py`: Raw operation scanning (15 tests)
7. `tests/test_stage_b_admitted_candidates.py`: Candidate admission verification (6 tests)
8. `tests/test_stage_b_canonical_extraction_pilot.py`: GitHub pilot extraction and validation (21 tests)
9. `tests/test_stage_b_canonical_generalization_stripe.py`: Stripe generalization extraction (15 tests)
10. `tests/test_stage_b_canonical_pilot_human_validation_packet.py`: Human validation packet tests (9 tests)
11. `tests/test_stage_b_extraction_readiness.py`: Full-cohort extraction readiness audit (4 tests)
12. `tests/test_stage_b_human_review_packet.py`: Stage B admission human review packet (9 tests)
13. `tests/test_stage_b_raw_sources.py`: Raw source integrity verification (4 tests)
14. `tests/test_stage_b_schema_feature_registry.py`: Schema feature support registry (16 tests)
15. `tests/test_stage_b_adversarial_feature_corpus.py`: Adversarial feature corpus and metamorphic tests (24 tests)
16. `tests/test_openapi_serialization.py`: OpenAPI JSON and form-urlencoded serialization (8 tests)

---

## 5. Deterministic Re-Extraction Stability Audit

Deterministic re-extraction was performed into isolated temporary directories for the two admitted pilot slots.

| Slot ID | Operation | Pinned Timestamp | Contract Byte Match | Lineage Byte Match | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_GITHUB_01` | `pulls/create` | `2026-10-12T18:15:00Z` | IDENTICAL (Bitwise 1:1) | IDENTICAL (Bitwise 1:1) | PASS |
| `SLOT_STRIPE_02` | `PostShippingRates` | `2026-10-19T18:04:16Z` | IDENTICAL (Bitwise 1:1) | IDENTICAL (Bitwise 1:1) | PASS |

---

## 6. Canonical Artifact Hash Registry

Authoritative hashes for active canonical contracts on disk:
- `data_stage_b/canonical/SLOT_GITHUB_01/canonical_contract.json`: `43c7a75070e310e13499f8128d6d3a061b46de94238cb5c8ca7044ca103b23b9`
- `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json`: `c7e2a3a33078a892ca861684ca963dd00a3ea7cdbd0a9cb2e215b2912547cdbc`

---

## 7. Status Invariant and Lifecycle Enforcement

1. `SLOT_GITHUB_01`:
   - Lifecycle Status: `CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY`
   - Author Review Decision: `APPROVE_WRAPPER_POLICY`
   - Independent Validation Claimed: `False`
2. `SLOT_STRIPE_02`:
   - Lifecycle Status: `EXTRACTED_PENDING_HUMAN_VALIDATION`
   - Author Review Decision: `None` (unreviewed)
   - Independent Validation Claimed: `False`
3. Zero Operations marked `CANONICAL_FAITHFUL`: Verified.
4. Canonical Directory Cleanliness: Strictly contains only `SLOT_GITHUB_01` and `SLOT_STRIPE_02` directories and `global_field_lineage_index.jsonl`.
