# Stage B Batch Extraction Pipeline V3 Results

**Execution Date:** October 26, 2026  
**Pipeline Version:** `3.0.0`  
**Governing Conversion Policy:** `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md`  
**Governing Reference Policy:** `results_stage_b/OPENAPI_REFERENCE_RESOLUTION_POLICY_001.md`  
**Governing Parameter Policy:** `results_stage_b/OPENAPI_PARAMETER_INHERITANCE_POLICY_001.md`  
**Governing FormData Policy:** `results_stage_b/OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001.md`  
**Lifecycle Status Assigned:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  
**Quarantined Output Base:** `data_stage_b/extraction_candidates_v3/`  

---

## 1. Accounting Summary across Active Manifest Operations

| Metric Category | Count | Methodological Notes |
| :--- | :---: | :--- |
| **Total Active Manifest Operations** | **30** | Complete set of admitted Stage B operations. |
| **Existing Pilots Skipped** | **2** | `SLOT_GITHUB_01` (validated) and `SLOT_STRIPE_02` (pending validation) preserved. |
| **Eligible Operations Attempted** | **28** | Total operations evaluated by Pipeline V3. |
| **Candidates Successfully Generated (V3)** | **18** | Quarantined in `data_stage_b/extraction_candidates_v3/<SLOT_ID>/`. |
| **Candidates Generated without Adapters** | **13** | Monomorphic OpenAPI 3.0 operations with standard dialect conversion. |
| **Candidates Generated with Parameter Inheritance Adapter** | **2** | `SLOT_CHATWOOT_02`, `SLOT_CHATWOOT_03` (path parameters inherited). |
| **Candidates Generated with FormData Adapter** | **3** | `SLOT_SLACK_01`, `SLOT_SLACK_02`, `SLOT_SLACK_03` (formData mapped to form). |
| **Candidates Generated with Local Ref Adapter** | **0** | DigitalOcean spec requires sibling files not present in pinned raw bundle. |
| **Operations Rejected Fail-Closed** | **10** | Documented in `V3_REJECTION_REGISTER.md`. |
| **Remaining Blocked AST Source Code Slots** | **6** | 3 MCP SQLite (`CAND-009`) + 3 MCP GitHub (`CAND-010`). |
| **Remaining Blocked Polymorphic Union Slots** | **1** | `SLOT_STRIPE_03` (`PostRefunds`, Protocol Amendment 003). |
| **Remaining Blocked Missing-File Slots** | **3** | `SLOT_DO_01`, `SLOT_DO_02`, `SLOT_DO_03` (`CAND-003`). |
| **Remaining Human Validation Requirements** | **18** | All 18 candidates held at `EXTRACTED_PENDING_HUMAN_VALIDATION`. |

---

## 2. Successfully Generated V3 Candidate Cohort (18)

| Slot ID | Operation ID | Source Candidate | Adapters Used | Extracted Surfaces | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_BOX_01` | `post_folders` | `CAND-005` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_02` | `post_collaborations` | `CAND-005` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_03` | `post_users` | `CAND-005` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `CAND-011` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CAND-011` | ParameterInheritanceAdapter | `path`, `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CAND-011` | ParameterInheritanceAdapter | `path`, `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | `CAND-001` | None | `path`, `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | `CAND-001` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_01` | `showLoadingAnimation` | `CAND-013` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_02` | `setWebhookEndpoint` | `CAND-013` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_03` | `markMessagesAsRead` | `CAND-013` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_SLACK_01` | `conversations.create` | `CAND-006` | OpenAPI2FormDataAdapter | `header`, `form` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_SLACK_02` | `users.profile.set` | `CAND-006` | OpenAPI2FormDataAdapter | `header`, `form` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_SLACK_03` | `reminders.add` | `CAND-006` | OpenAPI2FormDataAdapter | `header`, `form` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_STRIPE_01` | `PostPayouts` | `CAND-002` | None | `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_01` | `UpdateAccount` | `CAND-004` | None | `path`, `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_02` | `CreateMessage` | `CAND-004` | None | `path`, `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_03` | `CreateCall` | `CAND-004` | None | `path`, `body` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |

---

## 3. Rejected Operations Accounting (10)

| Slot ID | Operation ID | Source ID | Rejection Code | Category | Operational Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | `ERR_LOCAL_REF_FILE_NOT_FOUND` | `MISSING_LOCAL_REFERENCE_FILE` | Target file `resources/floating_ips/floatingIPs_create.yml` not in pinned source bundle. |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `ERR_LOCAL_REF_FILE_NOT_FOUND` | `MISSING_LOCAL_REFERENCE_FILE` | Target file `resources/domains/domains_create.yml` not in pinned source bundle. |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `ERR_LOCAL_REF_FILE_NOT_FOUND` | `MISSING_LOCAL_REFERENCE_FILE` | Target file `resources/droplets/droplets_create.yml` not in pinned source bundle. |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `FEAT_AST_SOURCE_CODE` | `NON_OPENAPI_SPECIFICATION` | TypeScript AST requires dedicated AST parser framework. |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `FEAT_AST_SOURCE_CODE` | `NON_OPENAPI_SPECIFICATION` | TypeScript AST requires dedicated AST parser framework. |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `FEAT_AST_SOURCE_CODE` | `NON_OPENAPI_SPECIFICATION` | TypeScript AST requires dedicated AST parser framework. |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | `FEAT_AST_SOURCE_CODE` | `NON_OPENAPI_SPECIFICATION` | Python AST requires dedicated AST parser framework. |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | `FEAT_AST_SOURCE_CODE` | `NON_OPENAPI_SPECIFICATION` | Python AST requires dedicated AST parser framework. |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | `FEAT_AST_SOURCE_CODE` | `NON_OPENAPI_SPECIFICATION` | Python AST requires dedicated AST parser framework. |
| `SLOT_STRIPE_03` | `PostRefunds` | `CAND-002` | `FEAT_POLYMORPHIC_UNION` | `UNSUPPORTED_SCHEMA_TOPOLOGY` | Polymorphic union schema excluded under Protocol Amendment 003. |
