# OpenAPI 3.0 to JSON Schema Draft-07 Conversion and Dialect Governance Policy

**Policy ID:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Policy Version:** `1.0.0`  
**Effective Date:** October 26, 2026  
**Source Dialect:** OpenAPI 3.0.x Schema Object (based on extended JSON Schema Draft-04)  
**Target Dialect:** JSON Schema Draft-07 (`http://json-schema.org/draft-07/schema#`)  
**Cryptographic Policy Hash (SHA-256):** `ca17608c3a1fcee075e5706928bfbc7f958d6e59e447e9461350f4afc9191290`  
**Status:** `ACTIVE_AND_ENFORCED`  

---

## 1. Scientific Mandate & Problem Formulation

In modern autonomous agent benchmarking, function calling tool definitions rely fundamentally on standard JSON Schema Draft-07 contracts. When extracting real-world API operation specifications into tool interfaces, extractors frequently ingest OpenAPI 3.0.x schemas.

A critical semantic discrepancy separates OpenAPI 3.0.x from JSON Schema Draft-07:
1. **OpenAPI 3.0 Semantics:** `nullable: true` is an active modifier keyword that alters the associated primitive `type` declaration, allowing the property value to be `null` in addition to the specified type.
2. **JSON Schema Draft-07 Semantics:** `nullable` is an unrecognized keyword. Standard Draft-07 meta-schemas do not define `nullable`, and conformant validators ignore it completely during evaluation. In Draft-07, nullability must be represented as a primitive type union: `type: [<type>, "null"]`.
3. **The Preservation Fallacy:** Copying `{"type": "string", "nullable": true}` verbatim into a Draft-07 contract causes standard validators to reject `null` values as schema violations (`ValidationError: None is not of type 'string'`). Consequently, verbatim syntactic copying produces a **semantic regression**, not semantic preservation.

This policy establishes an explicit, auditable governance framework that classifies all schema conversions into four mutually exclusive categories.

---

## 2. Four-Tier Dialect Governance Classification

```
+-------------------------------------------------------------------------------+
|             OpenAPI 3.0 to JSON Schema Draft-07 Dialect Taxonomy              |
+-------------------------------------------------------------------------------+
| Tier A: Safe Syntactic Preservation                                           |
|         Keywords with identical syntax and identical Draft-07 semantics       |
|         -> Classification: PRESERVED                                          |
+-------------------------------------------------------------------------------+
| Tier B: Explicit Semantic-Preserving Conversion                               |
|         Syntactic transformations required to maintain source validation      |
|         -> Classification: INTENTIONAL_REPRESENTATION_CHANGE                  |
+-------------------------------------------------------------------------------+
| Tier C: Explicit Representation-Changing Normalization                        |
|         Architectural adaptations (e.g. wrapper synthesis, form encoding)     |
|         -> Classification: WRAPPER_NORMALIZATION                              |
+-------------------------------------------------------------------------------+
| Tier D: Unsupported / Rejected Constructs                                     |
|         Constructs lacking unambiguous Draft-07 mapping; fail-closed          |
|         -> Classification: UNSUPPORTED_OR_UNVERIFIED                          |
+-------------------------------------------------------------------------------+
```

---

## 3. Detailed Category Specifications

### Category A: Safe Syntactic Preservation
Keywords that possess identical syntax and identical assertion semantics across both OpenAPI 3.0.x and JSON Schema Draft-07:
- Primitive type assertions: `type: "string"` (when non-nullable), `type: "integer"`, `type: "number"`, `type: "boolean"`, `type: "object"`, `type: "array"`.
- Structural keywords: `properties`, `required`, `items`, `additionalProperties` (boolean or schema).
- Validation constraints: `minimum`, `maximum`, `multipleOf`, `minLength`, `maxLength`, `pattern`, `minItems`, `maxItems`, `uniqueItems`, `minProperties`, `maxProperties`, `enum`, `const`.
- Informational annotations: `title`, `description`, `default`.

**Governance Rule:** These keywords are classified as `PRESERVED` only when unaffected by dialect modifiers.

---

### Category B: Explicit Semantic-Preserving Conversion

#### 1. Nullable Modifier (`nullable: true` with explicit type)
- **Source Syntax:** `{"type": "<T>", "nullable": true}`
- **Target Draft-07 Syntax:** `{"type": ["<T>", "null"]}`
- **Constraint Retention:** All sibling constraints (`minimum`, `maximum`, `pattern`, `minLength`, etc.) are preserved verbatim.
- **Enum Interaction Rule:** Under OpenAPI 3.0 specification section 4.7.24.1: *"The value of nullable has no effect on the enum values. Therefore, null is not an allowed value for enum unless it is explicitly included."* In Draft-07, if `type: ["string", "null"]` is declared with `enum: ["A", "B"]`, passing `null` fails Draft-07 evaluation because `null` is absent from `enum`. The extractor must not synthesize `null` into an enum if the raw source omits it; constraint behavior is strictly preserved.
- **Quarantine:** The OpenAPI-specific `nullable` keyword must be excised from the generated Draft-07 contract.
- **Provenance Accounting:** Recorded in `field_lineage.jsonl` as `INTENTIONAL_REPRESENTATION_CHANGE` and in `difference_register.json` under policy pointer `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`. Never labeled verbatim preservation.

#### 2. Redundant Nullable Modifier (`nullable: false`)
- **Source Syntax:** `{"type": "<T>", "nullable": false}`
- **Target Draft-07 Syntax:** `{"type": "<T>"}`
- **Quarantine:** Excised as redundant syntax because Draft-07 primitive types exclude `null` by definition.
- **Classification:** `WRAPPER_NORMALIZATION`.

#### 3. Exclusive Bounds (`exclusiveMinimum` / `exclusiveMaximum` boolean)
- **Source Syntax (Draft-04 / OAS 3.0):** `{"minimum": <N>, "exclusiveMinimum": true}`
- **Target Draft-07 Syntax:** `{"exclusiveMinimum": <N>}` (numeric bound; `minimum` removed).
- **Classification:** `INTENTIONAL_REPRESENTATION_CHANGE`.
- **Rationale:** Draft-07 requires numeric bounds for `exclusiveMinimum`; boolean values cause `jsonschema.Draft7Validator` SchemaErrors.

#### 4. Singular Example (`example: <V>`)
- **Source Syntax:** `{"example": <V>}`
- **Target Draft-07 Syntax:** Retained as informative metadata or converted to `examples: [<V>]`.
- **Classification:** `DOCUMENTED_ANNOTATION`.

---

### Category C: Explicit Representation-Changing Normalization

#### 1. Wrapper Closed-Object Policy (`WRAPPER_CLOSED_OBJECT_POLICY_001`)
- Synthesizes top-level tool call wrappers (`path`, `query`, `header`, `body`) and closes them with `additionalProperties: false`.
- **Classification:** `WRAPPER_NORMALIZATION`.
- **Mandate:** Requires explicit human validation sign-off.

#### 2. Transport Serialization Metadata (`SERIALIZATION_TRANSPORT_METADATA_001`)
- OpenAPI form serialization metadata (`style`, `explode`, `allowReserved`) is quarantined in `x-openapi-encoding` or `x-benchmark-metadata`.
- **Classification:** `WRAPPER_NORMALIZATION`.

---

### Category D: Unsupported and Rejected Constructs (Fail-Closed)

#### 1. Request-Surface `readOnly` Properties
- **Source Pattern:** Property marked `readOnly: true` inside a request body schema (`requestBody`).
- **Semantic Assessment:** In autonomous function calling, tool arguments represent HTTP write request payloads. Properties designated `readOnly` in OpenAPI specifications are designated for HTTP response bodies and MUST NOT be sent by the client (RFC 7231 / OpenAPI 3.0 section 4.7.24).
- **Enforcement Rule:** If an extracted operation defines `readOnly: true` on a request-surface property, the candidate extractor MUST fail closed under `ERR_READONLY_IN_REQUEST_SURFACE` unless governed by an explicit request-surface projection filter policy.

#### 2. Polymorphic Discriminators (`discriminator`)
- Unhandled by monomorphic extractors; fails closed under `ERR_POLYMORPHIC_DISCRIMINATOR`.

#### 3. Dynamic Polymorphism (`oneOf` / `anyOf` on request body)
- Fails closed under `ERR_POLYMORPHIC_UNION`; governed under Protocol Amendment 003.

#### 4. Unregistered OAS Schema Keywords
- Any unmapped OpenAPI extension or keyword fails closed under `ERR_UNKNOWN_OAS_KEYWORD`.

---

## 4. Verification and Compliance Checklist

Every Stage B candidate extraction engine must satisfy the following invariants:
1. Zero unhandled `nullable: true` keywords present in output Draft-07 contracts.
2. Every `nullable: true` converted to `type: [<T>, "null"]`.
3. Sibling constraints (`enum`, `pattern`, bounds) retained without modification.
4. Converted fields recorded as `INTENTIONAL_REPRESENTATION_CHANGE`.
5. Historical V1 artifact bytes preserved immutably.
6. Absolute zero-potential-loss claims prohibited until human validation approves the conversion.
