# Contract Fragility: An Empirical Evaluation Protocol for Schema Complexity in LLM Tool Calling

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Benchmark_Protocol_%26_Specification-orange.svg)]()
[![CI](https://github.com/rishindra-mateti-tech/contract-fragility-schema-complexity-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/rishindra-mateti-tech/contract-fragility-schema-complexity-benchmark/actions)

> **Author:** Rishindra Mateti  
> **Location:** Dallas, TX, USA  
> **Contact:** contact@rishindramateti.com | [www.rishindramateti.com](https://www.rishindramateti.com) | [ORCID: 0009-0009-5880-8727](https://orcid.org/0009-0009-5880-8727)

---

## 1. Overview & Research Scope

Tool-augmented Large Language Models (LLMs) and autonomous agent frameworks (e.g., Anthropic's Model Context Protocol, OpenAI Function Calling, Google Agent Development Kit) rely fundamentally on **JSON Schema (Draft-07)** contracts to interface with external databases, APIs, and execution environments.

While recent literature has extensively addressed context-window exhaustion via tool retrieval (ToolBench, AnyTool, RAG-MCP), the causal impact of **internal contract structural design**—specifically object nesting depth, optionality density, enum constraint specificity, and identifier ambiguity—remains an unstandardized empirical question.

This repository provides an open-source, reproducible **experimental benchmark protocol, evaluation specification, and testbed**. It is designed to evaluate contract fragility across **20 synthetic API-inspired tool specifications** and **80 systematically mutated schema conditions**, accompanied by property-based mutation isolation tests and a pre-deployment static schema linter.

---

## 2. Current Status: Exploratory 30-Call Pilot

> [!IMPORTANT]
> **Status: Exploratory Pilot Execution (30 Calls)**  
> The telemetry currently committed in `results/` reflects an exploratory pilot run of extreme schema mutations (30 API calls across 5 suites) profiling `gemini-3.1-flash-lite-preview`. 
>
> **Honest Assessment of Current Findings:**
> 1. **No Statistical Degradation Yet:** The current pilot ($N=5$) shows 100% syntax and selection accuracy. While semantic exact match dropped from 60% (canonical) to 20% (ambiguous), this sample size is too small for statistical significance. We do not claim proven model degradation yet.
> 2. **Extreme Mutations Working:** The benchmark mutations were substantially hardened (3-level nesting, 15-field distractor bloat, docstring removal), successfully forcing the model to fail semantic extraction without breaking the pipeline.
> 3. **Next Steps:** A full multi-provider execution (e.g., Mistral, Llama-3) across the complete dataset is required to test for statistically significant fragility.

---

## 3. The Three-Task Decoupled Evaluation Framework

To isolate cause and effect, the evaluation harness decouples tool calling into three orthogonal benchmarks:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EVALUATION HARNESS                              │
└────────────────────────────────────────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│     TASK 1:      │       │     TASK 2:      │       │     TASK 3:      │
│     Argument     │       │       Tool       │       │    Execution     │
│   Construction   │       │    Selection     │       │    Semantics     │
│ (No Distractors) │       │ (Multi-Tool Set) │       │  (Factual Match) │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

1. **Task 1: Argument Construction (Parameter Complexity Isolation):**  
   Exactly one target tool is provided in the prompt (zero distractors). Measures how structural hierarchy (flat vs. nested), optionality bloat, and identifier abbreviations causally impact syntactic validation pass rates (`Draft7Validator`).
2. **Task 2: Tool Selection (Identifier & Metadata Confusion Isolation):**  
   The target tool is injected alongside four synthetic, domain-matched competing distractor tools with **randomized presentation order** to eliminate positional bias. Measures Top-1 tool selection accuracy and false invocation rates under clean vs. ambiguous identifiers.
3. **Task 3: Execution Semantics (Recursive Field-Level Grounding):**  
   Evaluates outputs that successfully pass syntactic schema validation, measuring recursive field-by-field Exact Match (EM) and precision/recall against ground-truth values to detect argument hallucination.

---

## 4. Synthetic Corpus Provenance & Controlled Mutations

To eliminate operational security hazards (such as accidental cloud mutations or secret leakage) while maintaining high structural realism, the dataset uses **20 synthetic tool specifications modeled after established enterprise API patterns** across Fintech, Cloud Infrastructure, CRM, and Observability. Complete provenance details are documented in [`data/PROVENANCE.md`](data/PROVENANCE.md).

Each base schema undergoes four controlled programmatic mutations holding user intent frozen:
* **`canonical` (Baseline):** Clean, flat parameter hierarchy with explicit field names and descriptive docstrings.
* **`nested_hierarchy`:** Properties are encapsulated into a nested sub-object (`request_payload`), introducing structural depth.
* **`optionality_bloat`:** Six optional enterprise metadata properties (`tags`, `correlation_id`, `idempotency_key`, etc.) are appended to measure context distraction.
* **`ambiguous_identifiers`:** Both tool-level names and parameter descriptors are replaced with generic abbreviations and tokens (`process_action`, `target_id`, `qty`, `spec`, `val`).

### Mutation Isolation Verification
To prove that each mutation alters **only its intended property** and leaves all other schema dimensions invariant, the repository includes comprehensive unit tests in [`tests/test_mutations.py`](tests/test_mutations.py):
* `test_canonical_invariance`: Asserts Draft-07 syntax validity and exact parameter replication.
* `test_nested_hierarchy_isolation`: Asserts that `request_payload` is the sole root property and sub-properties retain exact original types and enums.
* `test_optionality_bloat_isolation`: Asserts that all required fields remain 100% unchanged and only non-required metadata fields are appended.
* `test_ambiguous_identifiers_isolation`: Asserts that property counts, types, and enum domains are preserved while names and descriptions are mutated.
* `test_distractor_tools_integrity`: Asserts that distractor catalogs contain valid Draft-07 schemas without target tool collisions.

---

## 5. Threats to Validity: Provider-Mediated Interfaces

Commercial provider tool-calling APIs (including Google GenAI / Gemini Function Calling, OpenAI Structured Outputs, and Anthropic Tools) implement proprietary server-side validation layers, grammar-constrained decoding masks, and vendor-specific system prompting.

Consequently:
1. **Scope of Claims:** Empirical metrics collected through vendor APIs characterize the **provider-mediated tool-calling interface**, rather than raw, unconstrained transformer attention over JSON schemas.
2. **Experimental Disentanglement:** Our benchmark specification defines two distinct evaluation regimes:
   * **Regime A (Provider-Mediated):** Evaluating vendor function-calling endpoints with vendor-native schema compilation.
   * **Regime B (Unconstrained Raw Calling):** Injecting raw JSON Schemas into the prompt with temperature sampling and standard JSON extraction, isolating raw generative competence from vendor-side schema repair.

---

## 6. Repository Structure

```
contract-fragility-schema-complexity-benchmark/
├── README.md                          # Project documentation and protocol specification
├── LICENSE                            # Apache License 2.0
├── requirements.txt                   # Verified dependencies
├── .env.example                       # Documented environment template
├── .gitignore                         # Build and cache ignore patterns
├── data/
│   ├── base_schemas.json              # 20 synthetic API-inspired tool specifications
│   ├── mutated_schemas.json           # 80 controlled structural conditions
│   ├── distractor_tools.json          # Synthetic domain-matched distractor suites for Task 2
│   ├── build_dataset.py               # Dataset generation and schema sanitization script
│   └── PROVENANCE.md                  # Comprehensive dataset manifest and provenance records
├── src/
│   ├── __init__.py                    # Package initialization
│   ├── schema_mutator.py              # Programmatic mutation engine generating controlled variants
│   ├── validator.py                   # Strict Draft-07 syntax validator & recursive semantic evaluator
│   ├── benchmark_runner.py            # Three-task benchmark runner with retry backoff & availability telemetry
│   ├── stats_analyzer.py              # Wilson score 95% CIs, McNemar paired exact tests, and LaTeX exporter
│   ├── human_eval_auditor.py          # Ground-truth fulfillability and argument hallucination auditor
│   └── linter.py                      # Pre-deployment static schema linter (SchemaFragilityLinter)
├── tests/
│   └── test_mutations.py              # Property-based unit tests verifying mutation isolation
├── results/
│   ├── raw_benchmark_results.json     # Granular telemetry: timestamps, prompts, retry counts, latencies, tokens
│   ├── summary_metrics.json           # Tabulated pass rates, availability rates, and significance tests
│   ├── human_evaluation_audit.json    # Human fulfillability audit log
│   ├── README.md                      # Telemetry schema, smoke test disclosures, and scaling roadmap
│   └── tables/                        # Publication-ready LaTeX tables
└── paper/
    ├── Contract_Fragility_Paper.tex   # Full academic protocol manuscript (IEEEtran compsoc format)
    ├── references.bib                 # Verified bibliography (BFCL, EMNLP ToolPreferences, TSCG, etc.)
    └── Contract_Fragility_Paper.pdf   # Compiled paper PDF
```

---

## 7. Quickstart & Reproduction

### Prerequisites
* Python 3.10+
* Google GenAI API Key (or equivalent OpenAI / Ollama endpoint)

### Installation
```bash
git clone https://github.com/rishindra-mateti-tech/contract-fragility-schema-complexity-benchmark.git
cd contract-fragility-schema-complexity-benchmark
pip install -r requirements.txt
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

### Running Mutation Isolation Tests
```bash
python -m unittest tests/test_mutations.py
```

### Running the Benchmark Runner (Smoke Test or Sweep)
```bash
# Run single-suite smoke test verification
python src/benchmark_runner.py --model gemini-3.1-flash-lite-preview --max-suites 1 --delay 4.0

# Run full multi-suite sweep
python src/benchmark_runner.py --model gemini-3.1-flash-lite-preview --max-suites 20 --delay 4.0
```

### Computing Statistical Significance & Generating Tables
```bash
python src/stats_analyzer.py
```

### Performing Human Evaluation & Fulfillability Audit
```bash
python src/human_eval_auditor.py
```

### Auditing Tool Contracts with the Static Linter
```bash
python src/linter.py data/base_schemas.json
```

---

## 8. Static Schema Fragility Linter (`SchemaFragilityLinter`)

As an engineering contribution, this repository includes an open-source pre-deployment static analysis linter that audits JSON Schema definitions for candidate structural risks identified by this protocol:
* `DEEP_HIERARCHICAL_NESTING`: Flags nested object hierarchies that cause models to flatten or omit parameters.
* `AMBIGUOUS_IDENTIFIER`: Flags generic names (`id`, `data`, `val`) that induce tool selection confusion.
* `EXCESSIVE_OPTIONALITY_BLOAT`: Flags schemas where optional fields outnumber required fields by more than 2:1.
* `MISSING_PARAMETER_DOCSTRING`: Flags parameters lacking descriptive documentation.
* `UNBOUND_ENUM_SPECIFICATION`: Detects when natural language docstrings list discrete options without formal JSON Schema `enum` constraints.

---

## 9. Citation

If you reference this benchmark protocol, dataset, or linter in your research, please cite:

```bibtex
@misc{mateti2026contractfragility,
  title={Contract Fragility: An Empirical Evaluation Protocol for Schema Complexity in LLM Tool Calling},
  author={Mateti, Rishindra},
  howpublished={Unpublished Benchmark Protocol},
  year={2026}
}
```

---

## 10. License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
