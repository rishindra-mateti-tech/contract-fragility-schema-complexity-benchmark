# Stage B Canonical Extraction Pilot Human Validation Packet: SLOT_GITHUB_01 (pulls/create)

**Document Role:** Designated Human Reviewer Validation Packet for Canonical Tool Extraction  
**Document Status:** `PENDING_HUMAN_VALIDATION` (Sign-off fields strictly unpopulated)  
**Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md`  
**Current Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION` (Strictly **not** elevated to `CANONICAL_FAITHFUL`)  
**Semantic Validation Decision:** `SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW`  
**Lossless Classification:** `SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY`  
**Target Slot:** `SLOT_GITHUB_01`  
**Target Operation:** `pulls/create` (`POST /repos/{owner}/{repo}/pulls`)  

---

## 1. Immutable Cryptographic Provenance

This section records the exact immutable cryptographic references for raw source inputs, extraction tooling, and emitted canonical artifacts:

| Provenance Property | Cryptographic Checksum / Identifier | Location / Source Path |
|---|---|---|
| **Raw Source Candidate ID** | `CAND-001` | `github/rest-api-description` (GitHub Descriptions) |
| **Source Cluster ID** | `CLUSTER_GITHUB` | Developer Platforms Cluster |
| **Raw Source Git Blob SHA** | `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d` | Git Object Store |
| **Raw Source File SHA-256** | `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194` | `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json` |
| **Raw JSON Pointer** | `#/paths/~1repos~1{owner}~1{repo}~1pulls/post` | RFC 6901 Pointer in `CAND-001` |
| **Extractor Script** | `src/extract_stage_b_canonical_contract.py` | Working Tree |
| **Extractor Script SHA-256** | `6031bc42c197c23b4722e3b3ef1975cf004fe058a7fee20adb238e01a5410602` | Extractor Engine Implementation |
| **Extractor Commit SHA** | `c778e63` | `feat(stage_b): add recursive schema preservation engine and negative drift tests` |
| **Canonical Contract SHA-256** | `54f78758f76fcd3a55f2d629f3eb66c7150567a9d4aea759577cafdace8ed1c1` | `data_stage_b/canonical/SLOT_GITHUB_01/canonical_contract.json` |
| **Field Lineage SHA-256** | `294066ce9cf0589645b2fed5fbe229c01c91f7e0042baf9bff801c50003c7da1` | `data_stage_b/canonical/SLOT_GITHUB_01/field_lineage.jsonl` |
| **Extraction Manifest SHA-256** | `ba888725b40e9d328f6cd662123bc6b33a7b1708a1e0ff7909ff0e45989549ef` | `data_stage_b/canonical/SLOT_GITHUB_01/extraction_manifest.json` |
| **Validation Report SHA-256** | `cdc218c4a2a035de58d2105d73a00763a995ff5013be590247b077c642f33279` | `data_stage_b/canonical/SLOT_GITHUB_01/validation_report.json` |
| **Semantic Report SHA-256** | `e11f72543e885bc901ef2587095491703f86c8ee83ca9b2a22883a486f0e32c9` | `data_stage_b/canonical/SLOT_GITHUB_01/semantic_preservation_report.json` |

---

## 2. Semantic Comparison & Keyword Equivalence

### 2.1 Complete 10-Field Bijective Mapping

Every raw field declared in the upstream specification maps bijectively into its corresponding canonical container location:

| Field Name | Transport Surface | Canonical JSON Pointer | Raw Source AST Pointer / Component | Declared Type | Required in Canonical? |
|---|---|---|---|---|---|
| `owner` | Path Parameter | `/properties/path/properties/owner` | `.../parameters/0` ($ref `#/components/parameters/owner`) | `string` | **Yes** (`path.required`) |
| `repo` | Path Parameter | `/properties/path/properties/repo` | `.../parameters/1` ($ref `#/components/parameters/repo`) | `string` | **Yes** (`path.required`) |
| `base` | Request Body | `/properties/body/properties/base` | `.../requestBody/content/application~1json/schema/properties/base` | `string` | **Yes** (`body.required`) |
| `body` | Request Body | `/properties/body/properties/body` | `.../requestBody/content/application~1json/schema/properties/body` | `string` | No |
| `draft` | Request Body | `/properties/body/properties/draft` | `.../requestBody/content/application~1json/schema/properties/draft` | `boolean` | No |
| `head` | Request Body | `/properties/body/properties/head` | `.../requestBody/content/application~1json/schema/properties/head` | `string` | **Yes** (`body.required`) |
| `head_repo` | Request Body | `/properties/body/properties/head_repo` | `.../requestBody/content/application~1json/schema/properties/head_repo` | `string` | No |
| `issue` | Request Body | `/properties/body/properties/issue` | `.../requestBody/content/application~1json/schema/properties/issue` | `integer` | No |
| `maintainer_can_modify` | Request Body | `/properties/body/properties/maintainer_can_modify` | `.../requestBody/content/application~1json/schema/properties/maintainer_can_modify` | `boolean` | No |
| `title` | Request Body | `/properties/body/properties/title` | `.../requestBody/content/application~1json/schema/properties/title` | `string` | No |

### 2.2 Complete 26-Keyword Equivalence Verification

The recursive preservation engine verified 26 distinct keyword instances across all 10 fields and 2 surface required arrays:

| Keyword | Instance Count | Canonical Pointers Evaluated | Equivalence Finding |
|---|---|---|---|
| `type` | 10 | `/properties/path/properties/{owner,repo}/type`, `/properties/body/properties/{base,body,draft,head,head_repo,issue,maintainer_can_modify,title}/type` | **100% IDENTICAL** (All primitive types match verbatim) |
| `description` | 10 | `/properties/path/properties/{owner,repo}/description`, `/properties/body/properties/{base,body,draft,head,head_repo,issue,maintainer_can_modify,title}/description` | **100% IDENTICAL** (Documentation text preserved verbatim) |
| `format` | 2 | `/properties/body/properties/head_repo/format` (`repo.nwo`), `/properties/body/properties/issue/format` (`int64`) | **100% IDENTICAL** (Specialized string & integer formats preserved) |
| `example` | 2 | `/properties/body/properties/head_repo/example` (`octo-org/octo-repo`), `/properties/body/properties/issue/example` (`1`) | **100% IDENTICAL** (Upstream examples preserved verbatim) |
| `required` | 2 | `/properties/path/required` (`["owner", "repo"]`), `/properties/body/required` (`["base", "head"]`) | **100% IDENTICAL** (Required fields match upstream declarations) |

- **Total Keywords Evaluated:** 26
- **Equivalent Keywords:** 26 / 26 (100.0%)
- **Dropped Keywords:** 0
- **Mismatched Keywords:** 0

### 2.3 Required-Field Comparison

- **Path Surface Requiredness:** Upstream path parameters `{owner}` and `{repo}` are mandatory in HTTP URI templates. Both appear in canonical `path.required = ["owner", "repo"]`.
- **Body Surface Requiredness:** Upstream OpenAPI `requestBody.schema.required` specifies `["head", "base"]`. Sorted canonical required array is `body.required = ["base", "head"]`.
- **Top-Level Requiredness:** Root required array lists `["body", "path"]` (the two surfaces containing mandatory inputs). Absent surfaces (`query`, `header`) are not listed.

### 2.4 Transport-Surface Isolation & Zero-Leak Verification

- **Path Surface (`properties.path`):** Strictly contains `owner` and `repo`.
- **Body Surface (`properties.body`):** Strictly contains 8 request body properties. Path parameters `owner` and `repo` do **not** leak into `properties.body`.
- **Query Surface (`properties.query`):** Empty object with `additionalProperties: false` (zero query parameters in raw operation).
- **Header Surface (`properties.header`):** Empty object with `additionalProperties: false` (zero task headers in raw operation).

### 2.5 Zero-Loss Verification Categories

- **Dropped Properties:** 0 (0 out of 10 fields dropped)
- **Invented / Phantom Fields:** 0 (0 unmapped fields added)
- **Type Coercions:** 0 (Zero type alterations)
- **Constraint / Bound Omissions:** 0 (All declared formats, examples, and required markers preserved)
- **Polymorphic Pruning:** 0 (No variants dropped; schema contains zero `oneOf`/`anyOf` object unions)
- **Recursion Truncation:** 0 (Observed depth = 2, strictly $\le 5$)

---

## 3. Explicit Transformation Review & Wrapper Policy Disclosure

The human reviewer must explicitly inspect and evaluate the three intentional structural transformations applied during canonical extraction:

### 3.1 Root Wrapper Synthesis (`TRANSFORM_ROOT_WRAPPER_SYNTHESIS`)
- **Category:** `BENCHMARK_WRAPPER_NORMALIZATION`
- **Canonical Pointer:** `/` (properties: `path`, `query`, `header`, `body`)
- **Rationale:** OpenAPI HTTP operations accept parameters across disparate transport surfaces (URI path templates, query strings, headers, and HTTP request bodies). Large Language Model tool-calling protocols execute over a single unified JSON arguments object. The canonical representation synthesizes a single root Draft-07 object enclosing four discrete transport containers.
- **Semantic Classification:** **Non-lossless structural envelope synthesis** (not raw-source equivalence).

### 3.2 Transport Surface Wrappers
- **Category:** `BENCHMARK_WRAPPER_NORMALIZATION`
- **Canonical Pointers:** `/properties/path`, `/properties/query`, `/properties/header`, `/properties/body`
- **Rationale:** Preserves explicit separation between URL routing parameters and JSON payload bodies, preventing argument collision while maintaining single-turn constructibility.

### 3.3 Closed-Object Wrapper Policy (`WRAPPER_CLOSED_OBJECT_POLICY_001`)

> ### **CRITICAL DISCLOSURE FOR HUMAN REVIEWER**
> **Closing `additionalProperties` is a deliberate, benchmark-required non-lossless normalization policy (`WRAPPER_CLOSED_OBJECT_POLICY_001`), NOT raw-source equivalence.**
>
> - **Raw OpenAPI Behavior:** The raw GitHub specification omitted `additionalProperties` at the `requestBody.schema` level. Under standard JSON Schema / OpenAPI 3.0 semantics, omitting `additionalProperties` defaults to **open/permissive** validation (payloads with unrecognized extra keys are accepted).
> - **Canonical Benchmark Normalization:** The canonical contract explicitly sets `"additionalProperties": false` across the root envelope and all transport surface containers (`path`, `query`, `header`, `body`).
> - **Formal Rationale:** Closed schemas are essential in tool-calling benchmarks to evaluate whether models hallucinate extraneous arguments and to enforce deterministic evaluation.
> - **Semantic Impact:** This normalization intentionally tightens schema permissiveness from open to closed. As a consequence, the canonical extraction is categorized as **`SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY`** and **must not be described as unconditionally lossless**.

---

## 4. Designated Human Reviewer Decision Options

The human reviewer must select exactly one of the following formal review decisions:

1. **`APPROVE_WRAPPER_POLICY`**:
   The reviewer verifies that all 10 fields and 26 keywords match upstream declarations with 100% equivalence, confirms that the closed-object policy (`additionalProperties: false`) is an acceptable benchmark normalization, and approves advancing the operation toward canonical cohort ratification.
2. **`REQUEST_CHANGES`**:
   The reviewer requires modifications to extractor logic, descriptions, metadata, or documentation before the extraction can be approved.
3. **`REJECT_EXTRACTION`**:
   The reviewer rejects the canonical extraction of `SLOT_GITHUB_01`, requiring disqualification or a formal protocol amendment.

---

## 5. Human Reviewer Checklist

The human reviewer must verify each of the following points prior to recording a sign-off decision:

- [ ] **Provenance Verification:** Raw file SHA-256 (`ba5ddc1eeeede9f3...`) and Git blob SHA (`a91fa76a34558f5e...`) match `raw_sources_provenance_registry.json`.
- [ ] **Exact Pointer Resolution:** JSON Pointer `#/paths/~1repos~1{owner}~1{repo}~1pulls/post` resolves unambiguously in `CAND-001`.
- [ ] **Field Coverage Verification:** All 10 fields (2 path + 8 body) are accounted for with zero missing and zero phantom fields.
- [ ] **Keyword Equivalence Verification:** All 26 keyword instances match upstream declarations verbatim (zero dropped, zero mismatched).
- [ ] **Transport Separation Verified:** Path parameters `owner` and `repo` do not leak into `body`.
- [ ] **No Unqualified "Lossless" Claims:** Confirmed that the extraction report and artifacts do not claim unconditional losslessness.
- [ ] **Closed-Object Wrapper Policy Evaluated:** Evaluated `WRAPPER_CLOSED_OBJECT_POLICY_001` and confirmed its non-lossless tightening rationale.
- [ ] **Status Invariant Verified:** Operation remains at `EXTRACTED_PENDING_HUMAN_VALIDATION` and is **not** labeled `CANONICAL_FAITHFUL`.

---

## 6. Human Reviewer Sign-Off Block (UNPOPULATED)

*Note: All fields below are strictly unpopulated pending designated human reviewer execution. Automated tools are forbidden from signing this block.*

| Sign-Off Field | Field Value (To Be Completed by Human Reviewer) |
|---|---|
| **Reviewer Name** | `[UNPOPULATED - PENDING HUMAN REVIEW]` |
| **Reviewer Role** | `[UNPOPULATED - AUTHOR_MANUAL_REVIEW or INDEPENDENT_REVIEW]` |
| **Review Date (UTC)** | `[UNPOPULATED - YYYY-MM-DD]` |
| **Reviewed Packet Git Commit** | `[UNPOPULATED - Commit SHA of reviewed packet]` |
| **Reviewed Packet Git Blob SHA** | `[UNPOPULATED - Git blob SHA of reviewed packet]` |
| **Reviewed Packet SHA-256** | `[UNPOPULATED - File SHA-256 of reviewed packet snapshot]` |
| **Reviewed Canonical Contract SHA-256** | `54f78758f76fcd3a55f2d629f3eb66c7150567a9d4aea759577cafdace8ed1c1` |
| **Reviewed Semantic Report SHA-256** | `e11f72543e885bc901ef2587095491703f86c8ee83ca9b2a22883a486f0e32c9` |
| **Human Review Decision** | `[UNPOPULATED - APPROVE_WRAPPER_POLICY / REQUEST_CHANGES / REJECT_EXTRACTION]` |
| **Wrapper Policy Acceptance Note** | `[UNPOPULATED - Explicit note stating whether reviewer accepts closed-object wrapper policy]` |
