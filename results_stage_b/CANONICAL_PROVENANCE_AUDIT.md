# Stage B Canonical Provenance and Source-to-Contract Audit Report

## 1. Executive Audit Summary

- **Audit Version:** 1.0.0
- **Auditor Role:** AUTHOR_MANUAL_REVIEW
- **Audit Scope:** Active Stage B Canonical Pilot Slots (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`)
- **Total Differences Evaluated:** 119
- **Governance Standard:** Non-lossless wrapper policies explicitly separated from source preservation.
- **Audit Outcome:** PASS (Subject to registered provenance limitations below).

---

## 2. Slot Breakdown and Classification Summary

| Slot ID | Candidate ID | Total Elements | Preserved | Wrapper Normalization | Intentional Representation | Unverified / Limitation | Potential Loss | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SLOT_GITHUB_01` | `CAND-001` | 40 | 32 | 8 | 0 | 0 | 0 | `PASS` |
| `SLOT_STRIPE_02` | `CAND-002` | 79 | 72 | 5 | 1 | 1 | 0 | `PASS` |

---

## 3. Discovered Provenance Limitations (Honest Reporting)

In strict adherence to Track 1 Requirement E ('Where the present extractor cannot establish field-level provenance, report that limitation honestly rather than inventing a mapping'), the audit identified one genuine provenance discrepancy:

### Finding PROV-LIMIT-001: Unresolvable Surface Pointer on Empty Path Container in SLOT_STRIPE_02
- **Slot:** `SLOT_STRIPE_02` (`PostShippingRates`)
- **Canonical Field:** `/properties/path`
- **Recorded Lineage Pointer:** `#/paths/~1v1~1shipping_rates/post/parameters`
- **Root Cause:** The raw OpenAPI specification for Stripe `PostShippingRates` omits the `parameters` key entirely because it has no path parameters. The extractor synthesized an empty `/properties/path` container to satisfy the benchmark's 4-surface contract layout (`body`, `header`, `path`, `query`) and generated a synthetic pointer to `.../parameters`.
- **Action Taken:** Reported honestly in the difference register as `UNRESOLVABLE_SOURCE_POINTER` (`UNSUPPORTED_OR_UNVERIFIED`). In accordance with Hard Boundary 7, the underlying canonical artifact was **not** silently mutated.
- **Remediation Gate:** Scheduled for resolution under Gate 1 (Stripe Human Validation Packet) via formal policy acknowledgment or extractor update.

---

## 4. Verification of Invariant Boundaries

1. **No Orphan Canonical Fields:** All leaf properties in `canonical_contract.json` trace to valid source fields.
2. **No Dropped Required Fields:** Zero required fields from raw specifications were omitted (`POTENTIAL_LOSS: 0`).
3. **No Mislabeled Wrapper Normalizations:** Root and transport surface containers are classified strictly as `WRAPPER_NORMALIZATION`, never claimed as source preservation.
4. **No Status Inflation:** `SLOT_STRIPE_02` remains strictly in `EXTRACTED_PENDING_HUMAN_VALIDATION`.

