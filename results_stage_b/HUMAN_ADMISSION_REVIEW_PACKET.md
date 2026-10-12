# Stage B Candidate Admission Human Review Packet

**Document Role:** Human Review Gate & Provenance Verification Packet  
**Document Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)  
**Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md`  
**Review Instructions:** [AUTHOR_REVIEW_INSTRUCTIONS.md](AUTHOR_REVIEW_INSTRUCTIONS.md)  
**Operation Manifest SHA-256:** `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326`  
**Decisions Artifact SHA-256:** `2b9668fdbe8c84e53303228dc9b60240250bf732382087fc73945987c03b563d`  
**Reviewed Packet Base SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`  
**Date (UTC):** `2026-10-12T18:15:00Z`  

---

## 1. Review Packet Protocol & Reviewer Guidance

This review packet compiles the five replacement candidate operations admitted into Stage B under status `ADMITTED_PENDING_EXTRACTION`. Author manual review (`AUTHOR_MANUAL_REVIEW`) has been completed and approved by Rishindra Mateti.

### Reviewer Roles & Independence Boundary:
- **`AUTHOR_MANUAL_REVIEW` (COMPLETED)**: Conducted by benchmark author Rishindra Mateti on 2026-10-12 to confirm cryptographic provenance, protocol compliance, and domain engineering rationale. *Author review confirms provenance and authorial design decisions but DOES NOT constitute independent third-party validation.*
- **`INDEPENDENT_REVIEW` (NOT CONDUCTED)**: External, independent researcher with no authorship or conflict of interest. *Independent review has NOT occurred.*

All classifications recorded herein represent **conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review**.

Zero extraction code, derived schemas, mutations, mock runtime harnesses, or model evaluations have been generated.

---

## 2. Operation Review Pages

### Operation Review 1: `pulls/create` (Slot: `SLOT_GITHUB_01`)

#### A. Operation Identification & Source Link / Pointer
- **Slot Name:** GitHub Developer Platforms Slot (`SLOT_GITHUB_01`)
- **Domain:** Developer Platforms
- **Replaced Operation:** `issues/create`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 6 exceeding MAX_RECURSION_DEPTH=5 and polymorphic object unions across assignees, labels, and milestone properties.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `pulls/create`
- **HTTP Method & Endpoint:** `POST /repos/{owner}/{repo}/pulls`
- **Exact OpenAPI Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls/post`
- **Source Project:** GitHub (github/rest-api-description) (`CAND-001`)
- **Raw On-Disk Source Path:** `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json`

#### B. Cryptographic Provenance & Artifact SHAs
- **Raw Source Git Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Raw Source File SHA-256:** `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194`
- **Reviewed Operation Manifest SHA-256:** `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326`
- **Reviewed Decisions Artifact SHA-256:** `2b9668fdbe8c84e53303228dc9b60240250bf732382087fc73945987c03b563d`

#### C. Selection Rationale (Why Selected)
- **Rationale:** High-fidelity developer platform operation. Cleanly bounded at recursion depth 2 with 10 properties (4 required: 2 path parameters '{owner}', '{repo}', plus 2 body fields 'head', 'base'). Schema parameters can be formulated in a single turn without inspecting prior responses (SINGLE_TURN_CONSTRUCTIBLE), but execution is not state-independent: mock execution requires pre-configured repository and base/head branch fixtures (FIXTURE_REQUIRED). Avoids structural bloat and polymorphic object unions of issues/create.
- **Complexity Tier:** `MODERATE`
- **Maximum Nesting Depth:** 2 (Protocol limit: $\le 5$)
- **Property Count:** 10 (Required properties: 4)
- **Optional Field Ratio:** 0.6
- **Input Surfaces:** `body, path`
- **Content Types:** `application/json`
- **Estimated Token Footprint:** ~179 tokens

#### D. Required Future Mock Fixtures
- `repository_fixture`
- `base_branch_fixture`
- `head_branch_fixture`
- **Mock Feasibility Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Mock Feasibility Notes:** Local mock execution requires an in-memory repository store that registers pull requests and validates head/base branches. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### E. Operational Statefulness & Invocation Mode Classification
*Note: Conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review.*
- **`schema_invocation_mode`:** `SINGLE_TURN_CONSTRUCTIBLE`
- **`external_prerequisite_state`:** `FIXTURE_REQUIRED`
- **Mock Fixtures Required:** `repository_fixture, base_branch_fixture, head_branch_fixture`
- **State Partitioning Rationale:** Schema arguments can be formulated in a single turn without inspecting prior tool outputs (`SINGLE_TURN_CONSTRUCTIBLE`), but runtime mock execution requires pre-configured fixtures (`FIXTURE_REQUIRED`). This strictly separates schema single-turn constructibility from API/runtime state independence.

#### F. Competing Candidates Evaluated & Rejected

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `pulls/submit-review` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn dependent operation: requires a pre-existing review_id created in a prior review turn. Cannot be invoked reliably in a single-turn benchmark without multi-turn state pre-seeding. |
| `pulls/create-review-comment` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Requires specific line/commit_id diff context and pull_number; less representative of primary top-level creation actions than pulls/create. |
| `codespaces/create-with-pr-for-authenticated-user` | `POST /repos/{owner}/{repo}/pulls/{pull_number}/codespaces` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Specialized virtual machine / container infrastructure provisioning rather than core developer collaborative workflow. |

#### G. Checkbox List for Human Reviewer
- [x] **Provenance Verification:** Raw file SHA-256 (`ba5ddc1eeeede9f3...`) and Git blob SHA (`a91fa76a34558f5e...`) match pinned registry.
- [x] **JSON Pointer Resolution:** Pointer `#/paths/~1repos~1{owner}~1{repo}~1pulls/post` resolves unambiguously in `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json`.
- [x] **Structural Rules Compliance:** Observed depth 2 $\le 5$, 0 object unions, 0 binary/multipart formats, 0 cycles, 0 external refs.
- [x] **Invocation Mode Verified:** Operation is constructible in a single turn (`SINGLE_TURN_CONSTRUCTIBLE`).
- [x] **Fixture Requirements Verified:** Deterministic mock fixtures are minimal and feasible (`FIXTURE_REQUIRED`).
- [x] **Domain Representation:** Operation represents authentic production workflow for Developer Platforms.
- [x] **Mock Feasibility Pre-Screen:** Local hermetic mock execution is feasible given declared fixtures.

#### H. Human Review Sign-Off Block
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Artifact SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Review Decision:** `APPROVE`
- **Review Notes / Conditions:** Author manual review confirms cryptographic provenance, protocol compliance, depth <= 5 bounds, zero object unions, and domain representative workflow fit. Does not claim independent validation.

---

### Operation Review 2: `PostPayouts` (Slot: `SLOT_STRIPE_01`)

#### A. Operation Identification & Source Link / Pointer
- **Slot Name:** Stripe Payments Slot A (`SLOT_STRIPE_01`)
- **Domain:** Payments
- **Replaced Operation:** `PostCustomers`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 6 exceeding MAX_RECURSION_DEPTH=5 and polymorphic address/metadata object unions.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `PostPayouts`
- **HTTP Method & Endpoint:** `POST /v1/payouts`
- **Exact OpenAPI Pointer:** `#/paths/~1v1~1payouts/post`
- **Source Project:** Stripe (stripe/openapi) (`CAND-002`)
- **Raw On-Disk Source Path:** `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`

#### B. Cryptographic Provenance & Artifact SHAs
- **Raw Source Git Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Raw Source File SHA-256:** `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776`
- **Reviewed Operation Manifest SHA-256:** `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326`
- **Reviewed Decisions Artifact SHA-256:** `2b9668fdbe8c84e53303228dc9b60240250bf732382087fc73945987c03b563d`

#### C. Selection Rationale (Why Selected)
- **Rationale:** Core merchant balance routing operation. Cleanly bounded at depth 3 with 10 properties (2 required: 'amount' and 'currency'). Schema parameters can be formulated in a single turn without prior entity outputs (SINGLE_TURN_CONSTRUCTIBLE), but execution is not state-independent: mock execution requires active merchant account capability and a sufficient available ledger-balance fixture (FIXTURE_REQUIRED). Avoids recursive depth bloat (depth 6) and polymorphic address objects of PostCustomers.
- **Complexity Tier:** `MODERATE`
- **Maximum Nesting Depth:** 3 (Protocol limit: $\le 5$)
- **Property Count:** 10 (Required properties: 2)
- **Optional Field Ratio:** 0.8
- **Input Surfaces:** `body`
- **Content Types:** `application/x-www-form-urlencoded`
- **Estimated Token Footprint:** ~186 tokens

#### D. Required Future Mock Fixtures
- `merchant_account_fixture`
- `payout_capability_active_fixture`
- `sufficient_ledger_balance_fixture`
- **Mock Feasibility Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Mock Feasibility Notes:** Local mock execution requires tracking merchant ledger balance and returning deterministic payout records. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### E. Operational Statefulness & Invocation Mode Classification
*Note: Conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review.*
- **`schema_invocation_mode`:** `SINGLE_TURN_CONSTRUCTIBLE`
- **`external_prerequisite_state`:** `FIXTURE_REQUIRED`
- **Mock Fixtures Required:** `merchant_account_fixture, payout_capability_active_fixture, sufficient_ledger_balance_fixture`
- **State Partitioning Rationale:** Schema arguments can be formulated in a single turn without inspecting prior tool outputs (`SINGLE_TURN_CONSTRUCTIBLE`), but runtime mock execution requires pre-configured fixtures (`FIXTURE_REQUIRED`). This strictly separates schema single-turn constructibility from API/runtime state independence.

#### F. Competing Candidates Evaluated & Rejected

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `PostTransfers` | `POST /v1/transfers` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Ranked #2 for fund routing (score 96, depth 3, 9 props). Structurally valid, but PostPayouts is preferred as it represents direct merchant settlement rather than intra-account transfer. |
| `PostAccountLinks` | `POST /v1/account_links` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn dependent operation: requires a pre-existing connected account ID ('account'), introducing entity linkage statefulness. |
| `PostPayoutsPayoutCancel` | `POST /v1/payouts/{payout}/cancel` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Lifecycle state mutation requiring a pre-existing payout ID in path that is currently in a pending/cancellable lifecycle state. |

#### G. Checkbox List for Human Reviewer
- [x] **Provenance Verification:** Raw file SHA-256 (`7cff4cc46d065410...`) and Git blob SHA (`f1cedf38e0178538...`) match pinned registry.
- [x] **JSON Pointer Resolution:** Pointer `#/paths/~1v1~1payouts/post` resolves unambiguously in `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`.
- [x] **Structural Rules Compliance:** Observed depth 3 $\le 5$, 0 object unions, 0 binary/multipart formats, 0 cycles, 0 external refs.
- [x] **Invocation Mode Verified:** Operation is constructible in a single turn (`SINGLE_TURN_CONSTRUCTIBLE`).
- [x] **Fixture Requirements Verified:** Deterministic mock fixtures are minimal and feasible (`FIXTURE_REQUIRED`).
- [x] **Domain Representation:** Operation represents authentic production workflow for Payments.
- [x] **Mock Feasibility Pre-Screen:** Local hermetic mock execution is feasible given declared fixtures.

#### H. Human Review Sign-Off Block
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Artifact SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Review Decision:** `APPROVE`
- **Review Notes / Conditions:** Author manual review confirms cryptographic provenance, protocol compliance, depth <= 5 bounds, zero object unions, and domain representative workflow fit. Does not claim independent validation.

---

### Operation Review 3: `PostShippingRates` (Slot: `SLOT_STRIPE_02`)

#### A. Operation Identification & Source Link / Pointer
- **Slot Name:** Stripe Payments Slot B (`SLOT_STRIPE_02`)
- **Domain:** Payments
- **Replaced Operation:** `PostPaymentIntents`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 9 (492 properties) exceeding MAX_RECURSION_DEPTH=5 and wide polymorphic payment_method_options anyOf unions.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `PostShippingRates`
- **HTTP Method & Endpoint:** `POST /v1/shipping_rates`
- **Exact OpenAPI Pointer:** `#/paths/~1v1~1shipping_rates/post`
- **Source Project:** Stripe (stripe/openapi) (`CAND-002`)
- **Raw On-Disk Source Path:** `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`

#### B. Cryptographic Provenance & Artifact SHAs
- **Raw Source Git Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Raw Source File SHA-256:** `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776`
- **Reviewed Operation Manifest SHA-256:** `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326`
- **Reviewed Decisions Artifact SHA-256:** `2b9668fdbe8c84e53303228dc9b60240250bf732382087fc73945987c03b563d`

#### C. Selection Rationale (Why Selected)
- **Rationale:** Highly representative commerce and checkout configuration operation. Exhibits rich nested object architecture (depth 4 with nested 'delivery_estimate' and 'fixed_amount' objects containing currency and duration units) while strictly complying with the frozen bound d <= 5. Schema parameters can be formulated in a single turn (SINGLE_TURN_CONSTRUCTIBLE); runtime execution requires an authenticated merchant account context fixture (FIXTURE_REQUIRED). Replaces the extreme bloat and 492-property depth-9 explosion of PostPaymentIntents with a rigorous, tractable complex contract.
- **Complexity Tier:** `COMPLEX_NESTED`
- **Maximum Nesting Depth:** 4 (Protocol limit: $\le 5$)
- **Property Count:** 17 (Required properties: 7)
- **Optional Field Ratio:** 0.5882
- **Input Surfaces:** `body`
- **Content Types:** `application/x-www-form-urlencoded`
- **Estimated Token Footprint:** ~280 tokens

#### D. Required Future Mock Fixtures
- `authenticated_account_context_fixture`
- **Mock Feasibility Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Mock Feasibility Notes:** Deterministic creation endpoint; mock returns standard shipping_rate resource. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### E. Operational Statefulness & Invocation Mode Classification
*Note: Conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review.*
- **`schema_invocation_mode`:** `SINGLE_TURN_CONSTRUCTIBLE`
- **`external_prerequisite_state`:** `FIXTURE_REQUIRED`
- **Mock Fixtures Required:** `authenticated_account_context_fixture`
- **State Partitioning Rationale:** Schema arguments can be formulated in a single turn without inspecting prior tool outputs (`SINGLE_TURN_CONSTRUCTIBLE`), but runtime mock execution requires pre-configured fixtures (`FIXTURE_REQUIRED`). This strictly separates schema single-turn constructibility from API/runtime state independence.

#### F. Competing Candidates Evaluated & Rejected

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `PostInvoicesInvoiceAttachPayment` | `POST /v1/invoices/{invoice}/attach_payment` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires a pre-existing unpaid invoice in open lifecycle state ('/v1/invoices/{invoice}/attach_payment'). Cannot be tested in isolation without seeded invoice state. |
| `PostInvoicesInvoicePay` | `POST /v1/invoices/{invoice}/pay` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires a pre-existing unpaid invoice in open lifecycle state ('/v1/invoices/{invoice}/pay'). |
| `PostTaxRates` | `POST /v1/tax_rates` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Depth 3, 11 properties; structurally valid, but PostShippingRates provides richer structural nesting diversity (depth 4, 17 properties, 7 required) while adhering to all protocol constraints. |

#### G. Checkbox List for Human Reviewer
- [x] **Provenance Verification:** Raw file SHA-256 (`7cff4cc46d065410...`) and Git blob SHA (`f1cedf38e0178538...`) match pinned registry.
- [x] **JSON Pointer Resolution:** Pointer `#/paths/~1v1~1shipping_rates/post` resolves unambiguously in `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`.
- [x] **Structural Rules Compliance:** Observed depth 4 $\le 5$, 0 object unions, 0 binary/multipart formats, 0 cycles, 0 external refs.
- [x] **Invocation Mode Verified:** Operation is constructible in a single turn (`SINGLE_TURN_CONSTRUCTIBLE`).
- [x] **Fixture Requirements Verified:** Deterministic mock fixtures are minimal and feasible (`FIXTURE_REQUIRED`).
- [x] **Domain Representation:** Operation represents authentic production workflow for Payments.
- [x] **Mock Feasibility Pre-Screen:** Local hermetic mock execution is feasible given declared fixtures.

#### H. Human Review Sign-Off Block
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Artifact SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Review Decision:** `APPROVE`
- **Review Notes / Conditions:** Author manual review confirms cryptographic provenance, protocol compliance, depth <= 5 bounds, zero object unions, and domain representative workflow fit. Does not claim independent validation.

---

### Operation Review 4: `create-a-webhook` (Slot: `SLOT_CHATWOOT_01`)

#### A. Operation Identification & Source Link / Pointer
- **Slot Name:** Chatwoot CRM & Support Slot (`SLOT_CHATWOOT_01`)
- **Domain:** CRM/Support
- **Replaced Operation:** `create-a-contact`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to format: binary on avatar property, violating the multipart/binary exclusion rule.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `create-a-webhook`
- **HTTP Method & Endpoint:** `POST /api/v1/accounts/{account_id}/webhooks`
- **Exact OpenAPI Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post`
- **Source Project:** Chatwoot (chatwoot/chatwoot) (`CAND-011`)
- **Raw On-Disk Source Path:** `data_stage_b/raw/CAND-011/b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589.json`

#### B. Cryptographic Provenance & Artifact SHAs
- **Raw Source Git Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Raw Source File SHA-256:** `c8cba6e5975ee286593866f20652e29154717b835dc6324af7433bb497e7ab43`
- **Reviewed Operation Manifest SHA-256:** `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326`
- **Reviewed Decisions Artifact SHA-256:** `2b9668fdbe8c84e53303228dc9b60240250bf732382087fc73945987c03b563d`

#### C. Selection Rationale (Why Selected)
- **Rationale:** Standard event automation integration in customer support systems. Combines path routing ('account_id') with a structured JSON body containing an array of 10 distinct event enums ('subscriptions'). Schema parameters are constructible in a single turn without prior entity outputs (SINGLE_TURN_CONSTRUCTIBLE); runtime execution requires an existing account fixture corresponding to the path parameter (FIXTURE_REQUIRED). Avoids the multipart/form-data binary upload violation that disqualified create-a-contact.
- **Complexity Tier:** `MODERATE`
- **Maximum Nesting Depth:** 4 (Protocol limit: $\le 5$)
- **Property Count:** 4 (Required properties: 1)
- **Optional Field Ratio:** 0.75
- **Input Surfaces:** `body, path`
- **Content Types:** `application/json`
- **Estimated Token Footprint:** ~126 tokens

#### D. Required Future Mock Fixtures
- `account_fixture`
- **Mock Feasibility Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Mock Feasibility Notes:** Webhook receiver store can be mocked deterministically by recording webhook registration in mock state. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### E. Operational Statefulness & Invocation Mode Classification
*Note: Conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review.*
- **`schema_invocation_mode`:** `SINGLE_TURN_CONSTRUCTIBLE`
- **`external_prerequisite_state`:** `FIXTURE_REQUIRED`
- **Mock Fixtures Required:** `account_fixture`
- **State Partitioning Rationale:** Schema arguments can be formulated in a single turn without inspecting prior tool outputs (`SINGLE_TURN_CONSTRUCTIBLE`), but runtime mock execution requires pre-configured fixtures (`FIXTURE_REQUIRED`). This strictly separates schema single-turn constructibility from API/runtime state independence.

#### F. Competing Candidates Evaluated & Rejected

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `update-canned-response-in-account` | `PATCH /api/v1/accounts/{account_id}/canned_responses/{id}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires a pre-existing canned response ID in path ('/canned_responses/{id}'). Cannot be tested in isolation without seeded canned response state. |
| `update-a-webhook` | `PATCH /api/v1/accounts/{account_id}/webhooks/{webhook_id}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: requires pre-existing webhook ID in path ('/webhooks/{webhook_id}'). |
| `add-new-canned-response-to-account` | `POST /api/v1/accounts/{account_id}/canned_responses` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Structurally simpler (depth 3, 3 props, flat string pair) without array/enum diversity; create-a-webhook is more representative of programmatic integration complexity. |

#### G. Checkbox List for Human Reviewer
- [x] **Provenance Verification:** Raw file SHA-256 (`c8cba6e5975ee286...`) and Git blob SHA (`b0b3ca6332f0627a...`) match pinned registry.
- [x] **JSON Pointer Resolution:** Pointer `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post` resolves unambiguously in `data_stage_b/raw/CAND-011/b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589.json`.
- [x] **Structural Rules Compliance:** Observed depth 4 $\le 5$, 0 object unions, 0 binary/multipart formats, 0 cycles, 0 external refs.
- [x] **Invocation Mode Verified:** Operation is constructible in a single turn (`SINGLE_TURN_CONSTRUCTIBLE`).
- [x] **Fixture Requirements Verified:** Deterministic mock fixtures are minimal and feasible (`FIXTURE_REQUIRED`).
- [x] **Domain Representation:** Operation represents authentic production workflow for CRM/Support.
- [x] **Mock Feasibility Pre-Screen:** Local hermetic mock execution is feasible given declared fixtures.

#### H. Human Review Sign-Off Block
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Artifact SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Review Decision:** `APPROVE`
- **Review Notes / Conditions:** Author manual review confirms cryptographic provenance, protocol compliance, depth <= 5 bounds, zero object unions, and domain representative workflow fit. Does not claim independent validation.

---

### Operation Review 5: `showLoadingAnimation` (Slot: `SLOT_LINE_01`)

#### A. Operation Identification & Source Link / Pointer
- **Slot Name:** LINE Logistics & Communications Slot (`SLOT_LINE_01`)
- **Domain:** Logistics/Communications
- **Replaced Operation:** `replyMessage`
- **Replaced Exclusion Rationale:** Disqualified from canonical cohort due to observed recursion depth 13 and wide 11-variant discriminated object union in messages array.
- **Admission Decision:** **`ADMITTED_PENDING_EXTRACTION`**
- **Admitted Operation ID:** `showLoadingAnimation`
- **HTTP Method & Endpoint:** `POST /v2/bot/chat/loading/start`
- **Exact OpenAPI Pointer:** `#/paths/~1v2~1bot~1chat~1loading~1start/post`
- **Source Project:** LINE (line/line-openapi) (`CAND-013`)
- **Raw On-Disk Source Path:** `data_stage_b/raw/CAND-013/11f1fdb91092246f881edd1a9457cb37327a6c5d.yml`

#### B. Cryptographic Provenance & Artifact SHAs
- **Raw Source Git Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Raw Source File SHA-256:** `41033aa8491fc67ab09c4ec322f2aab072ae7b9402297e8c4f042eda0c2dd1fc`
- **Reviewed Operation Manifest SHA-256:** `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326`
- **Reviewed Decisions Artifact SHA-256:** `2b9668fdbe8c84e53303228dc9b60240250bf732382087fc73945987c03b563d`

#### C. Selection Rationale (Why Selected)
- **Rationale:** Authentic messaging interaction endpoint in the LINE bot ecosystem ('/v2/bot/chat/loading/start'). Schema arguments ('chatId' and bounded integer 'loadingSeconds' [5-60s]) can be formulated in a single turn without inspecting prior responses (SINGLE_TURN_CONSTRUCTIBLE). Crucially, external prerequisite state is classified as FIXTURE_REQUIRED (not NONE) because the pinned LINE OpenAPI specification explicitly models response 400 for 'An invalid chat ID is specified', confirming that server-side chat/user identity validation is represented in the contract semantics. Avoids depth-13 recursion and polymorphic discriminated message unions of replyMessage.
- **Complexity Tier:** `FLAT`
- **Maximum Nesting Depth:** 3 (Protocol limit: $\le 5$)
- **Property Count:** 2 (Required properties: 1)
- **Optional Field Ratio:** 0.5
- **Input Surfaces:** `body`
- **Content Types:** `application/json`
- **Estimated Token Footprint:** ~89 tokens

#### D. Required Future Mock Fixtures
- `target_chat_or_user_fixture`
- **Mock Feasibility Status:** **`PENDING`** (Held strictly pending empirical validation)
- **Mock Feasibility Notes:** Deterministic response simulation; mock validates chatId against active target chat fixture and verifies loadingSeconds range (5-60s), returning HTTP 202. Feasibility is pending extraction verification and implementation of the hermetic mock harness.

#### E. Operational Statefulness & Invocation Mode Classification
*Note: Conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review.*
- **`schema_invocation_mode`:** `SINGLE_TURN_CONSTRUCTIBLE`
- **`external_prerequisite_state`:** `FIXTURE_REQUIRED`
- **Mock Fixtures Required:** `target_chat_or_user_fixture`
- **State Partitioning Rationale:** Schema arguments can be formulated in a single turn without inspecting prior tool outputs (`SINGLE_TURN_CONSTRUCTIBLE`), but runtime mock execution requires pre-configured fixtures (`FIXTURE_REQUIRED`). This strictly separates schema single-turn constructibility from API/runtime state independence.

#### F. Competing Candidates Evaluated & Rejected

| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| `updateRichMenuAlias` | `POST /v2/bot/richmenu/alias/{richMenuAliasId}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: administrative alias mapping requiring pre-existing richMenuAliasId in path. |
| `linkRichMenuIdToUser` | `POST /v2/bot/user/{userId}/richmenu/{richMenuId}` | `MULTI_TURN_DEPENDENT` | `LIFECYCLE_STATE_REQUIRED` | Multi-turn lifecycle dependency: depth 1 path-only mapping; lacks request body and structural depth. |
| `testWebhookEndpoint` | `POST /v2/bot/channel/webhook/test` | `SINGLE_TURN_CONSTRUCTIBLE` | `FIXTURE_REQUIRED` | Diagnostic health probe ('/channel/webhook/test') rather than conversational bot interaction. |

#### G. Checkbox List for Human Reviewer
- [x] **Provenance Verification:** Raw file SHA-256 (`41033aa8491fc67a...`) and Git blob SHA (`11f1fdb91092246f...`) match pinned registry.
- [x] **JSON Pointer Resolution:** Pointer `#/paths/~1v2~1bot~1chat~1loading~1start/post` resolves unambiguously in `data_stage_b/raw/CAND-013/11f1fdb91092246f881edd1a9457cb37327a6c5d.yml`.
- [x] **Structural Rules Compliance:** Observed depth 3 $\le 5$, 0 object unions, 0 binary/multipart formats, 0 cycles, 0 external refs.
- [x] **Invocation Mode Verified:** Operation is constructible in a single turn (`SINGLE_TURN_CONSTRUCTIBLE`).
- [x] **Fixture Requirements Verified:** Deterministic mock fixtures are minimal and feasible (`FIXTURE_REQUIRED`).
- [x] **Domain Representation:** Operation represents authentic production workflow for Logistics/Communications.
- [x] **Mock Feasibility Pre-Screen:** Local hermetic mock execution is feasible given declared fixtures.

#### H. Human Review Sign-Off Block
- **Reviewer Name:** `Rishindra Mateti`
- **Reviewer Role:** `AUTHOR_MANUAL_REVIEW`
- **Review Date:** `2026-10-12`
- **Reviewed Artifact SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`
- **Review Decision:** `APPROVE`
- **Review Notes / Conditions:** Author manual review confirms cryptographic provenance, protocol compliance, depth <= 5 bounds, zero object unions, and domain representative workflow fit. Does not claim independent validation.

---

## 3. Human Sign-Off Summary Table

| Slot ID | Admitted Operation | Reviewer Name | Reviewer Role | Decision | Sign-Off Date |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `SLOT_GITHUB_01` | `pulls/create` | `Rishindra Mateti` | `AUTHOR_MANUAL_REVIEW` | `APPROVE` | `2026-10-12` |
| `SLOT_STRIPE_01` | `PostPayouts` | `Rishindra Mateti` | `AUTHOR_MANUAL_REVIEW` | `APPROVE` | `2026-10-12` |
| `SLOT_STRIPE_02` | `PostShippingRates` | `Rishindra Mateti` | `AUTHOR_MANUAL_REVIEW` | `APPROVE` | `2026-10-12` |
| `SLOT_CHATWOOT_01` | `create-a-webhook` | `Rishindra Mateti` | `AUTHOR_MANUAL_REVIEW` | `APPROVE` | `2026-10-12` |
| `SLOT_LINE_01` | `showLoadingAnimation` | `Rishindra Mateti` | `AUTHOR_MANUAL_REVIEW` | `APPROVE` | `2026-10-12` |

