# Stage B Full-Cohort Extraction Readiness Audit Report

## 1. Executive Overview
This static audit evaluates all 30 active Stage B candidate operations and 7 tracked excluded operations against the capabilities of the current Stage B extraction engine. Rather than assuming candidates are extractable from top-level summaries, this audit recursively traverses the pinned raw specifications to assess concrete schema constructs, transport surfaces, and serialization requirements.

### Key Findings
1. **Currently Extractable Operations (6 / 30)**: Five active operations (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`, `SLOT_STRIPE_01`, `SLOT_GITHUB_02`, `SLOT_GITHUB_03`) can be extracted with zero semantic loss under the approved `WRAPPER_CLOSED_OBJECT_POLICY_001`.
2. **Operations Requiring Extractor Capabilities (23 / 30)**: 24 active operations require specific engineering capabilities before extraction can proceed safely without data loss:
   - **YAML Specification Support (9 operations)**: DigitalOcean (3), Twilio (3), and LINE (3) use YAML raw files. Current extractor expects JSON.
   - **Swagger 2.0 in:body Parameter Support (3 operations)**: Chatwoot operations declare bodies in parameter lists instead of OpenAPI 3.0 requestBody.
   - **Query & Header Parameter Surfaces (6 operations)**: Box and Slack operations require extracting query strings and header parameters into tool surfaces.
   - **MCP Codebase AST Tool Extraction (6 operations)**: SQLite (Python) and GitHub MCP (TypeScript) define schemas in code rather than OpenAPI documents.
3. **Operations Requiring Protocol Amendments (1 / 30)**: `PostRefunds` (`SLOT_STRIPE_03`) contains polymorphic union schemas and is governed under Amendment 003.

---

## 2. Granular Cluster-by-Cluster Analysis

### Cluster: `CLUSTER_BOX`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_BOX_01` | `post_folders` | Yes | 4 | 3 / 6 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_BOX_02` | `post_collaborations` | Yes | 3 | 4 / 11 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_BOX_03` | `post_users` | Yes | 5 | 1 / 21 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |

### Cluster: `CLUSTER_CHATWOOT`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_CHATWOOT_02` | `create-an-account-user` | Yes | 3 | 2 / 2 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_CHATWOOT_03` | `create-a-conversation` | Yes | 3 | 0 / 1 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | Yes | 4 | 0 / 3 | application/json | `READY_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_CAND-011_create-a-contact` | `create-a-contact` | No (Excluded) | 3 | 0 / 7 | application/json | `EXCLUDED` |

### Cluster: `CLUSTER_DIGITALOCEAN`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_DO_01` | `floating_ips_create` | Yes | 1 | 0 / 0 | None | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_DO_02` | `domains_create` | Yes | 1 | 0 / 0 | None | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_DO_03` | `droplets_create` | Yes | 1 | 0 / 0 | None | `REQUIRES_EXTRACTOR_CAPABILITY` |

### Cluster: `CLUSTER_GITHUB`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_GITHUB_02` | `repos/create-commit-status` | Yes | 2 | 1 / 4 | application/json | `READY_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | Yes | 2 | 1 / 23 | application/json | `READY_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_GITHUB_01` | `pulls/create` | Yes | 2 | 2 / 8 | application/json | `READY_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_CAND-001_issues/create` | `issues/create` | No (Excluded) | 6 | 3 / 15 | application/json | `EXCLUDED` |

### Cluster: `CLUSTER_LINE`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_LINE_02` | `setWebhookEndpoint` | Yes | 3 | 1 / 1 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_LINE_03` | `markMessagesAsRead` | Yes | 5 | 2 / 2 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_LINE_01` | `showLoadingAnimation` | Yes | 3 | 1 / 2 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_CAND-013_pushMessage` | `pushMessage` | No (Excluded) | 13 | 3 / 15 | application/json | `EXCLUDED` |
| `SLOT_CAND-013_replyMessage` | `replyMessage` | No (Excluded) | 13 | 3 / 14 | application/json | `EXCLUDED` |

### Cluster: `CLUSTER_MCP_GITHUB`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_MCP_GITHUB_01` | `search_repositories` | Yes | 1 | 1 / 3 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_MCP_GITHUB_02` | `create_issue` | Yes | 2 | 3 / 7 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_MCP_GITHUB_03` | `create_or_update_file` | Yes | 1 | 5 / 5 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |

### Cluster: `CLUSTER_MCP_SQLITE`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_MCP_SQLITE_01` | `read_query` | Yes | 1 | 1 / 1 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_MCP_SQLITE_02` | `describe_table` | Yes | 1 | 1 / 1 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_MCP_SQLITE_03` | `write_query` | Yes | 1 | 1 / 1 | application/json | `REQUIRES_EXTRACTOR_CAPABILITY` |

### Cluster: `CLUSTER_SLACK`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_SLACK_01` | `conversations.create` | Yes | 1 | 0 / 0 | application/json, application/x-www-form-urlencoded | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_SLACK_02` | `users.profile.set` | Yes | 1 | 0 / 0 | application/json, application/x-www-form-urlencoded | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_SLACK_03` | `reminders.add` | Yes | 1 | 0 / 0 | application/json, application/x-www-form-urlencoded | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_CAND-006_chat.postMessage` | `chat.postMessage` | No (Excluded) | 1 | 0 / 0 | application/json, application/x-www-form-urlencoded | `EXCLUDED` |

### Cluster: `CLUSTER_STRIPE`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_STRIPE_03` | `PostRefunds` | Yes | 4 | 0 / 12 | application/x-www-form-urlencoded | `REQUIRES_PROTOCOL_AMENDMENT` |
| `SLOT_STRIPE_01` | `PostPayouts` | Yes | 3 | 2 / 10 | application/x-www-form-urlencoded | `READY_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_STRIPE_02` | `PostShippingRates` | Yes | 5 | 8 / 19 | application/x-www-form-urlencoded | `READY_WITH_EXPLICIT_WRAPPER_POLICY` |
| `SLOT_CAND-002_PostCustomers` | `PostCustomers` | No (Excluded) | 6 | 6 / 51 | application/x-www-form-urlencoded | `EXCLUDED` |
| `SLOT_CAND-002_PostPaymentIntents` | `PostPaymentIntents` | No (Excluded) | 9 | 49 / 492 | application/x-www-form-urlencoded | `EXCLUDED` |

### Cluster: `CLUSTER_TWILIO`

| Slot ID | Operation ID | Active? | Depth | Required / Total | Content-Type | Readiness State |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `SLOT_TWILIO_01` | `UpdateAccount` | Yes | 3 | 0 / 2 | application/x-www-form-urlencoded | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_TWILIO_02` | `CreateMessage` | Yes | 3 | 1 / 26 | application/x-www-form-urlencoded | `REQUIRES_EXTRACTOR_CAPABILITY` |
| `SLOT_TWILIO_03` | `CreateCall` | Yes | 3 | 2 / 38 | application/x-www-form-urlencoded | `REQUIRES_EXTRACTOR_CAPABILITY` |

---

## 3. Extractor Capability Gap Analysis

| Capability Gap | Affected Clusters | Affected Operations | Recommended Implementation Path |
| :--- | :--- | :---: | :--- |
| **YAML Parser Support** | DigitalOcean, Twilio, LINE | 9 | Integrate `yaml.safe_load` fallback when file extension is `.yaml` or `.yml`. |
| **Swagger 2.0 `in: body`** | Chatwoot | 3 | Add branch in extractor detecting `in: body` parameters and mapping to canonical body container. |
| **Query Parameter Extraction** | Box, Slack | 6 | Map `in: query` parameters into canonical `/properties/query/properties` container. |
| **Header Parameter Extraction** | Slack, Twilio | 3 | Map non-auth `in: header` parameters into `/properties/header/properties` container. |
| **MCP Tool AST Parser** | MCP SQLite, MCP GitHub | 6 | Parse Python AST (`server.py`) and TypeScript AST (`index.ts`) into canonical Draft-07 schemas. |
| **Polymorphic Union Protocol** | Stripe (`PostRefunds`) | 1 | Ratify explicit benchmark union evaluation protocol under Amendment 003. |

---

## 4. Verification and Governance Protocol
- All raw sources audited in this report have been verified for byte-exact Git blob SHA and SHA-256 match against the provenance registry.
- No canonical contracts were created or altered during this audit.
- `SLOT_STRIPE_02` remains strictly in `EXTRACTED_PENDING_HUMAN_VALIDATION`.
- Status `CANONICAL_FAITHFUL` remains strictly unassigned.
