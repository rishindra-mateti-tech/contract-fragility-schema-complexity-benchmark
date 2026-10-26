# Stage B Batch Extraction Pipeline V2 Scope Freeze and Protocol Baseline

**Protocol Status:** `FROZEN_AND_ENFORCED`  
**Pipeline Version:** `2.0.0`  
**Execution Date:** October 26, 2026  
**Governing Conversion Policy:** `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md`  
**Conversion Policy SHA-256:** `ca17608c3a1fcee075e5706928bfbc7f958d6e59e447e9461350f4afc9191290`  
**Target Output Directory:** `data_stage_b/extraction_candidates_v2/`  
**Preserved Historical Baseline:** `data_stage_b/extraction_candidates/` (Batch-V1 permanently immutable)  

---

## 1. Context and Methodological Imperative

Batch-V1 extraction candidates exposed an OpenAPI 3.0 to JSON Schema Draft-07 dialect discrepancy:
- OpenAPI 3.0 `nullable: true` was copied verbatim into candidate contracts declaring JSON Schema Draft-07.
- Because Draft-07 ignores `nullable`, standard Draft-07 validators rejected `null` payloads, creating a silent semantic divergence.
- Claims of "zero potential loss" and "full preservation" in Batch-V1 are retracted for dialect-affected slots.

Batch Pipeline V2 implements a deterministic, auditable, and fail-closed upgrade governed by `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`.

---

## 2. Strict Operational Boundaries

1. **Immutable Historical Baseline:** All 13 directories under `data_stage_b/extraction_candidates/` remain byte-for-byte immutable. They are not overwritten, moved, or deleted.
2. **Dedicated V2 Quarantine:** All V2 candidate bundles are isolated under `data_stage_b/extraction_candidates_v2/<SLOT_ID>/`.
3. **Canonical Directory Untouched:** `data_stage_b/canonical/` remains strictly restricted to `SLOT_GITHUB_01` and `SLOT_STRIPE_02`.
4. **Lifecycle State Invariance:** Every successfully extracted V2 candidate is assigned status `EXTRACTED_PENDING_HUMAN_VALIDATION`. No operation is elevated to `CANONICAL_FAITHFUL`.
5. **Zero Model or Live Runtime Activity:** Zero model evaluations, zero API calls, zero mock runtime executions, and zero mutation operators.
6. **Punctuation Standard:** Strictly zero em dashes and zero en dashes; hyphens, commas, or parentheses only.
7. **Anti-AI Tone Standard:** Zero emojis, zero subjective filler claims.

---

## 3. Cohort Partitioning

| Partition Category | Slot Count | Slot Identifiers | Action in V2 |
| :--- | :---: | :--- | :--- |
| **Existing Pilots (Skipped)** | 2 | `SLOT_GITHUB_01`, `SLOT_STRIPE_02` | Preserved in `data_stage_b/canonical/` |
| **Polymorphic Union (Excluded)** | 1 | `SLOT_STRIPE_03` (`PostRefunds`) | Excluded under Protocol Amendment 003 |
| **Eligible Monomorphic Candidates** | 13 | `SLOT_BOX_01..03`, `SLOT_CHATWOOT_01`, `SLOT_GITHUB_02..03`, `SLOT_LINE_01..03`, `SLOT_STRIPE_01`, `SLOT_TWILIO_01..03` | Extracted into `data_stage_b/extraction_candidates_v2/` under Policy 001 |
| **Fail-Closed Rejected Operations** | 14 | `SLOT_DO_01..03`, `SLOT_SLACK_01..03`, `SLOT_MCP_SQLITE_01..03`, `SLOT_MCP_GITHUB_01..03`, `SLOT_CHATWOOT_02..03` | Rejected fail-closed; recorded in `BATCH_V2_REJECTION_REGISTER.md` |
| **Total Active Manifest Operations** | **30** | All admitted Stage B operations accounted for | Complete mathematical accounting |

---

## 4. Required Candidate Bundle Structure (V2)

Each of the 13 V2 candidate directories must contain exactly 8 standard review artifacts:
1. `candidate_contract.json` (Valid JSON Schema Draft-07, `nullable` converted to type array `[T, "null"]` and keyword removed, `x-benchmark-metadata` with policy provenance).
2. `field_lineage.jsonl` (Field lineage with `transformation_category: "INTENTIONAL_REPRESENTATION_CHANGE"` for converted fields).
3. `difference_register.json` (Record of structural differences with policy pointers).
4. `difference_register.md` (Tabular difference report).
5. `extraction_metadata.json` (Cryptographic hashes, dialect metadata, policy SHA-256).
6. `feature_inventory.json` (Granular schema feature accounting).
7. `serialization_characterization.json` (Transport surface mapping).
8. `review_packet.md` (Author human-validation review document).
