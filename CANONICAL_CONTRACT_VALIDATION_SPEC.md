# Canonical Contract Validation Specification & Lineage Verification Protocol

**Document Role:** Formal Specification for Automated Contract Validation and Field-Lineage Verification  
**Date (UTC):** October 12, 2026  
**Status:** READY_FOR_IMPLEMENTATION_APPROVAL  
**Governing Phase:** Phase 4 Extraction Verification Blueprint  
**Reference Specification:** [STAGE_B_EXTRACTION_SPEC.md](file:///c:/Users/rishi/OneDrive/Desktop/Education/contract-fragility-schema-complexity-benchmark/STAGE_B_EXTRACTION_SPEC.md)

---

## 1. Executive Protocol & Core Invariants

This specification defines the rigorous verification protocols that govern whether an extracted canonical schema is mathematically and structurally valid. No extracted schema may be used in benchmark evaluations, subjected to mutation calculus, or referenced in paper metrics without passing this multi-stage validation engine.

### Operational Principles
1. **Zero Lenience:** Validation is fail-fast and binary. A schema either satisfies 100% of defined invariants or it is rejected.
2. **Draft-07 Standard Conformance:** Every canonical contract must be an authentic, valid JSON Schema Draft-07 document.
3. **Bijective Lineage Integrity:** Every single property in the derived contract must trace directly to a verified location in the frozen raw source document.
4. **4-Gate Admission Pipeline:** The promotion from `PROVISIONAL_CANONICAL_CANDIDATE` to `CANONICAL_FAITHFUL` requires passing all four gates sequentially.

---

## 2. Gate 1: Extraction Engine Pass Invariants

Before automated schema validation commences, the extraction engine itself must report a successful, clean extraction:
- **Clean Execution:** Zero unhandled exceptions or runtime panics during parsing or pointer navigation.
- **Byte Stability:** Re-running the extractor on the same raw file must yield byte-for-byte identical output (identical SHA-256).
- **Failure Cleanliness:** If extraction fails for any reason, no partial schema may remain on disk, and a detailed entry must be logged in `results_stage_b/extraction_failure_report.json`.

---

## 3. Gate 2: Automated Contract Validator Specification

The automated validator (`src/validate_stage_b_canonical_contracts.py`) executes five invariant suites against every generated canonical contract file:

### 3.1 Suite A: JSON Schema Draft-07 Meta-Validation
- **Meta-Schema Assertion:** The root schema must explicitly declare:
  `"$schema": "http://json-schema.org/draft-07/schema#"`
- **Draft7Validator Verification:** Must invoke Python `jsonschema.Draft7Validator.check_schema(schema_dict)`. Any `SchemaError` causes immediate validation failure.
- **Type Keyword Validity:** All `type` declarations must be valid Draft-07 primitive type strings (`"string"`, `"number"`, `"integer"`, `"boolean"`, `"array"`, `"object"`, `"null"`) or arrays thereof.

### 3.2 Suite B: Root Wrapper Structural Invariants (OpenAPI Operations)
- **Allowed Top-Level Properties:** The root schema object must contain *strictly and only* the following keys:
  - `"$schema"` (string)
  - `"title"` (non-empty string)
  - `"description"` (non-empty string)
  - `"type"` (must equal `"object"`)
  - `"properties"` (object)
  - `"required"` (array of strings, may be empty or contain subset of `["path", "query", "header", "body"]`)
  - `"additionalProperties"` (must equal `false`)
  - `"x-benchmark-metadata"` (object)
- **Mandatory Surface Containers:** The `properties` dictionary must contain exactly four surface containers:
  `{"path", "query", "header", "body"}`.
  No additional surface containers are permitted.
- **Container Structure:** Each of the four surface containers must conform to:
  ```json
  {
    "type": "object",
    "properties": { ... },
    "additionalProperties": false
  }
  ```
  If the container defines required fields, `"required"` must be an array of strings listing properties defined in that container's `"properties"`.

### 3.3 Suite C: Root Wrapper Structural Invariants (MCP Tools)
- **Mandatory RPC Container:** For MCP tools, `properties` must contain exactly one container: `"arguments"`.
- **Top-Level Required:** Must equal `["arguments"]`.
- **Root additionalProperties:** Must equal `false`.

### 3.4 Suite D: Surface-Internal Integrity Invariants
- **Required Array Consistency:** For every object schema at every nesting level ($0 \le d \le 5$):
  - Every string in `"required"` must be a defined key in that object's `"properties"`.
  - The `"required"` array must contain zero duplicate elements.
  - The `"required"` array must be sorted in ascending Unicode code-point order.
- **`additionalProperties: false` Enforcement:** Every object definition at every level must explicitly declare `"additionalProperties": false`. Open schemas (`additionalProperties: true` or omitted) are strictly forbidden in canonical contracts.
- **Recursion Depth Ceiling:**
  - Let $d(\text{root}) = 0$.
  - Traversing into an object's property increments depth: $d(\text{child}) = d(\text{parent}) + 1$.
  - Traversing into an array's `items` schema increments depth: $d(\text{items}) = d(\text{parent}) + 1$.
  - The maximum depth observed anywhere in the schema tree must satisfy:
    $$\max(d) \le 5$$
  - If $\max(d) > 5$, the validator fails the schema with `RECURSION_DEPTH_EXCEEDED`.

### 3.5 Suite E: Enum Value Integrity
- **Non-Empty Enums:** Any `"enum"` array must contain at least one element.
- **Homogeneous Primitive Types:** All elements within an enum array must share the same primitive JSON type (string, integer, or boolean).
- **Code-Point Uniqueness:** Enum arrays must contain zero duplicates. For string enums, elements must be sorted in ascending Unicode code-point order.

### 3.6 Suite F: Benchmark Metadata Invariants (`x-benchmark-metadata`)
- Must contain all mandatory fields:
  - `candidate_source_id`: Valid candidate ID (e.g. `CAND-001`).
  - `source_cluster_id`: Valid cluster ID (e.g. `CLUSTER_GITHUB`).
  - `source_file_blob_sha`: Exactly 40-character hexadecimal Git blob SHA.
  - `operation_id`: Non-empty string matching manifest.
  - `source_spec_pointer`: Valid RFC 6901 pointer.
  - `extraction_timestamp`: ISO-8601 UTC timestamp.
  - `extractor_version`: SemVer string.
  - `admission_decision`: Valid decision status.
  - `source_structural_metrics`: Object containing `raw_parameter_count`, `raw_nesting_depth`, `raw_optional_ratio`, `raw_enum_density`.
  - `wrapped_contract_structural_metrics`: Object containing `total_property_count`, `wrapped_nesting_depth`, `surface_containers_present`, `surface_containers_required`.

---

## 4. Gate 3: Deterministic Lineage Verification Protocol

The lineage verification engine (`src/verify_canonical_lineage.py`) validates the cryptographic traceability of every extracted contract against `results_stage_b/canonical_field_lineage.jsonl`.

### 4.1 Lineage Record Schema
Each line in `canonical_field_lineage.jsonl` is a JSON object conforming to:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "canonical_schema_sha256",
    "canonical_json_pointer",
    "candidate_source_id",
    "source_cluster_id",
    "raw_source_blob_sha",
    "raw_source_pointers",
    "transformation_category",
    "is_reversible",
    "extractor_version",
    "extraction_timestamp",
    "reviewer_decision"
  ],
  "properties": {
    "canonical_schema_sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
    "canonical_json_pointer": { "type": "string", "pattern": "^/.*" },
    "candidate_source_id": { "type": "string" },
    "source_cluster_id": { "type": "string" },
    "raw_source_blob_sha": { "type": "string", "pattern": "^[0-9a-f]{40}$" },
    "raw_source_pointers": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "source_ast_span": {
      "type": "object",
      "properties": {
        "start_line": { "type": "integer" },
        "end_line": { "type": "integer" },
        "byte_offset": { "type": "integer" }
      }
    },
    "transformation_category": {
      "type": "string",
      "enum": [
        "IDENTITY",
        "SURFACE_WRAPPING",
        "REF_EXPANSION",
        "ALLOF_MERGE",
        "NULLABLE_STANDARDIZATION",
        "AST_TYPE_MAPPING",
        "RAW_SUMMARY",
        "RAW_DESCRIPTION",
        "DETERMINISTIC_TEMPLATE_FALLBACK"
      ]
    },
    "is_reversible": { "type": "boolean" },
    "extractor_version": { "type": "string" },
    "extraction_timestamp": { "type": "string" },
    "reviewer_decision": {
      "type": "string",
      "enum": ["PENDING_REVIEW", "APPROVED", "REJECTED"]
    }
  },
  "additionalProperties": false
}
```

### 4.2 Automated Lineage Verification Invariants
The verifier executes the following assertions for every property in every canonical contract:

1. **Complete Property Coverage (No Phantom Fields):**
   - Traverse the canonical contract and collect all JSON pointers to leaf and intermediate properties (e.g. `/properties/body/properties/name`).
   - Assert that *every single property pointer* exists in `canonical_field_lineage.jsonl`.
   - If any property is present in the schema but missing from the lineage ledger, fail immediately with `UNREGISTERED_CANONICAL_FIELD`.

2. **Pointer Existence in Raw Source:**
   - For every entry in `canonical_field_lineage.jsonl`, resolve each pointer in `raw_source_pointers` against the frozen raw source file on disk.
   - Assert that the target node exists in the raw source document.
   - If a raw source pointer resolves to `None` or fails RFC 6901 navigation, fail immediately with `BROKEN_RAW_SOURCE_POINTER`.

3. **Blob SHA Verification:**
   - Assert that `raw_source_blob_sha` matches the Git blob SHA of the raw source file on disk.

4. **Hash Continuity:**
   - Assert that `canonical_schema_sha256` exactly matches the SHA-256 hash of the canonical contract file on disk.

---

## 5. Gate 4: Mandatory Manual Review Gate

Automated checks verify syntax, types, and pointer arithmetic. The manual review gate provides human-in-the-loop verification of domain semantics and transport fidelity.

### 5.1 Review Criteria
A qualified human reviewer must review each candidate contract and answer the following checklist:
- [ ] **Transport Surface Correctness:** Are path parameters correctly placed in `path`? Query in `query`? Headers in `header`? Body in `body`?
- [ ] **Authentication Cleanliness:** Have all authentication credentials (`token`, `api_key`) been removed from model-facing arguments and preserved only in metadata?
- [ ] **Description Fidelity:** Does the tool description match upstream docs without subjective alteration or LLM hallucinations?
- [ ] **Polymorphic Variant Sanity:** If the operation contains unions (under Amendment 003), do the variants accurately reflect upstream API choices?
- [ ] **Business Logic Realism:** Can this endpoint be meaningfully invoked in a benchmark scenario with deterministic inputs?

### 5.2 Recording Sign-Off
- When approved, the reviewer updates the `reviewer_decision` in `canonical_field_lineage.jsonl` from `"PENDING_REVIEW"` to `"APPROVED"`.
- The reviewer records the sign-off in `results_stage_b/canonical_extraction_verification.md` with:
  - Operation ID
  - Date and reviewer identity
  - Explicit statement of approval
  - Git commit hash of the reviewed contract

---

## 6. Official Promotion Transition Matrix

| Current Admission Decision | Gate 1 Pass | Gate 2 Pass | Gate 3 Pass | Gate 4 Pass | Resulting Admission Decision | Permitted in Primary Benchmark? |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| `PROVISIONAL_CANONICAL_CANDIDATE` | YES | YES | YES | YES | **`CANONICAL_FAITHFUL`** | **YES** |
| `PROVISIONAL_CANONICAL_CANDIDATE` | YES | YES | YES | NO / PENDING | `PROVISIONAL_CANONICAL_CANDIDATE` | NO |
| `PROVISIONAL_CANONICAL_CANDIDATE` | YES | NO | Any | Any | `EXCLUDE_PENDING` | NO |
| `PROVISIONAL_CANONICAL_CANDIDATE` | NO | Any | Any | Any | `EXCLUDE_PENDING` | NO |
| `PROVISIONAL_FAITHFUL_UNION` | YES | YES | YES | YES | **`CANONICAL_FAITHFUL`** | **YES** |
| `PROVISIONAL_FAITHFUL_UNION` | YES | NO | Any | Any | `EXCLUDE_PENDING` | NO |
| `EXCLUDE_PENDING` | N/A | N/A | N/A | N/A | `EXCLUDE_PENDING` | NO |

> **Strict Non-Promotion Rule:** Under no circumstances may any operation be admitted into `CANONICAL_FAITHFUL` without all four gates passing. No temporary waivers, heuristic exceptions, or provisional allowances are permitted.
