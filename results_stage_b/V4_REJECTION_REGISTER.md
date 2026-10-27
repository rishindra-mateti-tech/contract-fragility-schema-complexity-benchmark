# Stage B Batch Extraction V4 Rejection Register

**Pipeline Version:** `4.0.0`  
**Total Operations Rejected:** 6  
**Governing Rule:** Fail-closed on all dynamic constructs, dialect conflicts, and unsupported topologies. Hand-written extraction patches are prohibited.

---

## 1. Rejection Inventory

| Slot ID | Operation ID | Source ID | Rejection Code | Category | Scientific Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_STRIPE_03` | `PostRefunds` | `CAND-002` | `FEAT_POLYMORPHIC_UNION` | UNSUPPORTED_SCHEMA_TOPOLOGY | Polymorphic union schemas require multi-schema extraction protocol (Protocol Amendment 003). |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `ERR_READONLY_IN_REQUEST_SURFACE` | UNSUPPORTED_REQUEST_SURFACE_READONLY | Request property declares 'readOnly: true', which is prohibited on HTTP write surfaces under OAS30_TO_DRAFT07_CONVERSION_POLICY_001. |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `ERR_READONLY_IN_REQUEST_SURFACE` | UNSUPPORTED_REQUEST_SURFACE_READONLY | Request property declares 'readOnly: true', which is prohibited on HTTP write surfaces under OAS30_TO_DRAFT07_CONVERSION_POLICY_001. |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | DYNAMIC_SCHEMA_CONSTRUCT | Dynamic runtime schema builder 'zodToJsonSchema' cannot be resolved statically without code execution |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | DYNAMIC_SCHEMA_CONSTRUCT | Dynamic runtime schema builder 'zodToJsonSchema' cannot be resolved statically without code execution |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | DYNAMIC_SCHEMA_CONSTRUCT | Dynamic runtime schema builder 'zodToJsonSchema' cannot be resolved statically without code execution |

---

## 2. Detailed Technical Breakdown of Rejections

### 2.1 Polymorphic Union Slot (`SLOT_STRIPE_03`)
- **Operation:** `PostRefunds` (`CAND-002`)
- **Blocker:** The schema root contains polymorphic `anyOf`/`oneOf` branching with discriminator fields.
- **Resolution Requirement:** Requires multi-schema extraction protocol under Protocol Amendment 003. Single-contract monomorphic adapters cannot represent this structure without epistemic distortion.

### 2.2 Unsupported Request-Surface ReadOnly Properties (`SLOT_DO_02`, `SLOT_DO_03`)
- **Operations:** `domains_create` (`SLOT_DO_02`), `droplets_create` (`SLOT_DO_03`) (`CAND-003`)
- **Blocker:** DigitalOcean models embed properties marked `readOnly: true` (e.g. `zone_file`, `ttl`, `retention_period_days`) directly within HTTP POST request payload models.
- **Resolution Requirement:** Under `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`, `readOnly: true` properties on HTTP write request surfaces represent semantic contradictions unless stripped by a formally audited write-projection adapter.

### 2.3 Dynamic TypeScript Runtime Schema Builders (`SLOT_MCP_GITHUB_01-03`)
- **Operations:** `search_repositories`, `create_issue`, `create_or_update_file` (`CAND-010`)
- **Blocker:** MCP GitHub tools declare input schemas via runtime function calls `zodToJsonSchema(SearchRepositoriesSchema)` importing Zod schemas from sibling TypeScript files.
- **Resolution Requirement:** Tree-sitter static AST analysis detects dynamic call expressions and external identifiers. Evaluating them requires running a Node.js interpreter, which violates static provenance invariants.
