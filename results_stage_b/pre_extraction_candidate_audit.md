# Stage B Candidate Pre-Screen Static Audit Report

**Document Type:** Reproducible Pre-Extraction Empirical Audit  
**Audit Script SHA-256:** `70168ac8c5aaae401564ebd16dbe87bec1185d7e70415b6f39e3461da030da1e`  
**Operation Manifest SHA-256:** `b5e186799aa317b2c7e2e2415199ec032b6317ab61f5708b5eee590ba1d79fdd`  
**Generated At (UTC):** `2026-10-12T03:30:00Z`  
**Environment:** Python `3.13.2` (win32) | PyYAML `6.0.3`  
**Execution Command:** `python src/audit_stage_b_candidate_prescreen.py --generated-at 2026-10-12T03:30:00Z`  

> **Reproducibility Note:** When executed with `--generated-at <TIMESTAMP>`, outputs are 100% byte-stable. Normal runtime execution without this argument is expected to vary only in timestamp metadata (`generated_at_utc`).

---

## 1. Executive Summary & Cohort Health

- **Total Operations Audited:** 32 operations across 10 source clusters.
- **Clean Provisional Candidates (`PASS`):** **24 operations** (Pass all 7 frozen canonical rules without cycles, depth <= 5, no binary inputs, no object unions, no conflicting allOf).
- **Provisional Candidates Pending Union Amendment:** **3 operations** (`Stripe PostRefunds`, `Stripe PostCustomers`, `Stripe PostPaymentIntents` — flagged solely due to finite object-level `anyOf` unsetting semantics, awaiting formal ratification under `PROTOCOL_AMENDMENT_003.md`).
- **Excluded Operations (`EXCLUDE_PENDING`):** **5 operations** (Slack `chat.postMessage`, LINE `pushMessage`, LINE `replyMessage`, Chatwoot `create-a-contact`, GitHub `issues/create`).
- **Replacement Slots Still Required:** **3 operations** (1 slot for LINE Logistics/Communications, 1 slot for Chatwoot CRM/Support, 1 slot for GitHub Developer Platforms).

---

## 2. Complete 32-Operation Pre-Screen Audit Matrix

| Cluster ID | Operation ID | HTTP / RPC | Source Spec Pointer | Depth | Cycles | Binary | Object Union | allOf Conflict | External Ref | Auth Fields | Audit Verdict |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `CLUSTER_BOX` | `post_collaborations` | POST | `#/paths/~1collaborations/post` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_BOX` | `post_folders` | POST | `#/paths/~1folders/post` | 4 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_BOX` | `post_users` | POST | `#/paths/~1users/post` | 5 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_CHATWOOT` | `create-a-contact` | POST | `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts/post` | 3 | PASS | FAIL | PASS | PASS | PASS | `None` | **EXCLUDE_PENDING** |
| `CLUSTER_CHATWOOT` | `create-a-conversation` | POST | `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts~1{contact_identifier}~1conversations/post` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_CHATWOOT` | `create-an-account-user` | POST | `#/paths/~1platform~1api~1v1~1accounts~1{account_id}~1account_users/post` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_DIGITALOCEAN` | `domains_create` | POST | `#/paths/~1v2~1domains/post` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_DIGITALOCEAN` | `droplets_create` | POST | `#/paths/~1v2~1droplets/post` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_DIGITALOCEAN` | `floating_ips_create` | POST | `#/paths/~1v2~1floating_ips/post` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_GITHUB` | `issues/create` | POST | `#/paths/~1repos~1{owner}~1{repo}~1issues/post` | 6 | PASS | PASS | FAIL | PASS | PASS | `None` | **EXCLUDE_PENDING** |
| `CLUSTER_GITHUB` | `repos/create-commit-status` | POST | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | 2 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_GITHUB` | `repos/create-for-authenticated-user` | POST | `#/paths/~1user~1repos/post` | 2 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_LINE` | `markMessagesAsRead` | POST | `#/paths/~1v2~1bot~1message~1markAsRead/post` | 5 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_LINE` | `pushMessage` | POST | `#/paths/~1v2~1bot~1message~1push/post` | 13 | PASS | PASS | FAIL | PASS | PASS | `None` | **EXCLUDE_PENDING** |
| `CLUSTER_LINE` | `replyMessage` | POST | `#/paths/~1v2~1bot~1message~1reply/post` | 13 | PASS | PASS | FAIL | PASS | PASS | `None` | **EXCLUDE_PENDING** |
| `CLUSTER_LINE` | `setWebhookEndpoint` | PUT | `#/paths/~1v2~1bot~1channel~1webhook~1endpoint/put` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_MCP_GITHUB` | `create_issue` | RPC_TOOL | `src/github/index.ts:create_issue` | 2 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_MCP_GITHUB` | `create_or_update_file` | RPC_TOOL | `src/github/index.ts:create_or_update_file` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_MCP_GITHUB` | `search_repositories` | RPC_TOOL | `src/github/index.ts:search_repositories` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_MCP_SQLITE` | `describe_table` | RPC_TOOL | `server.py:list_tools:describe-table` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_MCP_SQLITE` | `read_query` | RPC_TOOL | `server.py:list_tools:read-query` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_MCP_SQLITE` | `write_query` | RPC_TOOL | `server.py:list_tools:write-query` | 1 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_SLACK` | `chat.postMessage` | POST | `#/paths/~1chat.postMessage/post` | 1 | PASS | PASS | PASS | PASS | PASS | `header.token` | **EXCLUDE_PENDING** |
| `CLUSTER_SLACK` | `conversations.create` | POST | `#/paths/~1conversations.create/post` | 1 | PASS | PASS | PASS | PASS | PASS | `header.token` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_SLACK` | `reminders.add` | POST | `#/paths/~1reminders.add/post` | 1 | PASS | PASS | PASS | PASS | PASS | `header.token` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_SLACK` | `users.profile.set` | POST | `#/paths/~1users.profile.set/post` | 1 | PASS | PASS | PASS | PASS | PASS | `header.token` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_STRIPE` | `PostCustomers` | POST | `#/paths/~1v1~1customers/post` | 6 | PASS | PASS | FAIL | PASS | PASS | `None` | **FLAGGED_PENDING_UNION_AMENDMENT** |
| `CLUSTER_STRIPE` | `PostPaymentIntents` | POST | `#/paths/~1v1~1payment_intents/post` | 9 | PASS | PASS | FAIL | PASS | PASS | `None` | **FLAGGED_PENDING_UNION_AMENDMENT** |
| `CLUSTER_STRIPE` | `PostRefunds` | POST | `#/paths/~1v1~1refunds/post` | 3 | PASS | PASS | FAIL | PASS | PASS | `None` | **FLAGGED_PENDING_UNION_AMENDMENT** |
| `CLUSTER_TWILIO` | `CreateCall` | POST | `#/paths/~12010-04-01~1Accounts~1{AccountSid}~1Calls.json/post` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_TWILIO` | `CreateMessage` | POST | `#/paths/~12010-04-01~1Accounts~1{AccountSid}~1Messages.json/post` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |
| `CLUSTER_TWILIO` | `UpdateAccount` | POST | `#/paths/~12010-04-01~1Accounts~1{Sid}.json/post` | 3 | PASS | PASS | PASS | PASS | PASS | `None` | **PASS_PROVISIONAL_CANONICAL** |

---

## 3. Detailed Failure Diagnostic for Flagged & Excluded Operations

### `CLUSTER_CHATWOOT` : `create-a-contact`
- **Pointer:** `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts/post`
- **Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Audit Verdict:** `EXCLUDE_PENDING`
- **Blocking Rules:** MULTIPART_BINARY
- **Failure Rationale:**
  - Schema declares format=binary or type=file at #/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts/post/requestBody/content/application~1json/schema->#/components/schemas/public_contact_create_update_payload/properties/avatar

### `CLUSTER_GITHUB` : `issues/create`
- **Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1issues/post`
- **Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Audit Verdict:** `EXCLUDE_PENDING`
- **Blocking Rules:** DEPTH_6, OBJECT_UNION
- **Failure Rationale:**
  - Observed depth 6 exceeds maximum recursion depth limit of 5
  - Object-level oneOf variant[1] at #/paths/~1repos~1{owner}~1{repo}~1issues/post/requestBody/content/application~1json/schema/properties/labels/items/oneOf

### `CLUSTER_LINE` : `pushMessage`
- **Pointer:** `#/paths/~1v2~1bot~1message~1push/post`
- **Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Audit Verdict:** `EXCLUDE_PENDING`
- **Blocking Rules:** DEPTH_13, OBJECT_UNION
- **Failure Rationale:**
  - Observed depth 13 exceeds maximum recursion depth limit of 5
  - Polymorphic discriminator declared at #/paths/~1v2~1bot~1message~1push/post/requestBody/content/application~1json/schema->#/components/schemas/PushMessageRequest/properties/messages/items->#/components/schemas/Message
  - Polymorphic discriminator declared at #/paths/~1v2~1bot~1message~1push/post/requestBody/content/application~1json/schema->#/components/schemas/PushMessageRequest/properties/messages/items->#/components/schemas/Message/properties/quickReply->#/components/schemas/QuickReply/properties/items/items->#/components/schemas/QuickReplyItem/properties/action->#/components/schemas/Action

### `CLUSTER_LINE` : `replyMessage`
- **Pointer:** `#/paths/~1v2~1bot~1message~1reply/post`
- **Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Audit Verdict:** `EXCLUDE_PENDING`
- **Blocking Rules:** DEPTH_13, OBJECT_UNION
- **Failure Rationale:**
  - Observed depth 13 exceeds maximum recursion depth limit of 5
  - Polymorphic discriminator declared at #/paths/~1v2~1bot~1message~1reply/post/requestBody/content/application~1json/schema->#/components/schemas/ReplyMessageRequest/properties/messages/items->#/components/schemas/Message
  - Polymorphic discriminator declared at #/paths/~1v2~1bot~1message~1reply/post/requestBody/content/application~1json/schema->#/components/schemas/ReplyMessageRequest/properties/messages/items->#/components/schemas/Message/properties/quickReply->#/components/schemas/QuickReply/properties/items/items->#/components/schemas/QuickReplyItem/properties/action->#/components/schemas/Action

### `CLUSTER_STRIPE` : `PostCustomers`
- **Pointer:** `#/paths/~1v1~1customers/post`
- **Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Audit Verdict:** `FLAGGED_PENDING_UNION_AMENDMENT`
- **Blocking Rules:** DEPTH_6, OBJECT_UNION
- **Failure Rationale:**
  - Observed depth 6 exceeds maximum recursion depth limit of 5
  - Object-level anyOf variant[0] at #/paths/~1v1~1customers/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/address/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1customers/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/invoice_settings/properties/rendering_options/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1customers/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/metadata/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1customers/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/shipping/anyOf

### `CLUSTER_STRIPE` : `PostPaymentIntents`
- **Pointer:** `#/paths/~1v1~1payment_intents/post`
- **Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Audit Verdict:** `FLAGGED_PENDING_UNION_AMENDMENT`
- **Blocking Rules:** DEPTH_9, OBJECT_UNION
- **Failure Rationale:**
  - Observed depth 9 exceeds maximum recursion depth limit of 5
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/amount_details/properties/shipping/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/amount_details/properties/tax/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/mandate_data/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_data/properties/billing_details/properties/address/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/acss_debit/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/affirm/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/afterpay_clearpay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/alipay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/alma/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/amazon_pay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/au_becs_debit/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/bacs_debit/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/bancontact/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/billie/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/billie/anyOf/0/properties/company_details/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/billie/anyOf/0/properties/company_details/anyOf/0/properties/registered_address/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/bizum/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/blik/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/boleto/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/card/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/card/anyOf/0/properties/installments/properties/plan/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/card_present/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/cashapp/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/crypto/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/customer_balance/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/eps/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/fpx/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/giropay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/grabpay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/ideal/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/interac_present/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/kakao_pay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/klarna/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/konbini/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/kr_card/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/link/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/mb_way/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/mobilepay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/multibanco/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/naver_pay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/nz_bank_account/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/oxxo/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/p24/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/pay_by_bank/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/payco/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/paynow/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/paypal/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/paypay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/payto/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/pix/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/promptpay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/revolut_pay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/samsung_pay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/satispay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/scalapay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/sepa_debit/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/sequra/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/sofort/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/sunbit/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/swish/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/twint/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/upi/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/us_bank_account/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/wechat_pay/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payment_method_options/properties/zip/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/transfer_data/properties/metadata/anyOf
  - Object-level anyOf variant[0] at #/paths/~1v1~1payment_intents/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/transfer_data/properties/payment_data/properties/metadata/anyOf

### `CLUSTER_STRIPE` : `PostRefunds`
- **Pointer:** `#/paths/~1v1~1refunds/post`
- **Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Audit Verdict:** `FLAGGED_PENDING_UNION_AMENDMENT`
- **Blocking Rules:** OBJECT_UNION
- **Failure Rationale:**
  - Object-level anyOf variant[0] at #/paths/~1v1~1refunds/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/metadata/anyOf
