# Stage B Canonical Extraction Generalization Report — Multi-Slot Cohort Expansion

## Executive Summary
This report formalizes the successful bounded generalization pilot of the Stage B deterministic canonical extraction engine. The engine was expanded from the initial single-slot pilot (`SLOT_GITHUB_01`: `pulls/create`) to admit and extract complex form-encoded operations (`SLOT_STRIPE_02`: `PostShippingRates`), strictly observing the protocol-defined boundaries and state machine.

### Operations Cohort Summary

| Slot ID | Operation ID | HTTP Route | Candidate Source ID | Content-Type | Depth | Evaluated Keywords | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `SLOT_GITHUB_01` | `pulls/create` | `POST /repos/{owner}/{repo}/pulls` | `CAND-001` | `application/json` | 2 | 26 | `CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_STRIPE_02` | `PostShippingRates` | `POST /v1/shipping_rates` | `CAND-002` | `application/x-www-form-urlencoded` | 4 | 50 | `EXTRACTED_PENDING_HUMAN_VALIDATION` |

---

## 1. Key Generalization Invariants Verified

### A. Dynamic Manifest Metadata Selection
- Extraction is no longer driven by hard-coded pilot constants.
- Source specification pointers, target endpoints, raw file SHA-256 hashes, Git blob SHAs, complexity tiers, and candidate metadata are dynamically resolved from the frozen admission ledger `results_stage_b/candidate_admission_decisions.json`.
- Strict boundary guards raise hard errors (`ValueError("Hard boundary violation...")`) for any attempt to extract non-admitted operations or unselected slots.

### B. Form-Encoding Serialization Preservation (`application/x-www-form-urlencoded`)
- **Encoding Style & Explode**: Stripe endpoints utilize RFC-compliant `deepObject` encoding with `explode: true` for structured parameter hierarchies.
- The canonical representation avoids lossy string flattening, preserving clean Draft-07 objects and embedding explicit `x-openapi-encoding` metadata within the canonical body container:
  - `delivery_estimate`: `{style: deepObject, explode: true}`
  - `expand`: `{style: deepObject, explode: true}`
  - `fixed_amount`: `{style: deepObject, explode: true}`
  - `metadata`: `{style: deepObject, explode: true}`
- Complete serialization strategy metadata is recorded in `x-benchmark-metadata.serialization_metadata`.

### C. Structural Complexity & Recursion Depth
- **Depth Bound Compliance**: `SLOT_STRIPE_02` demonstrates recursion depth 4 (e.g. `body -> delivery_estimate -> maximum -> unit/value`), comfortably within the benchmark invariant $d \le 5$.
- **Nested Object Structures**: Fully verified across multi-level nested dictionaries (`delivery_estimate.maximum`, `delivery_estimate.minimum`, `fixed_amount.currency_options`).
- **Array Items & Constraints**: Array parameter `expand` preserves item schema (`type: string`, `maxLength: 5000`).
- **Dictionary/Map Schemas**: Preserves `additionalProperties: {type: string}` for `metadata` and object schemas for `currency_options.additionalProperties`.

---

## 2. Multi-Dimensional Semantic Preservation Audit

### Dimension 1: Exact Keyword Equivalence
- **Total Evaluated Keywords**: 50 keyword instances across all 8 body parameters and sub-properties.
- **Equivalent**: 50 / 50 (100%).
- **Dropped**: 0.
- **Mismatched**: 0.
- Zero loss of constraints, formats, enums, descriptions, defaults, or requiredness.

### Dimension 2: Transport Wrapper Synthesis
- Surface container normalization unifies inputs across four discrete containers:
  - `path`: 0 properties (cleanly empty, required: `[]`)
  - `query`: 0 properties (cleanly empty)
  - `header`: 0 properties (cleanly empty)
  - `body`: 8 properties (required: `['display_name']`)
- Tool description is selected deterministically per the precedence hierarchy (`summary -> description -> fallback`).

### Dimension 3: Closed Wrapper Policy Effects (`WRAPPER_CLOSED_OBJECT_POLICY_001`)
- **Root & Surface Envelopes**: Enforced as closed objects (`additionalProperties: false`) to eliminate model parameter hallucination.
- **Raw Body Nuance**:
  - For `SLOT_GITHUB_01`: Raw OpenAPI omitted `additionalProperties` (open by default). Closing was a benchmark tightening policy (`TIGHTENED_FROM_OPEN`).
  - For `SLOT_STRIPE_02`: Raw OpenAPI explicitly declared `"additionalProperties": false`. Canonical body schema is bitwise identical to raw (`PRESERVED_EXPLICIT_FALSE`).

### Dimension 4: Form-Encoding Serialization Preservation
- Verified bijective match between raw OpenAPI `encoding` definitions and canonical `properties.body.x-openapi-encoding` metadata.
- All 4 deepObject parameters verified for `style == "deepObject"` and `explode is True`.

### Dimension 5: Unsupported Constructs Audit
- **Count**: 0 unsupported constructs.
- No polymorphic unions (`anyOf` / `oneOf` object unions).
- No unresolvable `$ref` cycles.
- No binary or multipart/form-data schemas.

---

## 3. Provenance & Cryptographic Continuity

| Artifact Pointer | Git Blob / File SHA-256 | Records / Status |
| :--- | :--- | :--- |
| `raw_source_file_path` | `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776` | `CAND-002` |
| `raw_source_git_blob_sha` | `f1cedf38e0178538a3c72e750da80226df41e28c` | Git Blob |
| `canonical_contract.json` | `c7e2a3a33078a892b1dc85e4922119eb8bb08499252062f6b86b460dd80e22ea` | Draft-07 Tool Contract |
| `field_lineage.jsonl` | `57f00d2aa66b59368d40081d6d37013876e6a18d1844520979a4beeb4c28c8d8` | 27 Lineage Records |
| `extraction_manifest.json` | Manifest Metadata | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `canonical_field_lineage.jsonl` | Global Lineage Index | 42 Records (15 GitHub + 27 Stripe) |

---

## 4. Lifecycle Boundaries & Next Steps
- `SLOT_STRIPE_02` is currently held strictly at `EXTRACTED_PENDING_HUMAN_VALIDATION`.
- Neither independent validation nor author sign-off is claimed for `SLOT_STRIPE_02` until the generation and review of a formal Human Validation Packet.
- Status is strictly forbidden from advancing to `CANONICAL_FAITHFUL`.
