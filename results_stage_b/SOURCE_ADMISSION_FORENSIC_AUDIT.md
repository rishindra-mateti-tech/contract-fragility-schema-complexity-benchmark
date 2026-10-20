# Stage B Source Admission and Dataset Universe Forensic Audit

**Audit Status:** `COMPLETED_AND_CRYPTOGRAPHICALLY_VERIFIED`  
**All Raw Hash Checks:** `PASS (10/10)`  
**Independent Review Status:** `NOT_CONDUCTED (0/30)`  

---

## 1. Master Forensic Universe Accounting Table

| Forensic Dimension | Exact Metric | Primary Evidentiary Artifact | Verification Method |
| :--- | :---: | :--- | :--- |
| **Evaluated Candidate Sources** | `14` | `results_stage_b/stage_b_candidate_inventory.yaml` | Static catalog inventory |
| **Admitted Candidate Sources** | `10` | `results_stage_b/raw_sources_provenance_registry.json` | License & commit pinned verification |
| **Rejected Candidate Sources** | `1` | `results_stage_b/stage_b_candidate_inventory.yaml` | License redistribution exclusion (DataDog) |
| **Pending Candidate Sources** | `3` | `results_stage_b/stage_b_candidate_inventory.yaml` | Pre-extraction queue (PayPal, NYT, OpenAI) |
| **Pinned Raw Source Files** | `10` | `data_stage_b/raw/**` | Bit-level Git blob SHA & SHA-256 match |
| **Scanned Raw Operations** | `1346` | `results_stage_b/raw_operation_universe.json` | Full AST / JSON traversal across 8 OpenAPI specs |
| **Disqualified Operations** | `236` | `results_stage_b/raw_operation_universe.json` | Fail-closed static eligibility filtering |
| **Statically Eligible Operations** | `1110` | `results_stage_b/raw_operation_universe.json` | 1,109 clean monomorphic + 1 faithful union |
| **Initial Tracked Candidates** | `32` | `results_stage_b/pre_extraction_candidate_audit.json` | Pre-extraction structural audit |
| **Initial Excluded Operations** | `7` | `results_stage_b/pre_extraction_candidate_audit.json` | Polymorphic union or depth ceiling violations |
| **Replacement Slots Evaluated** | `5` | `results_stage_b/replacement_candidate_ranking.json` | GITHUB, STRIPE (x2), CHATWOOT, LINE |
| **Replacement Candidates Evaluated** | `25` | `results_stage_b/replacement_candidate_ranking.json` | 5 candidates per slot evaluated |
| **Replacement Candidates Admitted** | `5` | `results_stage_b/candidate_admission_decisions.json` | Author manual review sign-off |
| **Final Active Manifest Cohort** | `30` | `results_stage_b/stage_b_operation_manifest.yaml` | 24 clean initial + 1 union + 5 replacements |
| **Canonical Contracts Extracted** | `2` | `data_stage_b/canonical/**` | SLOT_GITHUB_01 & SLOT_STRIPE_02 pilots |
| **Independent Human Reviews** | **`0`** | `N/A` | **Strictly 0; independent review remains a future gate** |

---

## 2. Raw Source Files Cryptographic Verification

| Candidate ID | Project | File Size | Git Blob SHA Match | SHA-256 Match | Verification Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `CAND-001` | GitHub (github/rest-api-description) | 13018090 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-002` | Stripe (stripe/openapi) | 8317513 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-003` | DigitalOcean (digitalocean/openapi) | 124775 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-004` | Twilio (twilio/twilio-oai) | 1504725 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-005` | Box (box/box-openapi) | 1781543 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-006` | Slack (slackapi/slack-api-specs) | 1039581 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-009` | Model Context Protocol (modelcontextprotocol/servers - SQLite) | 18533 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-010` | Model Context Protocol (modelcontextprotocol/servers - GitHub) | 18123 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-011` | Chatwoot (chatwoot/chatwoot) | 537652 B | `PASS` | `PASS` | `VERIFIED` |
| `CAND-013` | LINE (line/line-openapi) | 190228 B | `PASS` | `PASS` | `VERIFIED` |

---

## 3. Disqualification Root Cause Overlap Matrix

In static analysis, structural disqualifications often overlap. The 236 disqualified operations partition into disjoint non-overlapping subsets as follows:

| Disqualification Root Cause Combination | Non-Overlapping Count | Percentage of Disqualified ($N=236$) |
| :--- | :---: | :---: |
| Depth Only ($d > 5$) | `44` | 18.6% |
| Object Union Only | `83` | 35.2% |
| Multipart / Binary Payload Only | `15` | 6.4% |
| Depth + Object Union | `90` | 38.1% |
| Depth + Multipart / Binary | `1` | 0.4% |
| Object Union + Multipart / Binary | `1` | 0.4% |
| All Three (Depth + Union + Multipart) | `2` | 0.8% |
| **Total Disqualified Operations** | **`236`** | **100.0%** |

> **Marginal Category Sums:** Depth violations total 137; Object Union violations total 176; Multipart/Binary violations total 19. Marginal sums exceed 236 due to multi-root co-occurrence.

---

## 4. Replacement Slots and Decision Lineage

| Slot ID | Replaced Operation | Admitted Operation | Candidate Pool Size | Human Review Status |
| :--- | :--- | :--- | :---: | :--- |
| `SLOT_GITHUB_01` | `issues/create` | `pulls/create` | `4` | `AUTHOR_MANUAL_REVIEW_COMPLETED` |
| `SLOT_STRIPE_01` | `PostCustomers` | `PostPayouts` | `4` | `AUTHOR_MANUAL_REVIEW_COMPLETED` |
| `SLOT_STRIPE_02` | `PostPaymentIntents` | `PostShippingRates` | `4` | `AUTHOR_MANUAL_REVIEW_COMPLETED` |
| `SLOT_CHATWOOT_01` | `create-a-contact` | `create-a-webhook` | `4` | `AUTHOR_MANUAL_REVIEW_COMPLETED` |
| `SLOT_LINE_01` | `replyMessage` | `showLoadingAnimation` | `4` | `AUTHOR_MANUAL_REVIEW_COMPLETED` |

---

## 5. Active Manifest Extraction Readiness Queue

| Extraction Readiness Category | Count | Definition & Implementation Constraint |
| :--- | :---: | :--- |
| `READY_WITH_EXPLICIT_WRAPPER_POLICY` | `6` | Operations structurally supported by current extractor under closed wrapper policy. |
| `REQUIRES_EXTRACTOR_CAPABILITY` | `23` | Requires query/header surface extractors, enum parsers, or AST compilers. |
| `REQUIRES_PROTOCOL_AMENDMENT` | `1` | Requires formal union expansion under Protocol Amendment 003 (Stripe `PostRefunds`). |
| `EXCLUDED` | `7` | Disqualified from canonical cohort due to wide object unions or excessive depth. |
| **Total Tracked Operations** | **`37`** | Comprehensive tracking across active and excluded operations. |

---

## 6. Scientific Truth and Epistemic Invariants

1. **Zero Ghost Candidates:** Every operation admitted into `stage_b_operation_manifest.yaml` traces directly to a verified raw file and Git blob SHA.
2. **Zero Inventions:** No synthetic schemas or synthetic properties were injected into candidate definitions.
3. **Author Review Integrity:** All human review decisions are documented as `AUTHOR_MANUAL_REVIEW`. Zero independent validations are claimed.
