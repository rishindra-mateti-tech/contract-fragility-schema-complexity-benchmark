# OpenAPI 3.0 to Draft-07 Dialect Correction Completion Report

**Block Status:** `COMPLETED_AND_REMOTE_VERIFIED`  
**Execution Date (UTC):** October 26, 2026  
**Governing Conversion Policy:** `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md`  
**Conversion Policy SHA-256:** `ca17608c3a1fcee075e5706928bfbc7f958d6e59e447e9461350f4afc9191290`  
**Audit Report:** `results_stage_b/OAS30_DRAFT07_COMPATIBILITY_AUDIT.md`  
**Batch V2 Results:** `results_stage_b/BATCH_V2_RESULTS.md`  
**Changelog:** `results_stage_b/BATCH_V1_TO_V2_CHANGELOG.md`  

**Full Automated Test Suite:** `239/239 PASSED (100%) in 93.58s`  
**Reproducibility Verification:** `9/9 CHECKS PASSED (100%)`  
**Epistemic Claim Linter:** `0 VIOLATIONS across 142 Markdown Documents (100% PASS)`  
**Historical V1 Baseline:** `100% BYTE-FOR-BYTE PRESERVED` (`data_stage_b/extraction_candidates/`)  
**Dedicated V2 Output Base:** `data_stage_b/extraction_candidates_v2/` (13 bundles, 104 artifacts)  

---

## 1. Executive Summary & Dialect Discrepancy Resolution

This block executed an urgent methodological correction addressing an OpenAPI 3.0 to JSON Schema Draft-07 dialect discrepancy identified in Batch-V1 extraction candidates:
1. In OpenAPI 3.0, `nullable: true` is an active modifier that extends a primitive type to accept `null`.
2. In JSON Schema Draft-07, `nullable` is an unrecognized keyword ignored by standard validators; nullability must be explicitly declared as a type union: `type: [<T>, "null"]`.
3. Verbatim copying of `{"type": "string", "nullable": true}` into Draft-07 contracts caused standard validators to reject valid `null` payloads (`ValidationError: None is not of type 'string'`), disproving prior claims of zero potential loss.

To resolve this discrepancy scientifically:
- A comprehensive static dialect audit was designed and executed across all 15 active Stage B operations (`src/audit_oas30_draft07_compatibility.py`).
- A formal four-tier conversion policy was enacted (`results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md`).
- A dedicated Batch Pipeline V2 was implemented (`src/stage_b_candidate_pipeline_v2.py`, `src/extract_stage_b_batch_candidates_v2.py`), generating 13 upgraded candidate bundles in `data_stage_b/extraction_candidates_v2/` while leaving historical V1 evidence completely untouched.
- Comprehensive semantic tests were automated (`tests/test_oas30_draft07_compatibility.py`), proving that null payloads pass V2 evaluation while failing V1, and that non-nullable enum boundaries remain strictly enforced.
- Reproducibility verification was expanded to 9 checks, confirming bit-for-bit re-extraction determinism for both V1 and V2 pipelines.

---

## 2. Dialect Audit and Candidate Accounting

### Candidate Cohort Partitioning

| Partition Category | Slot Count | Target Directory / Evidence Register | Status / Action |
| :--- | :---: | :--- | :--- |
| **Existing Pilot Slots (Skipped)** | 2 | `data_stage_b/canonical/` (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`) | Canonical directory untouched |
| **Polymorphic Union Slot (Excluded)** | 1 | `SLOT_STRIPE_03` (`PostRefunds`) | Excluded under Protocol Amendment 003 |
| **Batch Candidates Generated (V2)** | 13 | `data_stage_b/extraction_candidates_v2/` | Generated under Policy 001 (`EXTRACTED_PENDING_HUMAN_VALIDATION`) |
| **Operations Rejected Fail-Closed (V2)** | 14 | `results_stage_b/BATCH_V2_REJECTION_REGISTER.md` | Cleanly rejected without corrupted artifacts |
| **Total Active Manifest Operations** | **30** | `data_stage_b/admitted_manifest.json` | 100% accounted for |

### Dialect Audit Findings (928 Occurrences across 15 Slots)

- **V1 Candidates with Critical Divergence:** 1 slot (`SLOT_GITHUB_02`, where `target_url` and `description` had `nullable: true` copied into Draft-07).
- **V1 Candidates with Redundant Dialect Syntax:** 1 slot (`SLOT_BOX_01`, where `access` and `sync_state` had `nullable: false`).
- **Candidates with Non-Validating Annotations:** 5 slots (`SLOT_BOX_02`, `SLOT_BOX_03`, `SLOT_CHATWOOT_01`, `SLOT_GITHUB_03`, `SLOT_LINE_03` with singular `example` or `externalDocs`).
- **Candidates with Form Serialization Metadata:** 2 slots (`SLOT_STRIPE_01`, `SLOT_STRIPE_02` with `x-openapi-encoding`).
- **Candidates with Pure Syntactic Schemas:** 6 slots (`SLOT_GITHUB_01`, `SLOT_LINE_01`, `SLOT_LINE_02`, `SLOT_TWILIO_01`, `SLOT_TWILIO_02`, `SLOT_TWILIO_03`).

---

## 3. Policy Conversion Categories and Applied Transformations

All schema elements in V2 are categorized under `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`:

### Category A: Safe Syntactic Preservation (`PRESERVED`)
- Verbatim keyword preservation where syntax and assertion semantics are identical: `properties`, `required`, `type` (non-nullable), `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`, `items`, `minItems`, `maxItems`, `uniqueItems`, `enum`, `default`, `description`, `title`.

### Category B: Explicit Semantic-Preserving Conversion (`INTENTIONAL_REPRESENTATION_CHANGE`)
- **Nullable Type Union Transformation:** Applied to `SLOT_GITHUB_02` for `target_url` and `description`. Converted from `{"type": "string", "nullable": true}` to `{"type": ["string", "null"]}`. The OpenAPI keyword `nullable` is excised from the contract.
- **Redundant Nullable Quarantine:** Applied to `SLOT_BOX_01` for `access` and `sync_state`. The redundant keyword `nullable: false` is removed; primitive `type: "string"` is retained.
- **Lineage Classification:** Recorded in `field_lineage.jsonl` as `INTENTIONAL_REPRESENTATION_CHANGE` or `REPRESENTATION_NORMALIZATION`. Verbatim preservation labels are prohibited.

### Category C: Explicit Representation-Changing Normalization (`WRAPPER_NORMALIZATION`)
- **Closed-Object Wrapper Enforcement:** Applied to root and all transport surfaces (`path`, `query`, `header`, `body`) via `additionalProperties: false` under `WRAPPER_CLOSED_OBJECT_POLICY_001`.
- **Form Serialization Metadata:** Retained in `x-openapi-encoding` under `SERIALIZATION_TRANSPORT_METADATA_001`.

### Category D: Unsupported and Rejected Constructs (Fail-Closed)
- **Request-Surface `readOnly`:** Evaluated; zero occurrences in the 13 generated candidates. If encountered, fails closed under `ERR_READONLY_IN_REQUEST_SURFACE`.
- **Polymorphic Discriminator:** Rejects fail-closed under `ERR_POLYMORPHIC_DISCRIMINATOR`.
- **Object Unions:** Rejects fail-closed under `ERR_POLYMORPHIC_UNION`.

---

## 4. Retraction of Unqualified Preservation Claims

In compliance with epistemic governance:
1. All prior claims stating "zero extraction mismatches", "zero semantic potential losses", or "full semantic preservation" are formally retracted for Batch-V1 candidate slots containing `nullable: true` (specifically `SLOT_GITHUB_02`).
2. Batch-V1 candidates are designated `V1_REQUIRES_DIALECT_REVIEW` and superseded by V2.
3. Batch-V2 candidates are designated `V2_GENERATED_PENDING_HUMAN_VALIDATION`. Zero operations are designated `CANONICAL_FAITHFUL`.
4. This audit and conversion pipeline does NOT constitute independent third-party validation. Independent review remains a future publication gate.

---

## 5. Unresolved Scientific and Engineering Limitations

The following scientific boundaries and blockers remain active:
1. **14 Rejected Operations:** DigitalOcean (3), Slack (3), MCP SQLite (3), MCP GitHub (3), and Chatwoot (2) require non-monomorphic pipeline adapters (external URI ref bundling, `formData` transport mapping, Python/TypeScript AST extractors, and path-item parameter inheritance).
2. **Polymorphic Union Slot:** `PostRefunds` (`SLOT_STRIPE_03`) remains governed under Protocol Amendment 003 awaiting dedicated union validator construction.
3. **Wire Conformance Unvalidated:** In-process serialization equivalence is proven strictly at Tier 2. Live HTTP wire socket capture (Tier 3) and live server endpoint acceptance (Tier 4) remain unvalidated.
4. **Mock Execution and Model Evaluations:** Zero mock runtimes and zero LLM evaluations have been conducted.

---

## 6. Remote Verification Parity

Prior to final sign-off, all repository changes were committed in logical units, pushed to GitHub remote `origin/master`, and verified for exact bitwise parity:

| Verification Stage | Command / Metric | Result |
| :--- | :--- | :---: |
| **Commit 1 (Tracks 1 & 2)** | `46e48c7` | Dialect audit and conversion policy |
| **Commit 2 (Track 3)** | `2bb3309` | Pipeline V2 and 13 candidate bundles |
| **Commit 3 (Track 5)** | `74c29a9` | Claim ledger, dashboard, and reproducibility audit |
| **Final Local HEAD SHA** | `git rev-parse HEAD` | Verified identical to remote |
| **Final Remote HEAD SHA** | `git ls-remote origin refs/heads/master` | Verified identical to local |
| **Total Automated Tests** | `python -m pytest` | `239 passed in 93.58s` |
| **Reproducibility Checks** | `python scripts/verify_reproducibility.py` | `9/9 checks passed` |
| **Epistemic Monitored Claims** | `python -m src.lint_research_claims` | `0 violations across 142 files` |
