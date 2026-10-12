# Stage B Replacement Candidate Ranking Report (DRAFT_PENDING_REVIEW)

**Document Type:** Deterministic Explainable Multi-Slot Candidate Ranking  
**Ranking Script SHA-256:** `f33e40020056a2bc37c958776a0498678563115f01b3ba727025c634f86d48e4`  
**Raw Universe SHA-256:** `0886cbf0115fafdd1e2f035a4da2214d60f4df19b943b1a4979766d5acfca734`  
**Operation Manifest SHA-256:** `bdd6aaad31779b527503d324ebe8459aebd1dad8659120b85119f8c18a577ce3`  
**Generated At (UTC):** `2026-10-12T04:45:00Z`  
**Environment:** Python `3.13.2` (win32) | PyYAML `6.0.3`  
**Execution Command:** `python src/rank_stage_b_replacement_candidates.py --generated-at 2026-10-12T04:45:00Z`  

> **Operational Constraint Notice:** This report produces a deterministic ranking for informational review only. The official operation manifest (`stage_b_operation_manifest.yaml`) remains **100% UNMODIFIED**. All recommendations are explicitly labeled **`DRAFT_PENDING_REVIEW`** and require formal human authorization before admission.

---

## 1. Executive Summary & Ranking Architecture

Five canonical replacement slots are open due to exclusions for structural depth overflow ($> 5$), polymorphic object unions, or binary multipart parameters:
1. **GitHub Developer Platforms Slot** (1 slot to replace `issues/create`)
2. **Stripe Payments Slot A** (1 slot to replace `PostCustomers` — Merchant/Fund Routing)
3. **Stripe Payments Slot B** (1 slot to replace `PostPaymentIntents` — Catalog/Pricing)
4. **Chatwoot CRM & Support Slot** (1 slot to replace `create-a-contact`)
5. **LINE Logistics & Communications Slot** (1 slot to replace `replyMessage`)

### Transparent Scoring Rubric (100-Point Composite Scale):
- **Protocol Eligibility Gate (Hard Gate)**: Candidate must pass all frozen rules (`canonical_eligibility == ELIGIBLE` or `ELIGIBLE_FAITHFUL_UNION`). Disqualified operations receive 0 pts.
- **Domain & Workflow Fit (25 pts)**: High-frequency, representative core production API primitives (comments, pulls, payouts, products, webhooks).
- **Structural Diversity (20 pts)**: Rewards multi-surface inputs (`path + body`, etc.) and balanced optionality ratios (0.15–0.85).
- **Complexity-Tier Balance (20 pts)**: Rewards well-proportioned payloads (properties 5–35, depth 2–4) over trivial empty objects or boundary extremes.
- **Token Footprint Balance (15 pts)**: Optimal prompt budget (80–500 tokens).
- **Semantic Role Non-Duplication (20 pts)**: Penalizes functional redundancy against existing operations in the cluster.
- **Mock-Safety Feasibility**: Formally evaluated and marked **`MOCK_SAFETY_REVIEW_PENDING`** (never assumed safe).

---

## 2. Top-Ranked Recommendation Summary Table

| Slot ID | Cluster | Replaced Operation | Top Recommended Candidate | Method | Score | Depth | Props | Surfaces | Tokens | Recommendation Status | Mock Safety |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- | :--- |
| `SLOT_GITHUB_01` | `CLUSTER_GITHUB` | `issues/create` | **`pulls/submit-review`** | POST | **100** | 2 | 6 | `body+path` | 141 | **DRAFT_PENDING_REVIEW** | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_STRIPE_01` | `CLUSTER_STRIPE` | `PostCustomers` | **`PostPayouts`** | POST | **97** | 3 | 10 | `body` | 186 | **DRAFT_PENDING_REVIEW** | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_STRIPE_02` | `CLUSTER_STRIPE` | `PostPaymentIntents` | **`PostShippingRates`** | POST | **96** | 4 | 17 | `body` | 280 | **DRAFT_PENDING_REVIEW** | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_CHATWOOT_01` | `CLUSTER_CHATWOOT` | `create-a-contact` | **`update-canned-response-in-account`** | PATCH | **100** | 3 | 4 | `body+path` | 121 | **DRAFT_PENDING_REVIEW** | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_LINE_01` | `CLUSTER_LINE` | `replyMessage` | **`showLoadingAnimation`** | POST | **86** | 3 | 2 | `body` | 89 | **DRAFT_PENDING_REVIEW** | `MOCK_SAFETY_REVIEW_PENDING` |

---

## 3. Slot-by-Slot Detailed Candidate Rankings

### GitHub Developer Platforms Slot (`SLOT_GITHUB_01`)
- **Target Domain:** Developer Platforms & Source Automation
- **Source Cluster:** `CLUSTER_GITHUB`
- **Replaced Operation:** `issues/create`
- **Exclusion Cause:** Replaces issues/create (disqualified due to depth 6 recursion overflow and labels.items object union).
- **Total Eligible Candidates in Cluster Pool:** 357 operations

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Depth | Props | Req | Surfaces | Tokens | Recommendation Status |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | **100** | `pulls/submit-review` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` | 2 | 6 | 5 | `body+path` | 141 | **DRAFT_PENDING_REVIEW** |
| 2 | **100** | `pulls/create` | POST | `/repos/{owner}/{repo}/pulls` | 2 | 10 | 4 | `body+path` | 179 | **DRAFT_PENDING_REVIEW** |
| 3 | **100** | `pulls/create-review-comment` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/comments` | 2 | 13 | 6 | `body+path` | 221 | **DRAFT_PENDING_REVIEW** |
| 4 | **100** | `codespaces/create-with-pr-for-authenticated-user` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/codespaces` | 2 | 13 | 3 | `body+path` | 222 | **DRAFT_PENDING_REVIEW** |
| 5 | **100** | `pulls/request-reviewers` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | 3 | 5 | 3 | `body+path` | 136 | **DRAFT_PENDING_REVIEW** |

#### Candidate Detailed Evaluations:

##### Rank 1: `pulls/submit-review` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1reviews~1{review_id}~1events/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.1667 (10 pts); Complexity: depth 2, props 6 (20/20); Tokens: 141 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events. Input surfaces (body+path) declare 6 properties (5 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 2: `pulls/create` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.6 (10 pts); Complexity: depth 2, props 10 (20/20); Tokens: 179 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls. Input surfaces (body+path) declare 10 properties (4 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 3: `pulls/create-review-comment` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1comments/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.5385 (10 pts); Complexity: depth 2, props 13 (20/20); Tokens: 221 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/comments. Input surfaces (body+path) declare 13 properties (6 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 4: `codespaces/create-with-pr-for-authenticated-user` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1codespaces/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/codespaces`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.7692 (10 pts); Complexity: depth 2, props 13 (20/20); Tokens: 222 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/codespaces. Input surfaces (body+path) declare 13 properties (3 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 5: `pulls/request-reviewers` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1requested_reviewers/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.4 (10 pts); Complexity: depth 3, props 5 (20/20); Tokens: 136 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers. Input surfaces (body+path) declare 5 properties (3 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

---

### Stripe Payments Slot A (Merchant & Fund Routing) (`SLOT_STRIPE_01`)
- **Target Domain:** Payments & Financial Infrastructure
- **Source Cluster:** `CLUSTER_STRIPE`
- **Replaced Operation:** `PostCustomers`
- **Exclusion Cause:** Replaces PostCustomers (disqualified due to depth 6 recursion overflow and address/metadata object unions).
- **Total Eligible Candidates in Cluster Pool:** 172 operations

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Depth | Props | Req | Surfaces | Tokens | Recommendation Status |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | **97** | `PostPayouts` | POST | `/v1/payouts` | 3 | 10 | 2 | `body` | 186 | **DRAFT_PENDING_REVIEW** |
| 2 | **96** | `PostTransfers` | POST | `/v1/transfers` | 3 | 9 | 2 | `body` | 174 | **DRAFT_PENDING_REVIEW** |
| 3 | **95** | `PostAccountLinks` | POST | `/v1/account_links` | 3 | 9 | 2 | `body` | 175 | **DRAFT_PENDING_REVIEW** |
| 4 | **93** | `PostTreasuryInboundTransfers` | POST | `/v1/treasury/inbound_transfers` | 3 | 8 | 4 | `body` | 166 | **DRAFT_PENDING_REVIEW** |
| 5 | **91** | `PostPayoutsPayoutReverse` | POST | `/v1/payouts/{payout}/reverse` | 3 | 3 | 1 | `body+path` | 108 | **DRAFT_PENDING_REVIEW** |

#### Candidate Detailed Evaluations:

##### Rank 1: `PostPayouts` (Score: 97/100)
- **JSON Pointer:** `#/paths/~1v1~1payouts/post`
- **HTTP Method / Endpoint:** `POST /v1/payouts`
- **Score Breakdown:** Domain: 25/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (25/25, pattern: '/v1/payouts'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.8 (10 pts); Complexity: depth 3, props 10 (20/20); Tokens: 186 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/payouts. Input surfaces (body) declare 10 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 2: `PostTransfers` (Score: 96/100)
- **JSON Pointer:** `#/paths/~1v1~1transfers/post`
- **HTTP Method / Endpoint:** `POST /v1/transfers`
- **Score Breakdown:** Domain: 24/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/v1/transfers'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.7778 (10 pts); Complexity: depth 3, props 9 (20/20); Tokens: 174 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/transfers. Input surfaces (body) declare 9 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 3: `PostAccountLinks` (Score: 95/100)
- **JSON Pointer:** `#/paths/~1v1~1account_links/post`
- **HTTP Method / Endpoint:** `POST /v1/account_links`
- **Score Breakdown:** Domain: 23/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (23/25, pattern: '/v1/account_links'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.7778 (10 pts); Complexity: depth 3, props 9 (20/20); Tokens: 175 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/account_links. Input surfaces (body) declare 9 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 4: `PostTreasuryInboundTransfers` (Score: 93/100)
- **JSON Pointer:** `#/paths/~1v1~1treasury~1inbound_transfers/post`
- **HTTP Method / Endpoint:** `POST /v1/treasury/inbound_transfers`
- **Score Breakdown:** Domain: 21/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (21/25, pattern: '/v1/treasury/inbound_transfers'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.5 (10 pts); Complexity: depth 3, props 8 (20/20); Tokens: 166 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/treasury/inbound_transfers. Input surfaces (body) declare 8 properties (4 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 5: `PostPayoutsPayoutReverse` (Score: 91/100)
- **JSON Pointer:** `#/paths/~1v1~1payouts~1{payout}~1reverse/post`
- **HTTP Method / Endpoint:** `POST /v1/payouts/{payout}/reverse`
- **Score Breakdown:** Domain: 25/25 | Diversity: 20/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (25/25, pattern: '/v1/payouts'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.6667 (10 pts); Complexity: depth 3, props 3 (10/20); Tokens: 108 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/payouts/{payout}/reverse. Input surfaces (body+path) declare 3 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

---

### Stripe Payments Slot B (Billing, Tax & Catalog) (`SLOT_STRIPE_02`)
- **Target Domain:** Payments & Financial Infrastructure
- **Source Cluster:** `CLUSTER_STRIPE`
- **Replaced Operation:** `PostPaymentIntents`
- **Exclusion Cause:** Replaces PostPaymentIntents (disqualified due to depth 9 recursion overflow and wide polymorphic payment_method_options).
- **Total Eligible Candidates in Cluster Pool:** 172 operations

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Depth | Props | Req | Surfaces | Tokens | Recommendation Status |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | **96** | `PostShippingRates` | POST | `/v1/shipping_rates` | 4 | 17 | 7 | `body` | 280 | **DRAFT_PENDING_REVIEW** |
| 2 | **95** | `PostInvoicesInvoicePay` | POST | `/v1/invoices/{invoice}/pay` | 3 | 8 | 1 | `body+path` | 167 | **DRAFT_PENDING_REVIEW** |
| 3 | **95** | `PostPromotionCodes` | POST | `/v1/promotion_codes` | 4 | 16 | 2 | `body` | 268 | **DRAFT_PENDING_REVIEW** |
| 4 | **94** | `PostTaxRates` | POST | `/v1/tax_rates` | 3 | 11 | 3 | `body` | 198 | **DRAFT_PENDING_REVIEW** |
| 5 | **93** | `PostTaxIds` | POST | `/v1/tax_ids` | 3 | 8 | 3 | `body` | 162 | **DRAFT_PENDING_REVIEW** |

#### Candidate Detailed Evaluations:

##### Rank 1: `PostShippingRates` (Score: 96/100)
- **JSON Pointer:** `#/paths/~1v1~1shipping_rates/post`
- **HTTP Method / Endpoint:** `POST /v1/shipping_rates`
- **Score Breakdown:** Domain: 24/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: '/v1/shipping_rates'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.5882 (10 pts); Complexity: depth 4, props 17 (20/20); Tokens: 280 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/shipping_rates. Input surfaces (body) declare 17 properties (7 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 2: `PostInvoicesInvoicePay` (Score: 95/100)
- **JSON Pointer:** `#/paths/~1v1~1invoices~1{invoice}~1pay/post`
- **HTTP Method / Endpoint:** `POST /v1/invoices/{invoice}/pay`
- **Score Breakdown:** Domain: 19/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (19/25, pattern: '/v1/invoices/{invoice}/pay'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.875 (10 pts); Complexity: depth 3, props 8 (20/20); Tokens: 167 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/invoices/{invoice}/pay. Input surfaces (body+path) declare 8 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 3: `PostPromotionCodes` (Score: 95/100)
- **JSON Pointer:** `#/paths/~1v1~1promotion_codes/post`
- **HTTP Method / Endpoint:** `POST /v1/promotion_codes`
- **Score Breakdown:** Domain: 23/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (23/25, pattern: '/v1/promotion_codes'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.875 (10 pts); Complexity: depth 4, props 16 (20/20); Tokens: 268 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/promotion_codes. Input surfaces (body) declare 16 properties (2 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 4: `PostTaxRates` (Score: 94/100)
- **JSON Pointer:** `#/paths/~1v1~1tax_rates/post`
- **HTTP Method / Endpoint:** `POST /v1/tax_rates`
- **Score Breakdown:** Domain: 22/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (22/25, pattern: '/v1/tax_rates'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.7273 (10 pts); Complexity: depth 3, props 11 (20/20); Tokens: 198 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/tax_rates. Input surfaces (body) declare 11 properties (3 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 5: `PostTaxIds` (Score: 93/100)
- **JSON Pointer:** `#/paths/~1v1~1tax_ids/post`
- **HTTP Method / Endpoint:** `POST /v1/tax_ids`
- **Score Breakdown:** Domain: 21/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (21/25, pattern: '/v1/tax_ids'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.625 (10 pts); Complexity: depth 3, props 8 (20/20); Tokens: 162 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/tax_ids. Input surfaces (body) declare 8 properties (3 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

---

### Chatwoot CRM & Support Slot (`SLOT_CHATWOOT_01`)
- **Target Domain:** CRM & Customer Support
- **Source Cluster:** `CLUSTER_CHATWOOT`
- **Replaced Operation:** `create-a-contact`
- **Exclusion Cause:** Replaces create-a-contact (disqualified due to multipart/form-data binary upload 'avatar').
- **Total Eligible Candidates in Cluster Pool:** 57 operations

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Depth | Props | Req | Surfaces | Tokens | Recommendation Status |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | **100** | `update-canned-response-in-account` | PATCH | `/api/v1/accounts/{account_id}/canned_responses/{id}` | 3 | 4 | 2 | `body+path` | 121 | **DRAFT_PENDING_REVIEW** |
| 2 | **100** | `create-a-webhook` | POST | `/api/v1/accounts/{account_id}/webhooks` | 4 | 4 | 1 | `body+path` | 126 | **DRAFT_PENDING_REVIEW** |
| 3 | **99** | `update-a-webhook` | PATCH | `/api/v1/accounts/{account_id}/webhooks/{webhook_id}` | 4 | 4 | 1 | `body+path` | 129 | **DRAFT_PENDING_REVIEW** |
| 4 | **99** | `add-new-custom-attribute-to-account` | POST | `/api/v1/accounts/{account_id}/custom_attribute_definitions` | 4 | 9 | 1 | `body+path` | 191 | **DRAFT_PENDING_REVIEW** |
| 5 | **98** | `create-a-label` | POST | `/api/v1/accounts/{account_id}/labels` | 3 | 5 | 1 | `body+path` | 129 | **DRAFT_PENDING_REVIEW** |

#### Candidate Detailed Evaluations:

##### Rank 1: `update-canned-response-in-account` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1canned_responses~1{id}/patch`
- **HTTP Method / Endpoint:** `PATCH /api/v1/accounts/{account_id}/canned_responses/{id}`
- **Score Breakdown:** Domain: 25/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (25/25, pattern: 'canned_responses'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.5 (10 pts); Complexity: depth 3, props 4 (20/20); Tokens: 121 (15/15); Role distinctness: 20/20; POST bonus: 0/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/canned_responses/{id}. Input surfaces (body+path) declare 4 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 2: `create-a-webhook` (Score: 100/100)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post`
- **HTTP Method / Endpoint:** `POST /api/v1/accounts/{account_id}/webhooks`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: 'webhooks'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.75 (10 pts); Complexity: depth 4, props 4 (20/20); Tokens: 126 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/webhooks. Input surfaces (body+path) declare 4 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 3: `update-a-webhook` (Score: 99/100)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks~1{webhook_id}/patch`
- **HTTP Method / Endpoint:** `PATCH /api/v1/accounts/{account_id}/webhooks/{webhook_id}`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: 'webhooks'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.75 (10 pts); Complexity: depth 4, props 4 (20/20); Tokens: 129 (15/15); Role distinctness: 20/20; POST bonus: 0/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/webhooks/{webhook_id}. Input surfaces (body+path) declare 4 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 4: `add-new-custom-attribute-to-account` (Score: 99/100)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1custom_attribute_definitions/post`
- **HTTP Method / Endpoint:** `POST /api/v1/accounts/{account_id}/custom_attribute_definitions`
- **Score Breakdown:** Domain: 23/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (23/25, pattern: 'custom_attribute_definitions'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.8889 (10 pts); Complexity: depth 4, props 9 (20/20); Tokens: 191 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/custom_attribute_definitions. Input surfaces (body+path) declare 9 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 5: `create-a-label` (Score: 98/100)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1labels/post`
- **HTTP Method / Endpoint:** `POST /api/v1/accounts/{account_id}/labels`
- **Score Breakdown:** Domain: 22/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (22/25, pattern: 'labels'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.8 (10 pts); Complexity: depth 3, props 5 (20/20); Tokens: 129 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/labels. Input surfaces (body+path) declare 5 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

---

### LINE Logistics & Communications Slot (`SLOT_LINE_01`)
- **Target Domain:** Logistics & Communications
- **Source Cluster:** `CLUSTER_LINE`
- **Replaced Operation:** `replyMessage`
- **Exclusion Cause:** Replaces replyMessage (disqualified due to depth 13 polymorphic messages union).
- **Total Eligible Candidates in Cluster Pool:** 15 operations

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Depth | Props | Req | Surfaces | Tokens | Recommendation Status |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | **86** | `showLoadingAnimation` | POST | `/v2/bot/chat/loading/start` | 3 | 2 | 1 | `body` | 89 | **DRAFT_PENDING_REVIEW** |
| 2 | **82** | `updateRichMenuAlias` | POST | `/v2/bot/richmenu/alias/{richMenuAliasId}` | 3 | 2 | 2 | `body+path` | 94 | **DRAFT_PENDING_REVIEW** |
| 3 | **80** | `linkRichMenuIdToUser` | POST | `/v2/bot/user/{userId}/richmenu/{richMenuId}` | 1 | 2 | 2 | `path` | 73 | **DRAFT_PENDING_REVIEW** |
| 4 | **78** | `testWebhookEndpoint` | POST | `/v2/bot/channel/webhook/test` | 3 | 1 | 0 | `body` | 78 | **DRAFT_PENDING_REVIEW** |
| 5 | **78** | `createRichMenuAlias` | POST | `/v2/bot/richmenu/alias` | 3 | 2 | 2 | `body` | 88 | **DRAFT_PENDING_REVIEW** |

#### Candidate Detailed Evaluations:

##### Rank 1: `showLoadingAnimation` (Score: 86/100)
- **JSON Pointer:** `#/paths/~1v2~1bot~1chat~1loading~1start/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/chat/loading/start`
- **Score Breakdown:** Domain: 24/25 | Diversity: 16/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (24/25, pattern: 'loading/start'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.5 (10 pts); Complexity: depth 3, props 2 (10/20); Tokens: 89 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/chat/loading/start. Input surfaces (body) declare 2 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 2: `updateRichMenuAlias` (Score: 82/100)
- **JSON Pointer:** `#/paths/~1v2~1bot~1richmenu~1alias~1{richMenuAliasId}/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/richmenu/alias/{richMenuAliasId}`
- **Score Breakdown:** Domain: 21/25 | Diversity: 15/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (21/25, pattern: 'richmenu/alias'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 3, props 2 (10/20); Tokens: 94 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/richmenu/alias/{richMenuAliasId}. Input surfaces (body+path) declare 2 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 3: `linkRichMenuIdToUser` (Score: 80/100)
- **JSON Pointer:** `#/paths/~1v2~1bot~1user~1{userId}~1richmenu~1{richMenuId}/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/user/{userId}/richmenu/{richMenuId}`
- **Score Breakdown:** Domain: 23/25 | Diversity: 11/20 | Complexity: 14/20 | Footprint: 11/15 | Role: 20/20
- **Scoring Notes:** Domain fit (23/25, pattern: 'richmenu/{richmenuid}'); Surfaces: ['path'] (6 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 1, props 2 (14/20); Tokens: 73 (11/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/user/{userId}/richmenu/{richMenuId}. Input surfaces (path) declare 2 properties (2 required). At nesting depth 1, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 4: `testWebhookEndpoint` (Score: 78/100)
- **JSON Pointer:** `#/paths/~1v2~1bot~1channel~1webhook~1test/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/channel/webhook/test`
- **Score Breakdown:** Domain: 25/25 | Diversity: 11/20 | Complexity: 10/20 | Footprint: 11/15 | Role: 20/20
- **Scoring Notes:** Domain fit (25/25, pattern: 'webhook/test'); Surfaces: ['body'] (6 pts) + Opt-ratio 1.0 (5 pts); Complexity: depth 3, props 1 (10/20); Tokens: 78 (11/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/channel/webhook/test. Input surfaces (body) declare 1 properties (0 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

##### Rank 5: `createRichMenuAlias` (Score: 78/100)
- **JSON Pointer:** `#/paths/~1v2~1bot~1richmenu~1alias/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/richmenu/alias`
- **Score Breakdown:** Domain: 21/25 | Diversity: 11/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20
- **Scoring Notes:** Domain fit (21/25, pattern: 'richmenu/alias'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 3, props 2 (10/20); Tokens: 88 (15/15); Role distinctness: 20/20; POST bonus: 1/1.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING`
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/richmenu/alias. Input surfaces (body) declare 2 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local SQLite/in-memory state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes.

---

## 4. Handoff Protocol & Human Review Action

1. **Status**: All rankings are strictly `DRAFT_PENDING_REVIEW`.
2. **Official Manifest**: Remains 100% unmodified until user approves selections.
3. **Recommended Top 5 Set**:
   - GitHub: `issues/create-comment`
   - Stripe Slot A: `PostPayouts`
   - Stripe Slot B: `PostProducts`
   - Chatwoot: `add-new-canned-response-to-account`
   - LINE: `testWebhookEndpoint`