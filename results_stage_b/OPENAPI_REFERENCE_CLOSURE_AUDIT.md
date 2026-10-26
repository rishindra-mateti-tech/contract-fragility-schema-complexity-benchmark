# OpenAPI Reference Closure Audit Report

**Policy ID:** `OPENAPI_REFERENCE_RESOLUTION_POLICY_001`  
**Total Operations Audited:** 30  
**Single-File Root Operations:** 21  
**Multi-File / Ref Operations:** 3  
**Successful Closures:** 21  
**Failed Closures:** 3  

## Detailed Operation Accounting

| Slot ID | Operation ID | Source ID | Status | Error Code / Details |
| :--- | :--- | :--- | :--- | :--- |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | `CAND-001` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | `CAND-001` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_STRIPE_03` | `PostRefunds` | `CAND-002` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | `FAILED` | ERR_LOCAL_REF_FILE_NOT_FOUND |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | `FAILED` | ERR_LOCAL_REF_FILE_NOT_FOUND |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | `FAILED` | ERR_LOCAL_REF_FILE_NOT_FOUND |
| `SLOT_TWILIO_01` | `UpdateAccount` | `CAND-004` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_TWILIO_02` | `CreateMessage` | `CAND-004` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_TWILIO_03` | `CreateCall` | `CAND-004` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_BOX_01` | `post_folders` | `CAND-005` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_BOX_02` | `post_collaborations` | `CAND-005` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_BOX_03` | `post_users` | `CAND-005` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_SLACK_01` | `conversations.create` | `CAND-006` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_SLACK_02` | `users.profile.set` | `CAND-006` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_SLACK_03` | `reminders.add` | `CAND-006` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | `SKIPPED_NON_OPENAPI` | AST source code format '.py' does not use OpenAPI reference resolution. |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | `SKIPPED_NON_OPENAPI` | AST source code format '.py' does not use OpenAPI reference resolution. |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | `SKIPPED_NON_OPENAPI` | AST source code format '.py' does not use OpenAPI reference resolution. |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | `SKIPPED_NON_OPENAPI` | AST source code format '.ts' does not use OpenAPI reference resolution. |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | `SKIPPED_NON_OPENAPI` | AST source code format '.ts' does not use OpenAPI reference resolution. |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | `SKIPPED_NON_OPENAPI` | AST source code format '.ts' does not use OpenAPI reference resolution. |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CAND-011` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CAND-011` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_LINE_02` | `setWebhookEndpoint` | `CAND-013` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_LINE_03` | `markMessagesAsRead` | `CAND-013` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_GITHUB_01` | `pulls/create` | `CAND-001` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_STRIPE_01` | `PostPayouts` | `CAND-002` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_STRIPE_02` | `PostShippingRates` | `CAND-002` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `CAND-011` | `SINGLE_FILE_ROOT` | OK |
| `SLOT_LINE_01` | `showLoadingAnimation` | `CAND-013` | `SINGLE_FILE_ROOT` | OK |
