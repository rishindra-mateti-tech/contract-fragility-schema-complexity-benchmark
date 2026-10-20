# Stage B Schema Feature Support Policy and Governance Specification

## 1. Executive Protocol and Purpose

This policy governs the canonical extraction and schema normalization processes for the Stage B benchmark. The objective of canonical contract extraction is to produce Draft-07 tool call schemas that preserve real-world API constraints with maximum fidelity, while ensuring deterministic execution, evaluation hermeticity, and strict schema validation.

To avoid silent semantic loss or arbitrary schema mutation, every OpenAPI and JSON Schema construct observed across candidate specifications is classified into an explicit three-tiered taxonomy:
1. `PRESERVE_VERBATIM`: Features that must be extracted with 100% fidelity without renaming, coercion, pruning, or structural mutation.
2. `EXPLICIT_NORMALIZATION`: Transformations permitted only under explicit, versioned, and reviewed benchmark policies (e.g. `WRAPPER_CLOSED_OBJECT_POLICY_001` for tool parameter routing).
3. `REJECT_AND_REPORT`: Constructs that cause the extraction engine to fail-closed because downstream components (mutation operators, validators, mock executors) cannot evaluate them safely without introducing non-deterministic failure modes.

The authoritative machine-readable inventory is maintained in `results_stage_b/SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml`.

---

## 2. Three-Tier Taxonomy Definitions

### 2.1 PRESERVE_VERBATIM
A schema feature is designated `PRESERVE_VERBATIM` when its semantics in the raw source specification must be mapped directly to the canonical contract.
- The extractor must copy the property name, JSON Schema type, and all associated constraint keywords without modification.
- Keys must be sorted deterministically in dictionary representations.
- Lineage tracking must record the origin JSON pointer in the raw specification and the corresponding pointer in the canonical contract.
- Any discrepancy between the raw source keyword and canonical representation constitutes an extraction bug.

### 2.2 EXPLICIT_NORMALIZATION
A schema feature is designated `EXPLICIT_NORMALIZATION` when the raw OpenAPI specification relies on HTTP transport conventions that do not directly map to single-object function calling contracts.
- Such transformations are strictly prohibited unless authorized by a named policy.
- Example: `WRAPPER_CLOSED_OBJECT_POLICY_001` authorizes synthesizing root, `path_parameters`, and `body` wrapper objects with `additionalProperties: false` to ensure strict parameter routing.
- The extraction audit report must explicitly flag the normalization, document its impact on raw equivalence, and verify that payload properties within the wrappers remain unaltered.

### 2.3 REJECT_AND_REPORT
A schema feature is designated `REJECT_AND_REPORT` when it introduces semantic ambiguity, unbounded recursion, external dependencies, or unsupported transport mechanics.
- The extraction engine must halt immediately with a `FeatureUnsupportedError` specifying the offending feature identifier, JSON pointer, and rationale.
- The extraction engine must never silently drop, approximate, or coerce an unsupported feature.
- Admitting an operation containing a rejected feature requires a formal Protocol Amendment and implementation of dedicated validation mechanisms.

---

## 3. Comprehensive Feature Category Policies

### Category 1: Primitive Types
- `FEAT_PRIM_STRING` (PRESERVE_VERBATIM): Preserved with Draft-07 `type: "string"`.
- `FEAT_PRIM_INTEGER` (PRESERVE_VERBATIM): Preserved with `type: "integer"`.
- `FEAT_PRIM_NUMBER` (PRESERVE_VERBATIM): Preserved with `type: "number"`.
- `FEAT_PRIM_BOOLEAN` (PRESERVE_VERBATIM): Preserved with `type: "boolean"`.
- `FEAT_PRIM_NULL` (PRESERVE_VERBATIM): Preserved with `type: "null"` or type unions containing null.

### Category 2: Enums, Const, Defaults, and Examples
- `FEAT_ENUM_VALUES` (PRESERVE_VERBATIM): Enum arrays preserved verbatim with element order preserved.
- `FEAT_CONST_VALUE` (PRESERVE_VERBATIM): Const values preserved verbatim for exact literal enforcement.
- `FEAT_DEFAULT_VALUE` (PRESERVE_VERBATIM): Preserved as schema annotation to guide mock execution fallbacks and prompt context.
- `FEAT_EXAMPLE_SINGLE` and `FEAT_EXAMPLES_MULTI` (PRESERVE_VERBATIM): Retained as syntax documentation.

### Category 3: Bounds and Constraints
- `FEAT_NUM_MIN_MAX` (PRESERVE_VERBATIM): Minimum, maximum, exclusiveMinimum, and exclusiveMaximum bounds preserved verbatim.
- `FEAT_NUM_MULTIPLE_OF` (PRESERVE_VERBATIM): Division step constraints preserved verbatim.
- `FEAT_STR_LENGTH` (PRESERVE_VERBATIM): MinLength and maxLength limits preserved verbatim.
- `FEAT_STR_PATTERN` (PRESERVE_VERBATIM): Regular expression string patterns preserved verbatim.
- `FEAT_ARR_ITEM_BOUNDS` (PRESERVE_VERBATIM): MinItems, maxItems, and uniqueItems bounds preserved verbatim.
- `FEAT_OBJ_PROP_BOUNDS` (PRESERVE_VERBATIM): MinProperties and maxProperties bounds preserved verbatim.

### Category 4: Objects, Arrays, and Maps
- `FEAT_OBJ_PROPERTIES` (PRESERVE_VERBATIM): Properties dictionaries recursively extracted with sorted keys.
- `FEAT_OBJ_REQUIRED` (PRESERVE_VERBATIM): Required properties arrays preserved with alphabetical key ordering.
- `FEAT_ARR_ITEMS_SCHEMA` (PRESERVE_VERBATIM): Homogeneous array items schema recursively traversed and preserved.
- `FEAT_ARR_ITEMS_TUPLE` (REJECT_AND_REPORT): Positional tuple schemas (`items` as array or `prefixItems`) fail closed.
- `FEAT_ADDITIONAL_PROPS_BOOL_FALSE` (PRESERVE_VERBATIM): Payload-level explicit false preserved verbatim.
- `FEAT_ADDITIONAL_PROPS_BOOL_TRUE` (PRESERVE_VERBATIM): Payload-level open object behavior preserved without synthetic closure.
- `FEAT_ADDITIONAL_PROPS_SCHEMA_MAP` (PRESERVE_VERBATIM): Dynamic map schemas (e.g. string to string dictionaries) recursively preserved.
- `FEAT_WRAPPER_CLOSED_OBJECT` (EXPLICIT_NORMALIZATION): Synthetic root and transport wrapper objects enforce `additionalProperties: false` under `WRAPPER_CLOSED_OBJECT_POLICY_001`.

### Category 5: Schema References ($ref)
- `FEAT_REF_LOCAL_COMPONENTS` (PRESERVE_VERBATIM): Intra-document JSON pointers (e.g. `#/components/schemas/...` or `#/definitions/...`) dereferenced deterministically into canonical contract; origin pointer tracked in lineage records.
- `FEAT_REF_EXTERNAL_FILE` (REJECT_AND_REPORT): References targeting relative or absolute external file paths fail closed to preserve hermetic blob SHA constraints.
- `FEAT_REF_REMOTE_URL` (REJECT_AND_REPORT): Network URL references fail closed to ensure offline reproducibility.

### Category 6: Composition and Polymorphism
- `FEAT_COMP_ALLOF` (PRESERVE_VERBATIM / EXPERIMENTAL): AllOf schema conjunctions preserved in contract tree.
- `FEAT_COMP_ONEOF` (REJECT_AND_REPORT): Exclusive polymorphism fails closed in general extractor unless covered by a formal Protocol Amendment (such as Amendment 003 for `SLOT_STRIPE_03`).
- `FEAT_COMP_ANYOF` (REJECT_AND_REPORT): Inclusive polymorphism fails closed due to evaluation ambiguity.
- `FEAT_COMP_NOT` (REJECT_AND_REPORT): Schema negation fails closed.
- `FEAT_COMP_DISCRIMINATOR` (REJECT_AND_REPORT): Runtime discriminator dispatch fails closed until polymorphic union engine is standardized.

### Category 7: Modifiers and Metadata
- `FEAT_MOD_NULLABLE` (PRESERVE_VERBATIM): OpenAPI 3.0 `nullable: true` preserved verbatim.
- `FEAT_MOD_READONLY` (PRESERVE_VERBATIM): Preserved; validators enforce exclusion from client tool calls.
- `FEAT_MOD_WRITEONLY` (PRESERVE_VERBATIM): Preserved; allowed in client tool calls, excluded from response verification.
- `FEAT_MOD_DEPRECATED` (PRESERVE_VERBATIM): Retained as field deprecation metadata.
- `FEAT_META_TITLE_DESC` (PRESERVE_VERBATIM): Title and description text copied verbatim.
- `FEAT_META_FORMAT` (PRESERVE_VERBATIM): Semantic format strings (e.g. `date-time`, `email`, `uri`) preserved verbatim.

### Category 8: Transport Surfaces
- `FEAT_SURF_PATH_PARAMS` (EXPLICIT_NORMALIZATION): Extracted from OpenAPI path parameters; encapsulated in canonical `path_parameters` object wrapper.
- `FEAT_SURF_BODY_JSON` (EXPLICIT_NORMALIZATION): Extracted from OpenAPI requestBody with `application/json`; encapsulated in canonical `body` object wrapper.
- `FEAT_SURF_BODY_FORM` (EXPLICIT_NORMALIZATION): Extracted from OpenAPI requestBody with `application/x-www-form-urlencoded`; encapsulated in canonical `body` wrapper with form encoding metadata.
- `FEAT_SURF_QUERY_PARAMS` (EXPLICIT_NORMALIZATION / EXPERIMENTAL): Encapsulated in canonical `query_parameters` wrapper.
- `FEAT_SURF_HEADER_PARAMS` (EXPLICIT_NORMALIZATION / EXPERIMENTAL): Encapsulated in canonical `header_parameters` wrapper.
- `FEAT_SURF_COOKIE_PARAMS` (REJECT_AND_REPORT): Cookie parameters fail closed.

### Category 9: Content Types
- `FEAT_CT_APPLICATION_JSON` (PRESERVE_VERBATIM): Standard JSON payload format; fully supported.
- `FEAT_CT_APPLICATION_FORM_URLENCODED` (PRESERVE_VERBATIM): URL-encoded form format; fully supported with deepObject serialization semantics.
- `FEAT_CT_MULTIPART_FORM_DATA` (REJECT_AND_REPORT): Multipart file uploads fail closed.
- `FEAT_CT_TEXT_PLAIN` (REJECT_AND_REPORT): Raw text payloads fail closed.
- `FEAT_CT_APPLICATION_OCTET_STREAM` (REJECT_AND_REPORT): Binary octet streams fail closed.

### Category 10: Form-Encoding Modifiers
- `FEAT_FORM_DEEP_OBJECT` (EXPLICIT_NORMALIZATION): Nested object form serialization (`key[sub]=val`) supported via contract `form_encoding` metadata.
- `FEAT_FORM_STYLE_FORM` (PRESERVE_VERBATIM): Standard exploded form parameters supported.
- `FEAT_FORM_ALLOW_RESERVED` (REJECT_AND_REPORT): Unescaped reserved characters fail closed.
- `FEAT_FORM_PIPE_DELIMITED` (REJECT_AND_REPORT): Pipe-delimited arrays fail closed.
- `FEAT_FORM_SPACE_DELIMITED` (REJECT_AND_REPORT): Space-delimited arrays fail closed.

### Category 11: Binary and Multipart Uploads
- `FEAT_BIN_FORMAT_BINARY` (REJECT_AND_REPORT): Binary file parameters fail closed.
- `FEAT_BIN_FORMAT_BYTE` (REJECT_AND_REPORT): Base64 encoded binary parameters fail closed.
- `FEAT_BIN_STREAM` (REJECT_AND_REPORT): Streaming payloads fail closed.

### Category 12: Recursion and Schema Cycles
- `FEAT_REC_CYCLIC_SCHEMA` (REJECT_AND_REPORT): Cyclical schema references fail closed via cycle detection during dereferencing.
- `FEAT_REC_BOUNDED_DEPTH` (PRESERVE_VERBATIM): Hierarchical schemas with depth <= 5 are fully supported.
- `FEAT_REC_EXCESSIVE_DEPTH` (REJECT_AND_REPORT): Schemas exceeding depth ceiling of 5 fail closed.

---

## 4. Enforcement and Fail-Closed Verification

1. All extraction pipelines must invoke the registry validation engine (`src/schema_feature_registry.py`) before and during schema traversal.
2. If an extraction encounters a feature marked `REJECT_AND_REPORT` or `UNSUPPORTED_FAIL_CLOSED`, the engine raises an explicit exception detailing the violation.
3. Automated unit and metamorphic tests verify that any attempt to extract unsupported features halts deterministically without writing canonical output.
