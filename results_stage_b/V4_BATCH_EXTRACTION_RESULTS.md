# Stage B Batch Extraction Pipeline V4 Results

**Execution Date:** October 26, 2026  
**Pipeline Version:** `4.0.0`  
**Lifecycle Status Assigned:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  
**Quarantined Output Base:** `data_stage_b/extraction_candidates_v4/`  
**Independent Reviews Completed:** `0` (Strict Epistemic Boundary)  

---

## 1. Accounting Summary across Active Manifest Operations

| Metric Category | Count | Methodological Notes |
| :--- | :---: | :--- |
| **Total Active Manifest Operations** | **30** | Complete set of admitted Stage B operations. |
| **Existing Pilots Skipped** | **2** | `SLOT_GITHUB_01` and `SLOT_STRIPE_02` preserved byte-identically. |
| **Eligible Operations Attempted** | **28** | Evaluated under Pipeline 4.0.0. |
| **Candidates Successfully Generated (V4)** | **22** | Quarantined with 13 audit artifacts each. |
| -- Monomorphic OpenAPI (Unadapted) | 12 | Direct conversion under Policy 001. |
| -- Local Reference Resolver (`LocalReferenceResolver`) | 1 | `SLOT_DO_01` resolved via pinned source closure. |
| -- Parameter Inheritance (`ParameterInheritanceAdapter`) | 3 | Path-level parameters inherited on Chatwoot operations. |
| -- FormData Adapter (`OpenAPI2FormDataAdapter`) | 3 | Slack OpenAPI 2.0 formData mapped to form surface. |
| -- Python AST Adapter (`PythonAstToolExtractor`) | 3 | Pure static AST extraction for SQLite MCP tools. |
| -- TypeScript AST Adapter (`TypeScriptAstToolExtractor`) | 0 | Evaluated statically; all 3 rejected fail-closed. |
| **Operations Rejected Fail-Closed** | **6** | Documented in `V4_REJECTION_REGISTER.md`. |
| **Remaining Blocked Union Slots** | 1 | `SLOT_STRIPE_03` (polymorphic union requires Amendment 003). |
| **Remaining Blocked ReadOnly Request Slots** | 2 | `SLOT_DO_02`, `SLOT_DO_03` (`readOnly: true` on request surface). |
| **Remaining Blocked Dynamic TS Builder Slots** | 3 | `SLOT_MCP_GITHUB_01-03` (`zodToJsonSchema` dynamic runtime builders). |
| **Independent Human Reviews Completed** | **0** | Zero promotions to `CANONICAL_FAITHFUL`. |

---

## 2. Generated Candidate Cohort (22 Bundles)

| Slot ID | Operation ID | Source Dialect | Adapters Applied | Surfaces | Props | Req | Depth | Contract SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `SLOT_BOX_01` | `post_folders` | OpenAPI 3.0.2 | None | `body, query` | 2 | 0 | 5 | `8a809181ab139378...` |
| `SLOT_BOX_02` | `post_collaborations` | OpenAPI 3.0.2 | None | `body, query` | 2 | 0 | 4 | `051447d1104563b0...` |
| `SLOT_BOX_03` | `post_users` | OpenAPI 3.0.2 | None | `body, query` | 2 | 0 | 5 | `681abb137af1f033...` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 2 | 2 | 4 | `b5f8c68c4f874f45...` |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 2 | 2 | 3 | `930ac80c9aa789dc...` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | OpenAPI 3.1.0 | ParameterInheritanceAdapter | `body, path` | 2 | 2 | 3 | `78c770753bab0ffc...` |
| `SLOT_DO_01` | `floating_ips_create` | OpenAPI 3.0.0 | LocalReferenceResolver | `None` | 1 | 1 | 4 | `da4a4de3ad4ced30...` |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | OpenAPI 3.0.3 | None | `body, path` | 2 | 2 | 3 | `52101953ba1fcd28...` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | OpenAPI 3.0.3 | None | `body` | 1 | 1 | 3 | `37b950a9f8839677...` |
| `SLOT_LINE_01` | `showLoadingAnimation` | OpenAPI 3.0.0 | None | `body` | 1 | 1 | 3 | `209ced6d6b70a489...` |
| `SLOT_LINE_02` | `setWebhookEndpoint` | OpenAPI 3.0.0 | None | `body` | 1 | 1 | 3 | `2740fa0f3dd1cf8c...` |
| `SLOT_LINE_03` | `markMessagesAsRead` | OpenAPI 3.0.0 | None | `body` | 1 | 1 | 4 | `b26d9d2190863ded...` |
| `SLOT_MCP_SQLITE_01` | `read_query` | Python 3 AST | PythonAstToolExtractor | `rpc_arguments` | 1 | 1 | 2 | `89bcb10822856641...` |
| `SLOT_MCP_SQLITE_02` | `describe_table` | Python 3 AST | PythonAstToolExtractor | `rpc_arguments` | 1 | 1 | 2 | `49580f6765cd7cf4...` |
| `SLOT_MCP_SQLITE_03` | `write_query` | Python 3 AST | PythonAstToolExtractor | `rpc_arguments` | 1 | 1 | 2 | `bd65fe36f0f574a2...` |
| `SLOT_SLACK_01` | `conversations.create` | OpenAPI 2.0 | OpenAPI2FormDataAdapter | `form, header` | 2 | 0 | 3 | `28b70e9d402326d4...` |
| `SLOT_SLACK_02` | `users.profile.set` | OpenAPI 2.0 | OpenAPI2FormDataAdapter | `form, header` | 2 | 1 | 3 | `dc8b01901fa51364...` |
| `SLOT_SLACK_03` | `reminders.add` | OpenAPI 2.0 | OpenAPI2FormDataAdapter | `form, header` | 2 | 2 | 3 | `0ef02058cd82e805...` |
| `SLOT_STRIPE_01` | `PostPayouts` | OpenAPI 3.0.0 | None | `body` | 1 | 1 | 4 | `6e451eb90ab48ae6...` |
| `SLOT_TWILIO_01` | `UpdateAccount` | OpenAPI 3.0.1 | None | `body, path` | 2 | 1 | 3 | `cab1d96b6ef41164...` |
| `SLOT_TWILIO_02` | `CreateMessage` | OpenAPI 3.0.1 | None | `body, path` | 2 | 1 | 4 | `8b871cf394b99ea9...` |
| `SLOT_TWILIO_03` | `CreateCall` | OpenAPI 3.0.1 | None | `body, path` | 2 | 1 | 4 | `8738e94043ada0b2...` |

---

## 3. Strict Epistemic Invariants Enforced

1. **Quarantine Preserved:** All 22 bundles declare `lifecycle_status = "EXTRACTED_PENDING_HUMAN_VALIDATION"`.
2. **Zero `CANONICAL_FAITHFUL`:** Zero occurrences exist across all generated bundles.
3. **Zero Host Execution:** Python and TypeScript sources were analyzed solely via static syntax trees.
4. **Zero Network / API Calls:** Offline verification against pinned repository source files.
