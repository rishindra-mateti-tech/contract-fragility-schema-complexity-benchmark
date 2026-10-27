# Stage B V4 Candidate Provenance and Difference Audit

**Pipeline Version:** `4.0.0`  
**Total Candidates Audited:** 22  
**Total Audit Failures:** 0  
**Status:** `ALL_PASS`  

## Candidate Forensic Verification

| Slot ID | Operation ID | Source Dialect | Adapters Used | Surfaces | Fields | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| `SLOT_BOX_01` | `post_folders` | OpenAPI 3.0.2 | None | `body, query` | 2 | `PASS` |
| `SLOT_BOX_02` | `post_collaborations` | OpenAPI 3.0.2 | None | `body, query` | 2 | `PASS` |
| `SLOT_BOX_03` | `post_users` | OpenAPI 3.0.2 | None | `body, query` | 2 | `PASS` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 2 | `PASS` |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 2 | `PASS` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 2 | `PASS` |
| `SLOT_DO_01` | `floating_ips_create` | OpenAPI 3.0.0 | LocalReferenceResolver | `None` | 1 | `PASS` |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | OpenAPI 3.0.3 | None | `body, path` | 2 | `PASS` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | OpenAPI 3.0.3 | None | `body` | 1 | `PASS` |
| `SLOT_LINE_01` | `showLoadingAnimation` | OpenAPI 3.0.0 | None | `body` | 1 | `PASS` |
| `SLOT_LINE_02` | `setWebhookEndpoint` | OpenAPI 3.0.0 | None | `body` | 1 | `PASS` |
| `SLOT_LINE_03` | `markMessagesAsRead` | OpenAPI 3.0.0 | None | `body` | 1 | `PASS` |
| `SLOT_MCP_SQLITE_01` | `read_query` | Python 3 AST | PythonAstToolExtractor | `rpc_arguments` | 1 | `PASS` |
| `SLOT_MCP_SQLITE_02` | `describe_table` | Python 3 AST | PythonAstToolExtractor | `rpc_arguments` | 1 | `PASS` |
| `SLOT_MCP_SQLITE_03` | `write_query` | Python 3 AST | PythonAstToolExtractor | `rpc_arguments` | 1 | `PASS` |
| `SLOT_SLACK_01` | `conversations.create` | OpenAPI 2.0 | OpenAPI2FormDataAdapter | `form, header` | 2 | `PASS` |
| `SLOT_SLACK_02` | `users.profile.set` | OpenAPI 2.0 | OpenAPI2FormDataAdapter | `form, header` | 2 | `PASS` |
| `SLOT_SLACK_03` | `reminders.add` | OpenAPI 2.0 | OpenAPI2FormDataAdapter | `form, header` | 2 | `PASS` |
| `SLOT_STRIPE_01` | `PostPayouts` | OpenAPI 3.0.0 | None | `body` | 1 | `PASS` |
| `SLOT_TWILIO_01` | `UpdateAccount` | OpenAPI 3.0.1 | None | `body, path` | 2 | `PASS` |
| `SLOT_TWILIO_02` | `CreateMessage` | OpenAPI 3.0.1 | None | `body, path` | 2 | `PASS` |
| `SLOT_TWILIO_03` | `CreateCall` | OpenAPI 3.0.1 | None | `body, path` | 2 | `PASS` |
