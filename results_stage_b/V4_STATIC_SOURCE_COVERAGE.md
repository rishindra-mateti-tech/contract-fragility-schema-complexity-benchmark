# Stage B V4 Static Source Adapter Coverage

**Pipeline Version:** `4.0.0`  
**Total Admitted Operations:** 30  
**Successfully Extracted Candidates:** 22 (73.3%)  
**Skipped Pilots (Already Validated / Pilot):** 2  
**Rejected Fail-Closed:** 6  

---

## 1. Coverage by Source Dialect and Family

| Source Cluster ID | Source Project | Dialect | Total Slots | Generated | Rejected | Pilot Skipped | Adapters Active |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `CAND-001` | GitHub REST | OpenAPI 3.0.3 | 3 | 2 | 0 | 1 (`SLOT_GITHUB_01`) | None (monomorphic) |
| `CAND-002` | Stripe API | OpenAPI 3.0.0 | 3 | 1 | 1 | 1 (`SLOT_STRIPE_02`) | None (monomorphic) |
| `CAND-003` | DigitalOcean | OpenAPI 3.0.0 (Multi-File) | 3 | 1 | 2 | 0 | `LocalReferenceResolver` |
| `CAND-004` | Slack Web API | OpenAPI 2.0 (Swagger) | 3 | 3 | 0 | 0 | `OpenAPI2FormDataAdapter` |
| `CAND-005` | Box API | OpenAPI 3.0.2 | 3 | 3 | 0 | 0 | None (monomorphic) |
| `CAND-006` | Twilio API | OpenAPI 3.0.1 | 3 | 3 | 0 | 0 | None (monomorphic) |
| `CAND-007` | LINE Messaging | OpenAPI 3.0.0 | 3 | 3 | 0 | 0 | None (monomorphic) |
| `CAND-008` | Chatwoot API | OpenAPI 3.1.0 | 3 | 3 | 0 | 0 | `ParameterInheritanceAdapter` |
| `CAND-009` | SQLite MCP Server | Python 3 AST | 3 | 3 | 0 | 0 | `PythonAstToolExtractor` |
| `CAND-010` | GitHub MCP Server | TypeScript AST | 3 | 0 | 3 | 0 | `TypeScriptAstToolExtractor` |
| **Total** | | | **30** | **22** | **6** | **2** | |

---

## 2. Technical Capabilities Unlocked in V4

1. **Pinned Source Closure for DigitalOcean (`CAND-003`):**
   - 49 transitive specification files downloaded from pinned commit `e326f5060794769b6835084e48be7ce4db062d39`.
   - Resolves multi-file references offline without network access.
   - Unlocks `SLOT_DO_01` (`floating_ips_create`).

2. **Python AST Static Tool Extractor (`CAND-009`):**
   - Extracts Model Context Protocol tools declared as Python literal ASTs.
   - Unlocks `SLOT_MCP_SQLITE_01` (`read_query`), `SLOT_MCP_SQLITE_02` (`write_query`), and `SLOT_MCP_SQLITE_03` (`describe_table`).

3. **TypeScript AST Static Analysis (`CAND-010`):**
   - Evaluates TypeScript AST tools via Tree-sitter without Node.js execution.
   - Identifies runtime schema builder `zodToJsonSchema` and rejects fail-closed with structured evidence.

4. **Static Intermediate Representation (IR):**
   - Unifies OpenAPI parameters, request bodies, form data, and AST tool parameters into a common canonical representation conforming to `STATIC_SOURCE_INTERMEDIATE_REPRESENTATION_SPEC_001`.
