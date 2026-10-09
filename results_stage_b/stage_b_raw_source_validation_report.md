# Stage B Raw Source Validation Report

## 1. Executive Summary
- **Retrieval Status**: COMPLETE (10 raw source files retrieved across 10 approved sources).
- **Verification Status**: 100% PASS (All Git blob SHAs match GitHub Content API values; all SHA-256 hashes generated and recorded in sidecars).
- **Operation Pointer Resolution**: 100% PASS (All 30 candidate operations resolve deterministically against retrieved raw files).
- **Canonical Schema Creation**: ZERO (No benchmark schemas, normalized contracts, mutations, or mock executors created).

## 2. Retrieved Raw Sources & Provenance Verification

| Source ID | Project | Source File Path | Git Blob SHA | Downloaded File SHA-256 | Size (Bytes) | Operations Bound |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAND-001** | GitHub | `descriptions/api.github.com/api.github.com.json` | `a91fa76a34...` | `ba5ddc1eee...` | 13,018,090 | 3 ops |
| **CAND-002** | Stripe | `openapi/spec3.json` | `f1cedf38e0...` | `7cff4cc46d...` | 8,317,513 | 3 ops |
| **CAND-003** | DigitalOcean | `specification/DigitalOcean-public.v2.yaml` | `a26d71aa63...` | `e18ad525a3...` | 124,775 | 3 ops |
| **CAND-004** | Twilio | `spec/yaml/twilio_api_v2010.yaml` | `5b2e77834f...` | `052b294839...` | 1,504,725 | 3 ops |
| **CAND-005** | Box | `openapi.json` | `e740e641b8...` | `13cc601e01...` | 1,781,543 | 3 ops |
| **CAND-006** | Slack | `web-api/slack_web_openapi_v2_without_examples.json` | `f7b1affd1f...` | `8b92da26a3...` | 1,039,581 | 3 ops |
| **CAND-009** | Model Context Protocol | `src/sqlite/src/mcp_server_sqlite/server.py` | `1b97a6a490...` | `d3d58a6053...` | 18,533 | 3 ops |
| **CAND-010** | Model Context Protocol | `src/github/index.ts` | `0676a34c85...` | `bb964ea5a4...` | 18,123 | 3 ops |
| **CAND-011** | Chatwoot | `swagger/swagger.json` | `b0b3ca6332...` | `c8cba6e597...` | 537,652 | 3 ops |
| **CAND-013** | LINE | `messaging-api.yml` | `11f1fdb910...` | `41033aa849...` | 190,228 | 3 ops |

## 3. Operation Pointer Resolution Audit (30 Operations)

| Cluster ID | Operation ID | HTTP / RPC | Spec Pointer | Resolution Status | Matched Spec Keys / Symbol |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CLUSTER_GITHUB` | `repos/create-commit-status` | `POST` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | **RESOLVED** | keys: ['summary', 'description', 'tags'] |
| `CLUSTER_GITHUB` | `issues/create` | `POST` | `#/paths/~1repos~1{owner}~1{repo}~1issues/post` | **RESOLVED** | keys: ['summary', 'description', 'tags'] |
| `CLUSTER_GITHUB` | `repos/create-for-authenticated-user` | `POST` | `#/paths/~1user~1repos/post` | **RESOLVED** | keys: ['summary', 'description', 'tags'] |
| `CLUSTER_STRIPE` | `PostRefunds` | `POST` | `#/paths/~1v1~1refunds/post` | **RESOLVED** | keys: ['description', 'operationId', 'requestBody'] |
| `CLUSTER_STRIPE` | `PostCustomers` | `POST` | `#/paths/~1v1~1customers/post` | **RESOLVED** | keys: ['description', 'operationId', 'requestBody'] |
| `CLUSTER_STRIPE` | `PostPaymentIntents` | `POST` | `#/paths/~1v1~1payment_intents/post` | **RESOLVED** | keys: ['description', 'operationId', 'requestBody'] |
| `CLUSTER_DIGITALOCEAN` | `floating_ips_create` | `POST` | `#/paths/~1v2~1floating_ips/post` | **RESOLVED** | keys: ['$ref'] |
| `CLUSTER_DIGITALOCEAN` | `domains_create` | `POST` | `#/paths/~1v2~1domains/post` | **RESOLVED** | keys: ['$ref'] |
| `CLUSTER_DIGITALOCEAN` | `droplets_create` | `POST` | `#/paths/~1v2~1droplets/post` | **RESOLVED** | keys: ['$ref'] |
| `CLUSTER_TWILIO` | `UpdateAccount` | `POST` | `#/paths/~12010-04-01~1Accounts~1{Sid}.json/post` | **RESOLVED** | keys: ['description', 'summary', 'tags'] |
| `CLUSTER_TWILIO` | `CreateMessage` | `POST` | `#/paths/~12010-04-01~1Accounts~1{AccountSid}~1Messages.json/post` | **RESOLVED** | keys: ['description', 'summary', 'tags'] |
| `CLUSTER_TWILIO` | `CreateCall` | `POST` | `#/paths/~12010-04-01~1Accounts~1{AccountSid}~1Calls.json/post` | **RESOLVED** | keys: ['description', 'summary', 'tags'] |
| `CLUSTER_BOX` | `post_folders` | `POST` | `#/paths/~1folders/post` | **RESOLVED** | keys: ['operationId', 'summary', 'description'] |
| `CLUSTER_BOX` | `post_collaborations` | `POST` | `#/paths/~1collaborations/post` | **RESOLVED** | keys: ['operationId', 'summary', 'description'] |
| `CLUSTER_BOX` | `post_users` | `POST` | `#/paths/~1users/post` | **RESOLVED** | keys: ['operationId', 'summary', 'description'] |
| `CLUSTER_SLACK` | `conversations.create` | `POST` | `#/paths/~1conversations.create/post` | **RESOLVED** | keys: ['consumes', 'description', 'externalDocs'] |
| `CLUSTER_SLACK` | `users.profile.set` | `POST` | `#/paths/~1users.profile.set/post` | **RESOLVED** | keys: ['consumes', 'description', 'externalDocs'] |
| `CLUSTER_SLACK` | `chat.postMessage` | `POST` | `#/paths/~1chat.postMessage/post` | **RESOLVED** | keys: ['consumes', 'description', 'externalDocs'] |
| `CLUSTER_MCP_SQLITE` | `read_query` | `RPC_TOOL` | `server.py:list_tools:read-query` | **RESOLVED** | `name="read-query"` |
| `CLUSTER_MCP_SQLITE` | `describe_table` | `RPC_TOOL` | `server.py:list_tools:describe-table` | **RESOLVED** | `name="describe-table"` |
| `CLUSTER_MCP_SQLITE` | `write_query` | `RPC_TOOL` | `server.py:list_tools:write-query` | **RESOLVED** | `name="write-query"` |
| `CLUSTER_MCP_GITHUB` | `search_repositories` | `RPC_TOOL` | `src/github/index.ts:search_repositories` | **RESOLVED** | `name: "search_repositories"` |
| `CLUSTER_MCP_GITHUB` | `create_issue` | `RPC_TOOL` | `src/github/index.ts:create_issue` | **RESOLVED** | `name: "create_issue"` |
| `CLUSTER_MCP_GITHUB` | `create_or_update_file` | `RPC_TOOL` | `src/github/index.ts:create_or_update_file` | **RESOLVED** | `name: "create_or_update_file"` |
| `CLUSTER_CHATWOOT` | `create-an-account-user` | `POST` | `#/paths/~1platform~1api~1v1~1accounts~1{account_id}~1account_users/post` | **RESOLVED** | keys: ['tags', 'operationId', 'summary'] |
| `CLUSTER_CHATWOOT` | `create-a-contact` | `POST` | `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts/post` | **RESOLVED** | keys: ['tags', 'operationId', 'summary'] |
| `CLUSTER_CHATWOOT` | `create-a-conversation` | `POST` | `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts~1{contact_identifier}~1conversations/post` | **RESOLVED** | keys: ['tags', 'operationId', 'summary'] |
| `CLUSTER_LINE` | `setWebhookEndpoint` | `PUT` | `#/paths/~1v2~1bot~1channel~1webhook~1endpoint/put` | **RESOLVED** | keys: ['externalDocs', 'tags', 'operationId'] |
| `CLUSTER_LINE` | `replyMessage` | `POST` | `#/paths/~1v2~1bot~1message~1reply/post` | **RESOLVED** | keys: ['externalDocs', 'tags', 'operationId'] |
| `CLUSTER_LINE` | `pushMessage` | `POST` | `#/paths/~1v2~1bot~1message~1push/post` | **RESOLVED** | keys: ['externalDocs', 'tags', 'operationId'] |

## 4. Invariant Compliance
1. **Never Overwrite**: Each unique raw source file was downloaded once to its blob-SHA keyed file path.
2. **Sidecar Provenance**: Each raw source file has an accompanying `<blob_sha>.provenance.json` detailing upstream commit SHA, URLs, license blob SHA, and bound operation IDs.
3. **Deterministic Resolution**: All 30 operation pointers resolve deterministically without extracting, modifying, or normalizing schemas.
4. **No Premature Benchmarking**: Zero candidate schemas transformed or normalized. All operations remain in `DRAFT_OPERATION_SELECTION` state.
