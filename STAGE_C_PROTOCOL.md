# Stage C Benchmark Protocol: Controlled Mutation Benchmark and Task-Generation Engine

## 1. Governing Research Question

The Stage C benchmark investigation is framed under the following primary scientific research question:

> "Under controlled synthetic task conditions, how do specified schema transformations affect structured tool-use task completion?"

---

## 2. Benchmark Architecture and Objectives

Stage C provides a fully deterministic, pre-registered, synthetic benchmark foundation designed to isolate schema complexity effects on structured tool-use reliability in large language models.

### 2.1 Decoupled Benchmark Scope
Stage C creates benchmark infrastructure, synthetic base contracts, controlled schema mutations, latent-intent representations, task instances, and offline evaluation harnesses. It does NOT:
1. Run live LLM inference, API calls, or token-consuming benchmarks.
2. Utilize unvalidated Stage B candidates as empirical evidence.
3. Fabricate model outputs, accuracy metrics, confidence intervals, or p-values.
4. Conflate synthetic latent-intent mappings with real-world production API semantic equivalence.

---

## 3. Primary Task Categories

Stage C tasks evaluate three orthogonal aspects of tool-use competence under varying schema representations:

1. **Argument Construction:**
   - The user instruction requires invoking a single known target tool.
   - The model must construct a syntactically valid JSON argument object satisfying all required properties, nested containers, and value constraints.
   - Evaluated across baseline and mutated schema surfaces.

2. **Tool Selection Among Distractors:**
   - The user instruction corresponds to one target tool presented alongside controlled distractor tools.
   - Distractors share varying degrees of semantic domain proximity, parameter overlap, and naming similarity.
   - The model must select the exact target tool name and construct its arguments correctly.

3. **Abstention When No Valid Tool Applies:**
   - The user instruction requests an operation that cannot be fulfilled by any tool in the provided toolset.
   - The toolset contains near-miss distractors or partial matches.
   - The model must formally abstain (by emitting an explicit refusal, empty tool call, or dedicated abstention token) rather than hallucinating an invalid argument payload or calling an inappropriate tool.

---

## 4. Primary and Secondary Evaluation Outcomes

Evaluation operates strictly offline on structured response objects. The pre-registered metrics include:

### 4.1 Primary Metrics
- **Tool-Name Exact Match (`TN_EM`):** Binary indicator (0 or 1) indicating whether the selected tool identifier exactly matches the gold target tool name.
- **Syntax-Valid Argument Rate (`SVR`):** Binary indicator (0 or 1) indicating whether the emitted argument payload parses as valid JSON and satisfies structural Draft-07 validation against the active schema.
- **Semantic Argument Exact Match (`SEM`):** Binary indicator (0 or 1) indicating whether the decoded latent intent of the emitted argument payload exactly matches the gold latent intent values across all fields.
- **Abstention Precision and Recall (`ABS_P`, `ABS_R`):** Classification accuracy for abstention scenarios, differentiating valid refusals from hallucinated invocations or false refusals.

### 4.2 Secondary Diagnostic Metrics
- **Component-Level Precision and Recall (`COMP_P`, `COMP_R`):** Field-by-field correctness measuring precision and recall over required, optional, and nested properties.
- **Parse Failure Rate (`PFR`):** Rate of outputs that cannot be deserialized as JSON objects or structured tool calls.
- **Malformed JSON Rate (`MJR`):** Subcategory of parse failures caused by syntax truncation, invalid quotation, trailing commas, or broken escape sequences.
- **Latency and Token Metrics:** Recorded only if later provided directly by actual execution harnesses; never estimated or fabricated.

---

## 5. Controlled Mutation Families

Stage C isolates five controlled schema transformation families applied systematically to synthetic base contracts:

1. **`CANONICAL` (Baseline):**
   - The original, normalized base contract representing standard, clean Draft-07 schema definitions.
   - Serves as the experimental control condition.

2. **`NESTED_HIERARCHY`:**
   - Reorganizes flat or shallow parameter surfaces into deterministic nested container objects.
   - Tests model sensitivity to hierarchy depth, structural nesting, and container navigation.
   - Provides a mathematically reversible latent-intent mapping.

3. **`OPTIONALITY_BLOAT`:**
   - Injects controlled optional parameters, default values, and nullable constraints into the schema.
   - Tests whether increased schema surface area degrades argument precision or induces irrelevant argument hallucination.

4. **`AMBIGUOUS_IDENTIFIERS`:**
   - Systematically transforms field names using deterministic semantic aliases, domain abbreviations, and lexical synonyms under a controlled ambiguity dictionary.
   - Tests sensitivity to naming variation while preserving exact latent semantics.

5. **`DISTRACTOR_SET_COMPLEXITY`:**
   - Task-level mutation that increases the size and semantic proximity of candidate distractor tools.
   - Tests discriminative selection capability under high catalog density without altering target contract semantics.

---

## 6. Crucial Epistemic Boundary: Synthetic Latent-Intent vs Real APIs

A critical methodological boundary governs all Stage C claims:
- **Surface Transformation vs Intent Equivalence:** A mutation changes the surface representation (keys, nesting, optionality) of a synthetic schema.
- **Internal Task Equivalence Only:** Equivalence between a canonical contract and its mutated variant is established strictly through the benchmark's formal latent-intent specification and deterministic oracle codec.
- **Non-Proof of Production Equivalence:** A successful oracle round-trip within Stage C proves that the synthetic prompt and gold arguments encode the same latent variables. It is NOT proof of real-world API compatibility, endpoint semantic equivalence, or live wire interoperability.

---

## 7. Pre-Registered Experimental Governance

To prevent p-hacking, retrospective hypothesis construction, and selective metric reporting:
1. **Master Random Seeds:** Pinned master seed `42`, with deterministic linear congruential sub-seeds derived per base contract (`seed = master_seed * 1000 + contract_index`).
2. **Eligibility and Exclusion Criteria:** Base contracts must strictly pass Draft-07 validation, declare closed properties (`additionalProperties: false`), and possess bidirectional latent-intent codecs.
3. **No-Result Baseline:** Until empirical models are executed in a subsequent sanctioned phase, the benchmark repository resides strictly in `NO_EMPIRICAL_RESULTS_PRESENT` state.
4. **Multiple-Comparison Correction Plan:** Future empirical analyses must apply Benjamini-Hochberg False Discovery Rate (FDR) corrections (or Bonferroni adjustments) across mutation comparisons.
5. **Phase Stop Gates:** Stage C execution ends upon completing and auditing benchmark artifacts. Live model execution requires a separate, explicit user instruction and pre-execution audit.
