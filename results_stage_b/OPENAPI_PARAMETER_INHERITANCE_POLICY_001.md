# OpenAPI Path-Item Parameter Inheritance and Merging Governance Policy

**Policy Identifier:** `OPENAPI_PARAMETER_INHERITANCE_POLICY_001`  
**Policy Version:** `1.0.0`  
**Effective Date:** October 26, 2026  
**Status:** `FROZEN_AND_ENFORCED`  
**Governing Standard:** OpenAPI Specification 3.0.x (Sections 4.7.9 and 4.7.10)  

---

## 1. Epistemic Mandate and Architectural Background

In OpenAPI 3.0 and Swagger 2.0 specifications, parameters can be declared at two distinct architectural levels:
1. **Path Item Object level (`#/paths/~1.../parameters`):** Applies universally to all HTTP operations (GET, POST, PUT, DELETE) defined under that path endpoint.
2. **Operation Object level (`#/paths/~1.../post/parameters`):** Applies specifically to the individual operation.

Under the OpenAPI specification:
- Parameters defined at the Path Item level are inherited by all operations under that path.
- An operation can override an inherited parameter by defining a parameter with the identical `(name, in)` unique key.
- Operation-level parameters cannot delete or remove inherited parameters.

Previous pipeline versions (V1 and V2) failed closed whenever path-item level parameters were detected, rejecting valid monomorphic operations such as Chatwoot (`SLOT_CHATWOOT_02` and `SLOT_CHATWOOT_03`).

This policy establishes the exact merging algorithm, provenance requirements, and validation rules to safely inherit and merge parameters into benchmark tool contracts.

---

## 2. Parameter Merging Rules

### Rule 1: Unique Identification by `(name, in)`
Parameters are uniquely keyed by the 2-tuple `(name, in)`. Parameter names alone do not guarantee uniqueness across different locations (e.g., a header and a query parameter may share a name).

### Rule 2: Deterministic Override Precedence
When an Operation defines a parameter with the same `(name, in)` key as an inherited Path Item parameter:
- The Operation-level parameter definition takes precedence.
- The parameter is classified with `origin: "OPERATION_OVERRIDE"` and `override_status: "OVERRIDDEN"`.
- Both the original Path Item declaration pointer and the Operation declaration pointer are preserved in provenance.

### Rule 3: Path Template Consistency Assertion
The adapter asserts bidirectional consistency between the URI template and `in: "path"` parameters:
- Every template variable `{param_name}` in the endpoint URI must correspond to exactly one `in: "path"` parameter.
- Every `in: "path"` parameter must correspond to a template variable in the endpoint URI.
- Any mismatch raises `ERR_PATH_PARAM_MISMATCH` and fails extraction closed.

### Rule 4: Mandatory Path Parameter Requiredness
All `in: "path"` parameters must declare `required: true`. Any path parameter lacking `required: true` raises `ERR_PARAM_MISSING_SCHEMA`.

---

## 3. Provenance and Lineage Tracking

All parameter inheritance decisions must be recorded in the bundle artifact `adapter_decisions.json`. Each decision record contains:

1. `name`: Parameter identifier string.
2. `in`: Location container (`path`, `query`, `header`, `cookie`).
3. `origin`: One of `PATH_ITEM`, `OPERATION`, or `OPERATION_OVERRIDE`.
4. `override_status`: One of `INHERITED`, `OPERATION_LEVEL`, or `OVERRIDDEN`.
5. `path_declared_pointer`: JSON pointer to the parameter definition in Path Item (or `null` if defined only at operation level).
6. `path_resolved_pointer`: Resolved JSON pointer if Path Item parameter used `$ref`.
7. `op_declared_pointer`: JSON pointer to the parameter definition in Operation (or `null` if inherited from Path Item).
8. `op_resolved_pointer`: Resolved JSON pointer if Operation parameter used `$ref`.
9. `required`: Boolean requiredness status.
10. `schema`: Resolved parameter schema definition.

---

## 4. Error Code Reference

| Error Code | Meaning | Operational Action |
| :--- | :--- | :--- |
| `ERR_UNRESOLVED_PARAM_REF` | Parameter `$ref` failed to resolve within document. | Reject candidate fail-closed. |
| `ERR_PARAM_MISSING_SCHEMA` | Parameter lacks valid schema or required metadata. | Reject candidate fail-closed. |
| `ERR_PARAM_OVERRIDE_CONFLICT` | Conflicting duplicate parameters in the same scope. | Reject candidate fail-closed. |
| `ERR_PATH_PARAM_MISMATCH` | Discrepancy between URI template and path parameters. | Reject candidate fail-closed. |
| `ERR_DUPLICATE_OPERATION_PARAM` | Duplicate parameter declared at operation level. | Reject candidate fail-closed. |
