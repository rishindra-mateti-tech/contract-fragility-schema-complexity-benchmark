# Stage B Candidate Admission Gate Review & Decisions

**Document Role:** Stage B Candidate Admission Gatekeeper Review  
**Date (UTC):** 2026-10-12T18:15:00Z  
**Governing Policy:** `STAGE_B_CANDIDATE_ADMISSION_GATE`  
**Automated Static Gate Status:** ALL_SLOTS_DECIDED — `ADMITTED_PENDING_EXTRACTION`  
**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)  

---

## 1. Executive Summary & Corpus Composition Impact

This gatekeeper review formally evaluates and admits five replacement operations for the open canonical slots in Stage B. Each candidate was verified directly against the pinned raw OpenAPI specifications for structural eligibility, provenance immutability, operational statefulness, and future deterministic mock feasibility.

To prevent conflating schema-level single-turn constructibility with runtime state independence, every operation is characterized by conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review:
1. **`schema_invocation_mode`**: `SINGLE_TURN_CONSTRUCTIBLE` vs `MULTI_TURN_DEPENDENT`
2. **`external_prerequisite_state`**: `NONE` vs `FIXTURE_REQUIRED` vs `LIFECYCLE_STATE_REQUIRED`
3. **`mock_fixture_requirements`**: minimal deterministic fixtures required by mock runtime

| Slot ID | Slot Domain | Replaced Operation | Admitted Replacement | Invocation Mode | Prerequisite State | Mock Fixtures | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| `SLOT_GITHUB_01` | Developer Platforms | `issues/create` | `pulls/create` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | `repository_fixture, base_branch_fixture, head_branch_fixture` | **`ADMITTED_PENDING_EXTRACTION`** |
| `SLOT_STRIPE_01` | Payments | `PostCustomers` | `PostPayouts` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | `merchant_account_fixture, payout_capability_active_fixture, sufficient_ledger_balance_fixture` | **`ADMITTED_PENDING_EXTRACTION`** |
| `SLOT_STRIPE_02` | Payments | `PostPaymentIntents` | `PostShippingRates` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | `authenticated_account_context_fixture` | **`ADMITTED_PENDING_EXTRACTION`** |
| `SLOT_CHATWOOT_01` | CRM/Support | `create-a-contact` | `create-a-webhook` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | `account_fixture` | **`ADMITTED_PENDING_EXTRACTION`** |
| `SLOT_LINE_01` | Logistics/Communications | `replyMessage` | `showLoadingAnimation` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | `target_chat_or_user_fixture` | **`ADMITTED_PENDING_EXTRACTION`** |

### Benchmark Real-Cohort Composition Status
- **Clean Monomorphic Operations:** 29 (24 existing provisional candidates + 5 newly admitted replacement candidates)
- **Faithful-Union Operations (Amendment 003):** 1 (`Stripe PostRefunds`, provisional finite union)
- **Total Real Candidate Cohort:** **30 operations** (reaching target cohort size)
- **Open Replacement Slots Remaining:** **0**
- **Excluded Operations Tracked:** 7 (retained permanently in exclusion registry for benchmark provenance)
- **Admission Invariant:** Status remains strictly `ADMITTED_PENDING_EXTRACTION`. Zero operations are designated as `CANONICAL_FAITHFUL` until extraction, automated validation, field-lineage verification, and manual review are complete.
- **Human Review Gate:** Author manual review completed and approved (`AUTHOR_MANUAL_REVIEW_COMPLETED`). Independent review status remains strictly `NOT_CONDUCTED`.

---

## 2. Slot-by-Slot Admission Reviews

### 2.1 Slot: `SLOT_GITHUB_01` — GitHub Developer Platforms Slot

- **Target Domain:** Developer Platforms
- **Replaced Operation:** `issues/create`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 6 exceeding MAX_RECURSION_DEPTH=5 and polymorphic object unions across assignees, labels, and milestone properties.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `pulls/create`
- **Endpoint & Method:** `POST /repos/{owner}/{repo}/pulls`
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls/post`
- **Source Project:** GitHub (github/rest-api-description) (`CAND-001`)
- **Source Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Raw File SHA-256:** `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194`
- **Raw Source File:** `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json`

#### Structural & Complexity Profile
- **Maximum Nesting Depth:** 2 (Protocol threshold: $\le 5$)
- **Property Count:** 10
- **Required Properties Count:** 4
- **Optional Field Ratio:** 0.6
- **Input Surfaces:** `body, path`
- **Request Content-Type:** `application/json`
- **Estimated Token Footprint:** ~179 tokens
- **Static Eligibility Verdict:** `STATICALLY_ELIGIBLE_CANDIDATE`

#### Operational Statefulness & Invocation Mode Assessment
- **Schema Invocation Mode:** `SINGLE_TURN_CONSTRUCTIBLE`
- **External Prerequisite State:** `FIXTURE_REQUIRED`
- **Mock Fixture Requirements:**
  - `repository_fixture`
  - `base_branch_fixture`
  - `head_branch_fixture`
- **Analysis:** High-fidelity developer platform operation. Cleanly bounded at recursion depth 2 with 10 properties (4 required: 2 path parameters '{owner}', '{repo}', plus 2 body fields 'head', 'base'). Schema parameters can be formulated in a single turn without inspecting prior responses (SINGLE_TURN_CONSTRUCTIBLE), but execution is not state-independent: mock execution requires pre-configured repository and base/head branch fixtures (FIXTURE_REQUIRED). Avoids structural bloat and polymorphic object unions of issues/create.

#### Mock-Safety Feasibility Review
- **Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Assessment:** Local mock execution requires an in-memory repository store that registers pull requests and validates head/base branches. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### Automated / Agent-Assisted Static Admission Checklist
- [x] Immutable Provenance Verified: Raw file SHA-256 and Git blob SHA match pinned registry.
- [x] JSON Pointer Verified: Resolves unambiguously to target `POST` operation in raw spec.
- [x] Depth Bound Verified: Observed depth 2 strictly $\le 5$.
- [x] Union Freedom: Contains zero object-level oneOf/anyOf unions.
- [x] Format Compliance: Contains zero binary, multipart/form-data, or file payload parameters.
- [x] Reference Integrity: Zero cyclic refs and zero unresolved external $ref pointers.
- [x] Composition Integrity: Zero conflicting scalar type merges under allOf.
- [x] Operational Statefulness: Formally partitioned into invocation mode, prerequisite state, and mock fixtures.
- [x] Mock Feasibility: Recorded as `PENDING`, not assumed.

**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)

#### Human Sign-Off Record
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Packet Git Commit:** `bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e`
- **Reviewed Packet Git Blob SHA:** `ac7a02cf8543e3ec310bcf3928a44b7c66b7031d`
- **Reviewed Packet SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Sign-Off Recording Commit:** `5175e6f7f4049dbbbd3f94ed7e04c932b3d68066`
- **Human Sign-Off Decision:** `APPROVE` (Author manual review confirms provenance and protocol compliance; independent validation NOT claimed)
- **Provenance Note:** The author reviewed the packet snapshot identified above. The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256.

#### Evaluated & Rejected Competing Candidates

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `pulls/submit-review` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn dependent operation: requires a pre-existing review_id created in a prior review turn. Cannot be invoked reliably in a single-turn benchmark without multi-turn state pre-seeding. |
| `pulls/create-review-comment` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Requires specific line/commit_id diff context and pull_number; less representative of primary top-level creation actions than pulls/create. |
| `codespaces/create-with-pr-for-authenticated-user` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/codespaces` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Specialized virtual machine / container infrastructure provisioning rather than core developer collaborative workflow. |

---

### 2.2 Slot: `SLOT_STRIPE_01` — Stripe Payments Slot A

- **Target Domain:** Payments
- **Replaced Operation:** `PostCustomers`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 6 exceeding MAX_RECURSION_DEPTH=5 and polymorphic address/metadata object unions.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `PostPayouts`
- **Endpoint & Method:** `POST /v1/payouts`
- **JSON Pointer:** `#/paths/~1v1~1payouts/post`
- **Source Project:** Stripe (stripe/openapi) (`CAND-002`)
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Raw File SHA-256:** `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776`
- **Raw Source File:** `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`

#### Structural & Complexity Profile
- **Maximum Nesting Depth:** 3 (Protocol threshold: $\le 5$)
- **Property Count:** 10
- **Required Properties Count:** 2
- **Optional Field Ratio:** 0.8
- **Input Surfaces:** `body`
- **Request Content-Type:** `application/x-www-form-urlencoded`
- **Estimated Token Footprint:** ~186 tokens
- **Static Eligibility Verdict:** `STATICALLY_ELIGIBLE_CANDIDATE`

#### Operational Statefulness & Invocation Mode Assessment
- **Schema Invocation Mode:** `SINGLE_TURN_CONSTRUCTIBLE`
- **External Prerequisite State:** `FIXTURE_REQUIRED`
- **Mock Fixture Requirements:**
  - `merchant_account_fixture`
  - `payout_capability_active_fixture`
  - `sufficient_ledger_balance_fixture`
- **Analysis:** Core merchant balance routing operation. Cleanly bounded at depth 3 with 10 properties (2 required: 'amount' and 'currency'). Schema parameters can be formulated in a single turn without prior entity outputs (SINGLE_TURN_CONSTRUCTIBLE), but execution is not state-independent: mock execution requires active merchant account capability and a sufficient available ledger-balance fixture (FIXTURE_REQUIRED). Avoids recursive depth bloat (depth 6) and polymorphic address objects of PostCustomers.

#### Mock-Safety Feasibility Review
- **Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Assessment:** Local mock execution requires tracking merchant ledger balance and returning deterministic payout records. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### Automated / Agent-Assisted Static Admission Checklist
- [x] Immutable Provenance Verified: Raw file SHA-256 and Git blob SHA match pinned registry.
- [x] JSON Pointer Verified: Resolves unambiguously to target `POST` operation in raw spec.
- [x] Depth Bound Verified: Observed depth 3 strictly $\le 5$.
- [x] Union Freedom: Contains zero object-level oneOf/anyOf unions.
- [x] Format Compliance: Contains zero binary, multipart/form-data, or file payload parameters.
- [x] Reference Integrity: Zero cyclic refs and zero unresolved external $ref pointers.
- [x] Composition Integrity: Zero conflicting scalar type merges under allOf.
- [x] Operational Statefulness: Formally partitioned into invocation mode, prerequisite state, and mock fixtures.
- [x] Mock Feasibility: Recorded as `PENDING`, not assumed.

**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)

#### Human Sign-Off Record
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Packet Git Commit:** `bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e`
- **Reviewed Packet Git Blob SHA:** `ac7a02cf8543e3ec310bcf3928a44b7c66b7031d`
- **Reviewed Packet SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Sign-Off Recording Commit:** `5175e6f7f4049dbbbd3f94ed7e04c932b3d68066`
- **Human Sign-Off Decision:** `APPROVE` (Author manual review confirms provenance and protocol compliance; independent validation NOT claimed)
- **Provenance Note:** The author reviewed the packet snapshot identified above. The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256.

#### Evaluated & Rejected Competing Candidates

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `PostTransfers` | `POST /v1/transfers` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Ranked #2 for fund routing (score 96, depth 3, 9 props). Structurally valid, but PostPayouts is preferred as it represents direct merchant settlement rather than intra-account transfer. |
| `PostAccountLinks` | `POST /v1/account_links` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn dependent operation: requires a pre-existing connected account ID ('account'), introducing entity linkage statefulness. |
| `PostPayoutsPayoutCancel` | `POST /v1/payouts/{payout}/cancel` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Lifecycle state mutation requiring a pre-existing payout ID in path that is currently in a pending/cancellable lifecycle state. |

---

### 2.3 Slot: `SLOT_STRIPE_02` — Stripe Payments Slot B

- **Target Domain:** Payments
- **Replaced Operation:** `PostPaymentIntents`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 9 (492 properties) exceeding MAX_RECURSION_DEPTH=5 and wide polymorphic payment_method_options anyOf unions.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `PostShippingRates`
- **Endpoint & Method:** `POST /v1/shipping_rates`
- **JSON Pointer:** `#/paths/~1v1~1shipping_rates/post`
- **Source Project:** Stripe (stripe/openapi) (`CAND-002`)
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Raw File SHA-256:** `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776`
- **Raw Source File:** `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`

#### Structural & Complexity Profile
- **Maximum Nesting Depth:** 4 (Protocol threshold: $\le 5$)
- **Property Count:** 17
- **Required Properties Count:** 7
- **Optional Field Ratio:** 0.5882
- **Input Surfaces:** `body`
- **Request Content-Type:** `application/x-www-form-urlencoded`
- **Estimated Token Footprint:** ~280 tokens
- **Static Eligibility Verdict:** `STATICALLY_ELIGIBLE_CANDIDATE`

#### Operational Statefulness & Invocation Mode Assessment
- **Schema Invocation Mode:** `SINGLE_TURN_CONSTRUCTIBLE`
- **External Prerequisite State:** `FIXTURE_REQUIRED`
- **Mock Fixture Requirements:**
  - `authenticated_account_context_fixture`
- **Analysis:** Highly representative commerce and checkout configuration operation. Exhibits rich nested object architecture (depth 4 with nested 'delivery_estimate' and 'fixed_amount' objects containing currency and duration units) while strictly complying with the frozen bound d <= 5. Schema parameters can be formulated in a single turn (SINGLE_TURN_CONSTRUCTIBLE); runtime execution requires an authenticated merchant account context fixture (FIXTURE_REQUIRED). Replaces the extreme bloat and 492-property depth-9 explosion of PostPaymentIntents with a rigorous, tractable complex contract.

#### Mock-Safety Feasibility Review
- **Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Assessment:** Deterministic creation endpoint; mock returns standard shipping_rate resource. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### Automated / Agent-Assisted Static Admission Checklist
- [x] Immutable Provenance Verified: Raw file SHA-256 and Git blob SHA match pinned registry.
- [x] JSON Pointer Verified: Resolves unambiguously to target `POST` operation in raw spec.
- [x] Depth Bound Verified: Observed depth 4 strictly $\le 5$.
- [x] Union Freedom: Contains zero object-level oneOf/anyOf unions.
- [x] Format Compliance: Contains zero binary, multipart/form-data, or file payload parameters.
- [x] Reference Integrity: Zero cyclic refs and zero unresolved external $ref pointers.
- [x] Composition Integrity: Zero conflicting scalar type merges under allOf.
- [x] Operational Statefulness: Formally partitioned into invocation mode, prerequisite state, and mock fixtures.
- [x] Mock Feasibility: Recorded as `PENDING`, not assumed.

**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)

#### Human Sign-Off Record
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Packet Git Commit:** `bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e`
- **Reviewed Packet Git Blob SHA:** `ac7a02cf8543e3ec310bcf3928a44b7c66b7031d`
- **Reviewed Packet SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Sign-Off Recording Commit:** `5175e6f7f4049dbbbd3f94ed7e04c932b3d68066`
- **Human Sign-Off Decision:** `APPROVE` (Author manual review confirms provenance and protocol compliance; independent validation NOT claimed)
- **Provenance Note:** The author reviewed the packet snapshot identified above. The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256.

#### Evaluated & Rejected Competing Candidates

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `PostInvoicesInvoiceAttachPayment` | `POST /v1/invoices/{invoice}/attach_payment` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires a pre-existing unpaid invoice in open lifecycle state ('/v1/invoices/{invoice}/attach_payment'). Cannot be tested in isolation without seeded invoice state. |
| `PostInvoicesInvoicePay` | `POST /v1/invoices/{invoice}/pay` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires a pre-existing unpaid invoice in open lifecycle state ('/v1/invoices/{invoice}/pay'). |
| `PostTaxRates` | `POST /v1/tax_rates` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Depth 3, 11 properties; structurally valid, but PostShippingRates provides richer structural nesting diversity (depth 4, 17 properties, 7 required) while adhering to all protocol constraints. |

---

### 2.4 Slot: `SLOT_CHATWOOT_01` — Chatwoot CRM & Support Slot

- **Target Domain:** CRM/Support
- **Replaced Operation:** `create-a-contact`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to format: binary on avatar property, violating the multipart/binary exclusion rule.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `create-a-webhook`
- **Endpoint & Method:** `POST /api/v1/accounts/{account_id}/webhooks`
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post`
- **Source Project:** Chatwoot (chatwoot/chatwoot) (`CAND-011`)
- **Source Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Raw File SHA-256:** `c8cba6e5975ee286593866f20652e29154717b835dc6324af7433bb497e7ab43`
- **Raw Source File:** `data_stage_b/raw/CAND-011/b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589.json`

#### Structural & Complexity Profile
- **Maximum Nesting Depth:** 4 (Protocol threshold: $\le 5$)
- **Property Count:** 4
- **Required Properties Count:** 1
- **Optional Field Ratio:** 0.75
- **Input Surfaces:** `body, path`
- **Request Content-Type:** `application/json`
- **Estimated Token Footprint:** ~126 tokens
- **Static Eligibility Verdict:** `STATICALLY_ELIGIBLE_CANDIDATE`

#### Operational Statefulness & Invocation Mode Assessment
- **Schema Invocation Mode:** `SINGLE_TURN_CONSTRUCTIBLE`
- **External Prerequisite State:** `FIXTURE_REQUIRED`
- **Mock Fixture Requirements:**
  - `account_fixture`
- **Analysis:** Standard event automation integration in customer support systems. Combines path routing ('account_id') with a structured JSON body containing an array of 10 distinct event enums ('subscriptions'). Schema parameters are constructible in a single turn without prior entity outputs (SINGLE_TURN_CONSTRUCTIBLE); runtime execution requires an existing account fixture corresponding to the path parameter (FIXTURE_REQUIRED). Avoids the multipart/form-data binary upload violation that disqualified create-a-contact.

#### Mock-Safety Feasibility Review
- **Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Assessment:** Webhook receiver store can be mocked deterministically by recording webhook registration in mock state. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### Automated / Agent-Assisted Static Admission Checklist
- [x] Immutable Provenance Verified: Raw file SHA-256 and Git blob SHA match pinned registry.
- [x] JSON Pointer Verified: Resolves unambiguously to target `POST` operation in raw spec.
- [x] Depth Bound Verified: Observed depth 4 strictly $\le 5$.
- [x] Union Freedom: Contains zero object-level oneOf/anyOf unions.
- [x] Format Compliance: Contains zero binary, multipart/form-data, or file payload parameters.
- [x] Reference Integrity: Zero cyclic refs and zero unresolved external $ref pointers.
- [x] Composition Integrity: Zero conflicting scalar type merges under allOf.
- [x] Operational Statefulness: Formally partitioned into invocation mode, prerequisite state, and mock fixtures.
- [x] Mock Feasibility: Recorded as `PENDING`, not assumed.

**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)

#### Human Sign-Off Record
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Packet Git Commit:** `bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e`
- **Reviewed Packet Git Blob SHA:** `ac7a02cf8543e3ec310bcf3928a44b7c66b7031d`
- **Reviewed Packet SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Sign-Off Recording Commit:** `5175e6f7f4049dbbbd3f94ed7e04c932b3d68066`
- **Human Sign-Off Decision:** `APPROVE` (Author manual review confirms provenance and protocol compliance; independent validation NOT claimed)
- **Provenance Note:** The author reviewed the packet snapshot identified above. The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256.

#### Evaluated & Rejected Competing Candidates

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `update-canned-response-in-account` | `PATCH /api/v1/accounts/{account_id}/canned_responses/{id}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires a pre-existing canned response ID in path ('/canned_responses/{id}'). Cannot be tested in isolation without seeded canned response state. |
| `update-a-webhook` | `PATCH /api/v1/accounts/{account_id}/webhooks/{webhook_id}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires pre-existing webhook ID in path ('/webhooks/{webhook_id}'). |
| `add-new-canned-response-to-account` | `POST /api/v1/accounts/{account_id}/canned_responses` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Structurally simpler (depth 3, 3 props, flat string pair) without array/enum diversity; create-a-webhook is more representative of programmatic integration complexity. |

---

### 2.5 Slot: `SLOT_LINE_01` — LINE Logistics & Communications Slot

- **Target Domain:** Logistics/Communications
- **Replaced Operation:** `replyMessage`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 13 and wide 11-variant discriminated object union in messages array.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `showLoadingAnimation`
- **Endpoint & Method:** `POST /v2/bot/chat/loading/start`
- **JSON Pointer:** `#/paths/~1v2~1bot~1chat~1loading~1start/post`
- **Source Project:** LINE (line/line-openapi) (`CAND-013`)
- **Source Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Raw File SHA-256:** `41033aa8491fc67ab09c4ec322f2aab072ae7b9402297e8c4f042eda0c2dd1fc`
- **Raw Source File:** `data_stage_b/raw/CAND-013/11f1fdb91092246f881edd1a9457cb37327a6c5d.yml`

#### Structural & Complexity Profile
- **Maximum Nesting Depth:** 3 (Protocol threshold: $\le 5$)
- **Property Count:** 2
- **Required Properties Count:** 1
- **Optional Field Ratio:** 0.5
- **Input Surfaces:** `body`
- **Request Content-Type:** `application/json`
- **Estimated Token Footprint:** ~89 tokens
- **Static Eligibility Verdict:** `STATICALLY_ELIGIBLE_CANDIDATE`

#### Operational Statefulness & Invocation Mode Assessment
- **Schema Invocation Mode:** `SINGLE_TURN_CONSTRUCTIBLE`
- **External Prerequisite State:** `FIXTURE_REQUIRED`
- **Mock Fixture Requirements:**
  - `target_chat_or_user_fixture`
- **Analysis:** Authentic messaging interaction endpoint in the LINE bot ecosystem ('/v2/bot/chat/loading/start'). Schema arguments ('chatId' and bounded integer 'loadingSeconds' [5-60s]) can be formulated in a single turn without inspecting prior responses (SINGLE_TURN_CONSTRUCTIBLE). Crucially, external prerequisite state is classified as FIXTURE_REQUIRED (not NONE) because the pinned LINE OpenAPI specification explicitly models response 400 for 'An invalid chat ID is specified', confirming that server-side chat/user identity validation is represented in the contract semantics. Avoids depth-13 recursion and polymorphic discriminated message unions of replyMessage.

#### Mock-Safety Feasibility Review
- **Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Assessment:** Deterministic response simulation; mock validates chatId against active target chat fixture and verifies loadingSeconds range (5-60s), returning HTTP 202. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### Automated / Agent-Assisted Static Admission Checklist
- [x] Immutable Provenance Verified: Raw file SHA-256 and Git blob SHA match pinned registry.
- [x] JSON Pointer Verified: Resolves unambiguously to target `POST` operation in raw spec.
- [x] Depth Bound Verified: Observed depth 3 strictly $\le 5$.
- [x] Union Freedom: Contains zero object-level oneOf/anyOf unions.
- [x] Format Compliance: Contains zero binary, multipart/form-data, or file payload parameters.
- [x] Reference Integrity: Zero cyclic refs and zero unresolved external $ref pointers.
- [x] Composition Integrity: Zero conflicting scalar type merges under allOf.
- [x] Operational Statefulness: Formally partitioned into invocation mode, prerequisite state, and mock fixtures.
- [x] Mock Feasibility: Recorded as `PENDING`, not assumed.

**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)

#### Human Sign-Off Record
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Packet Git Commit:** `bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e`
- **Reviewed Packet Git Blob SHA:** `ac7a02cf8543e3ec310bcf3928a44b7c66b7031d`
- **Reviewed Packet SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Sign-Off Recording Commit:** `5175e6f7f4049dbbbd3f94ed7e04c932b3d68066`
- **Human Sign-Off Decision:** `APPROVE` (Author manual review confirms provenance and protocol compliance; independent validation NOT claimed)
- **Provenance Note:** The author reviewed the packet snapshot identified above. The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256.

#### Evaluated & Rejected Competing Candidates

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `updateRichMenuAlias` | `POST /v2/bot/richmenu/alias/{richMenuAliasId}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: administrative alias mapping requiring pre-existing richMenuAliasId in path. |
| `linkRichMenuIdToUser` | `POST /v2/bot/user/{userId}/richmenu/{richMenuId}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: depth 1 path-only mapping; lacks request body and structural depth. |
| `testWebhookEndpoint` | `POST /v2/bot/channel/webhook/test` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Diagnostic health probe ('/channel/webhook/test') rather than conversational bot interaction. |

---

## 3. Provenance & Reproducibility Certification

Every admitted operation is cryptographically pinned to an immutable Git blob SHA and raw source file SHA-256 digest. No modifications have been made to Stage A, frozen raw source files, or existing provisional candidates. The operation manifest (`stage_b_operation_manifest.yaml`) reflects these admissions under the status `ADMITTED_PENDING_EXTRACTION`. Author manual review has been completed and approved by Rishindra Mateti (`AUTHOR_MANUAL_REVIEW`). Independent third-party validation has not been conducted.
