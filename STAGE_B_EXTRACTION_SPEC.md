# Stage B Canonical-Contract Extraction Specification
**Benchmark:** Contract Fragility & Schema Complexity Benchmark  
**Phase:** Stage B Empirical Expansion (Real-Source Canonical Contracts)  
**Document Type:** Formal Design & Protocol Specification (Zero Implementation Code)  
**Status:** DRAFT_SPECIFICATION_PENDING_REVIEW  
**Version:** 1.0.0  
**Effective Date:** October 2026  

---

## 1. Executive Purpose & Scope

This specification establishes the formal protocol for translating frozen, immutable raw API specifications (OpenAPI 3.0/3.1 and Model Context Protocol tool declarations) into canonical, benchmark-grade tool contracts for the Stage B benchmark.

### Non-Negotiable Operational Invariants
1. **Design Only**: This document defines extraction algorithms, rules, constraints, and audit requirements. No schema extraction, transformation code, mutations, mock executors, or model runs may be initiated until this specification is reviewed and approved.
2. **Raw Immutability**: All files in `data_stage_b/raw/**` are immutable. Extractors must read raw files in read-only binary mode and emit derived contracts to separate target directories (`data_stage_b/canonical/**`).
3. **Traceability**: Every extracted field must have an explicit, machine-verifiable mapping back to its source location in the raw file.
4. **Zero Lossy Guesswork**: Operations whose semantic interfaces cannot be extracted deterministically without subjective simplification must be logged, flagged, and submitted to human review or formally excluded.

---

## 2. Canonical Input Contract Model

Real-world API operations accept parameters across distinct HTTP and RPC surfaces:
- **Path Parameters**: URL path template substitutions (e.g. `{owner}`, `{repo}`).
- **Query Parameters**: URL query string parameters (e.g. `?page=1&per_page=50`).
- **Headers**: Operation-specific HTTP request headers (e.g. idempotency keys, target channel flags).
- **Request Body**: Structured JSON or form payload (`application/json`, `application/x-www-form-urlencoded`).
- **RPC Tool Arguments**: MCP tool arguments residing in a unified `inputSchema` object.

### 2.1 Unified Benchmark Tool Contract Structure
For an LLM agent participating in standard function/tool-calling, all input surfaces must combine into a single top-level JSON Schema object of `type: "object"`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "<CanonicalToolIdentifier>",
  "description": "<SynthesizedOperationDescription>",
  "type": "object",
  "properties": {
    "<SurfaceScopedOrFlatProperty>": { ... }
  },
  "required": [ ... ],
  "additionalProperties": false,
  "x-benchmark-metadata": {
    "candidate_source_id": "CAND-001",
    "source_cluster_id": "CLUSTER_GITHUB",
    "source_file_blob_sha": "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d",
    "operation_id": "issues/create",
    "source_spec_pointer": "#/paths/~1repos~1{owner}~1{repo}~1issues/post",
    "extraction_timestamp": "2026-10-09T18:00:00Z",
    "extractor_version": "1.0.0",
    "input_surfaces_extracted": ["path", "body"],
    "parameter_count": 8,
    "nesting_depth": 2
  }
}
```

### 2.2 Surface Namespacing & Collision Disambiguation Protocol
A major failure mode in tool extraction is parameter collision across input surfaces (e.g. an endpoint with path parameter `id` and request body field `id`).

#### Namespacing Rules
1. **Default Non-Colliding Mode (Flattened with Provenance Annotation)**:
   - If an operation has zero parameter name collisions across surfaces, parameters may be presented at the top level with an internal annotation: `"x-source-surface": "path" | "query" | "body" | "header"`.
2. **Explicit Colliding Mode (Prefix Namespacing)**:
   - When a parameter name appears in more than one surface (e.g., path `id` and body `id`), the extractor **must not** arbitrarily overwrite or drop either field.
   - The extractor must namespace colliding surfaces explicitly using dot-delimited tokens:
     - `path.<param_name>`
     - `query.<param_name>`
     - `body.<param_name>`
     - `header.<param_name>`
   - If namespacing is applied to any colliding parameter in an operation, all parameters from the colliding surfaces must follow the uniform prefix rule, and the decision must be logged in the transformation log.
3. **MCP Tool Contracts**:
   - MCP tools define a single unified `inputSchema` by design; parameters remain un-prefixed (`"x-source-surface": "mcp_argument"`).

### 2.3 Requiredness Preservation Across Surfaces
Requiredness across disparate surfaces must be rigorously aggregated into the canonical `required` array:
1. **Path Parameters**: Path parameters are inherently mandatory for HTTP dispatch. Every extracted path parameter **must** be placed in the canonical `required` list.
2. **Query Parameters**: A query parameter is added to `required` if and only if the raw OpenAPI parameter definition has `required: true`.
3. **Request Body Fields**:
   - If the request body itself is marked `required: false` in OpenAPI, then body properties are optional at the tool level unless the body is provided. In the unified contract, if the overall body is optional, body sub-properties marked `required` within the body schema retain their required status only conditional on tool invocation intent.
   - For standard creation/action tools where the body is mandatory (`requestBody.required: true`), all properties listed in the body schema's `required` array are merged directly into the top-level `required` list.
4. **Deduplication**: The top-level `required` array must be sorted lexicographically and contain unique elements.

---

## 3. OpenAPI 3.0 / 3.1 Extraction Engine Protocol

### 3.1 JSON Pointer Navigation
All OpenAPI extractions must begin with an exact RFC 6901 JSON Pointer navigation against the raw, validated JSON or YAML document.
- Root navigation tokens: `#/paths/~1<escaped_path>/<http_method>`.
- Token unescaping: `~1` -> `/`, `~0` -> `~`.
- Path-level parameters (`#/paths/~1<escaped_path>/parameters`) must be inherited by the operation unless explicitly overridden at the operation level.

### 3.2 `$ref` Resolution Engine
OpenAPI schemas make heavy use of internal document references (`#/components/schemas/...`).

#### Reference Resolution Rules
1. **Internal-Only Bound**: In Stage B, only intra-document references (`#/...`) are valid. External HTTP references are strictly prohibited to ensure local reproducibility.
2. **Pointer Stack & Cycle Detection**:
   - The resolver must maintain a `visited_pointer_stack: Set[str]`.
   - When resolving `$ref: "#/components/schemas/Node"`, if `#/components/schemas/Node` is already in `visited_pointer_stack`, recursion is halted immediately.
   - The recursive field is terminated with:
     ```json
     {
       "type": "object",
       "description": "[Cyclic reference terminated at depth K]",
       "x-cyclic-ref-target": "#/components/schemas/Node"
     }
     ```
3. **Maximum Nesting Depth Bound**:
   - The resolver must enforce a strict `MAX_RECURSION_DEPTH = 5`.
   - Any property subtree exceeding depth 5 must be pruned to a generic container (`type: "object"` or `type: "string"`) and logged in the transformation log.
4. **Description and Sibling Preservation**:
   - In OpenAPI 3.1, sibling fields beside `$ref` are valid. In OpenAPI 3.0, sibling fields beside `$ref` are ignored by spec.
   - The Stage B extractor must preserve sibling `description` or `title` fields when present, merging them over the resolved component description.

### 3.3 OpenAPI 3.0 vs 3.1 Compatibility Handling
- **Nullability**:
  - OpenAPI 3.0: `type: "string"`, `nullable: true`.
  - OpenAPI 3.1 / JSON Schema 2020-12: `type: ["string", "null"]` or `anyOf: [{"type": "string"}, {"type": "null"}]`.
  - Canonical Target: Standardize to `anyOf: [{"type": "string"}, {"type": "null"}]` or canonical JSON Schema `type: ["string", "null"]` depending on target LLM provider tool parser constraints, with exact conversion logged.
- **ExclusiveMinimum / ExclusiveMaximum**:
  - OpenAPI 3.0: `minimum: 0`, `exclusiveMinimum: true`.
  - OpenAPI 3.1: `exclusiveMinimum: 0`.
  - Canonical Target: Standardize to OpenAPI 3.1 numeric bounds.

### 3.4 Compositional Operators (`allOf`, `oneOf`, `anyOf`)
1. **`allOf` (Intersection / Extension)**:
   - Must be flattened into a single merged object.
   - Properties from all sub-schemas are combined.
   - `required` arrays are unioned.
   - Conflicting property definitions must fail extraction and trigger manual review.
2. **`oneOf` / `anyOf` (Polymorphic Choice)**:
   - For parameter payloads where `oneOf` specifies primitive alternatives (e.g. `image` as string slug vs integer ID), retain the union as `oneOf: [{"type": "string"}, {"type": "integer"}]`.
   - For large polymorphic arrays (e.g. Slack Block Kit or LINE Flex Messages containing 15+ sub-types):
     - **Controlled Pruning Rule**: Retain the 2-3 most common core variants (e.g., `text` and `image`), prune secondary variants, and log the pruning in the transformation log.
     - Never silently drop an entire polymorphic field without documentation.
3. **Discriminators**:
   - If an explicit `discriminator: { propertyName: "type", mapping: ... }` exists, preserve the discriminator property in the object schema as a required enum.

### 3.5 Structural Constraints & Pruning Bounds
- **Enums**: All enum values must be preserved verbatim. Empty string enum values `""` must be flagged.
- **AdditionalProperties**: Set `additionalProperties: false` on canonical contracts to enforce strict structural adherence during model evaluation.
- **Default Values**: Preserve `default` values in the metadata and schema definition.

### 3.6 Exclusion Criteria for Non-Representable Operations
An operation must be marked **`EXCLUDE_PENDING`** and excluded from canonical benchmark admission if:
1. It relies on unresolvable external URI `$ref` dependencies.
2. It accepts unstructured binary streaming (`application/octet-stream`, `multipart/form-data` with dynamic file boundaries).
3. Resolving its request body yields exceeding 60 top-level properties or a prompt footprint > 2,000 tokens in isolation.
4. Its execution requires state transitions that cannot be simulated deterministically in a local mock.

---

## 4. Model Context Protocol (MCP) Static Extraction Protocol

### 4.1 Architecture & Scope
MCP tool declarations in `modelcontextprotocol/servers` are defined directly in programming language ASTs rather than OpenAPI JSON/YAML files.
- `CAND-009` (SQLite): Python (`server.py`) using `mcp.server.fastmcp` or `types.Tool(name=..., inputSchema=...)`.
- `CAND-010` (GitHub): TypeScript (`index.ts`) using Zod schemas (`z.object({...})`) passed to `server.setRequestHandler(ListToolsRequestSchema, ...)`.

### 4.2 Deterministic Extraction Methodology
1. **Python MCP Server (`server.py`)**:
   - Use Python's standard `ast` module.
   - Parse `server.py` into an Abstract Syntax Tree.
   - Locate function definitions or decorators registering tools (e.g., `list_tools` returning a list of `types.Tool` constructors).
   - Extract:
     - `name`: string literal.
     - `description`: string literal.
     - `inputSchema`: dictionary literal defining `type`, `properties`, and `required`.
   - If `inputSchema` is generated via dynamic runtime reflection (e.g. `pydantic.create_model(...)` without static literals), reject the tool as non-static.
2. **TypeScript MCP Server (`index.ts` / `schemas.ts`)**:
   - Parse TypeScript using a static AST parser (e.g. TypeScript Compiler API or static regex-anchored Zod parser).
   - Locate tool registration blocks matching `name: "<tool_name>"`.
   - Extract the corresponding Zod schema or JSON Schema definition.
   - Map Zod primitives to JSON Schema:
     - `z.string()` -> `{"type": "string"}`
     - `z.number().int()` -> `{"type": "integer"}`
     - `z.boolean()` -> `{"type": "boolean"}`
     - `z.array(...)` -> `{"type": "array", "items": ...}`
     - `z.enum([...])` -> `{"type": "string", "enum": [...]}`
     - `.optional()` -> omitted from `required` array.
     - `.describe("...")` -> `description`.

### 4.3 Static Verification Gate
If an MCP tool's parameter types or descriptions cannot be resolved solely from the static AST of the pinned source file without launching node or python runtimes, it must be rejected.

---

## 5. Fidelity, Provenance & Audit Logging

### 5.1 Machine-Readable Transformation Log Protocol
Every extraction action must append a JSON record to `results_stage_b/extraction_transformation_log.jsonl`.

```json
{
  "timestamp": "2026-10-09T18:00:00Z",
  "candidate_source_id": "CAND-001",
  "operation_id": "issues/create",
  "source_file_blob_sha": "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d",
  "source_spec_pointer": "#/paths/~1repos~1{owner}~1{repo}~1issues/post",
  "transformation_category": "MERGE_INPUT_SURFACES",
  "action": "SURFACE_MERGED",
  "details": {
    "surfaces_combined": ["path", "body"],
    "path_parameters_added": ["owner", "repo"],
    "body_parameters_added": ["title", "body", "assignee", "milestone", "labels", "assignees"],
    "namespacing_applied": false,
    "pruning_applied": false
  },
  "canonical_schema_sha256": "4b8f..."
}
```

### 5.2 Transformation Categories
- `MERGE_INPUT_SURFACES`: Path, query, and body combined into top-level tool contract.
- `RESOLVE_REF`: Component reference expanded inline.
- `CYCLE_TERMINATED`: Recursive pointer terminated.
- `PRUNE_POLYMORPHISM`: Complex union pruned to core representative variants.
- `STANDARDIZE_NULLABLE`: OpenAPI 3.0 `nullable` translated to standard union.
- `COLLISION_NAMESPACED`: Parameter collision disambiguated with surface prefix.

---

## 6. Verification & Validation Testing Framework

Before any derived canonical contract is admitted into the Stage B benchmark dataset, it must pass an automated four-stage verification gate:

1. **Meta-Schema Conformance**:
   - Every canonical schema must validate against the standard JSON Schema Draft-07 meta-schema via `jsonschema.Draft7Validator.check_schema()`.
2. **Bijective Field Traceability**:
   - For every property in the canonical contract, the test suite must assert that the property exists in the raw source specification at the mapped pointer.
3. **Constraint Invariant Preservation**:
   - Asserts that all properties marked `required` in the raw source are present in the canonical `required` list.
   - Asserts that all enum values match the raw source verbatim.
4. **Stratified Blinded Human Validation Protocol**:
   - Any operation involving `PRUNE_POLYMORPHISM` or `CYCLE_TERMINATED` must be flagged for blinded review by two annotators, who must independently rate semantic equivalence on a 1–5 scale. Operations scoring < 4.0 are discarded.

---

## 7. Stage B Dataset Rules

1. **Cohort Decoupling**:
   - Synthetic schemas ($N=20$) and canonical real-source schemas ($N=30$) must be tagged with explicit metadata (`schema_origin: "SYNTHETIC"` vs `schema_origin: "REAL_WORLD"`).
   - Benchmark reporting must present disaggregated performance across synthetic vs real cohorts, in addition to pooled scores.
2. **Mutation Freeze Gate**:
   - No Task 1 (parameter distortion), Task 2 (distractor injection), or Task 4 (abstention) mutations may be generated for real-source contracts until all 30 canonical contracts pass automated extraction validation and manual review.
3. **Execution Freeze Gate**:
   - No model calls may be initiated until the canonical dataset, mutations, mock simulators, and analysis plans are committed, frozen, and audited.

---

## 8. Operation Extraction Risk & Decision Matrix (30 Selected Operations)

Each of the 30 candidate operations is categorized into an anticipated extraction risk tier:
- **LOW**: Flat or standard schema; clean path/body boundaries; direct 1:1 mapping.
- **MEDIUM**: Multiple references, moderate nesting, arrays, or wide parameter lists.
- **HIGH**: Deep recursion, heavy polymorphism (`oneOf`), or complex polymorphic array elements.
- **EXCLUDE_PENDING**: Fails static representation; requires subjective truncation.

| Cluster ID | Source Project | Operation ID | HTTP / RPC | Input Surfaces | Nesting Depth | Anticipated Risk | Key Technical Challenges & Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CLUSTER_GITHUB` | GitHub | `repos/create-commit-status` | POST | Path + Body | 1 | **LOW** | Clean enum `state`; path parameters `owner`, `repo`, `sha` merged cleanly. |
| `CLUSTER_GITHUB` | GitHub | `issues/create` | POST | Path + Body | 2 | **LOW** | Path parameters `owner`, `repo` merged with string/array body. |
| `CLUSTER_GITHUB` | GitHub | `repos/create-for-authenticated-user` | POST | Body only | 1 | **MEDIUM** | Wide optionality (16 parameters); requires preserving default boolean semantics. |
| `CLUSTER_STRIPE` | Stripe | `PostRefunds` | POST | Body only | 2 | **LOW** | Clean `$ref` resolution to standard refund parameters and enum. |
| `CLUSTER_STRIPE` | Stripe | `PostCustomers` | POST | Body only | 3 | **MEDIUM** | Nested `address` and `shipping` objects; requires multi-level `$ref` resolution. |
| `CLUSTER_STRIPE` | Stripe | `PostPaymentIntents` | POST | Body only | 2 | **MEDIUM** | Resolving `automatic_payment_methods` and required currency/amount constraints. |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean | `floating_ips_create` | POST | Body only | 1 | **LOW** | Ultra-flat `$ref` resolution (`droplet_id`, `region`). |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean | `domains_create` | POST | Body only | 1 | **LOW** | Flat 2-parameter resource constructor. |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean | `droplets_create` | POST | Body only | 2 | **MEDIUM** | `image` parameter uses `oneOf` (slug string vs integer ID); resolve as primitive union. |
| `CLUSTER_TWILIO` | Twilio | `UpdateAccount` | POST | Path + Body | 1 | **LOW** | Path parameter `Sid` merged with `FriendlyName` and `Status` enum. |
| `CLUSTER_TWILIO` | Twilio | `CreateMessage` | POST | Path + Body | 2 | **LOW** | Path parameter `AccountSid` merged with string body and `MediaUrl` array. |
| `CLUSTER_TWILIO` | Twilio | `CreateCall` | POST | Path + Body | 1 | **MEDIUM** | Wide parameter list (9 properties); preserve PascalCase parameter identifiers. |
| `CLUSTER_BOX` | Box | `post_folders` | POST | Body only | 2 | **LOW** | Clean parent pointer object (`parent.id`). |
| `CLUSTER_BOX` | Box | `post_collaborations` | POST | Body only | 2 | **MEDIUM** | Multi-entity pointer (`item`, `accessible_by`, `role` enum); clean `$ref` trees. |
| `CLUSTER_BOX` | Box | `post_users` | POST | Body only | 1 | **MEDIUM** | 10 properties with enterprise role and status enums. |
| `CLUSTER_SLACK` | Slack | `conversations.create` | POST | Body only | 1 | **LOW** | Flat 2-parameter channel constructor (`name`, `is_private`). |
| `CLUSTER_SLACK` | Slack | `users.profile.set` | POST | Body only | 2 | **MEDIUM** | Nested `profile` key-value collection; resolve sub-object properties. |
| `CLUSTER_SLACK` | Slack | `chat.postMessage` | POST | Body only | 4 | **HIGH** | `blocks` parameter contains massive polymorphic union; prune to core blocks (`section`, `header`, `divider`) and log rule. |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | `read_query` | RPC | Tool Schema | 1 | **LOW** | Static AST extraction of `query` parameter from Python dataclass. |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | `describe_table` | RPC | Tool Schema | 1 | **LOW** | Static AST extraction of `table_name` parameter. |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | `write_query` | RPC | Tool Schema | 1 | **LOW** | Static AST extraction of `query` parameter. |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | `search_repositories` | RPC | Tool Schema | 1 | **LOW** | Static extraction of Zod schema (`query`, `page`, `perPage`). |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | `create_issue` | RPC | Tool Schema | 2 | **MEDIUM** | Static extraction of string arrays (`assignees`, `labels`) from Zod definition. |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | `create_or_update_file` | RPC | Tool Schema | 1 | **MEDIUM** | Multiple required string parameters (`owner`, `repo`, `path`, `content`, `message`). |
| `CLUSTER_CHATWOOT` | Chatwoot | `create-an-account-user` | POST | Path + Body | 1 | **LOW** | Path parameter `account_id` merged with `user_id` and `role` enum. |
| `CLUSTER_CHATWOOT` | Chatwoot | `create-a-contact` | POST | Path + Body | 2 | **MEDIUM** | Path parameter `inbox_identifier` merged with contact properties and `custom_attributes`. |
| `CLUSTER_CHATWOOT` | Chatwoot | `create-a-conversation` | POST | Path + Body | 2 | **LOW** | Path parameters `inbox_identifier`, `contact_identifier` merged with body. |
| `CLUSTER_LINE` | LINE | `setWebhookEndpoint` | PUT | Body only | 1 | **LOW** | Flat single-URL property constructor. |
| `CLUSTER_LINE` | LINE | `replyMessage` | POST | Body only | 3 | **MEDIUM** | `messages` array contains polymorphic objects; resolve discriminated union by `type`. |
| `CLUSTER_LINE` | LINE | `pushMessage` | POST | Body only | 3 | **HIGH** | `messages` array with broad polymorphic choices; prune to standard `text`/`image` types and log rule. |

---

## 9. Conclusion & Next Steps

This specification establishes an immutable protocol for Stage B canonical extraction. Once reviewed and approved:
1. An automated, read-only extractor script following Section 2 and Section 3 will be implemented.
2. Extracted canonical contracts will be saved to `data_stage_b/canonical/` alongside exhaustive machine-readable transformation logs in `results_stage_b/extraction_transformation_log.jsonl`.
3. The four-stage verification test suite (Section 6) will validate all derived contracts against raw sources before any mutation generation or model benchmarking is permitted.
