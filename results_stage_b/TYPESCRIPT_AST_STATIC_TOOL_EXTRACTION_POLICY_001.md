# TypeScript AST Static Tool Extraction Policy

**Policy ID:** `TYPESCRIPT_AST_STATIC_TOOL_EXTRACTION_POLICY_001`  
**Status:** `ENFORCED`  
**Effective Date:** October 26, 2026  
**Governing Candidate Source:** `CAND-010` (Model Context Protocol GitHub Server)  
**Static Parser:** `tree-sitter:0.25.2` with `tree-sitter-typescript:0.23.2`  
**Cryptographic Policy Hash (JSON):** `c7b54723b40fdd44767c03fbb3caa145dec98720b1ce504f7c3181880b8d8db9`  

---

## 1. Purpose and Scope

This policy governs the static extraction of RPC tool call contracts from TypeScript source code using pinned Tree-sitter abstract syntax tree analysis without code execution, runtime bundling, or dynamic evaluation.

During Batch Extraction V3, operations `SLOT_MCP_GITHUB_01` (`search_repositories`), `SLOT_MCP_GITHUB_02` (`create_issue`), and `SLOT_MCP_GITHUB_03` (`create_or_update_file`) were rejected fail-closed because they reside in TypeScript source files (`index.ts`).

This policy defines the structural invariants required to extract literal tool schemas and enforces fail-closed rejections for dynamic schema builders (`zod`, `zodToJsonSchema`), function-call-generated schemas, unknown object spreads, and imported schema variables.

---

## 2. Absolute Prohibitions

1. **No Runtime Execution or Bundling:** TypeScript source files must never be executed via Node.js, ts-node, Bun, or Deno.
2. **No Dynamic Schema Builders:** Tools relying on runtime schema generators (such as `zodToJsonSchema(SchemaName)`) must be rejected fail-closed under `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED`.
3. **No Regex Parsing:** Regular expressions are strictly prohibited as parsers or schema extractors.
4. **No Imported Dynamic Schemas:** Tool schemas whose definition resides in external unparsed modules (e.g. `from './schemas.js'`) must be rejected fail-closed under `ERR_IMPORTED_SCHEMA_REJECTED`.
5. **No Object Spreads or Computed Keys:** Object spreads (`...spread`) and computed property names (`[computedKey]`) are prohibited in literal tool schemas.
6. **No Lifecycle Elevation:** Generated candidates remain strictly `EXTRACTED_PENDING_HUMAN_VALIDATION`. Zero promotions to `CANONICAL_FAITHFUL` are permitted.

---

## 3. Allowed Literal Constructs

Tool extraction is permitted only when all structural schema nodes are composed of:
- String and number literal nodes (`string`, `number`).
- Boolean and null literal nodes (`true`, `false`, `null`).
- Object literal expressions with explicit string or identifier property keys.
- Array literal expressions containing literal elements.
- Unary expressions representing signed numeric literals (e.g. `-1`).

---

## 4. Provenance and Lineage Tracking

For every processed tool declaration, the extractor must capture and serialize:
- Source file path relative to repository root.
- Source file Git blob SHA-1 and SHA-256 checksums.
- Exact AST node type (`object`, `pair`, `call_expression`).
- Line and column boundaries: `row_start`, `col_start`, `row_end`, `col_end`.
- Exact source code snippet spanning the tool declaration.
- Cryptographic SHA-256 checksum of the source snippet.
- Normalized AST path.
- Parser version (`tree-sitter:0.25.2:tree-sitter-typescript:0.23.2`).

---

## 5. Fail-Closed Rejection Protocol

When an operation in the candidate universe relies on prohibited constructs:
1. The extractor must record a formal rejection entry rather than aborting the pipeline.
2. The rejection must document:
   - Specific rejection code (e.g. `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED`).
   - Line and column span of the offending AST construct.
   - Exact source snippet demonstrating the dynamic construct.
   - Epistemic rationale explaining why the construct cannot be statically resolved without code execution.
