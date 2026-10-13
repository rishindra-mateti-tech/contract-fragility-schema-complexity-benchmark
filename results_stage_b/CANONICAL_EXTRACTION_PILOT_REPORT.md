# Stage B Canonical Extraction Pilot Report: SLOT_GITHUB_01 (pulls/create)

## 1. Executive Summary & Semantic Decision

This report documents the refined extraction and validation of the **Stage B Canonical Contract Extraction Pilot** for:
- **Slot Identifier:** `SLOT_GITHUB_01`
- **Operation Identifier:** `pulls/create` (`POST /repos/{owner}/{repo}/pulls`)
- **Raw Candidate Source:** `CAND-001` (GitHub REST API OpenAPI 3.0 description)
- **Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md` (Extraction Rule Version `1.2.0`)
- **Evaluated Semantic Decision:** **`SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW`**
- **Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION` (strictly **not** elevated to `CANONICAL_FAITHFUL`)
- **Lossless Classification:** **`SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY`**

### Research Integrity Invariants Preserved
1. **Single-Operation Boundary:** Strictly extracted and audited only `SLOT_GITHUB_01`. No additional operations were admitted or converted.
2. **Zero Downstream Mutation / Execution Artifacts:** No mutations, mock executors, model calls, benchmark results, or empirical claims were generated.
3. **No Unqualified "Lossless" Claims:** The extraction is **not** claimed to be unconditionally lossless. While 100% of defined schema keywords and fields are preserved identically, the canonical contract enforces an explicit, non-lossless benchmark wrapper policy (`additionalProperties: false` across surface containers) to restrict tool-argument permissiveness for LLM evaluation.
4. **Elimination of Static Assumptions:** Fixed property-copy whitelists and fabricated line number maps were completely removed in favor of recursive schema extraction and programmatic lineage derivation.

---

## 2. Pinned Provenance & Source Anchors

| Provenance Property | Value / Cryptographic Reference |
|---|---|
| **Candidate Source ID** | `CAND-001` |
| **Source Cluster ID** | `CLUSTER_GITHUB` |
| **Domain** | Developer Platforms |
| **Pinned Raw Source File** | `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json` |
| **Raw Source Git Blob SHA** | `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d` |
| **Raw Source File SHA-256** | `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194` |
| **Raw JSON Pointer** | `#/paths/~1repos~1{owner}~1{repo}~1pulls/post` |
| **HTTP Method & Path** | `POST /repos/{owner}/{repo}/pulls` |
| **Request Content-Type** | `application/json` |

---

## 3. Extracted Canonical Artifact Inventory

The extraction engine (`src/extract_stage_b_canonical_contract.py`) and multi-suite validator (`src/validate_stage_b_canonical_contract.py`) emitted the following deterministic artifacts under `data_stage_b/canonical/SLOT_GITHUB_01/`:

| Artifact File | Format | SHA-256 Checksum | Description |
|---|---|---|---|
| `canonical_contract.json` | JSON (Draft-07) | `54f78758f76fcd3a55f2d629f3eb66c7150567a9d4aea759577cafdace8ed1c1` | Canonical Draft-07 tool schema with single-column surface containers |
| `field_lineage.jsonl` | JSON Lines | `294066ce9cf0589645b2fed5fbe229c01c91f7e0042baf9bff801c50003c7da1` | 15 deterministic property lineage records (10 leaf + 4 surface + 1 description) |
| `extraction_manifest.json` | JSON | `ba888725b40e9d328f6cd662123bc6b33a7b1708a1e0ff7909ff0e45989549ef` | Cryptographic provenance manifest with raw, script, and artifact hashes |
| `validation_report.json` | JSON | `cdc218c4a2a035de58d2105d73a00763a995ff5013be590247b077c642f33279` | Multi-suite validation report (43 / 43 checks PASS) |
| `semantic_preservation_report.json` | JSON | `e11f72543e885bc901ef2587095491703f86c8ee83ca9b2a22883a486f0e32c9` | Recursive keyword-by-keyword semantic equivalence audit |

In addition, `results_stage_b/canonical_field_lineage.jsonl` is synchronized with the slot's lineage records.

---

## 4. Semantic Preservation & Keyword Equivalence Audit

The enhanced recursive preservation engine audited the operation across four structured dimensions:

### 4.1 Field Coverage Audit (10 / 10 = 100%)
- **Path Parameters (2):** `owner`, `repo`
- **Body Properties (8):** `base`, `body`, `draft`, `head`, `head_repo`, `issue`, `maintainer_can_modify`, `title`
- **Missing Raw Fields:** 0
- **Extraneous / Hallucinated Fields:** 0
- **Field Coverage Ratio:** `1.0` (100.0%)

### 4.2 Keyword Equivalence Audit (26 / 26 Keyword Instances Equivalent)
Every supported schema keyword present in the raw specification was recursively compared against its canonical counterpart:
- **`type` (10 instances):** All match identically (e.g. `string`, `boolean`, `integer`).
- **`description` (10 instances):** All match raw documentation strings verbatim.
- **`format` (2 instances):** `head_repo.format == "repo.nwo"`, `issue.format == "int64"` preserved identically.
- **`example` (2 instances):** `head_repo.example == "octo-org/octo-repo"`, `issue.example == 1` preserved identically.
- **`required` (2 instances):**
  - Path container required: `["owner", "repo"]` (matches path parameter list).
  - Body container required: `["base", "head"]` (matches raw `requestBody.schema.required`).
- **Dropped Keywords:** 0
- **Mismatched Keywords:** 0

### 4.3 Explicitly Approved Transformations & Non-Lossless Wrapper Policies

| Transformation ID | Category | Canonical Pointer | Rationale & Semantic Impact | Strictly Lossless? |
|---|---|---|---|---|
| `TRANSFORM_ROOT_WRAPPER_SYNTHESIS` | `BENCHMARK_WRAPPER_NORMALIZATION` | `/` | HTTP operations accept parameters across URI path templates, query parameters, headers, and request bodies. The canonical representation wraps these disjoint surfaces into a single Draft-07 object with four discrete transport containers (`path`, `query`, `header`, `body`). | **No** (structural wrapper synthesis) |
| `TRANSFORM_WRAPPER_CLOSED_OBJECT` | `BENCHMARK_WRAPPER_NORMALIZATION` | `/additionalProperties`, `/properties/*/additionalProperties` | Tool-calling parameter interfaces require closed object schemas (`additionalProperties: false`) to constrain LLM argument hallucination and enforce strict validation. Raw OpenAPI specification omitted `additionalProperties` (which in JSON Schema defaults to permissive/open validation). This normalization tightens schema permissiveness. | **No** (tightens permissiveness from open to closed) |
| `TRANSFORM_TOOL_DESCRIPTION_SELECTION` | `DETERMINISTIC_METADATA_MAPPING` | `/description` | Selected raw operation `summary` ("Create a pull request") per deterministic precedence hierarchy (Step 1: summary, Step 2: description, Step 3: template fallback). | **Yes** (verbatim raw text preservation) |

### 4.4 Unsupported Constructs Audit
- **Unsupported Keywords Encountered:** 0
- **Cyclic References:** 0
- **Object-Level Polymorphic Unions (`anyOf`/`oneOf`):** 0
- **Recursion Depth:** Observed depth = 2 (strictly $\le 5$)
- **File / Multipart Uploads:** 0

---

## 5. Lineage Derivation & Line Span Justification

Static, hand-coded line maps (e.g. `body_line_map = {"title": 70827, ...}`) have been entirely removed.
- **Programmatic Derivation:** Lineage records and source pointers are derived programmatically via RFC 6901 navigation of the parsed OpenAPI AST.
- **Explicit AST Line Span Omission:** Because standard Python JSON decoders parse byte streams into memory structures without preserving token line/column offsets, exact source AST line spans are recorded as `null` with explicit documentation:
  `"source_ast_span": null`
  `"source_ast_span_reason": "Standard JSON parser does not preserve token line offsets; exact AST line spans require full JSON AST parsing with source mapping."`

---

## 6. Deliberate Drift & Negative Regression Verification

Automated regression tests in `tests/test_stage_b_canonical_extraction_pilot.py` demonstrate immediate detection and rejection across 11 distinct drift scenarios:

| Drift Regression Scenario | Expected Validator Action | Test Suite Result |
|---|---|---|
| **Field Renaming** (e.g. `title` $\to$ `pr_title`) | Fails `body_properties_exact` check | PASS |
| **Missing Required Field** (dropping `head`) | Fails `body_required_exact` check | PASS |
| **Phantom / Invented Field** (injecting `phantom_field`) | Fails `body_properties_exact` check | PASS |
| **Transport Separation Leak** (leaking `owner` into `body`) | Fails `transport_separation_no_path_leak_into_body` check | PASS |
| **Recursion Depth Violation** (nesting depth $> 5$) | Fails `recursion_depth_within_bound` check | PASS |
| **Lost String Pattern Drift** (raw defines `pattern`, canonical drops it) | Fails `semantic_keyword_equivalence_verified` (`DROPPED_KEYWORD`) | PASS |
| **Lost Numeric Bound Drift** (raw defines `minimum`, canonical drops it) | Fails `semantic_keyword_equivalence_verified` (`DROPPED_KEYWORD`) | PASS |
| **Lost Array Items Schema Drift** (raw defines `items`, canonical drops it) | Fails `semantic_keyword_equivalence_verified` (`DROPPED_KEYWORD`) | PASS |
| **`additionalProperties` Difference Drift** (raw specifies schema, canonical alters it) | Fails `semantic_keyword_equivalence_verified` (`MISMATCH`) | PASS |
| **Nested Keyword Mismatch Drift** (nested `minLength` altered) | Fails `semantic_keyword_equivalence_verified` (`MISMATCH`) | PASS |
| **Out-of-Scope Slot Boundary** (attempting non-pilot extraction) | Raises explicit hard-boundary `ValueError` | PASS |

---

## 7. Pilot Gate Conclusion

The pilot extraction for `SLOT_GITHUB_01` (`pulls/create`) is classified as:
### **`SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW`**

- **Keyword Equivalence:** 100% verified across all raw keywords.
- **Field Coverage:** 100% verified (10/10).
- **Wrapper Normalization:** Formally audited, documented, and qualified as non-lossless wrapper policy.
- **Next Required Step:** Formal human reviewer sign-off prior to canonical cohort promotion.
- **Boundary Invariant:** The operation remains strictly at `EXTRACTED_PENDING_HUMAN_VALIDATION` and is **not** elevated to `CANONICAL_FAITHFUL`.
