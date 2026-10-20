# Stage B Full-Cohort Extraction Readiness Matrix

## Cohort Summary
- **Audited At (UTC)**: `2026-10-20T04:01:41Z`
- **Total Tracked Operations**: `37`
- **Active Benchmark Operations**: `30`
- **Excluded Operations**: `7`

### Readiness Distribution
| Readiness State | Active Count | Excluded Count | Total Count |
| :--- | :---: | :---: | :---: |
| `READY_FOR_EXTRACTION` | 0 | 0 | 0 |
| `READY_WITH_EXPLICIT_WRAPPER_POLICY` | 6 | 0 | 6 |
| `REQUIRES_PROTOCOL_AMENDMENT` | 1 | 0 | 1 |
| `REQUIRES_EXTRACTOR_CAPABILITY` | 23 | 0 | 23 |
| `EXCLUDED` | 0 | 7 | 7 |

---

## Active Operations Readiness Ledger (30 Operations)

| Slot ID | Operation ID | Cluster | Format | Content-Type | Depth | Refs | Readiness State | Blockers / Status |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :--- |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | `CLUSTER_GITHUB` | `.json` | `application/json` | 2 | 0 | `READY_WITH_EXPLICIT_WRAPPER_POLICY` | None (Supported with wrapper policy) |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | `CLUSTER_GITHUB` | `.json` | `application/json` | 2 | 0 | `READY_WITH_EXPLICIT_WRAPPER_POLICY` | None (Supported with wrapper policy) |
| `SLOT_STRIPE_03` | `PostRefunds` | `CLUSTER_STRIPE` | `.json` | `application/x-www-form-urlencoded` | 4 | 0 | `REQUIRES_PROTOCOL_AMENDMENT` | Operation declares polymorphic unions (oneOf=0, anyOf=2, discriminator=0).; Candidate declared as faithful union under Amendment 003; requires ratified multi-schema extraction protocol. |
| `SLOT_DO_01` | `floating_ips_create` | `CLUSTER_DIGITALOCEAN` | `.yaml` | `N/A` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_DO_02` | `domains_create` | `CLUSTER_DIGITALOCEAN` | `.yaml` | `N/A` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_DO_03` | `droplets_create` | `CLUSTER_DIGITALOCEAN` | `.yaml` | `N/A` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_TWILIO_01` | `UpdateAccount` | `CLUSTER_TWILIO` | `.yaml` | `application/x-www-form-urlencoded` | 3 | 1 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_TWILIO_02` | `CreateMessage` | `CLUSTER_TWILIO` | `.yaml` | `application/x-www-form-urlencoded` | 3 | 5 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_TWILIO_03` | `CreateCall` | `CLUSTER_TWILIO` | `.yaml` | `application/x-www-form-urlencoded` | 3 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_BOX_01` | `post_folders` | `CLUSTER_BOX` | `.json` | `application/json` | 4 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation declares 1 query parameters; extractor currently produces empty query containers. |
| `SLOT_BOX_02` | `post_collaborations` | `CLUSTER_BOX` | `.json` | `application/json` | 3 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation declares 2 query parameters; extractor currently produces empty query containers. |
| `SLOT_BOX_03` | `post_users` | `CLUSTER_BOX` | `.json` | `application/json` | 5 | 1 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation declares 1 query parameters; extractor currently produces empty query containers. |
| `SLOT_SLACK_01` | `conversations.create` | `CLUSTER_SLACK` | `.json` | `application/json, application/x-www-form-urlencoded` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation declares 1 header parameters; extractor currently produces empty header containers.; Operation declares Swagger 2.0 in:formData parameters; extractor currently requires requestBody.content. |
| `SLOT_SLACK_02` | `users.profile.set` | `CLUSTER_SLACK` | `.json` | `application/json, application/x-www-form-urlencoded` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation declares 1 header parameters; extractor currently produces empty header containers.; Operation declares Swagger 2.0 in:formData parameters; extractor currently requires requestBody.content. |
| `SLOT_SLACK_03` | `reminders.add` | `CLUSTER_SLACK` | `.json` | `application/json, application/x-www-form-urlencoded` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation declares 1 header parameters; extractor currently produces empty header containers.; Operation declares Swagger 2.0 in:formData parameters; extractor currently requires requestBody.content. |
| `SLOT_MCP_SQLITE_01` | `read_query` | `CLUSTER_MCP_SQLITE` | `.py` | `application/json` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Source file is code (.py); current extractor script only traverses OpenAPI/Swagger specifications, not Python/TypeScript ASTs. |
| `SLOT_MCP_SQLITE_02` | `describe_table` | `CLUSTER_MCP_SQLITE` | `.py` | `application/json` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Source file is code (.py); current extractor script only traverses OpenAPI/Swagger specifications, not Python/TypeScript ASTs. |
| `SLOT_MCP_SQLITE_03` | `write_query` | `CLUSTER_MCP_SQLITE` | `.py` | `application/json` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Source file is code (.py); current extractor script only traverses OpenAPI/Swagger specifications, not Python/TypeScript ASTs. |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | `CLUSTER_MCP_GITHUB` | `.ts` | `application/json` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Source file is code (.ts); current extractor script only traverses OpenAPI/Swagger specifications, not Python/TypeScript ASTs. |
| `SLOT_MCP_GITHUB_02` | `create_issue` | `CLUSTER_MCP_GITHUB` | `.ts` | `application/json` | 2 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Source file is code (.ts); current extractor script only traverses OpenAPI/Swagger specifications, not Python/TypeScript ASTs. |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | `CLUSTER_MCP_GITHUB` | `.ts` | `application/json` | 1 | 0 | `REQUIRES_EXTRACTOR_CAPABILITY` | Source file is code (.ts); current extractor script only traverses OpenAPI/Swagger specifications, not Python/TypeScript ASTs. |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | `CLUSTER_CHATWOOT` | `.json` | `application/json` | 3 | 1 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation defines 1 path-level parameter(s) on parent path item not inherited in operation parameters. |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | `CLUSTER_CHATWOOT` | `.json` | `application/json` | 3 | 1 | `REQUIRES_EXTRACTOR_CAPABILITY` | Operation defines 2 path-level parameter(s) on parent path item not inherited in operation parameters. |
| `SLOT_LINE_02` | `setWebhookEndpoint` | `CLUSTER_LINE` | `.yml` | `application/json` | 3 | 1 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_LINE_03` | `markMessagesAsRead` | `CLUSTER_LINE` | `.yml` | `application/json` | 5 | 2 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |
| `SLOT_GITHUB_01` | `pulls/create` | `CLUSTER_GITHUB` | `.json` | `application/json` | 2 | 0 | `READY_WITH_EXPLICIT_WRAPPER_POLICY` | None (Supported with wrapper policy) |
| `SLOT_STRIPE_01` | `PostPayouts` | `CLUSTER_STRIPE` | `.json` | `application/x-www-form-urlencoded` | 3 | 0 | `READY_WITH_EXPLICIT_WRAPPER_POLICY` | None (Supported with wrapper policy) |
| `SLOT_STRIPE_02` | `PostShippingRates` | `CLUSTER_STRIPE` | `.json` | `application/x-www-form-urlencoded` | 5 | 0 | `READY_WITH_EXPLICIT_WRAPPER_POLICY` | None (Supported with wrapper policy) |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `CLUSTER_CHATWOOT` | `.json` | `application/json` | 4 | 1 | `READY_WITH_EXPLICIT_WRAPPER_POLICY` | None (Supported with wrapper policy) |
| `SLOT_LINE_01` | `showLoadingAnimation` | `CLUSTER_LINE` | `.yml` | `application/json` | 3 | 1 | `REQUIRES_EXTRACTOR_CAPABILITY` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration. |

---

## Excluded Operations Ledger (7 Disqualified Operations)

| Operation ID | Cluster | Disqualification Root Cause |
| :--- | :--- | :--- |
| `chat.postMessage` | `CLUSTER_SLACK` | Operation declares 1 header parameters; extractor currently produces empty header containers.; Operation declares Swagger 2.0 in:formData parameters; extractor currently requires requestBody.content. |
| `pushMessage` | `CLUSTER_LINE` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration.; Operation declares 1 header parameters; extractor currently produces empty header containers.; Operation declares polymorphic unions (oneOf=0, anyOf=0, discriminator=2). |
| `replyMessage` | `CLUSTER_LINE` | Raw file is YAML (.yaml/.yml); current extractor script requires JSON parser integration.; Operation declares polymorphic unions (oneOf=0, anyOf=0, discriminator=2). |
| `create-a-contact` | `CLUSTER_CHATWOOT` | Operation defines 1 path-level parameter(s) on parent path item not inherited in operation parameters. |
| `issues/create` | `CLUSTER_GITHUB` | Operation declares polymorphic unions (oneOf=9, anyOf=0, discriminator=0). |
| `PostCustomers` | `CLUSTER_STRIPE` | Operation declares polymorphic unions (oneOf=0, anyOf=16, discriminator=0). |
| `PostPaymentIntents` | `CLUSTER_STRIPE` | Operation declares polymorphic unions (oneOf=0, anyOf=188, discriminator=0). |
