# Stage B V4 Static Source-Adapter Scope Freeze Baseline

**Status:** `LOCKED_AND_ENFORCED`  
**Execution Date:** October 26, 2026  
**Baseline Commit SHA:** `ec486d3255b73225ba65fc498e33be36d80b63e3`  
**Target Pipeline Version:** `4.0.0`  
**Target Candidate Root:** `data_stage_b/extraction_candidates_v4/`  

---

## 1. Baseline Verification Status

Prior to initiating any code changes or source acquisition for Track 1 through Track 7, the entire Stage B test, audit, and reproducibility suite was executed from a clean working tree:

- **Unit and Integration Test Suite:** 275 tests passed in 104.03s (`python -m pytest`).
- **Hermetic Reproducibility Suite:** 10/10 checks passed (`python scripts/verify_reproducibility.py`).
- **Source Admission Forensic Audit:** 10 raw sources and 30 manifest operations cryptographically verified (`python src/audit_stage_b_source_admission.py`).
- **Dialect Compatibility Audit:** 928 occurrences surveyed across 15 slots (`python src/audit_oas30_draft07_compatibility.py`).
- **Epistemic Research Claim Linter:** 210 markdown files scanned, 0 violations (`python -m src.lint_research_claims`).

---

## 2. Target Scope and Intended Slots

The V4 static source-adapter expansion targets the remaining 9 monomorphic operations previously rejected due to multi-file reference absence or AST source formats:

| Target Slot ID | Candidate Source | Operation Identifier | Source Language / Dialect | Target Adapter Architecture |
| :--- | :--- | :--- | :--- | :--- |
| `SLOT_DO_01` | `CAND-003` (DigitalOcean) | `floating_ips_create` | OpenAPI 3.0.0 (multi-file `$ref`) | Pinned Local Source-Closure Resolver |
| `SLOT_DO_02` | `CAND-003` (DigitalOcean) | `domains_create` | OpenAPI 3.0.0 (multi-file `$ref`) | Pinned Local Source-Closure Resolver |
| `SLOT_DO_03` | `CAND-003` (DigitalOcean) | `droplets_create` | OpenAPI 3.0.0 (multi-file `$ref`) | Pinned Local Source-Closure Resolver |
| `SLOT_MCP_SQLITE_01` | `CAND-009` (SQLite MCP) | `read_query` | Python 3 AST source | Static Python AST Tool Extractor |
| `SLOT_MCP_SQLITE_02` | `CAND-009` (SQLite MCP) | `describe_table` | Python 3 AST source | Static Python AST Tool Extractor |
| `SLOT_MCP_SQLITE_03` | `CAND-009` (SQLite MCP) | `write_query` | Python 3 AST source | Static Python AST Tool Extractor |
| `SLOT_MCP_GITHUB_01` | `CAND-010` (GitHub MCP) | `search_repositories` | TypeScript AST source | Static TypeScript AST Tool Extractor |
| `SLOT_MCP_GITHUB_02` | `CAND-010` (GitHub MCP) | `create_issue` | TypeScript AST source | Static TypeScript AST Tool Extractor |
| `SLOT_MCP_GITHUB_03` | `CAND-010` (GitHub MCP) | `create_or_update_file` | TypeScript AST source | Static TypeScript AST Tool Extractor |

### Explicit Exclusions (Fail-Closed)
- **`SLOT_STRIPE_03` (`PostRefunds`):** Polymorphic union schema structure requiring multi-schema representations under Protocol Amendment 003. Strictly excluded from V4 batch generation.
- **Dynamic or Runtime Code Execution:** Zero runtime execution, importing, dynamic reflection, or guessing of values is permitted.

---

## 3. Historical Candidate Directory Immutability

Historical candidate extractions are frozen and must remain byte-for-byte immutable throughout this work:

1. **Batch V1:** `data_stage_b/extraction_candidates/<SLOT_ID>/` (13 candidates)
2. **Batch V2:** `data_stage_b/extraction_candidates_v2/<SLOT_ID>/` (13 candidates)
3. **Batch V3:** `data_stage_b/extraction_candidates_v3/<SLOT_ID>/` (18 candidates)

All new outputs must be written exclusively to:
- **Batch V4:** `data_stage_b/extraction_candidates_v4/<SLOT_ID>/`

---

## 4. Architectural Policies and Boundaries

### A. DigitalOcean Pinned Source-Closure Acquisition Policy
1. Acquisition is restricted strictly to local files transitively referenced by the pinned root specification `specification/DigitalOcean-public.v2.yaml`.
2. All retrieved files must originate from the exact immutable commit `e326f5060794769b6835084e48be7ce4db062d39` in `https://github.com/digitalocean/openapi`.
3. Floating branches (`main`, `master`), latest tags, and unrelated repository paths are prohibited.
4. Acquired files must be stored in a dedicated immutable closure directory (`data_stage_b/source_closures/CAND-003/`) and verified cryptographically before resolution.
5. Following acquisition, reference resolution must run entirely offline.

### B. Python AST Static Tool Extraction Policy
1. Parsing must be performed strictly using Python's built-in `ast` module.
2. Code execution, module importing (`importlib`, `__import__`), runtime evaluation (`eval`, `exec`), and dynamic reflection are prohibited.
3. Regex parsing is strictly forbidden.
4. Extraction must be limited to literal AST constructs (dict/list/string/number/bool/null literals, literal keyword arguments, and explicit schema objects).
5. Dynamic expressions, variable mutations, comprehensions, f-strings, string concatenations, and unresolved references must trigger a fail-closed rejection.
6. Exact source provenance (file path, AST node kind, line/column start/end, source snippet hash) must be recorded for every extracted element.

### C. TypeScript AST Static Tool Extraction Policy
1. Parsing must be executed using an offline TypeScript AST compiler bridge or parser.
2. Regex parsing is strictly prohibited.
3. Code evaluation, node execution, runtime bundling, and dynamic imports are forbidden.
4. Tool declarations must be extracted only from static literal constructs and literal type/schema definitions.
5. Dynamic object spreads, computed property names, and runtime schema builders must trigger a fail-closed rejection.
6. Exact line and column spans, AST node types, and source snippet SHA-256 hashes must be captured.

### D. Source-Neutral Intermediate Representation
All source representations (OpenAPI 3.0, OpenAPI 2.0 formData, Python AST, TypeScript AST) must map into a common intermediate schema representation (`src/stage_b_intermediate_representation.py`) prior to Draft-07 tool contract wrapping.

---

## 5. Epistemic Invariants and Lifecycle Truth

1. **No Independent Validation Claims:** No candidate generated in V4 is independently validated. Every candidate is created with status:
   `EXTRACTED_PENDING_HUMAN_VALIDATION`
2. **Prohibition of `CANONICAL_FAITHFUL`:** Zero candidates may receive or be described with `CANONICAL_FAITHFUL`.
3. **No Overstated Equivalence Claims:** Structural transformations and adapter decisions must be explicitly registered as `INTENTIONAL_REPRESENTATION_CHANGE` or `STRUCTURAL_CLOSURE`.
4. **No LLM or Benchmark Runs:** No LLM APIs, provider endpoints, benchmark executions, mutation operators, or paper result tables may be run or produced.
