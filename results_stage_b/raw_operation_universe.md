# Stage B Raw-Source Operation Universe Static Analysis Report

**Document Type:** Full Static-Analysis Universe Enumeration & Metric Audit  
**Scanner Script SHA-256:** `bf78f0d1caa7328f7abbf65b3ef90eb7710921b5b16f301f826bc6c88563f316`  
**Operation Manifest SHA-256:** `bdd6aaad31779b527503d324ebe8459aebd1dad8659120b85119f8c18a577ce3`  
**Provenance Registry SHA-256:** `14245163b15a5a23e84247dcc91cae725c6e883a62eda5646a0c2aea2673b699`  
**Generated At (UTC):** `2026-10-12T04:30:00Z`  
**Environment:** Python `3.13.2` (win32) | PyYAML `6.0.3`  
**Execution Command:** `python src/scan_stage_b_raw_operation_universe.py --generated-at 2026-10-12T04:30:00Z`  

> **Reproducibility Invariant:** When executed with `--generated-at <TIMESTAMP>`, outputs are 100% byte-stable. Normal runtime execution without this argument is expected to vary only in timestamp metadata (`generated_at_utc`).

> **Critical Governance Disclaimer on Static Eligibility:**  
> **Static eligibility** indicates solely that the raw OpenAPI operation satisfies preliminary static AST/syntax filter criteria (nesting depth $\le 5$, no intra-spec cycles, no external refs, no multipart/binary inputs, no object-level unions, and no conflicting `allOf`).  
> **Static eligibility does NOT constitute canonical-contract admission, extraction validation, mock feasibility, or experimental benchmark inclusion.**  
> `Stripe PostRefunds` is classified strictly as a provisional finite-union candidate under Amendment 003, and is not canonical until extraction, automated validation, and manual review are complete.

---

## 1. Executive Summary & Universe Scale

- **Total Active Operations Scanned:** **1346 operations** across 8 enterprise OpenAPI specifications.
- **Statically Eligible Candidates (Clean Monomorphic):** **1109 operations** (82.4% of universe).
- **Statically Eligible Candidates (Faithful Union under Amendment 003):** **1 operation** (`Stripe PostRefunds` — provisional finite-union candidate).
- **Disqualified Operations:** **236 operations** (17.5% of universe; fails depth $\le 5$, object union, binary format, or cycles).
- **Excluded Raw Sources:** **2 Model Context Protocol (MCP) tool sources** (`CLUSTER_MCP_SQLITE` / CAND-009 and `CLUSTER_MCP_GITHUB` / CAND-010) excluded from active candidate operations pending multi-file raw provenance expansion.

---

## 2. Active Source Cluster Breakdown Table

| Source Cluster ID | Source Project | Pinned Blob SHA | Raw File SHA-256 | Total Ops | Statically Eligible (Clean) | Faithful Union | Disqualified | Method Split |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `CLUSTER_GITHUB` | GitHub (github/rest-api-description) | `a91fa76a34...` | `ba5ddc1eee...` | 400 | **357** | 0 | 43 | POST: 193, PATCH: 73, PUT: 134 |
| `CLUSTER_STRIPE` | Stripe (stripe/openapi) | `f1cedf38e0...` | `7cff4cc46d...` | 307 | **171** | 1 | 135 | POST: 307 |
| `CLUSTER_DIGITALOCEAN` | DigitalOcean (digitalocean/openapi) | `a26d71aa63...` | `e18ad525a3...` | 258 | **258** | 0 | 0 | PUT: 70, POST: 169, PATCH: 19 |
| `CLUSTER_TWILIO` | Twilio (twilio/twilio-oai) | `5b2e77834f...` | `052b294839...` | 62 | **62** | 0 | 0 | POST: 62 |
| `CLUSTER_BOX` | Box (box/box-openapi) | `e740e641b8...` | `13cc601e01...` | 121 | **95** | 0 | 26 | POST: 74, PUT: 44, PATCH: 3 |
| `CLUSTER_SLACK` | Slack (slackapi/slack-api-specs) | `f7b1affd1f...` | `8b92da26a3...` | 94 | **94** | 0 | 0 | POST: 94 |
| `CLUSTER_CHATWOOT` | Chatwoot (chatwoot/chatwoot) | `b0b3ca6332...` | `c8cba6e597...` | 71 | **57** | 0 | 14 | PATCH: 24, POST: 45, PUT: 2 |
| `CLUSTER_LINE` | LINE (line/line-openapi) | `11f1fdb910...` | `41033aa849...` | 33 | **15** | 0 | 18 | POST: 31, PUT: 2 |

### 2.1 Excluded MCP Sources Audit Record

| Candidate Source ID | Cluster ID | Raw Source File | Exclusion Reason | Technical Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `CAND-009` | `CLUSTER_MCP_SQLITE` | `data_stage_b/raw/CAND-009/1b97a6a4903bd8961941cdff43df3b059e610e5f.py` | `MCP_COHORT_EXCLUDED_PENDING_MULTI_FILE_PROVENANCE` | Although genuine Python AST parsing successfully extracts all 6 SQLite tools, their exact line spans (lines 235-297), and their inputSchema AST dictionary literals, the companion TypeScript GitHub MCP source (CAND-010) cannot resolve its external Zod schema imports without unpinned dependencies. To prevent asymmetric cohort representation and adhere to benchmark protocol rules prohibiting hand-maintained metadata, both MCP sources are excluded from the candidate operation universe and ranking outputs. |
| `CAND-010` | `CLUSTER_MCP_GITHUB` | `data_stage_b/raw/CAND-010/0676a34c85537e610f911fbd73a5a079f38be18e.ts` | `UNRESOLVED_EXTERNAL_SCHEMA_IMPORTS` | CAND-010 delegates tool input schemas to zodToJsonSchema(CreateOrUpdateFileSchema, etc.), which are imported from ./schemas.js. Because ./schemas.js is an external unpinned file absent from the frozen raw snapshot, genuine static AST resolution of input-schema properties, required fields, and depth cannot be achieved from index.ts alone. In accordance with benchmark protocol rules strictly prohibiting hand-maintained metadata or unpinned crawls, this source is excluded from the active candidate operation universe. |

---

## 3. Structural Complexity & Disqualification Analysis

### 3.1 Recursion Depth Distribution

| Nesting Depth | Operation Count | Percentage of Universe | Canonical Status |
| :---: | :---: | :---: | :--- |
| Depth 1 | 435 | 32.3% | **ALLOWED** (Depth $\le 5$) |
| Depth 2 | 215 | 16.0% | **ALLOWED** (Depth $\le 5$) |
| Depth 3 | 378 | 28.1% | **ALLOWED** (Depth $\le 5$) |
| Depth 4 | 100 | 7.4% | **ALLOWED** (Depth $\le 5$) |
| Depth 5 | 81 | 6.0% | **ALLOWED** (Depth $\le 5$) |
| Depth 6 | 47 | 3.5% | **DISQUALIFIED** (Exceeds bound) |
| Depth 7 | 24 | 1.8% | **DISQUALIFIED** (Exceeds bound) |
| Depth 8 | 18 | 1.3% | **DISQUALIFIED** (Exceeds bound) |
| Depth 9 | 7 | 0.5% | **DISQUALIFIED** (Exceeds bound) |
| Depth 10 | 13 | 1.0% | **DISQUALIFIED** (Exceeds bound) |
| Depth 11 | 3 | 0.2% | **DISQUALIFIED** (Exceeds bound) |
| Depth 12 | 4 | 0.3% | **DISQUALIFIED** (Exceeds bound) |
| Depth 13 | 15 | 1.1% | **DISQUALIFIED** (Exceeds bound) |
| Depth 18 | 3 | 0.2% | **DISQUALIFIED** (Exceeds bound) |
| Depth 19 | 2 | 0.1% | **DISQUALIFIED** (Exceeds bound) |
| Depth 20 | 1 | 0.1% | **DISQUALIFIED** (Exceeds bound) |

### 3.2 Disqualification Root Cause Breakdown

| Violation Code | Occurrence Count | Description |
| :--- | :---: | :--- |
| `OBJECT_UNION` | 176 | Contains object-level oneOf, anyOf, or polymorphic discriminator |
| `DEPTH` | 137 | Maximum recursion depth exceeds frozen threshold of 5 |
| `MULTIPART_BINARY` | 19 | Declares binary/file payload format or multipart/form-data content type |

---

## 4. Notable Replacement Candidates & Boundary Contrasts

This section highlights candidate operations across the four clusters containing open replacement slots.

| Cluster | Endpoint / ID | Method | Depth | Props | Req | Opt Ratio | Surfaces | Tokens | Static Verdict | Key Constraint Notes |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :--- | :--- |
| `CLUSTER_CHATWOOT` | `add-new-canned-response-to-account` | POST | 3 | 3 | 1 | 0.6667 | `body+path` | 108 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_CHATWOOT` | `add-new-custom-attribute-to-account` | POST | 4 | 9 | 1 | 0.8889 | `body+path` | 191 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_CHATWOOT` | `create-a-webhook` | POST | 4 | 4 | 1 | 0.75 | `body+path` | 126 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_CHATWOOT` | `create-a-contact` | POST | 3 | 8 | 1 | 0.875 | `body+path` | 169 | **DISQUALIFIED** | MULTIPART_BINARY |
| `CLUSTER_GITHUB` | `repos/create-dispatch-event` | POST | 2 | 4 | 3 | 0.25 | `body+path` | 108 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_GITHUB` | `issues/create` | POST | 6 | 17 | 5 | 0.7059 | `body+path` | 296 | **DISQUALIFIED** | DEPTH_6; OBJECT_UNION |
| `CLUSTER_GITHUB` | `issues/create-comment` | POST | 2 | 4 | 4 | 0.0 | `body+path` | 113 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_GITHUB` | `pulls/create` | POST | 2 | 10 | 4 | 0.6 | `body+path` | 179 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_LINE` | `testWebhookEndpoint` | POST | 3 | 1 | 0 | 1.0 | `body` | 78 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_LINE` | `showLoadingAnimation` | POST | 3 | 2 | 1 | 0.5 | `body` | 89 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_LINE` | `pushMessage` | POST | 13 | 16 | 3 | 0.8125 | `body+header` | 338 | **DISQUALIFIED** | DEPTH_13; OBJECT_UNION |
| `CLUSTER_LINE` | `replyMessage` | POST | 13 | 14 | 3 | 0.7857 | `body` | 312 | **DISQUALIFIED** | DEPTH_13; OBJECT_UNION |
| `CLUSTER_LINE` | `linkRichMenuIdToUser` | POST | 1 | 2 | 2 | 0.0 | `path` | 73 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_STRIPE` | `PostCharges` | POST | 5 | 54 | 7 | 0.8704 | `body` | 730 | **DISQUALIFIED** | OBJECT_UNION |
| `CLUSTER_STRIPE` | `PostCustomers` | POST | 6 | 51 | 6 | 0.8824 | `body` | 702 | **DISQUALIFIED** | DEPTH_6; OBJECT_UNION |
| `CLUSTER_STRIPE` | `PostPaymentIntents` | POST | 9 | 492 | 49 | 0.9004 | `body` | 6020 | **DISQUALIFIED** | DEPTH_9; OBJECT_UNION |
| `CLUSTER_STRIPE` | `PostPayouts` | POST | 3 | 10 | 2 | 0.8 | `body` | 186 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |
| `CLUSTER_STRIPE` | `PostPrices` | POST | 6 | 44 | 7 | 0.8409 | `body` | 618 | **DISQUALIFIED** | DEPTH_6 |
| `CLUSTER_STRIPE` | `PostProducts` | POST | 7 | 37 | 9 | 0.7568 | `body` | 542 | **DISQUALIFIED** | DEPTH_7 |
| `CLUSTER_STRIPE` | `PostRefunds` | POST | 3 | 12 | 0 | 1.0 | `body` | 210 | **STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE** | Ratified Amendment 003 (Provisional Finite-Union) |
| `CLUSTER_STRIPE` | `PostTransfers` | POST | 3 | 9 | 2 | 0.7778 | `body` | 174 | **STATICALLY_ELIGIBLE_CANDIDATE** | Clean pass |

---

## 5. Provenance & Reproducibility Certification

All 10 raw source files are verified against immutable Git blob hashes and SHA-256 digests. This scanner operates strictly read-only and guarantees byte-stable deterministic outputs when invoked with an explicit `--generated-at` timestamp.