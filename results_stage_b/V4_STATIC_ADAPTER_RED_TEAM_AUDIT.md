# Stage B Static Source-Adapter Adversarial Red-Team Audit

## Executive Summary

This document reports on the adversarial security and dialect-integrity evaluation of the Stage B Static Source-Adapter Framework under Pipeline 4.0.0. The evaluation was performed against twenty-one dedicated adversarial attack vectors spanning Python AST parsing, TypeScript AST parsing, and Multi-File OpenAPI Reference Closures.

All 21 adversarial vectors passed verification without exception. The static adapters enforced fail-closed termination against every prohibited, dynamic, or malicious construct without executing host code or network requests.

- Audit Date: 2026-10-26
- Pipeline Version: 4.0.0
- Total Vectors Tested: 21
- Total Vectors Passed: 21 (100%)
- Total Invariant Violations: 0
- Execution Mode: Pure Static AST and Offline Filesystem Confinement

---

## 1. Threat Models and Defense Architecture

### 1.1 Python Dynamic Code Execution Threat Model
- Risk: Parsing Python tools by importing modules (`importlib`) or executing AST (`eval()`, `exec()`) exposes the benchmark to arbitrary code execution, environment poisoning, and non-deterministic schema generation.
- Defense: `PythonAstToolExtractor` operates exclusively on Python's built-in `ast` module. No modules are imported, no bytecode is compiled, and no runtime state is created. Any dynamic identifier, function call, variable reference, or computed attribute triggers an immediate, structured `PythonAstExtractionError`.

### 1.2 TypeScript Runtime Schema Builder Threat Model
- Risk: MCP TypeScript tools frequently use dynamic schema builders (such as `zodToJsonSchema`) or import schemas from sibling modules. Inferring these schemas at runtime requires running a Node.js runtime, which violates deterministic offline audit invariants.
- Defense: `TypeScriptAstToolExtractor` utilizes Tree-sitter (`tree-sitter:0.25.2` and `tree-sitter-typescript:0.23.2`) to inspect syntax trees statically. Dynamic schema builders, function calls (`call_expression`), unknown object spreads, and imported identifiers are rejected fail-closed with structured diagnostic records.

### 1.3 Filesystem Traversal and SSRF Threat Model
- Risk: Multi-file OpenAPI references (`$ref`) can attempt to escape repository root boundaries via `../` path traversal, access sensitive host files (`/etc/passwd`), or trigger remote SSRF network requests (`https://...`).
- Defense: `LocalReferenceResolver` strictly prohibits URI schemes (`http://`, `https://`, `ftp://`, `file://`), absolute filesystem paths, and relative paths escaping the declared closure root or bundle root. All multi-file accesses are strictly confined to the pinned source-closure directory and verified against cryptographic SHA-256 manifests.

### 1.4 Cyclical Reference Recursion Threat Model
- Risk: Recursive data models (e.g. self-referential schemas) can induce infinite loops or stack overflow errors during schema expansion.
- Defense: `LocalReferenceResolver` tracks the lexical call path as an ordered list of `(file_path, pointer)` tuples. Any re-encounter of an active target token raises `ERR_REFERENCE_CYCLE_DETECTED` fail-closed.

---

## 2. Adversarial Test Vector Results

### 2.1 Python AST Test Suite (7 Vectors)

| Vector ID | Attack / Invariant Description | Target Error / Code | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `PY-01` | Pure literal schema dictionary input | Extraction Success | Valid dictionary extracted | PASSED |
| `PY-02` | Dynamic variable identifier passed as `inputSchema` | `ERR_DYNAMIC_VARIABLE_REJECTED` | Fail-closed exception raised | PASSED |
| `PY-03` | Function-call-generated schema constructor | `ERR_COMPUTED_SCHEMA_CONSTRUCTION` | Fail-closed exception raised | PASSED |
| `PY-04` | Imported module attribute passed as schema | `ERR_DYNAMIC_ATTRIBUTE_REJECTED` | Fail-closed exception raised | PASSED |
| `PY-05` | Computed tool name via string concatenation | `ERR_STRING_CONCATENATION_REJECTED` | Fail-closed exception raised | PASSED |
| `PY-06` | Deeply nested object/array literal preservation | Structural Preservation | Exact key hierarchy preserved | PASSED |
| `PY-07` | Source span and snippet hash stability | Deterministic Coordinates | Bit-identical coordinates verified | PASSED |

### 2.2 TypeScript AST Test Suite (7 Vectors)

| Vector ID | Attack / Invariant Description | Target Error / Code | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TS-01` | Pure literal object tool declaration | Extraction Success | Valid tool definition extracted | PASSED |
| `TS-02` | Unknown object spread (`...baseProps`) in schema | `ERR_UNKNOWN_SPREAD_REJECTED` | Fail-closed rejection recorded | PASSED |
| `TS-03` | Computed property name (`[key]: val`) | `ERR_COMPUTED_PROPERTY_REJECTED` | Fail-closed rejection recorded | PASSED |
| `TS-04` | Runtime schema builder call (`zodToJsonSchema`) | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | Fail-closed rejection recorded | PASSED |
| `TS-05` | Imported identifier passed as schema | `ERR_IMPORTED_SCHEMA_REJECTED` | Fail-closed rejection recorded | PASSED |
| `TS-06` | Deeply nested TypeScript literal preservation | Structural Preservation | Exact hierarchy preserved | PASSED |
| `TS-07` | Tree-sitter line/column span stability | Deterministic Coordinates | Bit-identical coordinates verified | PASSED |

### 2.3 Reference Closure Test Suite (7 Vectors)

| Vector ID | Attack / Invariant Description | Target Error / Code | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `REF-01` | Valid local multi-file relative reference | Resolution Success | Target schema node dereferenced | PASSED |
| `REF-02` | Path traversal escaping closure root (`../../`) | `ERR_PATH_TRAVERSAL_DETECTED` | Fail-closed exception raised | PASSED |
| `REF-03` | Remote URI reference (`https://...`) | `ERR_REMOTE_REF_PROHIBITED` | Fail-closed exception raised | PASSED |
| `REF-04` | Mutually recursive reference loop (A -> B -> A) | `ERR_REFERENCE_CYCLE_DETECTED` | Fail-closed exception raised | PASSED |
| `REF-05` | Tampered/stale closure file on disk | Cryptographic Hash Mismatch | Integrity mismatch flagged | PASSED |
| `REF-06` | Non-existent JSON Pointer fragment | `ERR_FRAGMENT_NOT_FOUND` | Fail-closed exception raised | PASSED |
| `REF-07` | Malformed or conflicting reference document | Fail-closed Exception | Document parse failure caught | PASSED |

---

## 3. Epistemic Status and Lifecycle Safeguards

1. Quarantined Candidate State: No test vector or extraction run promoted any candidate to `CANONICAL_FAITHFUL`. All candidate bundles remain quarantined at `EXTRACTED_PENDING_HUMAN_VALIDATION`.
2. Independent Review Preservation: Author test suite executions and automated validations are explicitly documented as internal verification, not independent human validation.
3. Zero Dynamic Execution: Zero subprocesses invoked Python or Node.js runtimes to execute target source code. All analyses were conducted via parser syntax trees.
