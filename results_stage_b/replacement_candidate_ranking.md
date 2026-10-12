# Stage B Replacement Candidate Ranking Report (DRAFT_PENDING_REVIEW)

**Document Type:** Deterministic Explainable Multi-Slot Candidate Ranking  
**Ranking Script SHA-256:** `212462e8323027dcfe79dac9024fed0ec20d00ee93deee5ae00c633deb223c3a`  
**Ranking Config SHA-256:** `f7dff5f3e9e8155e0babbaecb51da0981eb252787c177ec2cc4f48eb7f0a13ed`  
**Raw Universe SHA-256:** `9fdb53f08049f5e3c8257ccfc6f305dcf1ed16cba5047124eb528900e12b8096`  
**Operation Manifest SHA-256:** `bdd6aaad31779b527503d324ebe8459aebd1dad8659120b85119f8c18a577ce3`  
**Generated At (UTC):** `2026-10-12T04:45:00Z`  
**Environment:** Python `3.13.2` (win32) | PyYAML `6.0.3`  
**Execution Command:** `python src/rank_stage_b_replacement_candidates.py --generated-at 2026-10-12T04:45:00Z`  

> **Operational Constraint Notice:** This report produces a deterministic ranking for informational review only. The official operation manifest (`stage_b_operation_manifest.yaml`) remains **100% UNMODIFIED**. All recommendations are explicitly labeled **`DRAFT_PENDING_REVIEW`** and require formal human authorization before admission.

> **Scientific Modesty Principles:**  
> 1. **Co-Leading Ties:** Multiple operations sharing the top score are preserved as co-leading candidates. A score of 100 does not imply a uniquely best choice.  
> 2. **Mock-Safety Inactive:** Mock-safety feasibility contributes strictly 0 points until empirical mock state execution is verified.  
> 3. **Statefulness Transparency:** Operations depending on pre-existing external state (e.g. `pulls/submit-review` depending on `review_id`) are explicitly flagged; self-contained constructors (e.g. `pulls/create`) must be evaluated alongside them.

---

## 1. Executive Summary & Ranking Architecture

Five canonical replacement slots are open due to exclusions for structural depth overflow ($> 5$), polymorphic object unions, or binary multipart parameters:
1. **GitHub Developer Platforms Slot** (1 slot to replace `issues/create`)
2. **Stripe Payments Slot A** (1 slot to replace `PostCustomers` — Merchant/Fund Routing)
3. **Stripe Payments Slot B** (1 slot to replace `PostPaymentIntents` — Catalog/Pricing)
4. **Chatwoot CRM & Support Slot** (1 slot to replace `create-a-contact`)
5. **LINE Logistics & Communications Slot** (1 slot to replace `replyMessage`)

### Transparent Scoring Rubric (Pinned in `results_stage_b/replacement_ranking_config.yaml`):
- **Protocol Eligibility Gate (Hard Gate)**: Candidate must pass all static filter rules (`static_eligibility == STATICALLY_ELIGIBLE_CANDIDATE` or `STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE`). Disqualified operations receive 0 pts.
- **Domain & Workflow Fit (25 pts)**: High-frequency, representative core production API primitives (comments, pulls, payouts, shipping rates, webhooks).
- **Structural Diversity (20 pts)**: Rewards multi-surface inputs (`path + body`, etc.) and balanced optionality ratios (0.10–0.90).
- **Complexity-Tier Balance (20 pts)**: Rewards well-proportioned payloads (properties 4–35, depth 2–4) over trivial empty objects or boundary extremes.
- **Token Footprint Balance (15 pts)**: Optimal prompt budget (80–500 tokens).
- **Semantic Role Non-Duplication (20 pts)**: Penalizes functional redundancy against existing operations in the cluster.
- **Mock-Safety Feasibility**: Formally evaluated and marked **`MOCK_SAFETY_REVIEW_PENDING`** (0 points contributed; never assumed safe).

---

## 2. Co-Leading Replacement Recommendations Summary Table

| Slot ID | Cluster | Replaced Operation | Top Candidate | Method | Score | Status Label | Depth | Props | Surfaces | Stateful? | Mock Safety |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| `SLOT_GITHUB_01` | `CLUSTER_GITHUB` | `issues/create` | **`pulls/submit-review`** | POST | **100** | `CO_LEADING_CANDIDATE (Tied)` | 2 | 6 | `body+path` | ⚠️ YES | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_STRIPE_01` | `CLUSTER_STRIPE` | `PostCustomers` | **`PostPayouts`** | POST | **97** | `CO_LEADING_CANDIDATE (Tied)` | 3 | 10 | `body` | NO | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_STRIPE_02` | `CLUSTER_STRIPE` | `PostPaymentIntents` | **`PostInvoicesInvoiceAttachPayment`** | POST | **99** | `CO_LEADING_CANDIDATE (Tied)` | 3 | 4 | `body+path` | ⚠️ YES | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_CHATWOOT_01` | `CLUSTER_CHATWOOT` | `create-a-contact` | **`update-canned-response-in-account`** | PATCH | **100** | `CO_LEADING_CANDIDATE (Tied)` | 3 | 4 | `body+path` | ⚠️ YES | `MOCK_SAFETY_REVIEW_PENDING` |
| `SLOT_LINE_01` | `CLUSTER_LINE` | `replyMessage` | **`showLoadingAnimation`** | POST | **87** | `CO_LEADING_CANDIDATE (Tied)` | 3 | 2 | `body` | NO | `MOCK_SAFETY_REVIEW_PENDING` |

---

## 3. Slot-by-Slot Detailed Candidate Rankings

### GitHub Developer Platforms Slot (`SLOT_GITHUB_01`)
- **Target Domain:** Developer Platforms & Source Automation
- **Source Cluster:** `CLUSTER_GITHUB`
- **Replaced Operation:** `issues/create`
- **Exclusion Cause:** Replaces issues/create (disqualified due to depth 6 recursion overflow and labels.items object union).
- **Statefulness Guidance:** pulls/submit-review requires an existing review_id (stateful dependency). Self-contained operations such as pulls/create should be evaluated alongside it.

- **Total Statically Eligible Candidates in Cluster Pool:** 357 operations
- **Co-Leading Candidates Count:** 5

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Status Label | Depth | Props | Req | Surfaces | Stateful? |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| 1 | **100** | `pulls/submit-review` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` | `CO_LEADING_CANDIDATE (Tied)` | 2 | 6 | 5 | `body+path` | ⚠️ YES |
| 2 | **100** | `pulls/create` | POST | `/repos/{owner}/{repo}/pulls` | `CO_LEADING_CANDIDATE (Tied)` | 2 | 10 | 4 | `body+path` | NO |
| 3 | **100** | `pulls/create-review-comment` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/comments` | `CO_LEADING_CANDIDATE (Tied)` | 2 | 13 | 6 | `body+path` | NO |
| 4 | **100** | `codespaces/create-with-pr-for-authenticated-user` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/codespaces` | `CO_LEADING_CANDIDATE (Tied)` | 2 | 13 | 3 | `body+path` | NO |
| 5 | **100** | `pulls/request-reviewers` | POST | `/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers` | `CO_LEADING_CANDIDATE (Tied)` | 3 | 5 | 3 | `body+path` | NO |

#### Candidate Detailed Evaluations:

##### Rank 1: `pulls/submit-review` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1reviews~1{review_id}~1events/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.1667 (10 pts); Complexity: depth 2, props 6 (20/20); Tokens: 141 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction). [WARNING: POTENTIALLY_STATEFUL_DEPENDENCY: Requires a pre-existing review_id created in a prior review turn. Cannot be called without prior state setup; self-contained pulls/create should be evaluated alongside it.]
- **Statefulness Warning:** POTENTIALLY_STATEFUL_DEPENDENCY: Requires a pre-existing review_id created in a prior review turn. Cannot be called without prior state setup; self-contained pulls/create should be evaluated alongside it.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events. Input surfaces (body+path) declare 6 properties (5 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 2: `pulls/create` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.6 (10 pts); Complexity: depth 2, props 10 (20/20); Tokens: 179 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls. Input surfaces (body+path) declare 10 properties (4 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 3: `pulls/create-review-comment` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1comments/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.5385 (10 pts); Complexity: depth 2, props 13 (20/20); Tokens: 221 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/comments. Input surfaces (body+path) declare 13 properties (6 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 4: `codespaces/create-with-pr-for-authenticated-user` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1codespaces/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/codespaces`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.7692 (10 pts); Complexity: depth 2, props 13 (20/20); Tokens: 222 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/codespaces. Input surfaces (body+path) declare 13 properties (3 required). At nesting depth 2, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 5: `pulls/request-reviewers` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls~1{pull_number}~1requested_reviewers/post`
- **HTTP Method / Endpoint:** `POST /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/pulls'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.4 (10 pts); Complexity: depth 3, props 5 (20/20); Tokens: 136 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers. Input surfaces (body+path) declare 5 properties (3 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

---

### Stripe Payments Slot A (`SLOT_STRIPE_01`)
- **Target Domain:** Merchant Fund Routing & Balances
- **Source Cluster:** `CLUSTER_STRIPE`
- **Replaced Operation:** `PostCustomers`
- **Exclusion Cause:** Replaces PostCustomers (disqualified due to depth 6 recursion overflow and address/metadata anyOf unions).
- **Statefulness Guidance:** None; endpoints evaluate standard merchant balance and transfer structures.
- **Total Statically Eligible Candidates in Cluster Pool:** 172 operations
- **Co-Leading Candidates Count:** 1

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Status Label | Depth | Props | Req | Surfaces | Stateful? |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| 1 | **97** | `PostPayouts` | POST | `/v1/payouts` | `CO_LEADING_CANDIDATE (Tied)` | 3 | 10 | 2 | `body` | NO |
| 2 | **96** | `PostTransfers` | POST | `/v1/transfers` | `RANK_2` | 3 | 9 | 2 | `body` | NO |
| 3 | **94** | `PostAccountLinks` | POST | `/v1/account_links` | `RANK_3` | 3 | 9 | 2 | `body` | NO |
| 4 | **91** | `PostPayoutsPayoutCancel` | POST | `/v1/payouts/{payout}/cancel` | `RANK_4` | 3 | 2 | 1 | `body+path` | NO |
| 5 | **91** | `PostPayoutsPayoutReverse` | POST | `/v1/payouts/{payout}/reverse` | `RANK_5` | 3 | 3 | 1 | `body+path` | NO |

#### Candidate Detailed Evaluations:

##### Rank 1: `PostPayouts` (Score: 97/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1v1~1payouts/post`
- **HTTP Method / Endpoint:** `POST /v1/payouts`
- **Score Breakdown:** Domain: 25/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (25/25, pattern: '/payouts'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.8 (10 pts); Complexity: depth 3, props 10 (20/20); Tokens: 186 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/payouts. Input surfaces (body) declare 10 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 2: `PostTransfers` (Score: 96/100 — `RANK_2`)
- **JSON Pointer:** `#/paths/~1v1~1transfers/post`
- **HTTP Method / Endpoint:** `POST /v1/transfers`
- **Score Breakdown:** Domain: 24/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/transfers'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.7778 (10 pts); Complexity: depth 3, props 9 (20/20); Tokens: 174 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/transfers. Input surfaces (body) declare 9 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 3: `PostAccountLinks` (Score: 94/100 — `RANK_3`)
- **JSON Pointer:** `#/paths/~1v1~1account_links/post`
- **HTTP Method / Endpoint:** `POST /v1/account_links`
- **Score Breakdown:** Domain: 22/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: '/account_links'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.7778 (10 pts); Complexity: depth 3, props 9 (20/20); Tokens: 175 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/account_links. Input surfaces (body) declare 9 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 4: `PostPayoutsPayoutCancel` (Score: 91/100 — `RANK_4`)
- **JSON Pointer:** `#/paths/~1v1~1payouts~1{payout}~1cancel/post`
- **HTTP Method / Endpoint:** `POST /v1/payouts/{payout}/cancel`
- **Score Breakdown:** Domain: 25/25 | Diversity: 20/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (25/25, pattern: '/payouts'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.5 (10 pts); Complexity: depth 3, props 2 (10/20); Tokens: 95 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/payouts/{payout}/cancel. Input surfaces (body+path) declare 2 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 5: `PostPayoutsPayoutReverse` (Score: 91/100 — `RANK_5`)
- **JSON Pointer:** `#/paths/~1v1~1payouts~1{payout}~1reverse/post`
- **HTTP Method / Endpoint:** `POST /v1/payouts/{payout}/reverse`
- **Score Breakdown:** Domain: 25/25 | Diversity: 20/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (25/25, pattern: '/payouts'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.6667 (10 pts); Complexity: depth 3, props 3 (10/20); Tokens: 108 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/payouts/{payout}/reverse. Input surfaces (body+path) declare 3 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

---

### Stripe Payments Slot B (`SLOT_STRIPE_02`)
- **Target Domain:** Billing, Tax, & Commerce
- **Source Cluster:** `CLUSTER_STRIPE`
- **Replaced Operation:** `PostPaymentIntents`
- **Exclusion Cause:** Replaces PostPaymentIntents (disqualified due to depth 9 recursion overflow and wide payment_method_options unions).
- **Statefulness Guidance:** PostInvoicesInvoicePay depends on an unpaid invoice ID; PostShippingRates is self-contained.
- **Total Statically Eligible Candidates in Cluster Pool:** 172 operations
- **Co-Leading Candidates Count:** 2

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Status Label | Depth | Props | Req | Surfaces | Stateful? |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| 1 | **99** | `PostInvoicesInvoiceAttachPayment` | POST | `/v1/invoices/{invoice}/attach_payment` | `CO_LEADING_CANDIDATE (Tied)` | 3 | 4 | 1 | `body+path` | ⚠️ YES |
| 2 | **99** | `PostInvoicesInvoicePay` | POST | `/v1/invoices/{invoice}/pay` | `CO_LEADING_CANDIDATE (Tied)` | 3 | 8 | 1 | `body+path` | ⚠️ YES |
| 3 | **97** | `PostShippingRates` | POST | `/v1/shipping_rates` | `RANK_3` | 4 | 17 | 7 | `body` | NO |
| 4 | **96** | `PostTaxRates` | POST | `/v1/tax_rates` | `RANK_4` | 3 | 11 | 3 | `body` | NO |
| 5 | **94** | `PostPromotionCodes` | POST | `/v1/promotion_codes` | `RANK_5` | 4 | 16 | 2 | `body` | NO |

#### Candidate Detailed Evaluations:

##### Rank 1: `PostInvoicesInvoiceAttachPayment` (Score: 99/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1v1~1invoices~1{invoice}~1attach_payment/post`
- **HTTP Method / Endpoint:** `POST /v1/invoices/{invoice}/attach_payment`
- **Score Breakdown:** Domain: 23/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (23/25, pattern: '/invoices'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.75 (10 pts); Complexity: depth 3, props 4 (20/20); Tokens: 122 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction). [WARNING: Requires an existing unpaid invoice; PostShippingRates is self-contained.]
- **Statefulness Warning:** Requires an existing unpaid invoice; PostShippingRates is self-contained.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/invoices/{invoice}/attach_payment. Input surfaces (body+path) declare 4 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 2: `PostInvoicesInvoicePay` (Score: 99/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1v1~1invoices~1{invoice}~1pay/post`
- **HTTP Method / Endpoint:** `POST /v1/invoices/{invoice}/pay`
- **Score Breakdown:** Domain: 23/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (23/25, pattern: '/invoices'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.875 (10 pts); Complexity: depth 3, props 8 (20/20); Tokens: 167 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction). [WARNING: Requires an existing unpaid invoice; PostShippingRates is self-contained.]
- **Statefulness Warning:** Requires an existing unpaid invoice; PostShippingRates is self-contained.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/invoices/{invoice}/pay. Input surfaces (body+path) declare 8 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 3: `PostShippingRates` (Score: 97/100 — `RANK_3`)
- **JSON Pointer:** `#/paths/~1v1~1shipping_rates/post`
- **HTTP Method / Endpoint:** `POST /v1/shipping_rates`
- **Score Breakdown:** Domain: 25/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (25/25, pattern: '/shipping_rates'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.5882 (10 pts); Complexity: depth 4, props 17 (20/20); Tokens: 280 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/shipping_rates. Input surfaces (body) declare 17 properties (7 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 4: `PostTaxRates` (Score: 96/100 — `RANK_4`)
- **JSON Pointer:** `#/paths/~1v1~1tax_rates/post`
- **HTTP Method / Endpoint:** `POST /v1/tax_rates`
- **Score Breakdown:** Domain: 24/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: '/tax_rates'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.7273 (10 pts); Complexity: depth 3, props 11 (20/20); Tokens: 198 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/tax_rates. Input surfaces (body) declare 11 properties (3 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 5: `PostPromotionCodes` (Score: 94/100 — `RANK_5`)
- **JSON Pointer:** `#/paths/~1v1~1promotion_codes/post`
- **HTTP Method / Endpoint:** `POST /v1/promotion_codes`
- **Score Breakdown:** Domain: 22/25 | Diversity: 16/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: '/promotion_codes'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.875 (10 pts); Complexity: depth 4, props 16 (20/20); Tokens: 268 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v1/promotion_codes. Input surfaces (body) declare 16 properties (2 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

---

### Chatwoot CRM & Support Slot (`SLOT_CHATWOOT_01`)
- **Target Domain:** Customer Support Automation & Canned Responses
- **Source Cluster:** `CLUSTER_CHATWOOT`
- **Replaced Operation:** `create-a-contact`
- **Exclusion Cause:** Replaces create-a-contact (disqualified due to binary avatar property).
- **Statefulness Guidance:** update-canned-response-in-account requires account_id and canned response id.
- **Total Statically Eligible Candidates in Cluster Pool:** 57 operations
- **Co-Leading Candidates Count:** 2

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Status Label | Depth | Props | Req | Surfaces | Stateful? |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| 1 | **100** | `update-canned-response-in-account` | PATCH | `/api/v1/accounts/{account_id}/canned_responses/{id}` | `CO_LEADING_CANDIDATE (Tied)` | 3 | 4 | 2 | `body+path` | ⚠️ YES |
| 2 | **100** | `create-a-webhook` | POST | `/api/v1/accounts/{account_id}/webhooks` | `CO_LEADING_CANDIDATE (Tied)` | 4 | 4 | 1 | `body+path` | NO |
| 3 | **99** | `update-a-webhook` | PATCH | `/api/v1/accounts/{account_id}/webhooks/{webhook_id}` | `RANK_3` | 4 | 4 | 1 | `body+path` | NO |
| 4 | **98** | `add-new-automation-rule-to-account` | POST | `/api/v1/accounts/{account_id}/automation_rules` | `RANK_4` | 4 | 7 | 1 | `body+path` | NO |
| 5 | **97** | `update-automation-rule-in-account` | PATCH | `/api/v1/accounts/{account_id}/automation_rules/{id}` | `RANK_5` | 4 | 8 | 2 | `body+path` | NO |

#### Candidate Detailed Evaluations:

##### Rank 1: `update-canned-response-in-account` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1canned_responses~1{id}/patch`
- **HTTP Method / Endpoint:** `PATCH /api/v1/accounts/{account_id}/canned_responses/{id}`
- **Score Breakdown:** Domain: 25/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (25/25, pattern: 'canned_responses'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.5 (10 pts); Complexity: depth 3, props 4 (20/20); Tokens: 121 (15/15); Role distinctness: 20/20; POST bonus: 0/1; Mock-safety points: 0 (deferred pending extraction). [WARNING: Requires an existing canned response id to update; requires seeded mock state.]
- **Statefulness Warning:** Requires an existing canned response id to update; requires seeded mock state.
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/canned_responses/{id}. Input surfaces (body+path) declare 4 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 2: `create-a-webhook` (Score: 100/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post`
- **HTTP Method / Endpoint:** `POST /api/v1/accounts/{account_id}/webhooks`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: 'webhooks'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.75 (10 pts); Complexity: depth 4, props 4 (20/20); Tokens: 126 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/webhooks. Input surfaces (body+path) declare 4 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 3: `update-a-webhook` (Score: 99/100 — `RANK_3`)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks~1{webhook_id}/patch`
- **HTTP Method / Endpoint:** `PATCH /api/v1/accounts/{account_id}/webhooks/{webhook_id}`
- **Score Breakdown:** Domain: 24/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (24/25, pattern: 'webhooks'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.75 (10 pts); Complexity: depth 4, props 4 (20/20); Tokens: 129 (15/15); Role distinctness: 20/20; POST bonus: 0/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/webhooks/{webhook_id}. Input surfaces (body+path) declare 4 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 4: `add-new-automation-rule-to-account` (Score: 98/100 — `RANK_4`)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1automation_rules/post`
- **HTTP Method / Endpoint:** `POST /api/v1/accounts/{account_id}/automation_rules`
- **Score Breakdown:** Domain: 22/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: 'automation_rules'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.8571 (10 pts); Complexity: depth 4, props 7 (20/20); Tokens: 164 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/automation_rules. Input surfaces (body+path) declare 7 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 5: `update-automation-rule-in-account` (Score: 97/100 — `RANK_5`)
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1automation_rules~1{id}/patch`
- **HTTP Method / Endpoint:** `PATCH /api/v1/accounts/{account_id}/automation_rules/{id}`
- **Score Breakdown:** Domain: 22/25 | Diversity: 20/20 | Complexity: 20/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: 'automation_rules'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.75 (10 pts); Complexity: depth 4, props 8 (20/20); Tokens: 177 (15/15); Role distinctness: 20/20; POST bonus: 0/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /api/v1/accounts/{account_id}/automation_rules/{id}. Input surfaces (body+path) declare 8 properties (2 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

---

### LINE Logistics & Communications Slot (`SLOT_LINE_01`)
- **Target Domain:** Chat Experience & Bot Interactions
- **Source Cluster:** `CLUSTER_LINE`
- **Replaced Operation:** `replyMessage`
- **Exclusion Cause:** Replaces replyMessage (disqualified due to 11-variant discriminated message union).
- **Statefulness Guidance:** showLoadingAnimation requires a valid chatId; testWebhookEndpoint tests connectivity.
- **Total Statically Eligible Candidates in Cluster Pool:** 15 operations
- **Co-Leading Candidates Count:** 1

| Rank | Composite Score | Operation ID | HTTP | Endpoint | Status Label | Depth | Props | Req | Surfaces | Stateful? |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| 1 | **87** | `showLoadingAnimation` | POST | `/v2/bot/chat/loading/start` | `CO_LEADING_CANDIDATE (Tied)` | 3 | 2 | 1 | `body` | NO |
| 2 | **83** | `updateRichMenuAlias` | POST | `/v2/bot/richmenu/alias/{richMenuAliasId}` | `RANK_2` | 3 | 2 | 2 | `body+path` | NO |
| 3 | **79** | `linkRichMenuIdToUser` | POST | `/v2/bot/user/{userId}/richmenu/{richMenuId}` | `RANK_3` | 1 | 2 | 2 | `path` | NO |
| 4 | **79** | `createRichMenuAlias` | POST | `/v2/bot/richmenu/alias` | `RANK_4` | 3 | 2 | 2 | `body` | NO |
| 5 | **79** | `unlinkRichMenuIdFromUsers` | POST | `/v2/bot/richmenu/bulk/unlink` | `RANK_5` | 4 | 1 | 1 | `body` | NO |

#### Candidate Detailed Evaluations:

##### Rank 1: `showLoadingAnimation` (Score: 87/100 — `CO_LEADING_CANDIDATE (Tied)`)
- **JSON Pointer:** `#/paths/~1v2~1bot~1chat~1loading~1start/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/chat/loading/start`
- **Score Breakdown:** Domain: 25/25 | Diversity: 16/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (25/25, pattern: '/chat/loading/start'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.5 (10 pts); Complexity: depth 3, props 2 (10/20); Tokens: 89 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/chat/loading/start. Input surfaces (body) declare 2 properties (1 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 2: `updateRichMenuAlias` (Score: 83/100 — `RANK_2`)
- **JSON Pointer:** `#/paths/~1v2~1bot~1richmenu~1alias~1{richMenuAliasId}/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/richmenu/alias/{richMenuAliasId}`
- **Score Breakdown:** Domain: 22/25 | Diversity: 15/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: '/richmenu'); Surfaces: ['body', 'path'] (10 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 3, props 2 (10/20); Tokens: 94 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/richmenu/alias/{richMenuAliasId}. Input surfaces (body+path) declare 2 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 3: `linkRichMenuIdToUser` (Score: 79/100 — `RANK_3`)
- **JSON Pointer:** `#/paths/~1v2~1bot~1user~1{userId}~1richmenu~1{richMenuId}/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/user/{userId}/richmenu/{richMenuId}`
- **Score Breakdown:** Domain: 22/25 | Diversity: 11/20 | Complexity: 14/20 | Footprint: 11/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: '/richmenu'); Surfaces: ['path'] (6 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 1, props 2 (14/20); Tokens: 73 (11/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/user/{userId}/richmenu/{richMenuId}. Input surfaces (path) declare 2 properties (2 required). At nesting depth 1, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 4: `createRichMenuAlias` (Score: 79/100 — `RANK_4`)
- **JSON Pointer:** `#/paths/~1v2~1bot~1richmenu~1alias/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/richmenu/alias`
- **Score Breakdown:** Domain: 22/25 | Diversity: 11/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: '/richmenu'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 3, props 2 (10/20); Tokens: 88 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/richmenu/alias. Input surfaces (body) declare 2 properties (2 required). At nesting depth 3, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

##### Rank 5: `unlinkRichMenuIdFromUsers` (Score: 79/100 — `RANK_5`)
- **JSON Pointer:** `#/paths/~1v2~1bot~1richmenu~1bulk~1unlink/post`
- **HTTP Method / Endpoint:** `POST /v2/bot/richmenu/bulk/unlink`
- **Score Breakdown:** Domain: 22/25 | Diversity: 11/20 | Complexity: 10/20 | Footprint: 15/15 | Role: 20/20 | Mock Safety: 0/0 (deferred)
- **Scoring Notes:** Domain fit (22/25, pattern: '/richmenu'); Surfaces: ['body'] (6 pts) + Opt-ratio 0.0 (5 pts); Complexity: depth 4, props 1 (10/20); Tokens: 86 (15/15); Role distinctness: 20/20; POST bonus: 1/1; Mock-safety points: 0 (deferred pending extraction).
- **Mock Safety Status:** `MOCK_SAFETY_REVIEW_PENDING` (Contributed: 0 pts)
- **Mock Safety Analysis:** Mock execution requires local state simulation for /v2/bot/richmenu/bulk/unlink. Input surfaces (body) declare 1 properties (1 required). At nesting depth 4, deterministic mock verification requires validating contract arguments against local state machine. Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes. Contributes 0 points to candidate composite score.

---

## 4. Handoff Protocol & Human Review Action

1. **Status**: All rankings are strictly `DRAFT_PENDING_REVIEW`.
2. **Official Manifest**: Remains 100% unmodified until user approves selections.
3. **Stateful vs. Self-Contained Review Highlight**:
   - In GitHub Slot (`SLOT_GITHUB_01`), `pulls/submit-review` and `pulls/create` both score 100/100 (co-leaders). `pulls/submit-review` requires a pre-existing `review_id`, while `pulls/create` is a self-contained PR constructor. Human review should determine whether mock harness simplicity favors `pulls/create`.