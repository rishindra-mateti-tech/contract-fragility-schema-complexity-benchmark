# Stage B Research Claim Style Guide and Epistemic Governance

## 1. Principles of Epistemic Modesty

Scientific credibility requires rigorous alignment between claims and empirical evidence. In benchmark research, the risk of overclaiming is acute: implementation artifacts (such as local serializers or test harnesses) can easily be conflated with empirical proofs or server-side behavior.

Every statement in this repository must adhere to three core principles:
1. **Scope Precision:** State exactly what was tested, under what assumptions, and in what environment.
2. **Boundary Transparency:** Explicitly state what was not tested (e.g. unvalidated server-side behavior, unexecuted model calls).
3. **No Inflated Terminology:** Avoid absolutist, un-scoped terms such as "proves", "guarantees", "lossless", "faithful", or "production-ready" unless accompanied by explicit evidentiary boundaries.

---

## 2. Claim Classification Taxonomy

Every factual or scientific statement across the repository falls into one of five categories:

| Category | Definition | Evidentiary Standard |
| :--- | :--- | :--- |
| `FACTUAL` | Verifiable statements about code structure, files, counts, or Git history. | Direct inspection of repository artifacts, SHA hashes, or test results. |
| `METHODOLOGICAL` | Descriptions of evaluation protocols, mutation algorithms, or schema taxonomies. | Formal specification documents, deterministic algorithms, and unit test suites. |
| `EMPIRICAL` | Claims regarding LLM performance, error rates, failure modes, or statistical distributions. | Execution logs, statistical confidence intervals, and multi-model evaluation data. |
| `LIMITATION` | Explicit boundaries, unverified assumptions, or recognized implementation constraints. | Documented difference registers, audit findings, and threats to validity. |
| `FUTURE_WORK` | Planned future engineering gates, roadmap milestones, or proposed experiments. | Formally designated as unexecuted; zero empirical claims permitted. |

---

## 3. High-Risk Lexicon and Scoped Alternatives

The automated claim linter (`src/lint_research_claims.py`) flags any un-scoped or prohibited terms. Authors and agents must use the permitted scoped alternatives:

| Term | Risk Level | Prohibited Usage | Permitted Scoped Alternative |
| :--- | :--- | :--- | :--- |
| `proves` / `proven` | HIGH | "proves model degradation", "proves lossless round-trip" | "demonstrates in-process equivalence under test conditions", "evaluates" |
| `guaranteed` / `guarantee` | HIGH | "guarantees contract correctness", "guarantees wire compatibility" | "enforces structural validation via jsonschema", "verifies" |
| `lossless` | HIGH | "lossless extraction", "lossless serialization" | "semantically equivalent modulo wrapper policy", "in-process reversible under declared policy" |
| `faithful` / `canonical-faithful` | CRITICAL | Any use of `CANONICAL_FAITHFUL` without independent human review | `CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY`, `EXTRACTED_PENDING_HUMAN_VALIDATION` |
| `complete` / `completely` | MEDIUM | "complete schema equivalence", "completely validated" | "full property coverage", "evaluated across 15 criteria" |
| `independent validation` | CRITICAL | Claiming author review is independent | "author manual review (`AUTHOR_MANUAL_REVIEW`)", "independent review remains a future gate" |
| `production-ready` | HIGH | "production-ready tool contract" | "benchmarking contract", "evaluated Draft-07 representation" |
| `benchmark result` | HIGH | Stating Stage B has results | "infrastructure hardening", "baseline Stage A pilot results ($N=5$)" |
| `statistically significant` | HIGH | Claiming significance on exploratory data ($N=5$) | "exploratory pilot sample; statistical significance requires full-scale evaluation" |
| `endpoint-conformant` / `wire-conformant` | HIGH | Claiming wire/server conformance without network testing | "in-process representation conformance (Tier 2); wire and server acceptance unvalidated" |

---

## 4. Four-Tier Serialization Conformance Hierarchy

Whenever discussing data serialization (e.g. `openapi_serialization.py`), documentation must reference the specific tier:
- **Tier 1:** Canonical JSON structural preservation (in-memory schema).
- **Tier 2:** Local serializer/deserializer representation preservation (in-process round-trip under declared policy).
- **Tier 3:** Actual HTTP wire conformance (unvalidated without socket-level client capture).
- **Tier 4:** Server-side endpoint semantic acceptance (unvalidated without live API execution).

Claims of "lossless round-trip" are strictly restricted to Tier 2 in-process equivalence.
