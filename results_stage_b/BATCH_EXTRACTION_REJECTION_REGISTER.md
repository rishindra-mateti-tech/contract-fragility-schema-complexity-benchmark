# Stage B Batch Extraction Rejection Register

This register records every operation rejected during the Stage B batch extraction run.
In accordance with benchmark principles, rejections are valid, permanent scientific outputs documenting why candidate schemas cannot be extracted deterministically under current support policies.

Total rejections: 14

### `SLOT_DO_01` - `floating_ips_create`
- **Candidate Source ID**: `CAND-003`
- **Rejection Code**: `FEAT_REF_EXTERNAL_FILE`
- **Category**: `PROHIBITED_FEATURE`
- **Reason**: Operation defines external file reference: resources/floating_ips/floatingIPs_create.yml
- **Evidence**:
```json
{
  "ref": "resources/floating_ips/floatingIPs_create.yml",
  "pointer": "#/paths/~1v2~1floating_ips/post"
}
```

---
### `SLOT_DO_02` - `domains_create`
- **Candidate Source ID**: `CAND-003`
- **Rejection Code**: `FEAT_REF_EXTERNAL_FILE`
- **Category**: `PROHIBITED_FEATURE`
- **Reason**: Operation defines external file reference: resources/domains/domains_create.yml
- **Evidence**:
```json
{
  "ref": "resources/domains/domains_create.yml",
  "pointer": "#/paths/~1v2~1domains/post"
}
```

---
### `SLOT_DO_03` - `droplets_create`
- **Candidate Source ID**: `CAND-003`
- **Rejection Code**: `FEAT_REF_EXTERNAL_FILE`
- **Category**: `PROHIBITED_FEATURE`
- **Reason**: Operation defines external file reference: resources/droplets/droplets_create.yml
- **Evidence**:
```json
{
  "ref": "resources/droplets/droplets_create.yml",
  "pointer": "#/paths/~1v2~1droplets/post"
}
```

---
### `SLOT_SLACK_01` - `conversations.create`
- **Candidate Source ID**: `CAND-006`
- **Rejection Code**: `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED`
- **Category**: `UNSUPPORTED_SURFACE`
- **Reason**: Operation declares Swagger 2.0 in:formData parameters. Current benchmark extraction requires OpenAPI 3.0 requestBody.
- **Evidence**:
```json
{
  "param": "name",
  "pointer": "#/paths/~1conversations.create/post/parameters/1"
}
```

---
### `SLOT_SLACK_02` - `users.profile.set`
- **Candidate Source ID**: `CAND-006`
- **Rejection Code**: `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED`
- **Category**: `UNSUPPORTED_SURFACE`
- **Reason**: Operation declares Swagger 2.0 in:formData parameters. Current benchmark extraction requires OpenAPI 3.0 requestBody.
- **Evidence**:
```json
{
  "param": "name",
  "pointer": "#/paths/~1users.profile.set/post/parameters/1"
}
```

---
### `SLOT_SLACK_03` - `reminders.add`
- **Candidate Source ID**: `CAND-006`
- **Rejection Code**: `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED`
- **Category**: `UNSUPPORTED_SURFACE`
- **Reason**: Operation declares Swagger 2.0 in:formData parameters. Current benchmark extraction requires OpenAPI 3.0 requestBody.
- **Evidence**:
```json
{
  "param": "text",
  "pointer": "#/paths/~1reminders.add/post/parameters/1"
}
```

---
### `SLOT_MCP_SQLITE_01` - `read_query`
- **Candidate Source ID**: `CAND-009`
- **Rejection Code**: `NON_OPENAPI_SPEC_SOURCE_CODE`
- **Category**: `UNSUPPORTED_SPEC_FORMAT`
- **Reason**: Source file format '.py' is source code AST, not an OpenAPI specification.
- **Evidence**:
```json
{
  "ext": ".py",
  "path": "C:\\Users\\rishi\\OneDrive\\Desktop\\Education\\contract-fragility-schema-complexity-benchmark\\data_stage_b\\raw\\CAND-009\\1b97a6a4903bd8961941cdff43df3b059e610e5f.py"
}
```

---
### `SLOT_MCP_SQLITE_02` - `describe_table`
- **Candidate Source ID**: `CAND-009`
- **Rejection Code**: `NON_OPENAPI_SPEC_SOURCE_CODE`
- **Category**: `UNSUPPORTED_SPEC_FORMAT`
- **Reason**: Source file format '.py' is source code AST, not an OpenAPI specification.
- **Evidence**:
```json
{
  "ext": ".py",
  "path": "C:\\Users\\rishi\\OneDrive\\Desktop\\Education\\contract-fragility-schema-complexity-benchmark\\data_stage_b\\raw\\CAND-009\\1b97a6a4903bd8961941cdff43df3b059e610e5f.py"
}
```

---
### `SLOT_MCP_SQLITE_03` - `write_query`
- **Candidate Source ID**: `CAND-009`
- **Rejection Code**: `NON_OPENAPI_SPEC_SOURCE_CODE`
- **Category**: `UNSUPPORTED_SPEC_FORMAT`
- **Reason**: Source file format '.py' is source code AST, not an OpenAPI specification.
- **Evidence**:
```json
{
  "ext": ".py",
  "path": "C:\\Users\\rishi\\OneDrive\\Desktop\\Education\\contract-fragility-schema-complexity-benchmark\\data_stage_b\\raw\\CAND-009\\1b97a6a4903bd8961941cdff43df3b059e610e5f.py"
}
```

---
### `SLOT_MCP_GITHUB_01` - `search_repositories`
- **Candidate Source ID**: `CAND-010`
- **Rejection Code**: `NON_OPENAPI_SPEC_SOURCE_CODE`
- **Category**: `UNSUPPORTED_SPEC_FORMAT`
- **Reason**: Source file format '.ts' is source code AST, not an OpenAPI specification.
- **Evidence**:
```json
{
  "ext": ".ts",
  "path": "C:\\Users\\rishi\\OneDrive\\Desktop\\Education\\contract-fragility-schema-complexity-benchmark\\data_stage_b\\raw\\CAND-010\\0676a34c85537e610f911fbd73a5a079f38be18e.ts"
}
```

---
### `SLOT_MCP_GITHUB_02` - `create_issue`
- **Candidate Source ID**: `CAND-010`
- **Rejection Code**: `NON_OPENAPI_SPEC_SOURCE_CODE`
- **Category**: `UNSUPPORTED_SPEC_FORMAT`
- **Reason**: Source file format '.ts' is source code AST, not an OpenAPI specification.
- **Evidence**:
```json
{
  "ext": ".ts",
  "path": "C:\\Users\\rishi\\OneDrive\\Desktop\\Education\\contract-fragility-schema-complexity-benchmark\\data_stage_b\\raw\\CAND-010\\0676a34c85537e610f911fbd73a5a079f38be18e.ts"
}
```

---
### `SLOT_MCP_GITHUB_03` - `create_or_update_file`
- **Candidate Source ID**: `CAND-010`
- **Rejection Code**: `NON_OPENAPI_SPEC_SOURCE_CODE`
- **Category**: `UNSUPPORTED_SPEC_FORMAT`
- **Reason**: Source file format '.ts' is source code AST, not an OpenAPI specification.
- **Evidence**:
```json
{
  "ext": ".ts",
  "path": "C:\\Users\\rishi\\OneDrive\\Desktop\\Education\\contract-fragility-schema-complexity-benchmark\\data_stage_b\\raw\\CAND-010\\0676a34c85537e610f911fbd73a5a079f38be18e.ts"
}
```

---
### `SLOT_CHATWOOT_02` - `create-an-account-user`
- **Candidate Source ID**: `CAND-011`
- **Rejection Code**: `UNINHERITED_PATH_PARAMETERS`
- **Category**: `SPEC_STRUCTURE_AMBIGUITY`
- **Reason**: Operation defines 1 path-level parameter(s) on parent path item not inherited in operation parameters.
- **Evidence**:
```json
{
  "path_level_params_count": 1,
  "path_item": "#/paths/~1platform~1api~1v1~1accounts~1{account_id}~1account_users"
}
```

---
### `SLOT_CHATWOOT_03` - `create-a-conversation`
- **Candidate Source ID**: `CAND-011`
- **Rejection Code**: `UNINHERITED_PATH_PARAMETERS`
- **Category**: `SPEC_STRUCTURE_AMBIGUITY`
- **Reason**: Operation defines 2 path-level parameter(s) on parent path item not inherited in operation parameters.
- **Evidence**:
```json
{
  "path_level_params_count": 2,
  "path_item": "#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts~1{contact_identifier}~1conversations"
}
```

---
