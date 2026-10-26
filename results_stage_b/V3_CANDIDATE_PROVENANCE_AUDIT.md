# Stage B V3 Candidate Provenance and Difference Audit

**Pipeline Version:** `3.0.0`  
**Total Candidates Audited:** 18  
**Total Audit Failures:** 0  
**Status:** `ALL_PASS`  

## Candidate Forensic Verification

| Slot ID | Operation ID | Source Dialect | Adapters Used | Surfaces | Fields | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| `SLOT_BOX_01` | `post_folders` | OpenAPI 3.0.2 | None | `body, query` | 5 | `PASS` |
| `SLOT_BOX_02` | `post_collaborations` | OpenAPI 3.0.2 | None | `body, query` | 8 | `PASS` |
| `SLOT_BOX_03` | `post_users` | OpenAPI 3.0.2 | None | `body, query` | 19 | `PASS` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 4 | `PASS` |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 3 | `PASS` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 3 | `PASS` |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | OpenAPI 3.0.3 | None | `body, path` | 7 | `PASS` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | OpenAPI 3.0.3 | None | `body` | 23 | `PASS` |
| `SLOT_LINE_01` | `showLoadingAnimation` | OpenAPI 3.0.0 | None | `body` | 2 | `PASS` |
| `SLOT_LINE_02` | `setWebhookEndpoint` | OpenAPI 3.0.0 | None | `body` | 1 | `PASS` |
| `SLOT_LINE_03` | `markMessagesAsRead` | OpenAPI 3.0.0 | None | `body` | 1 | `PASS` |
| `SLOT_SLACK_01` | `conversations.create` | Swagger 2.0 | OpenAPI2FormDataAdapter | `form, header` | 3 | `PASS` |
| `SLOT_SLACK_02` | `users.profile.set` | Swagger 2.0 | OpenAPI2FormDataAdapter | `form, header` | 5 | `PASS` |
| `SLOT_SLACK_03` | `reminders.add` | Swagger 2.0 | OpenAPI2FormDataAdapter | `form, header` | 4 | `PASS` |
| `SLOT_STRIPE_01` | `PostPayouts` | OpenAPI 3.0.0 | None | `body` | 10 | `PASS` |
| `SLOT_TWILIO_01` | `UpdateAccount` | OpenAPI 3.0.1 | None | `body, path` | 3 | `PASS` |
| `SLOT_TWILIO_02` | `CreateMessage` | OpenAPI 3.0.1 | None | `body, path` | 27 | `PASS` |
| `SLOT_TWILIO_03` | `CreateCall` | OpenAPI 3.0.1 | None | `body, path` | 39 | `PASS` |
