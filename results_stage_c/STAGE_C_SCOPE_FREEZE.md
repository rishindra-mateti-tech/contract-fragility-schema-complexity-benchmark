# Stage C Scope Freeze Baseline

## 1. Executive Identification & Versioning

- **Benchmark Project:** Contract Fragility and Schema Complexity Benchmark
- **Phase:** Stage C Controlled Mutation Benchmark and Task-Generation Engine
- **Starting Git Commit SHA:** `57ee369f00b3fd03621f92b879abdc286e66bce2`
- **Protocol Version:** `1.0.0`
- **Freeze Date (UTC):** October 26, 2026
- **Author:** Rishindra Mateti
- **State Classification:** `INFRASTRUCTURE_DESIGN_ONLY`

---

## 2. Invariant Boundaries and Exclusions

### 2.1 Absolute Prohibitions
1. **Zero LLM / Model Inference:** No LLM API calls, provider endpoints (OpenAI, Anthropic, Google Gemini, Ollama, local models), live HTTP requests, browser automation, or token-consuming tasks.
2. **Zero Modification of Historical Stages:**
   - Stage A artifacts, empirical results, and manifests remain byte-identical and untouched.
   - Stage B raw sources (`data_stage_b/raw/`), provenance registries, candidate directories (`extraction_candidates/` V1, V2, V3, V4), canonical pilot directories (`data_stage_b/canonical/`), and historical reports remain byte-identical and untouched.
3. **Quarantined Status of Stage B Candidates:** Stage B extraction candidate bundles remain strictly held at `EXTRACTED_PENDING_HUMAN_VALIDATION`. They are NOT utilized as Stage C task instances or empirical research data.
4. **Zero Empirical Claims:** No claims of empirical performance, degradation curves, model vulnerabilities, or statistical significance may be asserted.
5. **Zero Result Fabrication:** No mock benchmark outputs, simulated LLM scores, p-values, confidence intervals, or paper tables may be generated.

---

## 3. Work Track Architecture

Stage C is partitioned into eight strictly decoupled tracks:

- **Track 0 - Scope Freeze and Preregistration:** Protocol definition, formal preregistration JSON, threats to validity, and protocol invariant tests.
- **Track 1 - Synthetic Base-Contract Corpus:** Deterministic generator producing at least 40 synthetic Draft-07 base contracts across controlled schema strata.
- **Track 2 - Latent Intent Representation and Oracle:** Formal latent-intent schema, bidirectional encode/decode codec, and benchmark-internal semantic oracle.
- **Track 3 - Controlled Mutation Compiler:** Deterministic, versioned schema mutation operators spanning CANONICAL, NESTED_HIERARCHY, OPTIONALITY_BLOAT, AMBIGUOUS_IDENTIFIERS, and DISTRACTOR_SET_COMPLEXITY.
- **Track 4 - Task Compiler and Gold Task Set:** Deterministic compiler producing at least 300 synthetic task instances across Argument Construction, Tool Selection, and Abstention.
- **Track 5 - Offline Evaluation Harness:** Offline response parser, evaluator, metrics calculator, and analysis schema with explicit `NO_EMPIRICAL_RESULTS_PRESENT` state.
- **Track 6 - Statistical Analysis Blueprint:** Pre-registered statistical analysis plan, paired comparison designs, multiple-testing corrections, and reporting templates.
- **Track 7 - Benchmark Audit, CI, and Reproducibility:** End-to-end reproducibility verifier, benchmark audit suite, CI workflow integration, and claim ledger updates.

---

## 4. Ground State Verification

Prior to initializing Track 1:
- Pytest Suite: 334 passed in 111.97s (100% pass rate).
- Reproducibility Checks: 11 of 11 checks passed.
- Red-Team Verification: 6 of 6 scenarios passed.
- Claim Linter: 291 markdown files scanned, 0 violations.
- Git Working Tree: Clean on `master` at commit `57ee369f00b3fd03621f92b879abdc286e66bce2`.
