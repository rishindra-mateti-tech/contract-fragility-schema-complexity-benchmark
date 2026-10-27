# Stage B Batch Extraction V4 Rejection Register

**Pipeline Version:** `4.0.0`  
**Total Rejections:** 6  

| Slot ID | Operation ID | Source ID | Rejection Code | Category | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_STRIPE_03` | `PostRefunds` | `CAND-002` | `FEAT_POLYMORPHIC_UNION` | UNSUPPORTED_SCHEMA_TOPOLOGY | Polymorphic union schemas require multi-schema extraction protocol (Protocol Amendment 003). |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `ERR_READONLY_IN_REQUEST_SURFACE` | UNSUPPORTED_REQUEST_SURFACE_READONLY | Request property declares 'readOnly: true', which is prohibited on HTTP write surfaces under OAS30_TO_DRAFT07_CONVERSION_POLICY_001. |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `ERR_READONLY_IN_REQUEST_SURFACE` | UNSUPPORTED_REQUEST_SURFACE_READONLY | Request property declares 'readOnly: true', which is prohibited on HTTP write surfaces under OAS30_TO_DRAFT07_CONVERSION_POLICY_001. |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | DYNAMIC_SCHEMA_CONSTRUCT | Dynamic runtime schema builder 'zodToJsonSchema' cannot be resolved statically without code execution |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | DYNAMIC_SCHEMA_CONSTRUCT | Dynamic runtime schema builder 'zodToJsonSchema' cannot be resolved statically without code execution |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `ERR_RUNTIME_SCHEMA_BUILDER_REJECTED` | DYNAMIC_SCHEMA_CONSTRUCT | Dynamic runtime schema builder 'zodToJsonSchema' cannot be resolved statically without code execution |
