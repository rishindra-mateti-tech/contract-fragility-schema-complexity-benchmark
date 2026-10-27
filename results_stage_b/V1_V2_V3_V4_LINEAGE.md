# Stage B Extraction Pipeline Lineage: V1 vs V2 vs V3 vs V4

**Date:** October 26, 2026  
**Comparative Scope:** Evolutionary tracking across Batch Extraction Pipelines V1, V2, V3, and V4.  

---

## 1. Evolution and Capability Matrix

| Architectural Feature | Batch Pipeline V1 | Batch Pipeline V2 | Batch Pipeline V3 | Batch Pipeline V4 |
| :--- | :--- | :--- | :--- | :--- |
| **Pipeline Version** | `1.0.0` | `2.0.0` | `3.0.0` | `4.0.0` |
| **Governing Policies** | 1 Policy | 1 Policy (Dialect) | 4 Policies (Dialect, Ref, Param, FormData) | 8 Policies (+Closure, PyAST, TsAST, IR) |
| **Dialect Handling** | Verbatim copy | Syntactic `type: [T, null]` | Retained Policy 001 | Retained Policy 001 |
| **Artifacts Per Bundle** | 8 artifacts | 8 artifacts | 11 artifacts | 13 artifacts (+IR, +StaticEvidence) |
| **Path Parameter Inheritance** | Unsupported | Unsupported | Supported via Adapter | Supported via Adapter |
| **OpenAPI 2.0 FormData** | Unsupported | Unsupported | Supported via Adapter | Supported via Adapter |
| **Multi-File Reference Closures** | Unsupported | Unsupported | Blocked on missing closure | Supported via Pinned Source Closure |
| **Python AST Tool Extraction** | Unsupported | Unsupported | Unsupported | Supported via Pure Static AST Adapter |
| **TypeScript AST Analysis** | Unsupported | Unsupported | Unsupported | Evaluated via Tree-sitter (fail-closed) |
| **Intermediate Representation** | None | None | None | `STATIC_SOURCE_INTERMEDIATE_REPRESENTATION_SPEC_001` |
| **Admitted Manifest Operations** | 30 | 30 | 30 | 30 |
| **Pilots Skipped** | 2 | 2 | 2 | 2 |
| **Candidates Generated** | 13 | 13 | 18 | **22** |
| **Operations Rejected Fail-Closed** | 15 | 15 | 10 | **6** |
| **Independent Reviews Completed** | 0 | 0 | 0 | **0** |
| **`CANONICAL_FAITHFUL` Promotions** | 0 | 0 | 0 | **0** |

---

## 2. Historical Immutability Assurance

All prior candidate directories are preserved byte-identically on disk:
- `data_stage_b/extraction_candidates/` (V1: 13 slots)
- `data_stage_b/extraction_candidates_v2/` (V2: 13 slots)
- `data_stage_b/extraction_candidates_v3/` (V3: 18 slots)
- `data_stage_b/extraction_candidates_v4/` (V4: 22 slots)
