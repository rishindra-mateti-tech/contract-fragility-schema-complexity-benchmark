# Stage B V3 Source Adapter Coverage and Architectural Analysis

**Execution Date:** October 26, 2026  
**Pipeline Version:** `3.0.0`  
**Evaluation Scope:** 30 Active Stage B Manifest Operations  

---

## 1. Adapter Framework Overview

Pipeline V3 introduced a modular, provenance-preserving adapter framework designed to unlock non-standard OpenAPI operations without ad-hoc workarounds:

| Adapter Component | Governing Policy | Capabilities and Invariants | Unlocked Operations |
| :--- | :--- | :--- | :--- |
| **`LocalReferenceResolver`** | `OPENAPI_REFERENCE_RESOLUTION_POLICY_001` | Relative local file resolution, path traversal prevention, zero network access, cycle detection, depth bound ($d \le 8$). | Evaluated across all 30 slots; safely rejected missing files in `CAND-003`. |
| **`ParameterInheritanceAdapter`** | `OPENAPI_PARAMETER_INHERITANCE_POLICY_001` | Path Item to Operation parameter inheritance, `(name, in)` override precedence, URI template reconciliation, required path parameter enforcement. | `SLOT_CHATWOOT_02`, `SLOT_CHATWOOT_03`. |
| **`OpenAPI2FormDataAdapter`** | `OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001` | Dedicated `form` surface container (`additionalProperties: false`), file/binary payload prohibition, zero mapping to `body`, explicit unvalidated wire conformance. | `SLOT_SLACK_01`, `SLOT_SLACK_02`, `SLOT_SLACK_03`. |

---

## 2. In-Depth Operational Analysis by Cluster

### A. Chatwoot Cluster (`CLUSTER_CHATWOOT` / `CAND-011`)
- **Previous Bottleneck:** `create-an-account-user` (`SLOT_CHATWOOT_02`) and `create-a-conversation` (`SLOT_CHATWOOT_03`) declare path parameters (`{account_id}`, `{inbox_identifier}`, `{contact_identifier}`) at the Path Item level rather than inside the operation block.
- **Adapter Execution:** `ParameterInheritanceAdapter` resolved the parent Path Item parameters from `#/components/parameters/...`, matched them against the URI template, and injected them into a dedicated `path` surface container.
- **Outcome:** Both operations successfully generated valid Draft-07 candidate contracts with `path` and `body` surfaces.

### B. Slack Cluster (`CLUSTER_SLACK` / `CAND-006`)
- **Previous Bottleneck:** Swagger 2.0 operations (`conversations.create`, `users.profile.set`, `reminders.add`) use `in: "formData"` parameters with `application/x-www-form-urlencoded` consumes declarations.
- **Adapter Execution:** `OpenAPI2FormDataAdapter` grouped all form parameters into a closed `form` container, separate from `header` parameters (e.g. `token`). No form parameter was mapped to `body`.
- **Outcome:** All 3 Slack operations successfully generated valid Draft-07 candidate contracts with discrete `form` and `header` surfaces.

### C. DigitalOcean Cluster (`CLUSTER_DIGITALOCEAN` / `CAND-003`)
- **Forensic Finding:** Root specification `a26d71aa637fd6c6241602e9862eae7fb3d1ed95.yaml` defines operations via relative file paths:
  - `floating_ips_create` points to `resources/floating_ips/floatingIPs_create.yml`
  - `domains_create` points to `resources/domains/domains_create.yml`
  - `droplets_create` points to `resources/droplets/droplets_create.yml`
- **Adapter Execution:** `LocalReferenceResolver` correctly attempted local resolution within the pinned `CAND-003` bundle root. Because only the single root file was pinned during original dataset retrieval, the referenced target files do not exist on disk.
- **Outcome:** Under strict zero-network and fail-closed rules, the resolver refused to make external network calls or synthesize content, rejecting all 3 operations under `ERR_LOCAL_REF_FILE_NOT_FOUND`.

---

## 3. Overall Manifest Operations Breakdown

- **Total Manifest Operations:** 30
- **Canonical Pilots (Skipped):** 2 (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`)
- **Successfully Extracted Candidates (V3):** 18
  - No adapter required: 13
  - Parameter inheritance adapter: 2 (`SLOT_CHATWOOT_02`, `SLOT_CHATWOOT_03`)
  - FormData surface adapter: 3 (`SLOT_SLACK_01`, `SLOT_SLACK_02`, `SLOT_SLACK_03`)
- **Rejected Fail-Closed:** 10
  - MCP AST source code: 6 (3 SQLite Python + 3 GitHub TypeScript)
  - Missing local reference files: 3 (DigitalOcean `CAND-003`)
  - Polymorphic union: 1 (Stripe `SLOT_STRIPE_03`)
