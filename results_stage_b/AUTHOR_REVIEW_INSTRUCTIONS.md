# Author Review Instructions for Stage B Candidate Admission

**Document Type:** Reviewer Guidance & Provenance Integrity Policy  
**Scope:** Stage B Benchmark Open Slots Candidate Admission Gate  
**Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md`  
**Associated Review Packet:** [HUMAN_ADMISSION_REVIEW_PACKET.md](HUMAN_ADMISSION_REVIEW_PACKET.md)  
**Associated Decisions Report:** [CANDIDATE_ADMISSION_REVIEW.md](CANDIDATE_ADMISSION_REVIEW.md)  

---

## 1. Purpose & Operational Scope of Author Review

This instruction document establishes the review protocol and scientific boundaries for manual reviews conducted on candidate operations admitted to the Stage B canonical benchmark cohort.

When a benchmark author performs a manual pre-extraction review:
1. **Cryptographic Provenance Confirmation:** The reviewer certifies that raw OpenAPI specifications on disk match their pinned Git blob SHAs and file SHA-256 digests in `raw_sources_provenance_registry.json`.
2. **JSON Pointer Resolution:** The reviewer verifies that OpenAPI JSON pointers resolve unambiguously to the intended HTTP method and operation ID in the raw source specifications.
3. **Protocol Compliance:** The reviewer confirms that frozen protocol constraints are strictly satisfied (maximum nesting depth $\le 5$, zero object-level unions, zero binary/multipart parameters, zero cyclic references, zero unresolved external references).
4. **Engineering Design Confirmation:** The reviewer confirms authorial design choices: that each candidate represents an authentic, high-frequency production workflow for the target domain, and that competing candidates were evaluated and rejected based on objective, documented technical rationales.
5. **Statefulness Model Partitioning:** The reviewer validates that schema-level single-turn constructibility is clearly decoupled from runtime state requirements (`SINGLE_TURN_CONSTRUCTIBLE` vs `FIXTURE_REQUIRED`), and that required mock fixtures are minimal and feasible.

---

## 2. Critical Boundary: Author Review vs. Independent Validation

> **SCIENTIFIC INTEGRITY INVARIANT:**  
> **Author review confirms cryptographic provenance, protocol adherence, and authorial design decisions, but it DOES NOT constitute independent third-party validation.**

### Reviewer Roles Defined:
- **`AUTHOR_MANUAL_REVIEW`**:
  - Performed by benchmark authors, core maintainers, or repository contributors.
  - Confirms that the candidate admission methodology was executed faithfully and that all recorded metadata is accurate.
  - **Does NOT** constitute third-party replication, external validation, or independent peer audit.
- **`INDEPENDENT_REVIEW`**:
  - Performed by an external, independent researcher who had no role in designing the benchmark, curating candidate sources, or authoring selection code.
  - **Status: NOT CONDUCTED.** Neither independent review nor external audit has taken place.
  - Benchmark publications, reports, and public documentation must NOT claim independent validation unless an unconflicted external researcher conducts and signs off under this role.

---

## 3. Human Review Procedure

A designated human reviewer must evaluate each of the five admitted operations in [HUMAN_ADMISSION_REVIEW_PACKET.md](HUMAN_ADMISSION_REVIEW_PACKET.md) using the following verification steps:

1. **Verify Raw Hashes**:
   Confirm that the on-disk file in `data_stage_b/raw/<source_id>/<blob_sha>.*` matches the raw file SHA-256 and Git blob SHA declared in the packet.
2. **Inspect Spec Node**:
   Navigate to the JSON pointer in the raw specification and inspect the parameters and requestBody schema definitions.
3. **Verify Invocation Mode & Fixtures**:
   Confirm whether an agent can formulate all schema arguments in a single turn without inspecting prior tool execution responses (`SINGLE_TURN_CONSTRUCTIBLE`). Confirm that required runtime fixtures (`FIXTURE_REQUIRED`) are documented and minimal.
4. **Audit Rejected Alternatives**:
   Ensure rejected competing operations were excluded for documented technical reasons (e.g. multi-turn review IDs, invoice payment lifecycle state, binary file uploads).
5. **Complete Sign-Off Block**:
   Record the review decision:
   - **Reviewer Name:** Legal or professional name of the reviewer.
   - **Reviewer Role:** `AUTHOR_MANUAL_REVIEW` (or `INDEPENDENT_REVIEW` if external).
   - **Review Date:** UTC ISO 8601 timestamp.
   - **Reviewed Artifact SHA-256:** SHA-256 digest of `stage_b_operation_manifest.yaml` and `candidate_admission_decisions.json`.
   - **Review Decision:**
     - `APPROVE`: Operation satisfies all criteria and is authorized for canonical extraction.
     - `REQUEST_CHANGES`: Issues identified requiring adjustment or re-ranking.
     - `REJECT`: Candidate disqualified; must be replaced from the eligible pool.
   - **Review Notes:** Summary of findings and conditions.

**Sign-off fields must remain unpopulated (`[PENDING_*]`) until a designated human reviewer actually executes this review.**
