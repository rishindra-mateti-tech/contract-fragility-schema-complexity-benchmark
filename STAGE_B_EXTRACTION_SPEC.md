# Stage B Canonical-Contract Extraction Specification
**Benchmark:** Contract Fragility & Schema Complexity Benchmark  
**Phase:** Stage B Empirical Expansion (Real-Source Canonical Contracts)  
**Document Type:** Formal Design & Protocol Specification (Zero Implementation Code)  
**Status:** REVISED_SPECIFICATION_PENDING_REVIEW  
**Version:** 1.1.0  
**Effective Date:** October 2026  

---

## 1. Executive Purpose & Scope

This specification establishes the formal protocol for translating frozen, immutable raw API specifications (OpenAPI 3.0/3.1 and Model Context Protocol tool declarations) into canonical, benchmark-grade tool contracts for the Stage B benchmark.

### Non-Negotiable Operational Invariants
1. **Design Only**: This document defines extraction algorithms, rules, constraints, and audit requirements. No schema extraction, transformation code, mutations, mock executors, or model runs may be initiated until this specification is reviewed and approved.
2. **Raw Immutability**: All files in `data_stage_b/raw/**` are immutable. Extractors must read raw files in read-only binary mode and emit derived contracts to separate target directories (`data_stage_b/canonical/**`).
3. **Traceability**: Every extracted field must have an explicit, machine-verifiable field-lineage record mapping back to its exact source location in the raw file.
4. **Zero Lossy Guesswork in Canonical Cohort**: The canonical real-world corpus (`CANONICAL_FAITHFUL`) strictly forbids lossy simplification, dropping of polymorphic variants, or heuristic truncation. Any operation whose full interface cannot be extracted deterministically without lossy pruning must be classified as `EXCLUDE_PENDING`.
5. **Stage A Isolation**: Stage A schemas, results, manifests, and scripts remain 100% frozen and untouched.

---

## 2. Canonical Input Contract Model

### 2.1 Uniform HTTP Surface Transport Representation
Real-world OpenAPI operations accept inputs across multiple surfaces: path templates, query strings, request headers, and request bodies. Rather than applying conditional flattening or collision-dependent prefixes, Stage B enforces **one uniform HTTP contract representation** for every OpenAPI operation:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "<CanonicalToolIdentifier>",
  "description": "<SynthesizedOperationDescription>",
  "type": "object",
  "properties": {
    "path": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ],
      "additionalProperties": false
    },
    "query": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ],
      "additionalProperties": false
    },
    "header": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ],
      "additionalProperties": false
    },
    "body": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ],
      "additionalProperties": false
    }
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
    "extractor_version": "1.1.0",
    "admission_decision": "CANONICAL_FAITHFUL",
    "source_structural_metrics": {
      "raw_parameter_count": 8,
      "raw_nesting_depth": 2,
      "raw_optional_ratio": 0.75,
      "raw_enum_density": 0.0
    },
    "wrapped_contract_structural_metrics": {
      "total_property_count": 10,
      "wrapped_nesting_depth": 3,
      "surface_containers_present": ["path", "body"],
      "surface_containers_required": ["path", "body"]
    }
  }
}
```

> **Important Transport Distinction:**  
> The 4-surface wrapper (`path`, `query`, `header`, `body`) is a **benchmark transport representation** designed to simulate real-world API call construction in tool calling. It is **not** an assertion that the upstream API specification itself was nested in this manner. To prevent empirical confounding, the benchmark records both `source_structural_metrics` and `wrapped_contract_structural_metrics`.

### 2.2 Deterministic Surface Behavior Rules
1. **Absent Surfaces**:
   - If an operation defines zero parameters for a given surface (e.g. no query parameters), that surface container is represented with empty properties:
     ```json
     "query": {
       "type": "object",
       "properties": {},
       "additionalProperties": false
     }
     ```
   - An absent surface container is **never** added to the top-level `required` array.
2. **Surface Container Requiredness**:
   - The top-level `required` array contains a surface name (`"path"`, `"query"`, `"header"`, or `"body"`) if and only if that surface contains at least one parameter marked `required` or if the request body itself is marked `required: true` in OpenAPI.
3. **Surface-Internal Requiredness**:
   - Within each surface container, source requiredness is preserved verbatim:
     - Path parameters: inherently mandatory; all path parameters appear in `path.required`.
     - Query parameters: added to `query.required` if and only if raw `required: true`.
     - Header parameters: added to `header.required` if and only if raw `required: true`.
     - Body properties: added to `body.required` if listed in the body schema's `required` array.
4. **Form Bodies**:
   - Form-encoded endpoints (`application/x-www-form-urlencoded` or `multipart/form-data`) map their parameter properties into the `"body"` container, with an explicit metadata annotation `"x-content-type": "application/x-www-form-urlencoded"`.
5. **Parameter Descriptions**:
   - Parameter descriptions are preserved verbatim at the property level.
6. **Property Ordering**:
   - Within each surface container and in every `required` array, property keys must be sorted **lexicographically** (`A-Z`).

### 2.3 RPC Tool Contract Representation (MCP Tools)
Model Context Protocol tools do not possess HTTP transport surfaces; they execute over JSON-RPC with a unified `inputSchema`.
To preserve native protocol semantics without synthesizing fictitious HTTP surfaces, MCP tools are represented via an `"arguments"` container:
```json
{
  "title": "<ToolName>",
  "description": "<ToolDescription>",
  "type": "object",
  "properties": {
    "arguments": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ],
      "additionalProperties": false
    }
  },
  "required": ["arguments"],
  "additionalProperties": false,
  "x-benchmark-metadata": { ... }
}
```

---

## 3. OpenAPI 3.0 / 3.1 Extraction Engine Protocol

### 3.1 JSON Pointer Navigation
- Navigation starts with RFC 6901 pointer resolution against the raw JSON/YAML file: `#/paths/~1<escaped_path>/<http_method>`.
- Path-level shared parameters (`#/paths/~1<escaped_path>/parameters`) are inherited deterministically into the operation unless explicitly overridden at the operation level by name and surface location.

### 3.2 Component `$ref` Resolution Engine
1. **Intra-Document Only**: References must reside within the same frozen document (`#/...`). External URI references are forbidden.
2. **Cycle Detection & Visited Pointer Stack**:
   - The engine maintains a `visited_pointer_stack: Set[str]`.
   - Circular `$ref` chains halt immediately. Any cyclic pointer detected is terminated with an explicit reference anchor and submitted to manual review.
3. **Recursion Limit**:
   - Maximum recursion depth is strictly bounded to `MAX_RECURSION_DEPTH = 5`.
4. **Sibling Field Merging**:
   - In OpenAPI 3.1, sibling fields alongside `$ref` are merged (with the sibling `description` overriding the referenced description). In OpenAPI 3.0, `$ref` resolution dereferences the target component first, preserving top-level parameter descriptions where specified.

### 3.3 Compositional Operators (`allOf`, `oneOf`, `anyOf`)
1. **`allOf` (Merging & Conflict Invariant)**:
   - Sub-schemas inside `allOf` are deterministically merged into a single object.
   - Properties are combined; required lists are unioned.
   - **Conflict Rule:** If any two sub-schemas define the same property name with conflicting types, constraints, or formats, the extractor **must not** guess, override, or silently drop either definition. The operation **must be marked `EXCLUDE_PENDING`**.
2. **`oneOf` / `anyOf` (Primitive Choice Only)**:
   - Permitted in the canonical cohort only when representing primitive type alternatives (e.g., `oneOf: [{"type": "string"}, {"type": "integer"}]`).
3. **Zero Pruning Rule for Canonical Cohort**:
   - **No controlled pruning** of complex polymorphic unions is permitted in the canonical real-world cohort.
   - If an operation requires dropping polymorphic variants (such as Slack Block Kit or LINE Flex Messages) to fit context windows, it is strictly disqualified from `CANONICAL_FAITHFUL` and categorized as `EXCLUDE_PENDING`.

### 3.4 OpenAPI 3.0 vs 3.1 Normalization
- **Nullable**: OpenAPI 3.0 `nullable: true` is translated to standard JSON Schema Draft-07 type union: `anyOf: [{"type": T}, {"type": "null"}]`.
- **Numeric Bounds**: OpenAPI 3.0 boolean `exclusiveMinimum: true` is normalized to Draft-07 numeric value.

---

## 4. Model Context Protocol (MCP) AST Extraction Protocol

### 4.1 AST-Only Requirement
MCP extraction must be **100% AST-based**. Textual regex matching, string splitting, or heuristics are **strictly prohibited** as primary extraction mechanisms. If static AST resolution cannot extract a tool's full contract, the tool must be excluded.

### 4.2 Python MCP Servers (`CAND-009`)
- Source: `src/sqlite/src/mcp_server_sqlite/server.py`
- Parser: Python standard library `ast` module.
- Method:
  1. Parse module into AST.
  2. Inspect function definitions and decorators registering tools (`@server.list_tools()`).
  3. Extract AST Call nodes instantiating `types.Tool(...)`.
  4. Evaluate string literals for `name`, `description`, and dictionary AST literals for `inputSchema`.
  5. Record exact AST node locations (`start_line`, `start_col`, `end_line`, `end_col`, `byte_offset`).

### 4.3 TypeScript MCP Servers (`CAND-010`)
- Source: `src/github/index.ts`
- Parser: **TypeScript Compiler API** (`ts.createSourceFile` or `ts-morph`).
- Method:
  1. Parse `index.ts` into a complete TypeScript Abstract Syntax Tree.
  2. Traverse AST to locate `server.setRequestHandler(ListToolsRequestSchema, ...)` and tool array returns.
  3. Extract tool name literals, description literals, and associated Zod object schemas (`z.object({...})`).
  4. Traverse Zod call chains AST:
     - `z.string()` -> `{"type": "string"}`
     - `z.number().int()` -> `{"type": "integer"}`
     - `z.array(T)` -> `{"type": "array", "items": ...}`
     - `z.enum([...])` -> `{"type": "string", "enum": [...]}`
     - `.optional()` -> omitted from `required`
     - `.describe("...")` -> `description`
  5. Record exact AST source spans (`start_line`, `start_col`, `end_line`, `end_col`, `byte_offset`).
  6. If dynamic reflection, runtime evaluation, or external unresolvable imports are encountered, classify as `EXCLUDE_PENDING`.

---

## 5. Deterministic Field-Lineage Traceability

The previous concept of "Bijective Field Traceability" is superseded by **Deterministic Field-Lineage Traceability**. 

### 5.1 Machine-Readable Lineage Record Specification
Every single property in every derived canonical contract must have a machine-readable entry in `results_stage_b/canonical_field_lineage.jsonl`:

```json
{
  "canonical_schema_sha256": "4b8f3e...",
  "canonical_json_pointer": "/properties/body/properties/title",
  "candidate_source_id": "CAND-001",
  "source_cluster_id": "CLUSTER_GITHUB",
  "raw_source_blob_sha": "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d",
  "raw_source_pointers": [
    "#/paths/~1repos~1{owner}~1{repo}~1issues/post/requestBody/content/application~1json/schema/properties/title"
  ],
  "source_ast_span": {
    "start_line": 14205,
    "end_line": 14208,
    "byte_offset": 521402
  },
  "transformation_category": "SURFACE_WRAPPING",
  "is_reversible": true,
  "extractor_version": "1.1.0",
  "extraction_timestamp": "2026-10-09T18:00:00Z",
  "reviewer_decision": "APPROVED"
}
```

### 5.2 Transformation Categories
- `IDENTITY`: Field preserved verbatim from source to destination.
- `SURFACE_WRAPPING`: Parameter placed into `path`, `query`, `header`, or `body` container.
- `REF_EXPANSION`: `$ref` component expanded inline.
- `ALLOF_MERGE`: Field combined via `allOf` composition.
- `NULLABLE_STANDARDIZATION`: Converted from OpenAPI 3.0 `nullable` to Draft-07 union.
- `AST_TYPE_MAPPING`: Converted from static TypeScript Zod AST to JSON Schema.

---

## 6. Comprehensive Validation & Manual Review Protocol

### 6.1 Automated Verification Suite
Derived contracts must pass an automated five-stage test suite:
1. **JSON Schema Draft-07 Meta-Validation**: Validated via `jsonschema.Draft7Validator.check_schema()`.
2. **Deterministic Field-Lineage Assertions**: Every derived property pointer must exist in `canonical_field_lineage.jsonl` with verified raw source pointers.
3. **Requiredness Preservation Invariant**: Every field marked required in a raw source surface must be required in that surface's derived container.
4. **Enum Verbatim Identity**: All enum arrays must match upstream bytes verbatim (same set, types, and values).
5. **No Undocumented Additions**: Zero synthetic properties may appear without an explicit lineage record.

### 6.2 Mandatory Manual Review Gate
Automated tests are necessary but not sufficient. **Manual review is mandatory** for any operation involving:
- `$ref` expansion across components
- `allOf` property merging
- `nullable` type conversion
- Surface wrapping or container placement
- Any non-identity transformation

Reviewers must inspect the lineage record, compare with raw source bytes, and record their explicit signed decision (`APPROVED` or `REJECTED`).

---

## 7. Cohort Isolation & Dataset Rules

### 7.1 Operation-Level Admission Decisions
Every operation in the benchmark catalog receives one of three immutable admission decisions:
1. **`CANONICAL_FAITHFUL`**: Full, faithful representation of the upstream API contract without lossy pruning, subjective simplification, or dropped variants. Eligible for main Stage B benchmark evaluation and causal claims.
2. **`LOSSY_DERIVED_EXPLORATORY`**: Operations requiring heuristic pruning or simplification to evaluate. Strictly quarantined in a separate cohort.
3. **`EXCLUDE_PENDING`**: Operations that cannot be extracted faithfully and are disqualified from canonical evaluation.

### 7.2 Strict Cohort Isolation Rules
- **No Pooling**: `LOSSY_DERIVED_EXPLORATORY` data must **never** be pooled with `CANONICAL_REAL_WORLD` or `SYNTHETIC` results in primary paper tables, causal effect estimates, or headline metrics.
- **Protocol Amendment Gate**: No operation may enter `LOSSY_DERIVED_EXPLORATORY` without a separately drafted, reviewed, and frozen protocol amendment.
- **Mutation & Run Freeze Gates**:
  - No Task 1/2 mutations may be generated until all canonical operations pass extraction validation and manual review.
  - Zero model runs may occur until the complete dataset, lineage records, and manifest are frozen.

---

## 8. Operation Extraction Risk & Decision Matrix (30 Selected Operations)

### Status Summary
- **`CANONICAL_FAITHFUL`**: **28 operations** (Approved for canonical extraction without lossy pruning).
- **`EXCLUDE_PENDING`**: **2 operations** (Disqualified from canonical cohort due to wide polymorphic unions).
- **Pending Replacement Operations**: **2 operations** (1 for Slack CRM cluster, 1 for LINE Communications cluster, to be admitted via official source-admission amendment).

### Complete 30-Operation Decision Table

| Cluster ID | Source Project | Operation ID | HTTP / RPC | Input Surfaces | Nesting Depth | Admission Decision | Extraction Risk | Technical Rationale & Exclusion Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CLUSTER_GITHUB` | GitHub | `repos/create-commit-status` | POST | Path + Body | 1 | **CANONICAL_FAITHFUL** | LOW | Flat status payload; path params `owner`, `repo`, `sha` wrapped in `path`; body wrapped in `body`. |
| `CLUSTER_GITHUB` | GitHub | `issues/create` | POST | Path + Body | 2 | **CANONICAL_FAITHFUL** | LOW | Path params `owner`, `repo` wrapped in `path`; body wrapped in `body`; string arrays preserved. |
| `CLUSTER_GITHUB` | GitHub | `repos/create-for-authenticated-user` | POST | Body only | 1 | **CANONICAL_FAITHFUL** | MEDIUM | 16 body properties wrapped in `body`; boolean defaults preserved verbatim. |
| `CLUSTER_STRIPE` | Stripe | `PostRefunds` | POST | Body only | 2 | **CANONICAL_FAITHFUL** | LOW | Clean `$ref` resolution to standard refund parameters and enum wrapped in `body`. |
| `CLUSTER_STRIPE` | Stripe | `PostCustomers` | POST | Body only | 3 | **CANONICAL_FAITHFUL** | MEDIUM | Multi-level `$ref` resolution for `address` and `shipping` objects inside `body`. |
| `CLUSTER_STRIPE` | Stripe | `PostPaymentIntents` | POST | Body only | 2 | **CANONICAL_FAITHFUL** | MEDIUM | Resolving `automatic_payment_methods` and required bounds inside `body`. |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean | `floating_ips_create` | POST | Body only | 1 | **CANONICAL_FAITHFUL** | LOW | Ultra-flat `$ref` resolution (`droplet_id`, `region`) inside `body`. |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean | `domains_create` | POST | Body only | 1 | **CANONICAL_FAITHFUL** | LOW | Flat 2-parameter resource constructor inside `body`. |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean | `droplets_create` | POST | Body only | 2 | **CANONICAL_FAITHFUL** | MEDIUM | `image` parameter uses primitive `oneOf` (slug string vs integer ID); wrapped in `body`. |
| `CLUSTER_TWILIO` | Twilio | `UpdateAccount` | POST | Path + Body | 1 | **CANONICAL_FAITHFUL** | LOW | Path param `Sid` wrapped in `path`; form body wrapped in `body` with `x-content-type`. |
| `CLUSTER_TWILIO` | Twilio | `CreateMessage` | POST | Path + Body | 2 | **CANONICAL_FAITHFUL** | LOW | Path param `AccountSid` in `path`; form params in `body`; `MediaUrl` array preserved. |
| `CLUSTER_TWILIO` | Twilio | `CreateCall` | POST | Path + Body | 1 | **CANONICAL_FAITHFUL** | MEDIUM | 9 form parameters in `body`; PascalCase identifiers preserved verbatim. |
| `CLUSTER_BOX` | Box | `post_folders` | POST | Body only | 2 | **CANONICAL_FAITHFUL** | LOW | Clean parent pointer object (`parent.id`) inside `body`. |
| `CLUSTER_BOX` | Box | `post_collaborations` | POST | Body only | 2 | **CANONICAL_FAITHFUL** | MEDIUM | Multi-entity pointer (`item`, `accessible_by`, `role` enum) inside `body`. |
| `CLUSTER_BOX` | Box | `post_users` | POST | Body only | 1 | **CANONICAL_FAITHFUL** | MEDIUM | 10 properties with enterprise role and status enums inside `body`. |
| `CLUSTER_SLACK` | Slack | `conversations.create` | POST | Body only | 1 | **CANONICAL_FAITHFUL** | LOW | Flat 2-parameter channel constructor inside `body`. |
| `CLUSTER_SLACK` | Slack | `users.profile.set` | POST | Body only | 2 | **CANONICAL_FAITHFUL** | MEDIUM | Nested `profile` key-value collection inside `body`. |
| `CLUSTER_SLACK` | Slack | `chat.postMessage` | POST | Body only | 4 | **EXCLUDE_PENDING** | HIGH | **DISQUALIFIED FROM CANONICAL COHORT.** `blocks` requires lossy pruning of polymorphic Block Kit union. |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | `read_query` | RPC | Tool Schema | 1 | **CANONICAL_FAITHFUL** | LOW | Static AST extraction of `query` parameter from Python AST node; wrapped in `arguments`. |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | `describe_table` | RPC | Tool Schema | 1 | **CANONICAL_FAITHFUL** | LOW | Static AST extraction of `table_name` parameter; wrapped in `arguments`. |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | `write_query` | RPC | Tool Schema | 1 | **CANONICAL_FAITHFUL** | LOW | Static AST extraction of `query` parameter; wrapped in `arguments`. |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | `search_repositories` | RPC | Tool Schema | 1 | **CANONICAL_FAITHFUL** | LOW | Static TypeScript Compiler AST extraction of Zod schema; wrapped in `arguments`. |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | `create_issue` | RPC | Tool Schema | 2 | **CANONICAL_FAITHFUL** | MEDIUM | Static TypeScript AST extraction of arrays (`assignees`, `labels`); wrapped in `arguments`. |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | `create_or_update_file` | RPC | Tool Schema | 1 | **CANONICAL_FAITHFUL** | MEDIUM | Static TypeScript AST extraction of required file parameters; wrapped in `arguments`. |
| `CLUSTER_CHATWOOT` | Chatwoot | `create-an-account-user` | POST | Path + Body | 1 | **CANONICAL_FAITHFUL** | LOW | Path param `account_id` in `path`; body params in `body`; role enum preserved. |
| `CLUSTER_CHATWOOT` | Chatwoot | `create-a-contact` | POST | Path + Body | 2 | **CANONICAL_FAITHFUL** | MEDIUM | Path param `inbox_identifier` in `path`; contact properties in `body`. |
| `CLUSTER_CHATWOOT` | Chatwoot | `create-a-conversation` | POST | Path + Body | 2 | **CANONICAL_FAITHFUL** | LOW | Path params in `path`; custom attributes in `body`. |
| `CLUSTER_LINE` | LINE | `setWebhookEndpoint` | PUT | Body only | 1 | **CANONICAL_FAITHFUL** | LOW | Flat single-URL property constructor inside `body`. |
| `CLUSTER_LINE` | LINE | `replyMessage` | POST | Body only | 3 | **CANONICAL_FAITHFUL** | MEDIUM | `messages` array contains discriminated union by `type`; preserved without pruning. |
| `CLUSTER_LINE` | LINE | `pushMessage` | POST | Body only | 3 | **EXCLUDE_PENDING** | HIGH | **DISQUALIFIED FROM CANONICAL COHORT.** Wide polymorphic message union requires lossy pruning. |

---

## 9. Next Steps Prior to Extraction Execution

1. Present this revised specification for user review.
2. Upon review, identify 2 replacement candidate operations (one for Slack, one for LINE) that can be faithfully extracted without lossy pruning, submit them to the source-admission protocol, and update the operation manifest to restore the 30-operation canonical target.
3. Implement the read-only, AST-safe extraction engine and lineage logger strictly in accordance with Sections 2, 3, 4, and 5.
