# Stage C Threats to Validity and Methodological Boundaries

## 1. Overview

This document systematically characterizes the threats to validity for the Stage C Controlled Mutation Benchmark, delineating construct validity, internal validity, external validity, and statistical conclusion validity.

---

## 2. Construct Validity

### 2.1 Synthetic Schema Design vs Real-World API Complexity
- **Threat:** Synthetic schemas generated under controlled strata may not capture the idiosyncratic, historical, or inconsistent design patterns present in multi-decade enterprise production APIs.
- **Mitigation & Boundary:** Stage C explicitly isolates structural complexity dimensions (nesting depth, optionality noise, identifier lexical ambiguity, catalog density) in a clean laboratory setting. It does NOT claim to model end-to-end production backend behavior or undocumented legacy quirks.

### 2.2 Latent Intent Representation vs True Semantic Equivalence
- **Threat:** Treating schema mutations as "semantically equivalent" risks conflating syntactic repackaging with authentic API wire compatibility.
- **Mitigation & Boundary:** Equivalence between a base contract and its mutated variant is defined and verified strictly through the benchmark's formal latent-intent representation and semantic oracle. This guarantees internal task equivalence for the synthetic evaluation, but does NOT assert that real-world service endpoints would accept such transformations interchangeably.

---

## 3. Internal Validity

### 3.1 Prompt Leakage and Lexical Cueing
- **Threat:** Natural-language user prompts that explicitly mirror schema property keys or tool identifiers provide shortcut cues to models, conflating superficial token matching with genuine structural schema comprehension.
- **Mitigation:** The task generation engine uses diverse paraphrasing templates and semantic concept descriptions rather than verbatim property keys. Automated adversarial leakage audits verify that gold tool names and exact field keys are not artificially presented as prompt hints.

### 3.2 Distractor Selection and Catalog Density Confounders
- **Threat:** Tool selection difficulty may be confounded by arbitrary distractor choice rather than controlled semantic proximity.
- **Mitigation:** Distractor generation is governed by a formalized catalog complexity model that measures lexical overlap, parameter similarity, and domain proximity deterministically from pinned seeds.

### 3.3 Evaluation Order and Presentation Bias
- **Threat:** Large language models exhibit recency and primacy biases based on the order in which tools are serialized in the system prompt.
- **Mitigation:** Tool presentation order is deterministically fixed and pre-registered per task instance, ensuring that baseline and mutated comparisons hold presentation order constant.

---

## 4. External Validity

### 4.1 Generalizability Across Model Architectures
- **Threat:** Fragility to specific mutations (such as nested hierarchy or optionality bloat) may reflect specific tokenizer properties, fine-tuning styles (e.g. JSON mode vs raw text), or context window architectures rather than universal LLM properties.
- **Mitigation:** No empirical claims or cross-model generalizations are asserted in Stage C. Future evaluations must report architecture-specific stratifications rather than pooled unweighted averages.

### 4.2 Non-Exhaustiveness of Schema Feature Space
- **Threat:** JSON Schema and OpenAPI specifications encompass advanced constructs (e.g. recursive schemas, complex pattern regexes, format validators) not exercised in Stage C.
- **Mitigation:** Stage C focuses strictly on the 5 pre-registered mutation families. Unsupported features are rejected fail-closed and formally documented in the exclusion registry.

---

## 5. Statistical Conclusion Validity

### 5.1 Multiple Hypothesis Testing Inflation
- **Threat:** Testing five mutation families across five primary metrics and three task categories creates multiple comparisons, inflating the risk of Type I errors (false positives).
- **Mitigation:** The statistical plan mandates Benjamini-Hochberg False Discovery Rate (FDR) corrections at alpha = 0.05 across all primary hypothesis families, alongside Bonferroni adjustments for omnibus comparisons.

### 5.2 Ceiling and Floor Effects
- **Threat:** Excessively trivial tasks produce ceiling performance (100% exact match), obscuring mutation effects, while overly convoluted tasks induce floor performance (0% exact match), preventing meaningful differentiation.
- **Mitigation:** Base contracts are stratified across low, medium, and high complexity strata to ensure diverse empirical variance across difficulty tiers.
