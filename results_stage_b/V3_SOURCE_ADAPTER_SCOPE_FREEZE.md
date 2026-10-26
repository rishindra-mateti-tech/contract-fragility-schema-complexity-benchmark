# Stage B Source-Adapter Framework and V3 Candidate Extraction Scope Freeze

**Protocol Status:** `FROZEN_AND_ENFORCED`  
**Pipeline Version:** `3.0.0`  
**Execution Date:** October 26, 2026  
**Governing Dialect Conversion Policy:** `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md`  
**Governing Reference Resolution Policy:** `results_stage_b/OPENAPI_REFERENCE_RESOLUTION_POLICY_001.md`  
**Governing Parameter Inheritance Policy:** `results_stage_b/OPENAPI_PARAMETER_INHERITANCE_POLICY_001.md`  
**Governing OAS2 FormData Surface Policy:** `results_stage_b/OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001.md`  
**Target Output Directory:** `data_stage_b/extraction_candidates_v3/`  
**Preserved Historical Baselines:**
- `data_stage_b/canonical/` (`SLOT_GITHUB_01`, `SLOT_STRIPE_02` permanently immutable)
- `data_stage_b/extraction_candidates/` (Batch-V1 permanently immutable)
- `data_stage_b/extraction_candidates_v2/` (Batch-V2 permanently immutable)

---

## 1. Context and Methodological Objective

The Stage B batch candidate extraction pipeline V2 successfully extracted 13 monomorphic candidate bundles under `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`. However, 14 manifest operations remained rejected fail-closed due to structural and syntactic features not supported by the basic single-file OAS 3.0 parser:

1. Local multi-file `$ref` resolution: DigitalOcean operations (`SLOT_DO_01`, `SLOT_DO_02`, `SLOT_DO_03` in `CAND-003`) point to relative file paths across sibling subdirectories.
2. OpenAPI 2.0 / Swagger `formData` transport: Slack operations (`SLOT_SLACK_01`, `SLOT_SLACK_02`, `SLOT_SLACK_03` in `CAND-006`) declare parameters with `in: "formData"` and URL-encoded form serialization.
3. Path-item level parameter inheritance: Chatwoot operations (`SLOT_CHATWOOT_02`, `SLOT_CHATWOOT_03` in `CAND-011`) declare path parameters (such as `{account_id}`) at the path-item object level rather than inside the operation object.

The objective of Stage B Pipeline V3 is to implement generic, provenance-preserving source adapters that unlock exactly these 8 operations without manual per-slot patching or ad-hoc workarounds.

Operations requiring AST-based extraction (MCP Python AST and MCP TypeScript AST) and polymorphic union schemas (`PostRefunds`) remain strictly out of scope and rejected fail-closed.

---

## 2. Strict Operational Boundaries

1. **Historical Immutability:** Historical V1 artifacts (`data_stage_b/extraction_candidates/`) and V2 artifacts (`data_stage_b/extraction_candidates_v2/`) remain byte-for-byte immutable. They are neither overwritten, modified, nor deleted.
2. **Canonical Preservation:** `data_stage_b/canonical/` remains strictly limited to `SLOT_GITHUB_01` (pilot, validated) and `SLOT_STRIPE_02` (generalization, pending human validation).
3. **Dedicated V3 Isolation:** All newly generated candidates are written exclusively to `data_stage_b/extraction_candidates_v3/<SLOT_ID>/`.
4. **Lifecycle State Invariance:** Every extracted candidate is assigned status `EXTRACTED_PENDING_HUMAN_VALIDATION`. Zero operations are designated `CANONICAL_FAITHFUL`.
5. **Fail-Closed AST and Polymorphism Rejection:**
   - MCP SQLite Python AST operations (`SLOT_MCP_SQLITE_01`, `SLOT_MCP_SQLITE_02`, `SLOT_MCP_SQLITE_03`) must be rejected fail-closed.
   - MCP GitHub TypeScript AST operations (`SLOT_MCP_GITHUB_01`, `SLOT_MCP_GITHUB_02`, `SLOT_MCP_GITHUB_03`) must be rejected fail-closed.
   - Polymorphic union operation `SLOT_STRIPE_03` (`PostRefunds`) must be rejected fail-closed under Protocol Amendment 003.
6. **Zero Model or Live Network Activity:** Zero model/API calls, zero live network or HTTP wire requests, zero mock runtime executions, and zero mutation operators.
7. **Punctuation Standard:** Strictly zero em dashes and zero en dashes; hyphens, commas, or parentheses only.
8. **Anti-AI Tone Standard:** Zero emojis, zero subjective filler claims.

---

## 3. Cohort Partitioning (30 Manifest Operations)

| Partition Category | Count | Slot Identifiers | Processing Action in V3 |
| :--- | :---: | :--- | :--- |
| **Existing Pilots (Skipped)** | 2 | `SLOT_GITHUB_01`, `SLOT_STRIPE_02` | Preserved in `data_stage_b/canonical/` |
| **V2-Supported Monomorphic Operations** | 13 | `SLOT_BOX_01..03`, `SLOT_CHATWOOT_01`, `SLOT_GITHUB_02..03`, `SLOT_LINE_01..03`, `SLOT_STRIPE_01`, `SLOT_TWILIO_01..03` | Extracted into `data_stage_b/extraction_candidates_v3/` under V3 schema bundling |
| **Unlocked Multi-File Ref Operations** | 3 | `SLOT_DO_01`, `SLOT_DO_02`, `SLOT_DO_03` | Unlocked via generic local multi-file ref resolver adapter |
| **Unlocked OpenAPI 2.0 FormData Operations** | 3 | `SLOT_SLACK_01`, `SLOT_SLACK_02`, `SLOT_SLACK_03` | Unlocked via dedicated OpenAPI 2.0 form-surface adapter |
| **Unlocked Path Parameter Inheritance Operations** | 2 | `SLOT_CHATWOOT_02`, `SLOT_CHATWOOT_03` | Unlocked via OpenAPI path-item parameter inheritance adapter |
| **Fail-Closed Rejected MCP Python AST Operations** | 3 | `SLOT_MCP_SQLITE_01`, `SLOT_MCP_SQLITE_02`, `SLOT_MCP_SQLITE_03` | Rejected fail-closed; documented in V3 Rejection Register |
| **Fail-Closed Rejected MCP TypeScript AST Operations** | 3 | `SLOT_MCP_GITHUB_01`, `SLOT_MCP_GITHUB_02`, `SLOT_MCP_GITHUB_03` | Rejected fail-closed; documented in V3 Rejection Register |
| **Fail-Closed Rejected Polymorphic Union Operations** | 1 | `SLOT_STRIPE_03` | Rejected fail-closed under Protocol Amendment 003 |
| **Total Stage B Manifest Operations** | **30** | Complete set of admitted operations | Complete and exact mathematical accounting |

Total candidate bundles to be produced in V3: **21** (13 previous + 8 newly unlocked).  
Total operations rejected fail-closed in V3: **7** (6 MCP AST + 1 polymorphic union).  
Total skipped pilot operations: **2**.

---

## 4. Required Candidate Bundle Structure (V3)

Each candidate directory under `data_stage_b/extraction_candidates_v3/<SLOT_ID>/` must contain exactly 10 artifacts:

1. `candidate_contract.json`: Valid JSON Schema Draft-07 tool contract. Conforms to dialect conversion policy (no bare `nullable`), with explicit surface separation (`query`, `path`, `header`, `cookie`, `body`, or `form`).
2. `field_lineage.jsonl`: Lineage log mapping every extracted field back to its raw specification path, recording adapter transformations and representation changes.
3. `difference_register.json`: Machine-readable register recording structural or dialect changes applied during extraction.
4. `difference_register.md`: Human-readable summary table of differences.
5. `extraction_metadata.json`: Hashes, engine metadata, policy SHA-256 references, and extraction timestamps.
6. `feature_inventory.json`: Schema feature inventory categorized against the Stage B feature registry.
7. `serialization_characterization.json`: Transport surface characterization (JSON body vs form-urlencoded vs path/query).
8. `review_packet.md`: Human review packet for independent audit.
9. `source_reference_closure.json`: Complete list of source specification files accessed during extraction with cryptographic SHA-256 hashes.
10. `adapter_decisions.json`: Explicit record of which adapters were invoked, parameters inherited, and reference resolutions performed.

---

## 5. Verification Gate for Track 0

- Pre-flight test suite execution: 239 tests passed in 101.31s.
- Reproducibility check: 9 reproducibility checks passed.
- Claim linter: 143 files scanned, 0 violations.
- Forensic admission audit: 10 raw sources verified, 30 manifest operations reconciled.
- Dialect audit: 928 dialect occurrences verified.
- Git working tree: Clean.
