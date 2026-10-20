# Stage B Threats to Validity Register

**Document Type:** Formal Epistemic Risk Register & Methodological Limitations  
**Document Status:** `ACTIVE_THREATS_REGISTER`  
**Governing Standard:** ACM / IEEE Empirical Research Guidelines  
**Associated Policy:** `docs/RESEARCH_CLAIM_STYLE_GUIDE.md`  

---

## 1. Overview and Epistemic Risk Management

Empirical evaluation of tool-augmented Large Language Models is vulnerable to subtle confounding factors, infrastructure artifacts, and statistical overclaiming. This register catalogs every identified threat across four standard empirical dimensions (Construct, Internal, External, and Conclusion Validity) alongside explicit mitigation protocols.

---

## 2. Construct Validity

Construct validity evaluates whether our operational metrics accurately measure intrinsic LLM contract comprehension and schema fragility.

| Threat ID | Identified Threat | Scientific Confounding Risk | Mitigation & Boundary Protocol |
| :--- | :--- | :--- | :--- |
| **THREAT_CON_01** | **Closed-Wrapper Normalization** | Extractor adds `additionalProperties: false` to transport containers under `WRAPPER_CLOSED_OBJECT_POLICY_001`. This is not raw-source equivalence. | Explicitly disclaimed in every contract metadata block. Classified as a deliberate benchmark evaluation choice to test strict argument formulation, never claimed as lossless. |
| **THREAT_CON_02** | **Synthetic Mutation Calculus** | Programmatic mutations (nesting, optionality bloat, identifier ambiguity) represent controlled perturbations that may differ from natural human developer schema evolution. | Grounded against empirical software evolution literature; validated by mutation isolation unit tests ensuring single-variable perturbation. |
| **THREAT_CON_03** | **Offline Mock Fidelity** | Hermetic mock state machines simulate server responses but cannot replicate undocumented edge-case backend exceptions. | Benchmarks model tool *invocation* (parameter formulation), not backend endpoint behavior. Focus is on client-side argument formulation. |

---

## 3. Internal Validity

Internal validity evaluates whether observed variations in model failure rates are truly caused by contract structure rather than extraneous experimental artifacts.

| Threat ID | Identified Threat | Scientific Confounding Risk | Mitigation & Boundary Protocol |
| :--- | :--- | :--- | :--- |
| **THREAT_INT_01** | **Provider-Mediated Grammar Masking** | Commercial API endpoints (OpenAI Structured Outputs, Gemini Function Calling) apply proprietary server-side grammar masks (e.g. FSM logit masking). This masks intrinsic model parameter formatting errors. | The benchmark explicitly partitions evaluations into **Regime A** (provider-mediated tool calling) and **Regime B** (unconstrained direct generation), isolating intrinsic reasoning from vendor masking. |
| **THREAT_INT_02** | **Positional and Order Effects** | The order in which properties, descriptions, or distractor tools are presented in prompt context can induce positional bias (e.g. primacy or recency bias). | Deterministic code-point lexicographical sorting of all keys and required arrays; randomized parameter permutations across factorial test runs. |
| **THREAT_INT_03** | **Prompt Formatting Variations** | Slight differences in system prompt framing between model providers could confound contract sensitivity comparisons. | Fixed, uniform tool-calling prompt harness with standardized few-shot framing and temperature set strictly to 0.0. |

---

## 4. External Validity

External validity evaluates whether benchmark findings generalize beyond the specific evaluated tools and environments.

| Threat ID | Identified Threat | Scientific Confounding Risk | Mitigation & Boundary Protocol |
| :--- | :--- | :--- | :--- |
| **THREAT_EXT_01** | **Lack of Live Socket / Wire Validation** | Serialization testing in `openapi_serialization.py` validates Tier 2 in-process representation, not actual TCP/HTTP wire socket transmission. | Documentation explicitly bounds claims to Tier 2 in-process equivalence. Wire conformance (Tier 3) and live server acceptance (Tier 4) are formally declared unvalidated. |
| **THREAT_EXT_02** | **Cohort Domain Concentration** | 30 active manifest operations sampled across 10 clusters may not represent all niche or legacy API protocols (e.g. SOAP, gRPC). | Stratified sample covers 7 distinct commercial domains (Developer Tools, Payments, Infrastructure, Telephony, Enterprise Storage, Collaboration, Customer Support). |
| **THREAT_EXT_03** | **Pretraining Contamination** | Widespread APIs (GitHub, Stripe) appear heavily in open-source code and documentation scraped for LLM pretraining, potentially giving models memorized advantages over obscure specs. | Controlled identifier ambiguity mutations (`ambiguous_identifiers`) neutralize memorized token associations by renaming tools and arguments to generic abstractions. |

---

## 5. Statistical Conclusion Validity

Statistical conclusion validity evaluates whether experimental sample sizes and mathematical analyses justify empirical assertions.

| Threat ID | Identified Threat | Scientific Confounding Risk | Mitigation & Boundary Protocol |
| :--- | :--- | :--- | :--- |
| **THREAT_STA_01** | **Exploratory Pilot Sample Size ($N=5$)** | Preliminary Stage A results reflect an exploratory pilot ($N=5$ calls per mutation). Drawing statistical conclusions from this sample is invalid. | Strictly disclaimed: "sample size is too small for statistical significance; we do not claim proven model degradation yet." Registered in `CLAIM_EVIDENCE_LEDGER.json`. |
| **THREAT_STA_02** | **Multiple Hypothesis Inflation (FDR)** | Factorial testing across 5 models, 4 mutations, and 5 recursion depths yields 100 simultaneous hypothesis comparisons, inflating Type I error rates. | Pre-registered statistical analysis plan requires Holm-Bonferroni or Benjamini-Hochberg False Discovery Rate corrections at $\alpha = 0.01$. |
| **THREAT_STA_03** | **Stochastic Model Variance** | Even at `temperature: 0.0`, GPU non-determinism and vendor infrastructure batching introduce run-to-run completion variance. | Mandatory 5-trial repetition per condition; reporting 95% confidence intervals and standard errors for all accuracy metrics. |
