# Stage B Canonical Extraction Pilot Report: SLOT_GITHUB_01 (pulls/create)

## 1. Executive Summary

This report documents the execution and validation of the **Stage B Canonical Contract Extraction Pilot** for the single admitted operation:
- **Slot Identifier:** `SLOT_GITHUB_01`
- **Operation Identifier:** `pulls/create` (`POST /repos/{owner}/{repo}/pulls`)
- **Raw Candidate Source:** `CAND-001` (GitHub REST API OpenAPI 3.0 description)
- **Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md` (Extraction Rule Version `1.2.0`)
- **Current Canonical Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION`

In strict compliance with benchmark research integrity boundaries:
1. **Single-Operation Isolation:** No other operation was extracted, converted, or mutated.
2. **Zero Downstream Mutation / Execution Artifacts:** No mutations, mock handlers, model calls, benchmark results, or empirical claims were generated.
3. **No Unwarranted Elevation:** The operation is explicitly classified as `EXTRACTED_PENDING_HUMAN_VALIDATION` and is **not** labeled `CANONICAL_FAITHFUL`.
4. **Frozen Boundary Invariants:** Pinned raw source files, Git blob SHAs, and Stage A benchmarks remain unaltered.

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
| **Source AST Line Span** | Lines 70801–70865 (65 lines) |
| **HTTP Method & Path** | `POST /repos/{owner}/{repo}/pulls` |
| **Request Content-Type** | `application/json` |

---

## 3. Extracted Canonical Artifact Inventory

The extraction engine (`src/extract_stage_b_canonical_contract.py`) generated the following deterministic artifacts under `data_stage_b/canonical/SLOT_GITHUB_01/`:

| Artifact File | Format | SHA-256 Checksum | Description |
|---|---|---|---|
| `canonical_contract.json` | JSON (Draft-07) | `8b7721b33ec204bf88667de03eb48cbf44a73c485f5dc11cc97d186c0ffaa6d7` | Canonical Draft-07 tool schema with strict single-column surface containers |
| `field_lineage.jsonl` | JSON Lines | `d61d41c684d6debbb30c38dcc66c6b6a018ae429306a10d7a0faa0e5f71a980c` | 15 deterministic property lineage records linking canonical fields to raw source |
| `extraction_manifest.json` | JSON | `10e0aa8b261b0c0344d5c4115162a4df8ddaf27be63969ee73507304f56860ca` | Cryptographic provenance manifest with raw, script, and artifact hashes |
| `validation_report.json` | JSON | `0e3860bb63273eef078ea2753aee246e7fca6dcfae89c6760b7b1d9bf5c1ce8c` | Automated validation report containing results for 39 invariant checks |

In addition, `results_stage_b/canonical_field_lineage.jsonl` was synchronized with the slot's lineage records.

---

## 4. Input Surface & Field Preservation Accounting

### 4.1 Structural Metrics
- **Total Leaf Properties Extracted:** 10
- **Path Parameters:** 2 (`owner`, `repo`)
- **Query Parameters:** 0 (container present with `additionalProperties: false`)
- **Header Parameters:** 0 (container present with `additionalProperties: false`)
- **Body Properties:** 8 (`base`, `body`, `draft`, `head`, `head_repo`, `issue`, `maintainer_can_modify`, `title`)
- **Excluded Fields:** 0
- **Dropped Properties:** 0
- **Invented / Phantom Fields:** 0
- **Type Coercions:** 0
- **Maximum Observed Schema Depth:** 2 (Strictly within benchmark limit $\le 5$)
- **Object Unions Present:** 0

### 4.2 Detailed Field Roster & Lineage Mapping

| Canonical Field Path | JSON Type | Required | Raw Source AST Line | Transformation Category | Reversible |
|---|---|---|---|---|---|
| `/description` | string | N/A | 70802–70803 | `RAW_SUMMARY` | Yes |
| `/properties/path` | object | Yes (`["body", "path"]`) | 70801–70865 | `SURFACE_WRAPPING` | Yes |
| `/properties/path/properties/owner` | string | Yes (`path.required`) | 70814–70815 | `SURFACE_WRAPPING` | Yes |
| `/properties/path/properties/repo` | string | Yes (`path.required`) | 70817–70818 | `SURFACE_WRAPPING` | Yes |
| `/properties/body` | object | Yes (`["body", "path"]`) | 70801–70865 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/base` | string | Yes (`body.required`) | 70841–70844 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/body` | string | No | 70845–70848 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/draft` | boolean | No | 70853–70856 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/head` | string | Yes (`body.required`) | 70831–70834 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/head_repo` | string | No | 70835–70838 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/issue` | integer | No | 70857–70860 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/maintainer_can_modify` | boolean | No | 70849–70852 | `SURFACE_WRAPPING` | Yes |
| `/properties/body/properties/title` | string | No | 70827–70830 | `SURFACE_WRAPPING` | Yes |
| `/properties/query` | object | No | 70801–70865 | `SURFACE_WRAPPING` | Yes |
| `/properties/header` | object | No | 70801–70865 | `SURFACE_WRAPPING` | Yes |

---

## 5. Automated Multi-Suite Validation Results

The multi-suite automated validator (`src/validate_stage_b_canonical_contract.py`) executed 39 distinct checks across 7 test suites. All checks passed with zero errors or warnings (`39 / 39 PASS`):

1. **Suite A: JSON Schema Draft-07 Meta-Validation**
   - Declared `$schema` equals `http://json-schema.org/draft-07/schema#` (`PASS`).
   - Meta-schema syntax validation via `jsonschema.Draft7Validator.check_schema` (`PASS`).

2. **Suite B: Root Wrapper Structural Invariants**
   - Top-level keys strictly match `{ $schema, additionalProperties, description, properties, required, title, type, x-benchmark-metadata }` (`PASS`).
   - Root `type` is `object` (`PASS`).
   - Root `additionalProperties` is `false` (`PASS`).
   - Surface containers are strictly `{ body, header, path, query }` (`PASS`).
   - Root `required` is sorted subset `["body", "path"]` (`PASS`).

3. **Suite C: Transport Separation & Surface Properties**
   - All four surface containers are `type: object` with `additionalProperties: false` (`PASS`).
   - Path surface contains exactly `owner` and `repo` with required array `["owner", "repo"]` (`PASS`).
   - Transport separation: `owner` and `repo` strictly do not leak into `body` (`PASS`).
   - Body surface contains exactly 8 declared properties (`PASS`).
   - Body `required` strictly equals `["base", "head"]` (`PASS`).
   - Query and header surfaces are strictly empty (`PASS`).

4. **Suite D: Recursion Depth & Additional Properties Bounds**
   - Maximum schema recursion depth is 2, strictly satisfying $\le 5$ (`PASS`).
   - Zero object-level unions (`anyOf`/`oneOf`) present across any property (`PASS`).

5. **Suite E: Deterministic Field-Lineage Traceability**
   - Complete 1:1 coverage: all 15 canonical pointers registered in lineage (`PASS`).
   - Zero extraneous lineage records (`PASS`).
   - Cryptographic continuity: all records embed matching canonical schema SHA-256 and raw source blob SHA (`PASS`).

6. **Suite F: Raw Source Lossless Completeness**
   - Raw source file exists, is valid JSON, and resolves source pointer `#/paths/~1repos~1{owner}~1{repo}~1pulls/post` (`PASS`).
   - Raw parameters match canonical path properties bijectively (`PASS`).
   - Raw requestBody properties match canonical body properties bijectively (`PASS`).
   - Raw requestBody required fields match canonical body required array (`PASS`).

7. **Suite G: Manifest Cryptographic Integrity**
   - Computed canonical contract SHA-256 matches manifest entry (`PASS`).
   - Disk raw source file SHA-256 matches manifest entry (`PASS`).
   - Operational status is confirmed as `EXTRACTED_PENDING_HUMAN_VALIDATION` (`PASS`).

---

## 6. Deliberate Drift & Negative Testing Verification

A dedicated regression suite in `tests/test_stage_b_canonical_extraction_pilot.py` verifies that the pipeline immediately detects and rejects deliberate specification drift:

| Drift Scenario Tested | Expected Validation Behavior | Test Result |
|---|---|---|
| **Field Renaming** (e.g. `title` $\to$ `pr_title`) | Fails `body_properties_exact` check | PASS |
| **Missing Required Field** (dropping `head`) | Fails `body_required_exact` check | PASS |
| **Phantom / Invented Field** (injecting `phantom_field`) | Fails `body_properties_exact` check | PASS |
| **Transport Leak** (leaking `owner` into `body`) | Fails `transport_separation_no_path_leak_into_body` check | PASS |
| **Depth Violation** (nesting depth $> 5$) | Fails `recursion_depth_within_bound` check | PASS |
| **Out-of-Scope Slot** (attempting extraction on non-pilot slot) | Raises explicit hard-boundary `ValueError` | PASS |

---

## 7. Conclusion & Next Gate

The extraction of `SLOT_GITHUB_01` (`pulls/create`) successfully validates the deterministic canonical extraction architecture under Draft-07 rules. The operation is currently staged at `EXTRACTED_PENDING_HUMAN_VALIDATION`. Advancing to `CANONICAL_FAITHFUL` will occur only after formal human reviewer sign-off following the completion of the canonical pilot gate.
