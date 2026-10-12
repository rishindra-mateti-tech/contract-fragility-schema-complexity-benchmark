# Stage B Extraction Implementation Checklist & Operational Blueprint

**Document Role:** Step-by-Step Implementation and Verification Checklist for the Stage B Extractor  
**Date (UTC):** October 12, 2026  
**Status:** READY_FOR_IMPLEMENTATION_APPROVAL  
**Governing Phase:** Phase 4 Extraction Verification Blueprint  
**Reference Specification:** [STAGE_B_EXTRACTION_SPEC.md](file:///c:/Users/rishi/OneDrive/Desktop/Education/contract-fragility-schema-complexity-benchmark/STAGE_B_EXTRACTION_SPEC.md)

---

## 1. System Overview & Pre-Flight Invariants

This checklist operationalizes the extraction rules defined in `STAGE_B_EXTRACTION_SPEC.md` and `PROTOCOL_AMENDMENT_003.md`. It provides the definitive implementation contract for building the extraction engine (`src/extract_stage_b_canonical_contracts.py`), verifying its output, logging deterministic lineage, and enforcing fail-safe execution.

### Non-Negotiable Operational Invariants
- **Read-Only Raw Sources:** No extraction code may write to, touch, or alter files in `data_stage_b/raw/**`.
- **Zero Lossy Guesswork:** No extraction heuristic may prune, truncate, or inject synthetic fallback objects (`{}`) into canonical schemas.
- **Strict Depth Ceiling:** Traversal depth exceeding `MAX_RECURSION_DEPTH = 5` is an automatic exclusion.
- **Stage A Absolute Quarantine:** Stage A artifacts (`data/`, `src/mutations.py`, `src/runner.py`, `tests/test_audit.py`, `tests/test_mutations.py`) remain completely untouched.
- **Provisional Status:** All extracted contracts are emitted as candidate artifacts; none become `CANONICAL_FAITHFUL` without passing all 4 verification gates.

---

## 2. Directory Layout & File Paths

| Role | Path | Mode | Encoding / Format |
| :--- | :--- | :---: | :--- |
| **Raw OpenAPI Specs** | `data_stage_b/raw/openapi/**` | READ-ONLY | Binary / UTF-8 |
| **Raw MCP Source Code** | `data_stage_b/raw/mcp/**` | READ-ONLY | Binary / UTF-8 |
| **Operation Manifest** | `results_stage_b/stage_b_operation_manifest.yaml` | READ-ONLY | UTF-8 YAML |
| **Candidate Audit Report** | `results_stage_b/pre_extraction_candidate_audit.json` | READ-ONLY | UTF-8 JSON |
| **Target Canonical Schemas** | `data_stage_b/canonical/{source_cluster_id}/{safe_op_id}.json` | WRITE | UTF-8 JSON (no BOM) |
| **Field-Lineage Ledger** | `results_stage_b/canonical_field_lineage.jsonl` | WRITE | UTF-8 JSONL |
| **Extraction Failure Report** | `results_stage_b/extraction_failure_report.json` | WRITE | UTF-8 JSON (no BOM) |
| **Extraction Verification Log** | `results_stage_b/canonical_extraction_verification.md` | WRITE | UTF-8 Markdown |

---

## 3. Pre-Flight Cryptographic Verification Checklist

Before processing any operation, the extraction runner must execute pre-flight cryptographic verification:

- [ ] **Task 3.1: Manifest Integrity Verification**
  - Compute SHA-256 of `results_stage_b/stage_b_operation_manifest.yaml`.
  - Assert that manifest contains exactly the expected candidate operations and cluster IDs.
- [ ] **Task 3.2: Raw Source File Hash Assertions**
  - For each raw source file referenced in the manifest, compute SHA-256 and Git blob SHA of the file on disk.
  - Assert exact match against the pinned values in `stage_b_operation_manifest.yaml`.
  - Abort immediately with exit code 1 if any raw file hash mismatches.
- [ ] **Task 3.3: Output Directory Cleanliness & Isolation**
  - Verify target directory `data_stage_b/canonical/` exists or create it cleanly.
  - Ensure no residual non-canonical files or partial extraction debris exist from previous runs.

---

## 4. Extraction Engine Step-by-Step Implementation Checklist

### Phase A: Parsing & Operation Locating
- [ ] **Task 4.1: Source Parser Initialization**
  - For OpenAPI files: Parse raw YAML/JSON using safe, byte-preserving loader (`yaml.CSafeLoader` or `yaml.SafeLoader` with strict duplicate-key detection).
  - For Python MCP (`server.py`): Parse module AST using Python `ast.parse()`.
  - For TypeScript MCP (`index.ts`): Parse file AST using TypeScript compiler API or verified Python-side TypeScript AST extractor.
- [ ] **Task 4.2: RFC 6901 Pointer Navigation**
  - Resolve exact operation node via `source_spec_pointer` from manifest (e.g. `#/paths/~1repos~1{owner}~1{repo}~1issues/post`).
  - Extract path-level parameters (`#/paths/~1<escaped_path>/parameters`) if present.
  - Merge path-level parameters with operation-level parameters; operation-level parameters override path-level parameters with identical `(name, in)` identity.

### Phase B: Parameter & Surface Partitioning
- [ ] **Task 4.3: Parameter Surface Separation**
  - Partition parameters into four distinct lists: `path_params`, `query_params`, `header_params`, `body_params`.
  - Discard path parameters not matching path template placeholders with warning if mismatched.
  - Track `in: header` parameters:
    - If parameter is an execution-environment credential (e.g., `token`, `Authorization`, `x-api-key`), record it in `authentication_fields` metadata and exclude from model-facing schema per Section 2.5 of extraction spec.
    - If parameter is genuine business input, place into `header` surface.
- [ ] **Task 4.4: Request Body Processing**
  - Inspect `requestBody/content`.
  - Verify content type:
    - `application/json`: Extract schema node under `application/json/schema`.
    - `application/x-www-form-urlencoded`: Extract schema node and set metadata `"x-content-type": "application/x-www-form-urlencoded"`.
    - `multipart/form-data` or binary uploads: **ABORT**; classify operation as `EXCLUDE_PENDING`.
  - Preserve `requestBody.required` boolean indicator.

### Phase C: Reference Resolution & Cycle/Depth Defense
- [ ] **Task 4.5: Reference Resolution Engine (`$ref`)**
  - Maintain call-scoped `visited_refs: Set[str]` stack to track reference traversal path.
  - Enforce intra-document reference constraint: assert `$ref` starts with `#`. If external URI, **ABORT** as `EXCLUDE_PENDING`.
  - **Cycle Check:** If `$ref` already in `visited_refs`, detect cycle, **ABORT** operation, and classify as `EXCLUDE_PENDING`.
  - **Depth Check:** Track current nesting depth $d$. If $d > 5$, **ABORT** operation and classify as `EXCLUDE_PENDING`.
  - Push `$ref` to `visited_refs`, resolve target component via RFC 6901 pointer, recurse, and pop on return.
- [ ] **Task 4.6: Compositional Operators Handling**
  - **`allOf` Merging:**
    - Recursively dereference all sub-schemas in `allOf`.
    - Union `properties` dictionaries.
    - Union `required` lists.
    - Check for property conflicts: If same property name defined with incompatible `type` or constraints, **ABORT** as `EXCLUDE_PENDING` with conflict reason logged.
  - **`oneOf` / `anyOf` Handling:**
    - For monomorphic candidates: Assert variants are strictly primitive types (e.g. `string` or `integer`). If object-level union encountered, **ABORT** as `EXCLUDE_PENDING`.
    - For faithful-union candidates (`PostRefunds` under Amendment 003): Preserve finite object/string variant schemas verbatim. Assert each variant is compliant with `UNION_VALIDATION_TEST_PLAN.md`.

### Phase D: Uniform HTTP Surface Wrapper Construction
- [ ] **Task 4.7: Transport Wrapper Packaging (OpenAPI Operations)**
  - Construct root object with `$schema: "http://json-schema.org/draft-07/schema#"`.
  - Set `title: <CanonicalToolIdentifier>`.
  - Set `description: <DeterministicOperationDescription>` following strict 3-step fallback:
    1. Raw `summary` (if non-empty)
    2. Raw `description` (if non-empty)
    3. Template `<HTTP_METHOD> <PATH> (<operationId>)`
  - Populate `properties` with four mandatory surface objects:
    - `"path"`: `{"type": "object", "properties": {...}, "required": [...], "additionalProperties": false}`
    - `"query"`: `{"type": "object", "properties": {...}, "required": [...], "additionalProperties": false}`
    - `"header"`: `{"type": "object", "properties": {...}, "required": [...], "additionalProperties": false}`
    - `"body"`: `{"type": "object", "properties": {...}, "required": [...], "additionalProperties": false}`
  - Determine top-level `required` array:
    - Add `"path"` if `path` has at least one required parameter.
    - Add `"query"` if `query` has at least one required parameter.
    - Add `"header"` if `header` has at least one required parameter.
    - Add `"body"` if request body is marked `required: true` or contains required properties.
  - Set root `additionalProperties: false`.
- [ ] **Task 4.8: Transport Wrapper Packaging (MCP Tools)**
  - Construct root object with `$schema: "http://json-schema.org/draft-07/schema#"`.
  - Set `title: <ToolName>`.
  - Set `description: <ToolDescription>` from AST string literal.
  - Populate `properties` with single container:
    - `"arguments"`: `{"type": "object", "properties": {...}, "required": [...], "additionalProperties": false}`
  - Set root `required: ["arguments"]`.
  - Set root `additionalProperties: false`.

### Phase E: Metadata & Structural Metrics Generation
- [ ] **Task 4.9: Metadata Population (`x-benchmark-metadata`)**
  - Attach comprehensive provenance metadata block:
    - `candidate_source_id`: Source identifier (e.g. `CAND-001`).
    - `source_cluster_id`: Cluster identifier (e.g. `CLUSTER_GITHUB`).
    - `source_file_blob_sha`: Pinned Git blob SHA of source file.
    - `operation_id`: Unique operation identifier.
    - `source_spec_pointer`: RFC 6901 pointer to raw operation.
    - `extraction_timestamp`: UTC ISO-8601 timestamp.
    - `extractor_version`: SemVer string (e.g. `1.1.0`).
    - `admission_decision`: `PROVISIONAL_CANONICAL_CANDIDATE` (or faithful union equivalent).
    - `source_structural_metrics`: `{raw_parameter_count, raw_nesting_depth, raw_optional_ratio, raw_enum_density}`.
    - `wrapped_contract_structural_metrics`: `{total_property_count, wrapped_nesting_depth, surface_containers_present, surface_containers_required}`.
    - `authentication_fields`: List of environment credentials extracted.

### Phase F: Deterministic Serialization & File Emission
- [ ] **Task 4.10: Code-Point Sorting & Deterministic Formatting**
  - Recursively sort all object keys in Unicode code-point ascending order (`sort_keys=True`).
  - Sort all elements within every `required` array in Unicode code-point ascending order.
  - Sort all elements within `enum` arrays in code-point order if string enums.
  - Serialize to JSON string with:
    - `indent=2`
    - `ensure_ascii=False` (preserve raw UTF-8 characters without `\uXXXX` escaping)
    - Trailing newline (`\n`)
    - Zero trailing commas
  - Write output to `data_stage_b/canonical/{source_cluster_id}/{safe_op_id}.json`.

---

## 5. Field-Lineage Ledger Emission Checklist

For every property generated in every canonical schema, emit a JSON record to `results_stage_b/canonical_field_lineage.jsonl`:

- [ ] **Task 5.1: Lineage Entry Creation**
  - Record `canonical_schema_sha256`: SHA-256 of the emitted canonical contract.
  - Record `canonical_json_pointer`: Exact RFC 6901 pointer within canonical contract (e.g. `/properties/body/properties/title`).
  - Record `candidate_source_id`, `source_cluster_id`, and `raw_source_blob_sha`.
  - Record `raw_source_pointers`: Array of raw pointers contributing to this field.
  - Record `transformation_category`: Exactly one of:
    `IDENTITY`, `SURFACE_WRAPPING`, `REF_EXPANSION`, `ALLOF_MERGE`, `NULLABLE_STANDARDIZATION`, `AST_TYPE_MAPPING`, `RAW_SUMMARY`, `RAW_DESCRIPTION`, `DETERMINISTIC_TEMPLATE_FALLBACK`.
  - Record `is_reversible`: Boolean indicator.
  - Record `extractor_version` and `extraction_timestamp`.
  - Record `reviewer_decision`: Initially `"PENDING_REVIEW"`.
- [ ] **Task 5.2: Deterministic Lineage Ledger Sorting**
  - Sort JSONL entries primarily by `candidate_source_id`, secondarily by `canonical_json_pointer`.
  - Serialize each JSON object on a single line with sorted keys.

---

## 6. Extraction Failure Reporting Specification

If an operation cannot be extracted faithfully, the extractor must not crash or silently emit a corrupted schema. It must append an entry to `results_stage_b/extraction_failure_report.json`:

```json
{
  "candidate_source_id": "CAND-001",
  "source_cluster_id": "CLUSTER_GITHUB",
  "operation_id": "issues/create",
  "source_spec_pointer": "#/paths/~1repos~1{owner}~1{repo}~1issues/post",
  "failure_timestamp_utc": "2026-10-12T05:00:00Z",
  "disqualification_reason": "RECURSION_DEPTH_EXCEEDED",
  "failing_pointer": "#/paths/~1repos~1{owner}~1{repo}~1issues/post/requestBody/content/application~1json/schema/properties/labels/items",
  "observed_value": 6,
  "threshold_limit": 5,
  "stack_trace_snippet": "RecursionDepthError: Depth 6 exceeds MAX_RECURSION_DEPTH=5 at #/components/schemas/label",
  "suggested_remedy": "Exclude operation from canonical cohort; consider shallow replacement or lossy exploratory branch."
}
```

### Disqualification Reason Taxonomy
- `RECURSION_DEPTH_EXCEEDED`: Depth exceeds 5.
- `CYCLIC_REFERENCE_DETECTED`: Circular `$ref` detected.
- `OBJECT_UNION_DISQUALIFIED`: Wide object-level union in baseline monomorphic cohort.
- `CONFLICTING_ALLOF_SCHEMAS`: Incompatible property definitions in `allOf`.
- `MULTIPART_OR_BINARY_PAYLOAD`: Requires file upload or binary payload.
- `EXTERNAL_REF_FORBIDDEN`: Pointer references external document.
- `PARSING_ERROR`: Malformed YAML/JSON or invalid syntax.

---

## 7. Expected Unit Test Fixtures (`tests/fixtures/`)

To guarantee extractor robustness prior to running against real production specs, the test suite must exercise these synthetic mock fixtures:

| Fixture Name | Path | Purpose & Expected Behavior |
| :--- | :--- | :--- |
| **`mock_clean_operation.yaml`** | `tests/fixtures/mock_clean_operation.yaml` | Perfect 2-surface operation; must extract cleanly to `PROVISIONAL_CANONICAL_CANDIDATE`. |
| **`mock_cyclic_ref.yaml`** | `tests/fixtures/mock_cyclic_ref.yaml` | Circular `$ref` (A -> B -> A); must trigger `CYCLIC_REFERENCE_DETECTED` and exit without infinite loop. |
| **`mock_depth_boundary.yaml`** | `tests/fixtures/mock_depth_boundary.yaml` | Two operations: one at depth 5 (PASS) and one at depth 6 (FAIL with `RECURSION_DEPTH_EXCEEDED`). |
| **`mock_conflicting_allof.yaml`** | `tests/fixtures/mock_conflicting_allof.yaml` | `allOf` with conflicting property types (`string` vs `integer`); must FAIL with `CONFLICTING_ALLOF_SCHEMAS`. |
| **`mock_binary_upload.yaml`** | `tests/fixtures/mock_binary_upload.yaml` | `multipart/form-data` endpoint; must FAIL with `MULTIPART_OR_BINARY_PAYLOAD`. |
| **`mock_auth_headers.yaml`** | `tests/fixtures/mock_auth_headers.yaml` | Operation with `Authorization` and `x-api-key`; must strip from model properties and record in metadata. |
| **`mock_unicode_sorting.yaml`** | `tests/fixtures/mock_unicode_sorting.yaml` | Object with unsorted keys and required fields; output must be strictly sorted by code-point. |

---

## 8. Four-Gate Promotion to `CANONICAL_FAITHFUL`

An operation may **never** be labeled `CANONICAL_FAITHFUL` upon initial extraction. It must systematically clear all four gates:

```
[ Raw Spec & Manifest ]
          │
          ▼
   [ Gate 1: Extraction Engine Pass ] ──► (FAIL: Write Failure Report & Stop)
          │
          ▼
   [ Gate 2: Automated Contract Validator Pass ] ──► (FAIL: Log Validation Errors)
          │
          ▼
   [ Gate 3: Lineage Verification Pass ] ──► (FAIL: Lineage Mismatch Flagged)
          │
          ▼
   [ Gate 4: Manual Review Sign-Off ] ──► (FAIL: Rejection Recorded)
          │
          ▼
  ═════════════════════════════════════
  PROMOTED TO CANONICAL_FAITHFUL
  ═════════════════════════════════════
```

1. **Gate 1: Extraction Engine Pass**  
   - Source parsed, references resolved, surfaces wrapped, metadata computed, file emitted without exceptions.
2. **Gate 2: Automated Contract Validator Pass**  
   - Conforms 100% to JSON Schema Draft-07 via `Draft7Validator.check_schema()` and transport wrapper invariants.
3. **Gate 3: Lineage Verification Pass**  
   - 100% of derived property pointers map to valid raw source locations in `canonical_field_lineage.jsonl`.
4. **Gate 4: Manual Review Sign-Off**  
   - Human reviewer inspects structural diff, validates transport surfaces, and commits signed `APPROVED` record.
