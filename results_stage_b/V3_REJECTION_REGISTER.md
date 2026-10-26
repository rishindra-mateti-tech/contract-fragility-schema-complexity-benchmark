# Stage B V3 Rejection Register

**Pipeline Version:** `3.0.0`  
**Total Rejected Operations:** 10  

| Slot ID | Operation ID | Source ID | Rejection Code | Category | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_STRIPE_03` | `PostRefunds` | `CAND-002` | `FEAT_POLYMORPHIC_UNION` | UNSUPPORTED_SCHEMA_TOPOLOGY | Polymorphic union requires multi-schema extraction protocol under Protocol Amendment 003. |
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | `ERR_LOCAL_REF_FILE_NOT_FOUND` | MISSING_LOCAL_REFERENCE_FILE | Referenced relative specification file is not present on disk in pinned source bundle. |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `ERR_LOCAL_REF_FILE_NOT_FOUND` | MISSING_LOCAL_REFERENCE_FILE | Referenced relative specification file is not present on disk in pinned source bundle. |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `ERR_LOCAL_REF_FILE_NOT_FOUND` | MISSING_LOCAL_REFERENCE_FILE | Referenced relative specification file is not present on disk in pinned source bundle. |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | `FEAT_AST_SOURCE_CODE` | NON_OPENAPI_SPECIFICATION | Source code AST requires dedicated AST compiler; prohibited from OpenAPI pipeline. |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | `FEAT_AST_SOURCE_CODE` | NON_OPENAPI_SPECIFICATION | Source code AST requires dedicated AST compiler; prohibited from OpenAPI pipeline. |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | `FEAT_AST_SOURCE_CODE` | NON_OPENAPI_SPECIFICATION | Source code AST requires dedicated AST compiler; prohibited from OpenAPI pipeline. |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `FEAT_AST_SOURCE_CODE` | NON_OPENAPI_SPECIFICATION | Source code AST requires dedicated AST compiler; prohibited from OpenAPI pipeline. |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `FEAT_AST_SOURCE_CODE` | NON_OPENAPI_SPECIFICATION | Source code AST requires dedicated AST compiler; prohibited from OpenAPI pipeline. |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `FEAT_AST_SOURCE_CODE` | NON_OPENAPI_SPECIFICATION | Source code AST requires dedicated AST compiler; prohibited from OpenAPI pipeline. |
