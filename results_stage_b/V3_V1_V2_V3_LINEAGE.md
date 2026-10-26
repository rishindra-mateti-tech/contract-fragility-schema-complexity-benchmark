# Stage B Extraction Pipeline Lineage: V1 vs V2 vs V3

**Date:** October 26, 2026  
**Comparative Scope:** Evolutionary tracking across Batch Extraction Pipelines V1, V2, and V3.  

---

## 1. Evolution and Capability Matrix

| Architectural Feature | Batch Pipeline V1 | Batch Pipeline V2 | Batch Pipeline V3 |
| :--- | :--- | :--- | :--- |
| **Pipeline Version** | `1.0.0` | `2.0.0` | `3.0.0` |
| **Governing Policies** | `WRAPPER_CLOSED_OBJECT_POLICY_001` | `OAS30_TO_DRAFT07_CONVERSION_POLICY_001` | 4 Governing Policies (Dialect, Ref, Param, FormData) |
| **Dialect Handling** | Verbatim `nullable: true` copy (inert in Draft-07) | Syntactic conversion: `type: [<T>, "null"]` | Retained Policy 001 dialect conversion |
| **Artifacts Per Bundle** | 8 artifacts | 8 artifacts | 11 artifacts (added closure & adapter decisions) |
| **Path Parameter Inheritance** | Unsupported (rejected fail-closed) | Unsupported (rejected fail-closed) | Supported via `ParameterInheritanceAdapter` |
| **OpenAPI 2.0 FormData Surface** | Unsupported (rejected fail-closed) | Unsupported (rejected fail-closed) | Supported via `OpenAPI2FormDataAdapter` |
| **Local Multi-File Resolution** | Unsupported (rejected fail-closed) | Unsupported (rejected fail-closed) | Bounded framework via `LocalReferenceResolver` |
| **AST Source Code Handling** | Rejected fail-closed | Rejected fail-closed | Rejected fail-closed |
| **Polymorphic Union Handling** | Rejected fail-closed | Rejected fail-closed | Rejected fail-closed |
| **Output Directory Quarantine** | `data_stage_b/extraction_candidates/` | `data_stage_b/extraction_candidates_v2/` | `data_stage_b/extraction_candidates_v3/` |
| **Candidates Generated** | 13 | 13 | **18** |
| **Operations Rejected** | 14 | 14 | **10** |
| **Pilots Skipped** | 2 | 2 | 2 |
| **Total Operations Accounted** | 30 | 30 | 30 |

---

## 2. Granular Operations Progression

| Slot ID | Operation ID | Source ID | Pipeline V1 Status | Pipeline V2 Status | Pipeline V3 Status | V3 Key Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_GITHUB_01` | `pulls/create` | `CAND-001` | Skipped (Pilot) | Skipped (Pilot) | Skipped (Pilot) | Existing Canonical Pilot |
| `SLOT_STRIPE_02` | `PostShippingRates` | `CAND-002` | Skipped (Pilot) | Skipped (Pilot) | Skipped (Pilot) | Existing Canonical Pilot |
| `SLOT_BOX_01` | `post_folders` | `CAND-005` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_BOX_02` | `post_collaborations` | `CAND-005` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_BOX_03` | `post_users` | `CAND-005` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `CAND-011` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CAND-011` | Rejected | Rejected | **Extracted (V3 Bundle)** | `ParameterInheritanceAdapter` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CAND-011` | Rejected | Rejected | **Extracted (V3 Bundle)** | `ParameterInheritanceAdapter` |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | `CAND-001` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | `CAND-001` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_LINE_01` | `showLoadingAnimation` | `CAND-013` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_LINE_02` | `setWebhookEndpoint` | `CAND-013` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_LINE_03` | `markMessagesAsRead` | `CAND-013` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_SLACK_01` | `conversations.create` | `CAND-006` | Rejected | Rejected | **Extracted (V3 Bundle)** | `OpenAPI2FormDataAdapter` |
| `SLOT_SLACK_02` | `users.profile.set` | `CAND-006` | Rejected | Rejected | **Extracted (V3 Bundle)** | `OpenAPI2FormDataAdapter` |
| `SLOT_SLACK_03` | `reminders.add` | `CAND-006` | Rejected | Rejected | **Extracted (V3 Bundle)** | `OpenAPI2FormDataAdapter` |
| `SLOT_STRIPE_01` | `PostPayouts` | `CAND-002` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_TWILIO_01` | `UpdateAccount` | `CAND-004` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_TWILIO_02` | `CreateMessage` | `CAND-004` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_TWILIO_03` | `CreateCall` | `CAND-004` | Extracted | Extracted (Policy 001) | Extracted (V3 Bundle) | Standard OAS 3.0 |
| `SLOT_DO_01` | `floating_ips_create` | `CAND-003` | Rejected | Rejected | Rejected | Missing target file on disk |
| `SLOT_DO_02` | `domains_create` | `CAND-003` | Rejected | Rejected | Rejected | Missing target file on disk |
| `SLOT_DO_03` | `droplets_create` | `CAND-003` | Rejected | Rejected | Rejected | Missing target file on disk |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CAND-010` | Rejected | Rejected | Rejected | TypeScript AST source code |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CAND-010` | Rejected | Rejected | Rejected | TypeScript AST source code |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CAND-010` | Rejected | Rejected | Rejected | TypeScript AST source code |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CAND-009` | Rejected | Rejected | Rejected | Python AST source code |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CAND-009` | Rejected | Rejected | Rejected | Python AST source code |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CAND-009` | Rejected | Rejected | Rejected | Python AST source code |
| `SLOT_STRIPE_03` | `PostRefunds` | `CAND-002` | Rejected | Rejected | Rejected | Polymorphic union schema |

---

## 3. Immutability Assurances

Historical V1 artifacts in `data_stage_b/extraction_candidates/` and V2 artifacts in `data_stage_b/extraction_candidates_v2/` remain byte-for-byte immutable. Pipeline V3 operates strictly in its dedicated quarantine directory `data_stage_b/extraction_candidates_v3/` without modifying prior outputs.
