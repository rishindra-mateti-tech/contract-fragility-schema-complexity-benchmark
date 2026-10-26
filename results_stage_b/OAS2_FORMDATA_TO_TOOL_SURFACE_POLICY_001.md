# OpenAPI 2.0 FormData to Tool Surface Governance Policy

**Policy Identifier:** `OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001`  
**Policy Version:** `1.0.0`  
**Effective Date:** October 26, 2026  
**Status:** `FROZEN_AND_ENFORCED`  
**Source Dialect:** Swagger / OpenAPI 2.0 (`in: formData`)  
**Target Tool Surface:** `form` (Discrete JSON Schema Draft-07 Object)  

---

## 1. Epistemic Mandate and Architectural Rationale

In Swagger / OpenAPI 2.0, HTTP request payloads for form submissions are modeled not as request bodies with media-type schemas, but as flat parameters with `in: "formData"` and operation-level `consumes` declarations (e.g., `application/x-www-form-urlencoded` or `multipart/form-data`).

Previous extraction pipelines either rejected `formData` operations outright or risked conflating form-encoded payloads with `application/json` request bodies.

### The Scientific Invariant
1. **Never conflate `formData` with `body`:** An HTTP form payload behaves differently from an `application/json` object payload. Mapping form fields into `body` misrepresents the transport contract.
2. **Dedicated Surface Container:** Form fields are gathered into a discrete top-level container named `form`, alongside standard containers (`query`, `path`, `header`).
3. **Explicit Provenance Classification:** Because transforming individual Swagger parameters into a single composite object is a structural modification, every adapted field must be classified as `INTENTIONAL_REPRESENTATION_CHANGE` in lineage records.

---

## 2. Policy Enforcement Rules

### Rule 1: Surface Isolation
- Parameters declaring `in: "formData"` are grouped into a closed object container under `properties.form`.
- Non-form parameters (`header`, `query`, `path`) remain isolated in their respective containers.
- The `form` container must declare `additionalProperties: false`.

### Rule 2: Ambiguity Fail-Closed
If an operation declares both `in: "formData"` parameters and an `in: "body"` parameter, extraction must fail closed with `ERR_BODY_FORMDATA_AMBIGUITY`.

### Rule 3: File Upload and Binary Prohibition
- Any form parameter declaring `type: "file"` is rejected fail-closed under `ERR_FILE_UPLOAD_PROHIBITED`.
- Any parameter declaring `format: "binary"` or `format: "byte"` is rejected fail-closed under `ERR_BINARY_FIELD_PROHIBITED`.

### Rule 4: Preserved Validation Keywords
The adapter preserves all valid constraint keywords: `type`, `description`, `default`, `enum`, `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`, `minItems`, `maxItems`, and `uniqueItems`.

### Rule 5: Explicit Wire Conformance Boundary
All generated candidate metadata must declare:
- `wire_conformance_claim: "HTTP_WIRE_CONFORMANCE_EXPLICITLY_UNVALIDATED"`
- `server_acceptance_claim: "SERVER_ACCEPTANCE_EXPLICITLY_UNVALIDATED"`

No empirical claim of live wire serialization or server acceptance is permitted without end-to-end integration testing against running services.

---

## 3. Error Code Reference

| Error Code | Category | Operational Action |
| :--- | :--- | :--- |
| `ERR_FILE_UPLOAD_PROHIBITED` | Modality Restriction | Reject candidate fail-closed. |
| `ERR_BINARY_FIELD_PROHIBITED` | Modality Restriction | Reject candidate fail-closed. |
| `ERR_BODY_FORMDATA_AMBIGUITY` | Transport Ambiguity | Reject candidate fail-closed. |
| `ERR_UNSUPPORTED_COLLECTION_FORMAT` | Array Serialization | Reject candidate fail-closed. |
| `ERR_UNSUPPORTED_FORM_TYPE` | Type System | Reject candidate fail-closed. |
