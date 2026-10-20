# Stage B Dataset Universe Accounting

## 1. Operational Overview

Stage B candidate selection begins with a broad survey of real-world production APIs and evaluates candidates through a multi-tier structural filter. This document provides complete mathematical reconciliation of every source, candidate, and operation considered.

```
14 Evaluated Candidate Sources (stage_b_candidate_inventory.yaml)
 │
 ├── 10 Admitted Sources (raw_sources_provenance_registry.json)
 │    │
 │    ├── 8 OpenAPI Specs ──► 1,346 Scanned Operations (raw_operation_universe.json)
 │    │                         ├── 1,110 Statically Eligible Operations
 │    │                         └── 236 Disqualified Operations (Depth, Union, Multipart)
 │    │
 │    └── 2 MCP RPC Servers (SQLite, GitHub) ──► Static AST RPC definitions
 │
 ├── 1 Disqualified Source (DataDog: Proprietary non-redistributable license)
 └── 3 Pending Review Sources (PayPal, NYT, OpenAI: Held for future evaluation)
```

---

## 2. Cluster Accounting Breakdown

| Cluster ID | Project Name | Raw Ops Scanned | Eligible Clean | Eligible Union | Disqualified | Manifest Slots |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `CLUSTER_BOX` | BOX | 121 | 95 | 0 | 26 | 3 |
| `CLUSTER_CHATWOOT` | CHATWOOT | 71 | 57 | 0 | 14 | 3 |
| `CLUSTER_DIGITALOCEAN` | DIGITALOCEAN | 258 | 258 | 0 | 0 | 3 |
| `CLUSTER_GITHUB` | GITHUB | 400 | 357 | 0 | 43 | 3 |
| `CLUSTER_LINE` | LINE | 33 | 15 | 0 | 18 | 3 |
| `CLUSTER_SLACK` | SLACK | 94 | 94 | 0 | 0 | 3 |
| `CLUSTER_STRIPE` | STRIPE | 307 | 171 | 1 | 135 | 3 |
| `CLUSTER_TWILIO` | TWILIO | 62 | 62 | 0 | 0 | 3 |
| `CLUSTER_MCP_SQLITE` | MCP SQLite | N/A (AST) | 3 | 0 | 0 | 3 |
| `CLUSTER_MCP_GITHUB` | MCP GitHub | N/A (AST) | 3 | 0 | 0 | 3 |
| **Total** | **10 Clusters** | **1346** | **1,115** | **1** | **236** | **30** |

---

## 3. Disqualification and Cohort Partitioning

Of the 1,346 scanned OpenAPI operations:
- **1,109 operations (82.4%)** are clean monomorphic operations passing all structural rules.
- **1 operation (0.1%)** is a finite faithful object union (`PostRefunds` under Amendment 003).
- **236 operations (17.5%)** are disqualified due to protocol constraints:
  * 137 operations exceed maximum recursion depth bound ($d > 5$).
  * 176 operations contain polymorphic object-level unions (`anyOf`/`oneOf`).
  * 19 operations require file upload or multipart/binary inputs.

From the eligible space, a balanced cohort of 30 operations (3 per cluster across 10 clusters) was admitted into `stage_b_operation_manifest.yaml`.

---

## 4. Extraction and Validation Status Truth

As of October 2026:
- **Total Active Slots:** 30
- **Extracted Pilots:** 2 (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`)
- **Author Validated:** 1 (`SLOT_GITHUB_01` with explicit wrapper policy)
- **Pending Human Validation:** 1 (`SLOT_STRIPE_02`)
- **Remaining Slots to Extract:** 28
- **Independent Validations:** 0 (prohibited from being claimed)
