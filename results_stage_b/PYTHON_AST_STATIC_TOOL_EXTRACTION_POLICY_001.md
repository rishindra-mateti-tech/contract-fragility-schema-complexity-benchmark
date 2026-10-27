# Python AST Static Tool Extraction Policy

**Policy ID:** `PYTHON_AST_STATIC_TOOL_EXTRACTION_POLICY_001`  
**Status:** `ENFORCED`  
**Effective Date:** October 26, 2026  
**Governing Candidate Source:** `CAND-009` (Model Context Protocol SQLite Server)  
**Static Parser:** Python Built-in `ast` Module  
**Cryptographic Policy Hash (JSON):** `0e30b10c1a1f0e1b3d910f6ea836f24e958ad0a346e33345de0b22e5fac9b190`  

---

## 1. Purpose and Scope

This policy defines the protocol for extracting RPC tool call contracts from Python source code exclusively using static abstract syntax tree (AST) analysis.

During Batch Extraction V3, operations `SLOT_MCP_SQLITE_01` (`read_query`), `SLOT_MCP_SQLITE_02` (`describe_table`), and `SLOT_MCP_SQLITE_03` (`write_query`) were rejected fail-closed because they reside in executable Python source files (`server.py`) rather than OpenAPI YAML/JSON documents.

This policy establishes strict invariants to guarantee that tool definitions, argument schemas, required fields, and types are extracted purely from literal AST syntax without executing, importing, or dynamically evaluating Python source code.

---

## 2. Absolute Prohibitions

1. **No Runtime Execution or Importing:** The source file must never be executed via Python runtime, imported (`importlib`, `__import__`), or executed in any subshell.
2. **No Dynamic Evaluation:** Built-ins such as `eval()`, `exec()`, or dynamic attribute access are forbidden.
3. **No Regex Parsing:** Regular expressions must never be used as the parser or extractor for AST structures.
4. **No Dynamic Construct Inferences:** Any tool whose argument schema relies on function calls, imported objects, variable mutations, dictionary unpacking (`**kwargs`), list unpacking (`*args`), f-strings, string concatenations, or list/dict comprehensions must be rejected fail-closed.
5. **No Lifecycle Elevation:** Generated candidates remain strictly `EXTRACTED_PENDING_HUMAN_VALIDATION`. Zero promotions to `CANONICAL_FAITHFUL` are permitted.

---

## 3. Allowed Literal Constructs

Tool extraction is permitted only when all structural schema nodes are composed of:
- `ast.Constant`: String, integer, float, boolean, and None literals.
- `ast.Dict`: Literal dictionary objects with string keys.
- `ast.List` and `ast.Tuple`: Literal array objects.
- `ast.UnaryOp`: Literal signed numeric values (e.g. `-1`).
- Keyword arguments passed directly to `types.Tool(...)` or `Tool(...)` constructors.

---

## 4. Provenance and Lineage Tracking

For every extracted tool and schema element, the extractor must capture and serialize:
- Source file path relative to repository root.
- Source file Git blob SHA-1 and SHA-256 checksums.
- Exact AST node type (`ast.Call`, `ast.Dict`, `ast.Constant`).
- Source line and column spans: `lineno`, `col_offset`, `end_lineno`, `end_col_offset`.
- SHA-256 checksum of the exact raw source code snippet spanning the tool declaration.
- Normalized static AST path (e.g. `Module/FunctionDef[main]/AsyncFunctionDef[handle_list_tools]/Return/List/Call[types.Tool:read-query]`).
- Parser identification and Python environment version.

---

## 5. Intermediate Representation Requirement

Extracted AST tool definitions must not be directly mapped into final Draft-07 tool contracts. Instead, the extractor must output an intermediate, source-neutral tool operation record (`src/stage_b_intermediate_representation.py`) documenting:
- Operation identifier and normalized tool name.
- Input surface container (parameters and schema constraints).
- Required field list.
- Static provenance evidence.
- Transformation lineage and adapter decisions.
