# Stage B Batch Extraction V2 Rejection Register

**Total Operations Rejected:** `14`  

| Slot ID | Operation ID | Source ID | Rejection Code | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CAND-011` | `UNINHERITED_PATH_PARAMETERS` | Operation defines 1 path-level parameter(s) on parent path item not inherited in operation parameters. |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CAND-011` | `UNINHERITED_PATH_PARAMETERS` | Operation defines 2 path-level parameter(s) on parent path item not inherited in operation parameters. |
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | Operation defines external file reference: resources/floating_ips/floatingIPs_create.yml |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | Operation defines external file reference: resources/domains/domains_create.yml |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | Operation defines external file reference: resources/droplets/droplets_create.yml |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | Source file format '.ts' is source code AST, not an OpenAPI specification. |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | Source file format '.ts' is source code AST, not an OpenAPI specification. |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | Source file format '.ts' is source code AST, not an OpenAPI specification. |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | Source file format '.py' is source code AST, not an OpenAPI specification. |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | Source file format '.py' is source code AST, not an OpenAPI specification. |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | Source file format '.py' is source code AST, not an OpenAPI specification. |
| `SLOT_SLACK_01` | `conversations.create` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | Operation declares Swagger 2.0 in:formData parameters. Current benchmark extraction requires OpenAPI 3.0 requestBody. |
| `SLOT_SLACK_02` | `users.profile.set` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | Operation declares Swagger 2.0 in:formData parameters. Current benchmark extraction requires OpenAPI 3.0 requestBody. |
| `SLOT_SLACK_03` | `reminders.add` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | Operation declares Swagger 2.0 in:formData parameters. Current benchmark extraction requires OpenAPI 3.0 requestBody. |
