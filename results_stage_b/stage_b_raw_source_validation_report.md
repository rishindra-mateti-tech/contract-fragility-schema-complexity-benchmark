# Stage B Raw Source Validation Report (Corrected)

## 1. Executive Summary & Audit History
- **Initial Bundle Status**: **`REJECTED (BYTE_INTEGRITY_FAILURE)`**
  - *Root Cause Diagnosis*: Default Git on Windows (`core.autocrlf=true`) without an explicit `.gitattributes` rule converted line endings (LF to CRLF) on fresh clone checkout. For example, `CAND-001` (`api.github.com.json`) expanded by 347,366 carriage return bytes (13,018,090 bytes -> 13,365,456 bytes), altering its computed Git blob SHA and failing fresh-clone identity checks.
  - *Remediation Applied*: Root `.gitattributes` established with `data_stage_b/raw/** -text` and `data_stage_b/** -text`, permanently disabling text and EOL normalization for all raw experimental artifacts across platforms.
- **Corrected Bundle Status**: **`APPROVED & VERIFIED (BINARY_EXACT)`**
  - All 10 raw source files re-fetched using binary-safe byte writes (`wb`) directly from pinned immutable commit SHAs.
  - Git blob SHA-1 (`sha1("blob <len>\0" + raw_bytes)`) strictly verified against pinned GitHub Contents API values.
  - Clean SHA-256 hashes recomputed over exact raw bytes and recorded in sidecars.
  - 100% deterministic pointer resolution confirmed across all 30 candidate operations.
  - Automated test suite updated to report all source mismatches exhaustively.

---

## 2. Corrected Raw Sources & Provenance Verification

| Source ID | Project | Source File Path | Git Blob SHA | Binary File SHA-256 | Size (Bytes) | Status | Bound Ops |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`CAND-001`** | GitHub | `descriptions/api.github.com/api.github.com.json` | `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d` | `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194` | 13,018,090 | **VERIFIED** | 3 ops |
| **`CAND-002`** | Stripe | `openapi/spec3.json` | `f1cedf38e0178538a3c72e750da80226df41e28c` | `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776` | 8,317,513 | **VERIFIED** | 3 ops |
| **`CAND-003`** | DigitalOcean | `specification/DigitalOcean-public.v2.yaml` | `a26d71aa637fd6c6241602e9862eae7fb3d1ed95` | `e18ad525a336da3dd83776659d5b574e30748b1d59efc53a42c86115b290a76a` | 124,775 | **VERIFIED** | 3 ops |
| **`CAND-004`** | Twilio | `spec/yaml/twilio_api_v2010.yaml` | `5b2e77834f20cbe5d3efeffd27326381fee6b07e` | `052b294839a56c89a921c77639305d99ad15be6e248bdeaef8975aea6cfcb339` | 1,504,725 | **VERIFIED** | 3 ops |
| **`CAND-005`** | Box | `openapi.json` | `e740e641b82d30e398a2a0d1b14b4c052e310422` | `13cc601e01a7b82133975aaf7aeffb1850159a10ac6365fae00d5af94406d9d4` | 1,781,543 | **VERIFIED** | 3 ops |
| **`CAND-006`** | Slack | `web-api/slack_web_openapi_v2_without_examples.json` | `f7b1affd1fb34f9473cd87980428883019b29c07` | `8b92da26a3c5b11d20042a9f36d81f1fa6fc9382c5ddc471babb68b91936bc3a` | 1,039,581 | **VERIFIED** | 3 ops |
| **`CAND-009`** | MCP SQLite | `src/sqlite/src/mcp_server_sqlite/server.py` | `1b97a6a4903bd8961941cdff43df3b059e610e5f` | `d3d58a605315e6bf360b43178d8a0a54a9098931bbc00974221ccf3d8e9ba863` | 18,533 | **VERIFIED** | 3 ops |
| **`CAND-010`** | MCP GitHub | `src/github/index.ts` | `0676a34c85537e610f911fbd73a5a079f38be18e` | `bb964ea5a47c00205805317a5a8066a955c59f500073a7c2cf0c2b4020ddeb3a` | 18,123 | **VERIFIED** | 3 ops |
| **`CAND-011`** | Chatwoot | `swagger/swagger.json` | `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589` | `c8cba6e5975ee286593866f20652e29154717b835dc6324af7433bb497e7ab43` | 537,652 | **VERIFIED** | 3 ops |
| **`CAND-013`** | LINE | `messaging-api.yml` | `11f1fdb91092246f881edd1a9457cb37327a6c5d` | `41033aa8491fc67ab09c4ec322f2aab072ae7b9402297e8c4f042eda0c2dd1fc` | 190,228 | **VERIFIED** | 3 ops |

---

## 3. Operation Pointer Resolution Audit (30 Operations)

| Cluster ID | Operation ID | HTTP / RPC | Spec Pointer | Resolution Status | Matched Spec Keys / Symbol |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CLUSTER_GITHUB` | `repos/create-commit-status` | POST | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | **RESOLVED** | `summary`, `description`, `tags` |
| `CLUSTER_GITHUB` | `issues/create` | POST | `#/paths/~1repos~1{owner}~1{repo}~1issues/post` | **RESOLVED** | `summary`, `description`, `tags` |
| `CLUSTER_GITHUB` | `repos/create-for-authenticated-user` | POST | `#/paths/~1user~1repos/post` | **RESOLVED** | `summary`, `description`, `tags` |
| `CLUSTER_STRIPE` | `PostRefunds` | POST | `#/paths/~1v1~1refunds/post` | **RESOLVED** | `description`, `operationId`, `requestBody` |
| `CLUSTER_STRIPE` | `PostCustomers` | POST | `#/paths/~1v1~1customers/post` | **RESOLVED** | `description`, `operationId`, `requestBody` |
| `CLUSTER_STRIPE` | `PostPaymentIntents` | POST | `#/paths/~1v1~1payment_intents/post` | **RESOLVED** | `description`, `operationId`, `requestBody` |
| `CLUSTER_DIGITALOCEAN` | `floating_ips_create` | POST | `#/paths/~1v2~1floating_ips/post` | **RESOLVED** | `$ref` |
| `CLUSTER_DIGITALOCEAN` | `domains_create` | POST | `#/paths/~1v2~1domains/post` | **RESOLVED** | `$ref` |
| `CLUSTER_DIGITALOCEAN` | `droplets_create` | POST | `#/paths/~1v2~1droplets/post` | **RESOLVED** | `$ref` |
| `CLUSTER_TWILIO` | `UpdateAccount` | POST | `#/paths/~12010-04-01~1Accounts~1{Sid}.json/post` | **RESOLVED** | `description`, `summary`, `tags` |
| `CLUSTER_TWILIO` | `CreateMessage` | POST | `#/paths/~12010-04-01~1Accounts~1{AccountSid}~1Messages.json/post` | **RESOLVED** | `description`, `summary`, `tags` |
| `CLUSTER_TWILIO` | `CreateCall` | POST | `#/paths/~12010-04-01~1Accounts~1{AccountSid}~1Calls.json/post` | **RESOLVED** | `description`, `summary`, `tags` |
| `CLUSTER_BOX` | `post_folders` | POST | `#/paths/~1folders/post` | **RESOLVED** | `operationId`, `summary`, `description` |
| `CLUSTER_BOX` | `post_collaborations` | POST | `#/paths/~1collaborations/post` | **RESOLVED** | `operationId`, `summary`, `description` |
| `CLUSTER_BOX` | `post_users` | POST | `#/paths/~1users/post` | **RESOLVED** | `operationId`, `summary`, `description` |
| `CLUSTER_SLACK` | `conversations.create` | POST | `#/paths/~1conversations.create/post` | **RESOLVED** | `consumes`, `description`, `externalDocs` |
| `CLUSTER_SLACK` | `users.profile.set` | POST | `#/paths/~1users.profile.set/post` | **RESOLVED** | `consumes`, `description`, `externalDocs` |
| `CLUSTER_SLACK` | `chat.postMessage` | POST | `#/paths/~1chat.postMessage/post` | **RESOLVED** | `consumes`, `description`, `externalDocs` |
| `CLUSTER_MCP_SQLITE` | `read_query` | RPC | `server.py:list_tools:read-query` | **RESOLVED** | `name="read-query"` |
| `CLUSTER_MCP_SQLITE` | `describe_table` | RPC | `server.py:list_tools:describe-table` | **RESOLVED** | `name="describe-table"` |
| `CLUSTER_MCP_SQLITE` | `write_query` | RPC | `server.py:list_tools:write-query` | **RESOLVED** | `name="write-query"` |
| `CLUSTER_MCP_GITHUB` | `search_repositories` | RPC | `src/github/index.ts:search_repositories` | **RESOLVED** | `name: "search_repositories"` |
| `CLUSTER_MCP_GITHUB` | `create_issue` | RPC | `src/github/index.ts:create_issue` | **RESOLVED** | `name: "create_issue"` |
| `CLUSTER_MCP_GITHUB` | `create_or_update_file` | RPC | `src/github/index.ts:create_or_update_file` | **RESOLVED** | `name: "create_or_update_file"` |
| `CLUSTER_CHATWOOT` | `create-an-account-user` | POST | `#/paths/~1platform~1api~1v1~1accounts~1{account_id}~1account_users/post` | **RESOLVED** | `tags`, `operationId`, `summary` |
| `CLUSTER_CHATWOOT` | `create-a-contact` | POST | `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts/post` | **RESOLVED** | `tags`, `operationId`, `summary` |
| `CLUSTER_CHATWOOT` | `create-a-conversation` | POST | `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts~1{contact_identifier}~1conversations/post` | **RESOLVED** | `tags`, `operationId`, `summary` |
| `CLUSTER_LINE` | `setWebhookEndpoint` | PUT | `#/paths/~1v2~1bot~1channel~1webhook~1endpoint/put` | **RESOLVED** | `externalDocs`, `tags`, `operationId` |
| `CLUSTER_LINE` | `replyMessage` | POST | `#/paths/~1v2~1bot~1message~1reply/post` | **RESOLVED** | `externalDocs`, `tags`, `operationId` |
| `CLUSTER_LINE` | `pushMessage` | POST | `#/paths/~1v2~1bot~1message~1push/post` | **RESOLVED** | `externalDocs`, `tags`, `operationId` |

---

## 4. Invariant Compliance
1. **Binary-Safe Ingestion**: All raw sources written using binary byte writes (`wb`), zero text decoding/re-encoding, and guarded by `.gitattributes` (`data_stage_b/raw/** -text`).
2. **Never Overwrite**: Each unique raw source file resides exclusively at its immutable blob-SHA filename.
3. **Exhaustive Error Reporting**: Test suite verifies all sources and operations in single runs, accumulating all discrepancies before assertion.
4. **Zero Premature Benchmarking**: All 30 operations remain strictly in `DRAFT_OPERATION_SELECTION` state with zero canonical schema generation, mutations, or model execution.
