# Contract Fragility: An Empirical Evaluation of Schema Complexity and Structural Degradation in LLM Tool Calling

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Empirical_Benchmark-success.svg)]()

> **Author:** Rishindra Mateti  
> **Affiliation:** Department of Computer Science, Wright State University, Dayton, OH, USA  
> **Contact:** contact@rishindramateti.com | [www.rishindramateti.com](https://www.rishindramateti.com) | [ORCID: 0009-0009-5880-8727](https://orcid.org/0009-0009-5880-8727)

---

## 1. Overview & Motivation

Tool-augmented Large Language Models (LLMs) and agentic runtimes (e.g., Anthropic's Model Context Protocol, OpenAI Function Calling, Google Agent Development Kit) rely fundamentally on **JSON Schema (Draft-07)** contracts to interact with external databases, APIs, and execution environments.

While recent literature has heavily targeted tool-retrieval scalability and context-window compression (such as ToolBench, AnyTool, and TSCG), the causal impact of **tool-contract structural design** (object nesting depth, optionality density, enum constraint specificity, and identifier ambiguity) has remained largely unmeasured.

This benchmark provides a controlled, reproducible empirical evaluation of contract fragility across **20 production-derived API specifications** and **80 systematically mutated schema conditions**.

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
   The target tool is injected alongside four domain-relevant, competing distractor tools. Measures Top-1 tool selection accuracy and false invocation rates under clean vs. ambiguous identifiers.
3. **Task 3: Execution Semantics (Factual Grounding Fidelity):**  
   Evaluates outputs that successfully pass syntactic schema validation, measuring Exact Match (EM) and field-level precision/recall against human-verified ground-truth values.

---

## 3. Dataset & Mutation Taxonomy

The dataset is derived from 20 permissively licensed (MIT, Apache-2.0, BSD) production specifications spanning Fintech, Cloud Infrastructure, Developer Tools, Observability, Logistics, and CRM.

Each base schema undergoes four controlled mutations holding the underlying query intent constant:
* **Canonical (Baseline):** Clean, flat parameter hierarchy with explicit field names and descriptive docstrings.
* **Nested Hierarchy:** Properties are wrapped into a nested sub-object (`request_payload`), introducing structural depth.
* **Optionality Bloat:** Six optional enterprise metadata properties (`tags`, `correlation_id`, `idempotency_key`, etc.) are appended to measure context distraction.
* **Ambiguous Identifiers:** Descriptive parameter names are replaced with common abbreviations (`target_id`, `qty`, `spec`, `val`).

---

## 4. Repository Structure

```
contract-fragility-schema-complexity-benchmark/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   ├── base_schemas.json             # 20 production-derived API specifications
│   ├── mutated_schemas.json          # 80 controlled schema conditions
│   ├── distractor_tools.json         # Plausible distractor tool suites for Task 2
│   └── build_dataset.py              # Script constructing the base dataset
├── src/
│   ├── __init__.py
│   ├── schema_mutator.py             # Mutation engine generating controlled variants
│   ├── validator.py                  # Strict Draft-07 syntax and semantic exact-match validator
│   ├── benchmark_runner.py           # Multi-task benchmark orchestrator for LLM APIs
│   ├── stats_analyzer.py             # Statistical significance, Wilson CIs, and LaTeX table exporter
│   └── linter.py                     # Static schema fragility linter (SchemaFragilityLinter)
├── results/
│   ├── raw_benchmark_results.json    # Complete, unedited telemetry logs of all model calls
│   ├── summary_metrics.json          # Tabulated pass rates, CIs, and p-values
│   └── tables/                       # Paper-ready LaTeX tables
└── paper/
    ├── Contract_Fragility_Paper.tex  # Full academic manuscript (IEEEtran format)
    ├── references.bib                # Complete bibliography
    └── Contract_Fragility_Paper.pdf  # Compiled clean PDF
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
```

### Running the Benchmark
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

As an engineering contribution, this repository includes a pre-deployment static analysis linter that checks JSON Schema definitions for known structural failure patterns:
* `DEEP_HIERARCHICAL_NESTING`: Flags nested object hierarchies that cause models to flatten or omit parameters.
* `AMBIGUOUS_IDENTIFIER`: Flags generic names (`id`, `data`, `val`) that induce tool selection confusion.
* `EXCESSIVE_OPTIONALITY_BLOAT`: Flags schemas where optional fields outnumber required fields by more than 2:1.
* `MISSING_PARAMETER_DOCSTRING`: Flags parameters lacking descriptive documentation.
* `UNBOUND_ENUM_SPECIFICATION`: Detects when natural language docstrings list discrete options without formal JSON Schema `enum` constraints.

---

## 7. Citation

If you use this benchmark, dataset, or linter in your research, please cite:

```bibtex
@article{mateti2026contractfragility,
  title={Contract Fragility: An Empirical Evaluation of Schema Complexity and Structural Degradation in LLM Tool Calling},
  author={Mateti, Rishindra},
  journal={Empirical Systems Research},
  year={2026}
}
```

---

## 8. License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
