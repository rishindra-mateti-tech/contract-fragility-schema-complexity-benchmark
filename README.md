# Contract Fragility: An Empirical Evaluation Protocol for Schema Complexity in LLM Tool Calling

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Benchmark_Protocol_%26_Specification-orange.svg)]()

> **Author:** Rishindra Mateti  
> **Affiliation:** Department of Computer Science, Wright State University, Dayton, OH, USA  
> **Contact:** contact@rishindramateti.com | [www.rishindramateti.com](https://www.rishindramateti.com) | [ORCID: 0009-0009-5880-8727](https://orcid.org/0009-0009-5880-8727)

---

## 1. Overview & Research Scope

Tool-augmented Large Language Models (LLMs) and agentic runtimes (e.g., Anthropic's Model Context Protocol, OpenAI Function Calling, Google Agent Development Kit) rely fundamentally on **JSON Schema (Draft-07)** contracts to interact with external databases, APIs, and execution environments.

While recent literature has heavily addressed tool-retrieval scalability and context-window compression (e.g., ToolBench, AnyTool, and TSCG), the causal impact of **internal contract structural design** (object nesting depth, optionality density, enum constraint specificity, and identifier ambiguity) has remained largely unmeasured.

This repository provides a formal, reproducible **experimental benchmark protocol and evaluation testbed** designed to evaluate contract fragility across **20 synthetic API-inspired tool specifications** and **80 systematically mutated schema conditions**.

---

## 2. The Three-Task Decoupled Evaluation Framework

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
   The target tool is injected alongside four domain-relevant, competing distractor tools with **randomized presentation order** to prevent positional bias. Measures Top-1 tool selection accuracy and false invocation rates under clean vs. ambiguous identifiers.
3. **Task 3: Execution Semantics (Recursive Field-Level Grounding):**  
   Evaluates outputs that successfully pass syntactic schema validation, measuring recursive field-by-field Exact Match (EM) and precision/recall against ground-truth values to detect argument hallucination.

---

## 3. Dataset Provenance & Structural Mutations

To eliminate operational security hazards (such as accidental cloud mutations or secret leakage) while maintaining high structural fidelity, the dataset uses **synthetic API-inspired specifications modeled after established enterprise API patterns** (Stripe, GitHub REST, Slack Web API, Kubernetes, AWS S3, Datadog, Twilio, and Zendesk). Complete provenance details are documented in [`data/PROVENANCE.md`](data/PROVENANCE.md).

Each base schema undergoes four controlled mutations holding the underlying query intent constant:
* **`canonical` (Baseline):** Clean, flat parameter hierarchy with explicit field names and descriptive docstrings.
* **`nested_hierarchy`:** Properties are wrapped into a nested sub-object (`request_payload`), introducing structural depth.
* **`optionality_bloat`:** Six optional enterprise metadata properties (`tags`, `correlation_id`, `idempotency_key`, etc.) are appended to measure context distraction.
* **`ambiguous_identifiers`:** Both tool-level names and parameter descriptors are replaced with generic abbreviations and tokens (`process_action`, `target_id`, `qty`, `spec`, `val`).

---

## 4. Repository Structure

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
│   ├── distractor_tools.json          # Domain-matched distractor suites for Task 2
│   ├── build_dataset.py               # Dataset generation and schema sanitization script
│   └── PROVENANCE.md                  # Comprehensive dataset manifest and provenance records
├── src/
│   ├── __init__.py                    # Package initialization
│   ├── schema_mutator.py              # Programmatic mutation engine generating controlled variants
│   ├── validator.py                   # Strict Draft-07 syntax validator & recursive semantic evaluator
│   ├── benchmark_runner.py            # Three-task benchmark runner with retry backoff & availability telemetry
│   ├── stats_analyzer.py              # Wilson score 95% CIs, McNemar paired exact tests, and LaTeX exporter
│   └── linter.py                      # Pre-deployment static schema linter (SchemaFragilityLinter)
├── results/
│   ├── raw_benchmark_results.json     # Telemetry logging: raw arguments, token counts, errors, latencies
│   ├── summary_metrics.json           # Tabulated pass rates, availability rates, and significance tests
│   └── tables/                        # Paper-ready LaTeX tables
└── paper/
    ├── Contract_Fragility_Paper.tex   # Full academic protocol manuscript (IEEEtran compsoc format)
    ├── references.bib                 # Verified bibliography (BFCL, EMNLP ToolPreferences, TSCG, etc.)
    └── Contract_Fragility_Paper.pdf   # Compiled paper PDF
```

---

## 5. Quickstart & Reproduction

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

### Running the Benchmark Protocol
```bash
python src/benchmark_runner.py
```

### Computing Statistical Significance & Generating Tables
```bash
python src/stats_analyzer.py
```

### Auditing Tool Contracts with the Static Linter
```bash
python src/linter.py data/base_schemas.json
```

---

## 6. Static Schema Fragility Linter (`SchemaFragilityLinter`)

As an engineering contribution, this repository includes an open-source pre-deployment static analysis linter that checks JSON Schema definitions for known structural failure patterns:
* `DEEP_HIERARCHICAL_NESTING`: Flags nested object hierarchies that cause models to flatten or omit parameters.
* `AMBIGUOUS_IDENTIFIER`: Flags generic names (`id`, `data`, `val`) that induce tool selection confusion.
* `EXCESSIVE_OPTIONALITY_BLOAT`: Flags schemas where optional fields outnumber required fields by more than 2:1.
* `MISSING_PARAMETER_DOCSTRING`: Flags parameters lacking descriptive documentation.
* `UNBOUND_ENUM_SPECIFICATION`: Detects when natural language docstrings list discrete options without formal JSON Schema `enum` constraints.

---

## 7. Citation

If you reference this benchmark protocol, dataset, or linter in your research, please cite:

```bibtex
@misc{mateti2026contractfragility,
  title={Contract Fragility: An Empirical Evaluation Protocol for Schema Complexity in LLM Tool Calling},
  author={Mateti, Rishindra},
  howpublished={Research Protocol and Benchmark Specification, Wright State University},
  year={2026}
}
```

---

## 8. License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
