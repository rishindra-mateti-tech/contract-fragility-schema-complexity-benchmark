# Static Source Intermediate Representation Specification

**Specification ID:** `STATIC_SOURCE_INTERMEDIATE_REPRESENTATION_SPEC_001`  
**Status:** `ENFORCED`  
**Version:** `1.0.0`  
**Effective Date:** October 26, 2026  

---

## 1. Purpose and Architectural Role

The Stage B Benchmark extracts tool call contracts across diverse source formats:
1. OpenAPI 3.0 / 3.0.3 single-file specifications (GitHub, Twilio, Box, Stripe, LINE).
2. OpenAPI 3.0 multi-file specifications with local `$ref` chains (DigitalOcean).
3. OpenAPI 3.0 specifications with path-item parameter inheritance (Chatwoot).
4. OpenAPI 2.0 / Swagger specifications with `formData` transport parameters (Slack).
5. Model Context Protocol Python 3 source code (`server.py`).
6. Model Context Protocol TypeScript source code (`index.ts`).

To prevent ad-hoc, dialect-specific patching and to establish rigorous provenance across heterogeneous source paradigms, this specification defines a canonical, source-neutral Intermediate Representation (IR).

The IR is a controlled extraction staging layer. It does NOT assert that OpenAPI schemas and language ASTs are semantically identical; rather, it makes every representational choice, surface consolidation, and provenance link explicit and auditable before final JSON Schema Draft-07 contract generation.

---

## 2. Core Schema Structure

Every intermediate representation artifact (`intermediate_representation.json`) must adhere to the following schema structure:

```json
{
  "ir_version": "1.0.0",
  "operation_identity": {
    "operation_id": "<string>",
    "slot_id": "<string>",
    "candidate_source_id": "<string>",
    "source_dialect": "<string>",
    "target_dialect": "JSON Schema Draft-07"
  },
  "source_file_closure": {
    "primary_source_file": "<string>",
    "primary_source_file_blob_sha": "<hex-sha1>",
    "primary_source_file_sha256": "<hex-sha256>",
    "closure_files_accessed": ["<string>"],
    "closure_manifest_sha256": "<hex-sha256 or null>"
  },
  "input_surface": {
    "type": "object",
    "properties": { "<prop_name>": { ... } },
    "required": ["<string>"],
    "additionalProperties": false,
    "sub_surfaces": {
      "path": ["<string>"],
      "query": ["<string>"],
      "header": ["<string>"],
      "form": ["<string>"],
      "body": ["<string>"],
      "rpc_arguments": ["<string>"]
    }
  },
  "schema_complexity_metrics": {
    "property_count": "<int>",
    "required_count": "<int>",
    "max_nesting_depth": "<int>",
    "has_nested_objects": "<bool>",
    "has_arrays": "<bool>",
    "has_enums": "<bool>"
  },
  "source_lineage_and_evidence": {
    "source_pointer": "<string or null>",
    "ast_span": {
      "lineno": "<int>",
      "col_offset": "<int>",
      "end_lineno": "<int>",
      "end_col_offset": "<int>"
    },
    "ast_path": "<string or null>",
    "source_snippet": "<string or null>",
    "source_snippet_sha256": "<hex-sha256 or null>",
    "parser_name": "<string>",
    "parser_version": "<string>"
  },
  "transformation_and_adapter_decisions": [
    {
      "adapter_name": "<string>",
      "action": "<string>",
      "reason": "<string>"
    }
  ],
  "unsupported_feature_flags": ["<string>"],
  "status_and_confidence": {
    "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
    "confidence_assessment": "STATICALLY_VERIFIED_LITERAL",
    "independent_validation_status": "NOT_INDEPENDENTLY_VALIDATED"
  }
}
```

---

## 3. Section Requirements and Invariants

### 3.1 Input Surface Normalization
- The root schema must always be `type: "object"`.
- `additionalProperties: false` is strictly required for tool call argument surfaces.
- For OpenAPI operations, `sub_surfaces` categorizes parameters by their declared `in` location (`path`, `query`, `header`, `form`, `body`).
- For Python/TypeScript AST tools, `sub_surfaces.rpc_arguments` lists all extracted arguments.

### 3.2 Epistemic and Provenance Traceability
- For OpenAPI sources: `source_pointer` records the JSON pointer (e.g. `#/paths/~1domains/post`).
- For AST sources: `ast_span` records 1-indexed line numbers and 0-indexed column offsets; `source_snippet_sha256` preserves cryptographic integrity of the extracted source code.
- Every adapter invocation (e.g. `LocalReferenceResolver`, `ParameterInheritanceAdapter`, `OpenAPI2FormDataAdapter`, `PythonAstToolExtractor`, `TypeScriptAstToolExtractor`) must add an entry to `transformation_and_adapter_decisions`.

### 3.3 Fail-Closed Rejections
When an operation cannot be resolved to a static literal schema (such as polymorphic unions, file uploads, or runtime schema builders), `unsupported_feature_flags` records the specific rejection category, and the operation is halted fail-closed.
