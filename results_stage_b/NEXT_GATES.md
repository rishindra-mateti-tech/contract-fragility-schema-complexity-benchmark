# Stage B Sequential Engineering and Validation Gates

## 1. Roadmap Architecture and Governance

To ensure methodical, auditable progress without violating benchmark boundaries, subsequent work across the benchmark lifecycle is structured into ten sequential gates. No gate may commence until all prerequisites and stop conditions of the preceding gate have been verified by automated tests and documented in signed provenance records.

---

## 2. Gate Definitions

### Gate 1: Human Validation Packet and Review for SLOT_STRIPE_02
- **Objective:** Complete formal human review for the second extracted pilot operation (`PostShippingRates`, `CAND-002`).
- **Prerequisites:** Completed Track 4 form serialization layer; clean test suite pass.
- **Deliverables:**
  * `results_stage_b/CANONICAL_STRIPE_HUMAN_VALIDATION_PACKET.md` documenting immutable blob SHAs, raw-to-canonical field mappings, deepObject form-encoding rules, and wrapper policy normalization.
  * Author review record populating `author_review_sign_off` with immutable Git commit provenance.
  * Status transition from `EXTRACTED_PENDING_HUMAN_VALIDATION` to `CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY`.
- **Stop Condition:** Halt upon author sign-off; do not extract new operations.

### Gate 2: Protocol Amendment for Polymorphic Unions (SLOT_STRIPE_03)
- **Objective:** Standardize multi-schema union evaluation mechanics for operations with `anyOf` / `oneOf` constructs.
- **Target Operation:** Stripe `PostRefunds` (`SLOT_STRIPE_03`), admitted under Protocol Amendment 003.
- **Deliverables:**
  * Formal specification for polymorphic branch validation in tool calling.
  * Discriminator mapping and multi-schema validator integration.
- **Stop Condition:** Verification by unit tests; no live model calls.

### Gate 3: YAML Specification Parser Integration (DigitalOcean, Twilio, LINE)
- **Objective:** Extend extraction pipeline to ingest OpenAPI specifications formatted in YAML.
- **Target Clusters:** `CLUSTER_DO` (`CAND-003`), `CLUSTER_TWILIO` (`CAND-004`), `CLUSTER_LINE` (`CAND-005`).
- **Deliverables:**
  * Deterministic YAML-to-dict parser preserving key ordering and line mapping.
  * Pilot extraction and semantic validation for `SLOT_DO_01`, `SLOT_TWILIO_01`, and `SLOT_LINE_01`.
- **Stop Condition:** Canonical contracts committed under `EXTRACTED_PENDING_HUMAN_VALIDATION`.

### Gate 4: Path-Level Parameter Inheritance (Chatwoot)
- **Objective:** Implement OpenAPI 3.0/3.1 inheritance for path parameters defined on parent path items.
- **Target Operations:** Chatwoot `create-an-account-user` (`SLOT_CHATWOOT_02`) and `create-a-conversation` (`SLOT_CHATWOOT_03`).
- **Deliverables:**
  * Path item parameter resolution merging parent and operation parameter lists.
  * Pilot extraction for Chatwoot account operations.
- **Stop Condition:** Verification that parent path parameters are correctly routed into canonical `path_parameters` wrapper.

### Gate 5: Query and Header Parameter Extraction (Box and Slack)
- **Objective:** Expand canonical contract wrapper schema to support optional query parameters and required authorization/custom headers.
- **Target Clusters:** `CLUSTER_BOX` (`CAND-006`) and `CLUSTER_SLACK` (Slack Web API).
- **Deliverables:**
  * Support for `query_parameters` and `header_parameters` wrappers with `additionalProperties: false`.
  * Canonical contract extraction and lineage generation for Box and Slack operations.
- **Stop Condition:** Zero surface leakage into body or path parameter containers.

### Gate 6: Model Context Protocol (MCP) AST Schema Extraction
- **Objective:** Extract tool contracts from Python and TypeScript MCP server codebases via AST analysis.
- **Target Operations:** SQLite MCP (`server.py`) and GitHub MCP (`index.ts`).
- **Deliverables:**
  * Python AST parser extracting function docstrings, type annotations, and Pydantic schemas.
  * TypeScript AST parser extracting Zod schema definitions.
  * Deterministic mapping to Draft-07 canonical contracts.
- **Stop Condition:** Provenance recorded to exact source code line offsets.

### Gate 7: Stage B Semantic Mutation Operator Engine
- **Objective:** Adapt Stage A mutation operators to the richer Stage B canonical contracts.
- **Mutation Dimensions:**
  * Permutation and renaming
  * Constraint tightening and relaxation
  * DeepObject flattening and unflattening
  * Type coercion and optionality toggling
- **Deliverables:**
  * Mutation generator module producing paired mutant contracts with known semantic deltas.
  * Comprehensive validator verifying mutant contract validity.
- **Stop Condition:** Zero false-positive mutations; automated verification of mutation distance.

### Gate 8: Mock Runtime Environment with Deterministic Fixtures
- **Objective:** Construct hermetic mock server fixtures for all active benchmark slots.
- **Deliverables:**
  * Provider response fixtures matching recorded OpenAPI 200/400 schemas.
  * Deterministic local executor simulating HTTP transport validation and state transitions.
- **Stop Condition:** Fully offline test harness with zero external network connectivity.

### Gate 9: Model Evaluation Execution and Empirical Fragility Analysis
- **Objective:** Execute structured tool-calling benchmarks across candidate language models.
- **Evaluated Models:** Frontier proprietary and open-weights instruction models.
- **Deliverables:**
  * Empirical fragility matrices measuring call failure rates as a function of schema depth, encoding style, and mutation type.
  * Statistical significance testing across model generations.
- **Stop Condition:** Raw execution logs, trajectory traces, and evaluation outputs archived with immutable cryptographic hashes.

### Gate 10: Independent Replication and External Peer Review
- **Objective:** Conduct independent third-party replication of the entire benchmark pipeline.
- **Deliverables:**
  * Independent reviewer validation packets with external cryptographic sign-offs.
  * Public release of evaluation dataset, code, and replication artifacts.
- **Stop Condition:** Full replication from clean repository clones across external compute environments.
