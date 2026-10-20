# Stage B Batch Candidate Extraction Results

## 1. Executive Summary
- **Execution Date**: 2026-10-20
- **Extractor Version**: `2.0.0`
- **Governing Specification**: `STAGE_B_EXTRACTION_SPEC.md`
- **Lifecycle Status Assigned**: `EXTRACTED_PENDING_HUMAN_VALIDATION`
- **Creation Mode**: `BATCH_GENERATED_CANDIDATE`
- **Independent Validation Claimed**: `False`

### Accounting Overview
- **Total Manifest Operations Considered**: 30
- **Already-Existing Pilot Slots Skipped**: 2 (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`)
- **Polymorphic Union Slots Excluded**: 1 (`SLOT_STRIPE_03`)
- **Eligible Operations Attempted**: 27
- **Candidates Successfully Generated (Quarantined)**: 13
- **Candidates Rejected (Fail-Closed)**: 14

---

## 2. Successfully Generated Extraction Candidates (13)
All candidates quarantined in `data_stage_b/extraction_candidates/<SLOT_ID>/`.

| Slot ID | Operation ID | Source Candidate | Output Path | Status |
|---|---|---|---|---|
| `SLOT_GITHUB_02` | `repos/create-commit-status` | `CAND-001` | `data_stage_b/extraction_candidates/SLOT_GITHUB_02` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | `CAND-001` | `data_stage_b/extraction_candidates/SLOT_GITHUB_03` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_01` | `UpdateAccount` | `CAND-004` | `data_stage_b/extraction_candidates/SLOT_TWILIO_01` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_02` | `CreateMessage` | `CAND-004` | `data_stage_b/extraction_candidates/SLOT_TWILIO_02` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_TWILIO_03` | `CreateCall` | `CAND-004` | `data_stage_b/extraction_candidates/SLOT_TWILIO_03` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_01` | `post_folders` | `CAND-005` | `data_stage_b/extraction_candidates/SLOT_BOX_01` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_02` | `post_collaborations` | `CAND-005` | `data_stage_b/extraction_candidates/SLOT_BOX_02` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_BOX_03` | `post_users` | `CAND-005` | `data_stage_b/extraction_candidates/SLOT_BOX_03` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_02` | `setWebhookEndpoint` | `CAND-013` | `data_stage_b/extraction_candidates/SLOT_LINE_02` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_03` | `markMessagesAsRead` | `CAND-013` | `data_stage_b/extraction_candidates/SLOT_LINE_03` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_STRIPE_01` | `PostPayouts` | `CAND-002` | `data_stage_b/extraction_candidates/SLOT_STRIPE_01` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `CAND-011` | `data_stage_b/extraction_candidates/SLOT_CHATWOOT_01` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `SLOT_LINE_01` | `showLoadingAnimation` | `CAND-013` | `data_stage_b/extraction_candidates/SLOT_LINE_01` | `EXTRACTED_PENDING_HUMAN_VALIDATION` |

---

## 3. Rejected Operations Summary (14)
Every rejected candidate is preserved as a valuable scientific failure record documenting exact specification blockers.

| Slot ID | Operation ID | Source Candidate | Rejection Code | Category |
|---|---|---|---|---|
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | `PROHIBITED_FEATURE` |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | `PROHIBITED_FEATURE` |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `FEAT_REF_EXTERNAL_FILE` | `PROHIBITED_FEATURE` |
| `SLOT_SLACK_01` | `conversations.create` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | `UNSUPPORTED_SURFACE` |
| `SLOT_SLACK_02` | `users.profile.set` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | `UNSUPPORTED_SURFACE` |
| `SLOT_SLACK_03` | `reminders.add` | `CAND-006` | `FEAT_SWAGGER_FORM_DATA_UNSUPPORTED` | `UNSUPPORTED_SURFACE` |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `NON_OPENAPI_SPEC_SOURCE_CODE` | `UNSUPPORTED_SPEC_FORMAT` |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CAND-011` | `UNINHERITED_PATH_PARAMETERS` | `SPEC_STRUCTURE_AMBIGUITY` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CAND-011` | `UNINHERITED_PATH_PARAMETERS` | `SPEC_STRUCTURE_AMBIGUITY` |
