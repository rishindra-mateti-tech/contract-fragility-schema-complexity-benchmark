# Stage B Batch Candidate Extraction V2 Results

**Execution Date:** `2026-10-26`  
**Pipeline Version:** `2.0.0`  
**Governing Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Conversion Policy Hash:** `ca17608c3a1fcee075e5706928bfbc7f958d6e59e447e9461350f4afc9191290`  
**Lifecycle Status Assigned:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  
**Quarantined Output Base:** `data_stage_b/extraction_candidates_v2/`  

## 1. Accounting Summary

- Total Manifest Operations: `30`
- Existing Pilots Skipped: `2`
- Polymorphic Union Excluded: `1`
- Eligible Operations Attempted: `27`
- Candidates Successfully Generated (V2): `13`
- Operations Cleanly Rejected (Fail-Closed): `14`

## 2. Successfully Generated Extraction Candidates V2 (13)

| Slot ID | Operation ID | Source Candidate | Schema Transformations | Status |
| :--- | :--- | :--- | :---: | :--- |
| `SLOT_BOX_01` | `post_folders` | `CAND-005` | `2` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_02` | `post_collaborations` | `CAND-005` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_03` | `post_users` | `CAND-005` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `CAND-011` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | `CAND-001` | `2` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | `CAND-001` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_01` | `showLoadingAnimation` | `CAND-013` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_02` | `setWebhookEndpoint` | `CAND-013` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_03` | `markMessagesAsRead` | `CAND-013` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_STRIPE_01` | `PostPayouts` | `CAND-002` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_01` | `UpdateAccount` | `CAND-004` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_02` | `CreateMessage` | `CAND-004` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_03` | `CreateCall` | `CAND-004` | `0` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |

## 3. Rejected Operations Register (14)

| Slot ID | Operation ID | Candidate Source | Rejection Code | Category |
| :--- | :--- | :--- | :--- | :--- |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CAND-011` | `UNINHERITED_PATH_PARAMETERS` | `SPEC_STRUCTURE_AMBIGUITY` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CAND-011` | `UNINHERITED_PATH_PARAMETERS` | `SPEC_STRUCTURE_AMBIGUITY` |
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | `PROHIBITED_FEATURE` |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | `PROHIBITED_FEATURE` |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | `PROHIBITED_FEATURE` |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_SLACK_01` | `conversations.create` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | `UNSUPPORTED_SURFACE` |
| `SLOT_SLACK_02` | `users.profile.set` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | `UNSUPPORTED_SURFACE` |
| `SLOT_SLACK_03` | `reminders.add` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | `UNSUPPORTED_SURFACE` |
