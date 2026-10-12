# Stage B Replacement Candidate Inventory (Draft Discovery)

**Document Role:** Discovery Draft Only (No Manifest Modifications, No Final Selections)  
**Date (UTC):** October 12, 2026  
**Governing Protocol:** `STAGE_B_EXTRACTION_SPEC.md`, `PROTOCOL_AMENDMENT_003.md`  
**Status:** PROVISIONAL_DISCOVERY_DRAFT  

---

## 1. Protocol Constraints & Scope Summary

In accordance with the Stage B Research Protocol, seven operations were excluded (`EXCLUDE_PENDING`) due to structural recursion depth overflow ($> 5$), polymorphic object unions, or binary multipart parameters. Two of these exclusions were previously filled, leaving **5 open canonical replacement slots** across 4 source clusters:

1. **GitHub Developer Platforms**: 1 slot (replacing `issues/create`)
2. **Stripe Payments Slot A**: 1 slot (replacing `PostCustomers`)
3. **Stripe Payments Slot B**: 1 slot (replacing `PostPaymentIntents`)
4. **Chatwoot CRM/Support**: 1 slot (replacing `create-a-contact`)
5. **LINE Logistics/Communications**: 1 slot (replacing `replyMessage`)

### Discovery Guidelines strictly followed:
- Evaluated candidates originate **exclusively** from the frozen raw source files and pinned blob SHAs.
- Exactly **3 candidates** evaluated per open slot (15 total candidates evaluated).
- Zero changes made to `results_stage_b/stage_b_operation_manifest.yaml`.
- Zero final selections made; all candidates are submitted for subsequent human review.

---

## 2. Slot-by-Slot Discovery Summary Table

| Slot ID | Cluster | Replaced Operation | Candidate Rank | Operation ID | HTTP Method | Depth | Props | Surfaces | Object Union | Binary | External Ref | Eligibility |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `SLOT_GITHUB_01` | `CLUSTER_GITHUB` | `issues/create` | 1 | `issues/create-comment` | POST | 2 | 4 | body+path | no | no | no | **ELIGIBLE** |
| `SLOT_GITHUB_01` | `CLUSTER_GITHUB` | `issues/create` | 2 | `pulls/create` | POST | 2 | 10 | body+path | no | no | no | **ELIGIBLE** |
| `SLOT_GITHUB_01` | `CLUSTER_GITHUB` | `issues/create` | 3 | `repos/create-dispatch-event` | POST | 2 | 4 | body+path | no | no | no | **ELIGIBLE** |
| `SLOT_STRIPE_01` | `CLUSTER_STRIPE` | `PostCustomers` | 1 | `PostPayouts` | POST | 3 | 10 | body | no | no | no | **ELIGIBLE** |
| `SLOT_STRIPE_01` | `CLUSTER_STRIPE` | `PostCustomers` | 2 | `PostTransfers` | POST | 3 | 9 | body | no | no | no | **ELIGIBLE** |
| `SLOT_STRIPE_01` | `CLUSTER_STRIPE` | `PostCustomers` | 3 | `PostAccountLinks` | POST | 3 | 9 | body | no | no | no | **ELIGIBLE** |
| `SLOT_STRIPE_02` | `CLUSTER_STRIPE` | `PostPaymentIntents` | 1 | `PostProducts` | POST | 4 | 37 | body | no | no | no | **ELIGIBLE** |
| `SLOT_STRIPE_02` | `CLUSTER_STRIPE` | `PostPaymentIntents` | 2 | `PostPrices` | POST | 5 | 44 | body | no | no | no | **ELIGIBLE** |
| `SLOT_STRIPE_02` | `CLUSTER_STRIPE` | `PostPaymentIntents` | 3 | `PostCharges` | POST | 5 | 54 | body | yes | no | no | **DISQUALIFIED** |
| `SLOT_CHATWOOT_01` | `CLUSTER_CHATWOOT` | `create-a-contact` | 1 | `add-new-canned-response-to-account` | POST | 3 | 2 | body | no | no | no | **ELIGIBLE** |
| `SLOT_CHATWOOT_01` | `CLUSTER_CHATWOOT` | `create-a-contact` | 2 | `create-a-webhook` | POST | 4 | 4 | body+path | no | no | no | **ELIGIBLE** |
| `SLOT_CHATWOOT_01` | `CLUSTER_CHATWOOT` | `create-a-contact` | 3 | `add-new-custom-attribute-to-account` | POST | 4 | 8 | body | no | no | no | **ELIGIBLE** |
| `SLOT_LINE_01` | `CLUSTER_LINE` | `replyMessage` | 1 | `testWebhookEndpoint` | POST | 3 | 1 | body | no | no | no | **ELIGIBLE** |
| `SLOT_LINE_01` | `CLUSTER_LINE` | `replyMessage` | 2 | `showLoadingAnimation` | POST | 3 | 2 | body | no | no | no | **ELIGIBLE** |
| `SLOT_LINE_01` | `CLUSTER_LINE` | `replyMessage` | 3 | `linkRichMenuIdToUser` | POST | 1 | 2 | path | no | no | no | **ELIGIBLE** |

---

## 3. Detailed Audit of Evaluated Candidates by Slot

### GitHub Developer Platforms Replacement Slot (`SLOT_GITHUB_01`)
- **Source Cluster:** `CLUSTER_GITHUB` (Developer Platforms)
- **Raw Source File:** `data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json`
- **Pinned Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Replaced Operation:** `issues/create`
- **Reason for Exclusion:** Observed recursion depth 6 exceeds MAX_RECURSION_DEPTH=5; contains polymorphic object-level oneOf union in labels.items.

#### Evaluated Candidates:

##### Candidate 1: `issues/create-comment`
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1issues~1{issue_number}~1comments/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Input Surfaces:** `body, path`
- **Maximum Nesting Depth:** 2 (Allowed: $\le 5$)
- **Total Property Count:** 4
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Direct complement to issue lifecycle; adds issue comments. Compact, high-signal developer action.

##### Candidate 2: `pulls/create`
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1pulls/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Input Surfaces:** `body, path`
- **Maximum Nesting Depth:** 2 (Allowed: $\le 5$)
- **Total Property Count:** 10
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Core code lifecycle primitive. Highly realistic multi-parameter pull request creation payload.

##### Candidate 3: `repos/create-dispatch-event`
- **JSON Pointer:** `#/paths/~1repos~1{owner}~1{repo}~1dispatches/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `a91fa76a34558f5ed28e245cb1a6c46a44a61f4d`
- **Input Surfaces:** `body, path`
- **Maximum Nesting Depth:** 2 (Allowed: $\le 5$)
- **Total Property Count:** 4
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Repository automation event trigger. Compact custom event dispatcher payload.

### Stripe Payments Replacement Slot A (`SLOT_STRIPE_01`)
- **Source Cluster:** `CLUSTER_STRIPE` (Payments & Financial Infrastructure)
- **Raw Source File:** `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`
- **Pinned Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Replaced Operation:** `PostCustomers`
- **Reason for Exclusion:** Observed recursion depth 6 exceeds MAX_RECURSION_DEPTH=5; contains polymorphic anyOf unions in address/metadata.

#### Evaluated Candidates:

##### Candidate 1: `PostPayouts`
- **JSON Pointer:** `#/paths/~1v1~1payouts/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 3 (Allowed: $\le 5$)
- **Total Property Count:** 10
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Outbound merchant fund settlement. Highly realistic financial primitive with 10 cleanly bounded properties.

##### Candidate 2: `PostTransfers`
- **JSON Pointer:** `#/paths/~1v1~1transfers/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 3 (Allowed: $\le 5$)
- **Total Property Count:** 9
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Internal balance routing primitive across connected accounts. Compact depth-3 parameter schema.

##### Candidate 3: `PostAccountLinks`
- **JSON Pointer:** `#/paths/~1v1~1account_links/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 3 (Allowed: $\le 5$)
- **Total Property Count:** 9
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Connected account onboarding link generator. Depth 3 with clean enum parameters.

### Stripe Payments Replacement Slot B (`SLOT_STRIPE_02`)
- **Source Cluster:** `CLUSTER_STRIPE` (Payments & Financial Infrastructure)
- **Raw Source File:** `data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json`
- **Pinned Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Replaced Operation:** `PostPaymentIntents`
- **Reason for Exclusion:** Observed recursion depth 9 exceeds MAX_RECURSION_DEPTH=5; contains wide polymorphic payment_method_options unions.

#### Evaluated Candidates:

##### Candidate 1: `PostProducts`
- **JSON Pointer:** `#/paths/~1v1~1products/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 4 (Allowed: $\le 5$)
- **Total Property Count:** 37
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Catalog product creation. Rich production payload (37 properties, depth 4) without exceeding depth limit or union constraints.

##### Candidate 2: `PostPrices`
- **JSON Pointer:** `#/paths/~1v1~1prices/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 5 (Allowed: $\le 5$)
- **Total Property Count:** 44
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Catalog pricing tier primitive. High structural complexity (44 properties, depth 5) cleanly operating at the maximum allowable bound.

##### Candidate 3: `PostCharges`
- **JSON Pointer:** `#/paths/~1v1~1charges/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 5 (Allowed: $\le 5$)
- **Total Property Count:** 54
- **Object Union Present:** yes
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **DISQUALIFIED**
- **Rejection Reason:** OBJECT_UNION
- **Evaluation Notes:** Evaluated boundary contrast candidate. DISQUALIFIED due to non-finite source/destination polymorphic object unions.

### Chatwoot CRM Replacement Slot (`SLOT_CHATWOOT_01`)
- **Source Cluster:** `CLUSTER_CHATWOOT` (CRM & Customer Support)
- **Raw Source File:** `data_stage_b/raw/CAND-011/b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589.json`
- **Pinned Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Replaced Operation:** `create-a-contact`
- **Reason for Exclusion:** Declared multipart/form-data with binary file upload parameter ('avatar').

#### Evaluated Candidates:

##### Candidate 1: `add-new-canned-response-to-account`
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1canned_responses/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 3 (Allowed: $\le 5$)
- **Total Property Count:** 2
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Agent macro creation. Fast, canonical text-only CRM payload without binary or multipart attachments.

##### Candidate 2: `create-a-webhook`
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Input Surfaces:** `body, path`
- **Maximum Nesting Depth:** 4 (Allowed: $\le 5$)
- **Total Property Count:** 4
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** CRM event subscription webhook configuration. Path and body parameters with URL validation.

##### Candidate 3: `add-new-custom-attribute-to-account`
- **JSON Pointer:** `#/paths/~1api~1v1~1accounts~1{account_id}~1custom_attribute_definitions/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 4 (Allowed: $\le 5$)
- **Total Property Count:** 8
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Custom CRM field schema builder. Depth 4 with clean attribute validation rules.

### LINE Communications Replacement Slot (`SLOT_LINE_01`)
- **Source Cluster:** `CLUSTER_LINE` (Logistics & Communications)
- **Raw Source File:** `data_stage_b/raw/CAND-013/11f1fdb91092246f881edd1a9457cb37327a6c5d.yml`
- **Pinned Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Replaced Operation:** `replyMessage`
- **Reason for Exclusion:** Observed recursion depth 13 exceeds MAX_RECURSION_DEPTH=5; messages array contains polymorphic 15-variant object union.

#### Evaluated Candidates:

##### Candidate 1: `testWebhookEndpoint`
- **JSON Pointer:** `#/paths/~1v2~1bot~1channel~1webhook~1test/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 3 (Allowed: $\le 5$)
- **Total Property Count:** 1
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** Operational endpoint verification webhook test. Depth 3 with clean single property endpoint payload.

##### Candidate 2: `showLoadingAnimation`
- **JSON Pointer:** `#/paths/~1v2~1bot~1chat~1loading~1start/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Input Surfaces:** `body`
- **Maximum Nesting Depth:** 3 (Allowed: $\le 5$)
- **Total Property Count:** 2
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** User visual feedback action. Compact depth 3 payload with chatId and loadingSeconds.

##### Candidate 3: `linkRichMenuIdToUser`
- **JSON Pointer:** `#/paths/~1v2~1bot~1user~1{userId}~1richmenu~1{richMenuId}/post`
- **HTTP Method:** `POST`
- **Source Blob SHA:** `11f1fdb91092246f881edd1a9457cb37327a6c5d`
- **Input Surfaces:** `path`
- **Maximum Nesting Depth:** 1 (Allowed: $\le 5$)
- **Total Property Count:** 2
- **Object Union Present:** no
- **Binary / Multipart Present:** no
- **Conflicting allOf Present:** no
- **External Reference Present:** no
- **Cyclic Reference Present:** no
- **Credential Handling Policy:** `UNIVERSAL_EXECUTOR_BOUND`
- **Canonical Eligibility:** **ELIGIBLE**
- **Rejection Reason:** None
- **Evaluation Notes:** User-level navigation menu binding. Flat path-parameter primitive linking menu to subscriber.

---

## 4. Key Architectural Observations & Contrast Findings

1. **Depth Limits & Object Unions in Payments (Stripe)**:
   - Primary business operations such as `PostCustomers` (depth 6) and `PostPaymentIntents` (depth 9) exceed the frozen depth bound ($5$).
   - In contrast, merchant movement primitives such as `PostPayouts` (depth 3, 10 properties) and `PostTransfers` (depth 3, 9 properties) are completely monomorphic and cleanly bounded.
   - Catalog operations `PostProducts` (depth 4, 37 properties) and `PostPrices` (depth 5, 44 properties) demonstrate rich schema complexity without violating depth limits.
   - Candidate `PostCharges` demonstrates why boundary disqualification is necessary: its source and destination objects declare non-finite unions that violate Section 3.3.

2. **Developer Platforms (GitHub)**:
   - `issues/create-comment` and `pulls/create` both provide high-density tool-calling primitives that operate cleanly at depth 2 without polymorphic unions.

3. **CRM & Support (Chatwoot)**:
   - `add-new-canned-response-to-account` and `create-a-webhook` offer clean text-based contracts completely free of the `multipart/form-data` binary upload that disqualified `create-a-contact`.

4. **Logistics & Communications (LINE)**:
   - Bypassing the deep polymorphic messaging array (depth 13) that disqualified `pushMessage` and `replyMessage`, `testWebhookEndpoint` and `showLoadingAnimation` provide well-formed, deterministic communications primitives.

---

## 5. Review & Handoff Gate

This inventory is submitted as an informational research document. No manifest modifications or extraction operations are authorized until human review approves formal admission.