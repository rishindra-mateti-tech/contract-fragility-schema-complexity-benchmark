# Stage B Benchmark Reproducibility and Verification Protocol

## 1. Overview and Engineering Objectives

This guide provides an end-to-end protocol for verifying the reproducibility, cryptographic integrity, and deterministic execution of the Stage B Contract Fragility and Schema Complexity Benchmark from a clean repository clone.

Every benchmark artifact, canonical contract, and provenance record is subject to:
1. Pinned dependencies: Guaranteed execution under Python 3.10+ with exact pinned packages in `requirements.txt`.
2. Raw specification immutability: Cryptographic SHA-256 and Git blob SHA checks against `data_stage_b/provenance/raw_source_registry.json`.
3. Deterministic re-extraction: Bit-for-bit byte identity when extracting canonical contracts under identical timestamps.
4. Fail-closed schema enforcement: Strict rejection of unsupported OpenAPI/JSON Schema constructs.
5. Strict status invariants: Non-elevation of unvalidated slots; `SLOT_STRIPE_02` remains held strictly at `EXTRACTED_PENDING_HUMAN_VALIDATION`, with zero claims of `CANONICAL_FAITHFUL`.

---

## 2. System Prerequisites

- Operating System: Linux, macOS, or Windows (with PowerShell / bash).
- Python: Version >= 3.10 (tested on Python 3.10, 3.11, 3.12, 3.13).
- Git: Version >= 2.30.

---

## 3. Step-by-Step Replication Protocol

### Step 1: Clone and Environment Initialization
```bash
git clone https://github.com/rishindra-mateti-tech/contract-fragility-schema-complexity-benchmark.git
cd contract-fragility-schema-complexity-benchmark

# Create isolated virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Pinned Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Pinned runtime dependencies:
- `pytest==9.1.1`
- `jsonschema==4.25.1`
- `pyyaml==6.0.3`

### Step 3: Run Automated Hermetic Verification Script
The repository provides a single executable script that verifies environment sanity, raw source hashes, full pytest execution, deterministic re-extraction, artifact integrity, directory cleanliness, and status invariants:
```bash
python scripts/verify_reproducibility.py
```

Expected output:
```text
======================================================================
Stage B Benchmark — Reproducibility & Integrity Verification
======================================================================
[PASS] Check 1: Environment Sanity
[PASS] Check 2: Raw Pinned Source Integrity
[PASS] Check 3: Full Pytest Suite
[PASS] Check 4: Deterministic Re-Extraction Byte Identity
[PASS] Check 5: Canonical Artifact Cryptographic Integrity
[PASS] Check 6: Canonical Directory Cleanliness
[PASS] Check 7: Lifecycle Status Invariants & Boundaries
======================================================================
RESULT: ALL 7 REPRODUCIBILITY CHECKS PASSED SUCCESSFULLY.
======================================================================
```

### Step 4: Run the Complete Pytest Suite
To execute the comprehensive automated test suite (163 tests covering Stage A, prescreen audits, mutations, schema feature registry, adversarial feature corpus, serialization, and pilots):
```bash
python -m pytest -v
```

### Step 5: Verify Deterministic Re-Extraction of Pilots
To manually verify that the canonical extraction engine reproduces byte-identical contracts:
```bash
# Verify SLOT_GITHUB_01 (pulls/create)
python src/extract_stage_b_canonical_contract.py --slot-id SLOT_GITHUB_01 --generated-at 2026-10-12T18:15:00Z --output-dir /tmp/gh_reextract

# Compare byte identity with repository artifact
diff /tmp/gh_reextract/canonical_contract.json data_stage_b/canonical/SLOT_GITHUB_01/canonical_contract.json

# Verify SLOT_STRIPE_02 (PostShippingRates)
python src/extract_stage_b_canonical_contract.py --slot-id SLOT_STRIPE_02 --generated-at 2026-10-19T18:04:16Z --output-dir /tmp/stripe_reextract

# Compare byte identity with repository artifact
diff /tmp/stripe_reextract/canonical_contract.json data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json
```

---

## 4. Cryptographic Provenance Reference

Authoritative artifact hashes on disk:
- `data_stage_b/canonical/SLOT_GITHUB_01/canonical_contract.json`:
  `43c7a75070e310e13499f8128d6d3a061b46de94238cb5c8ca7044ca103b23b9`
- `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json`:
  `c7e2a3a33078a892ca861684ca963dd00a3ea7cdbd0a9cb2e215b2912547cdbc`

Raw source specification hashes:
- `CAND-001` (GitHub OpenAPI JSON): `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194`
- `CAND-002` (Stripe OpenAPI JSON): `19614457e5e347ba07e15e8b4e7b8979c52220ea1901a88bb3e81bfb3e15fba2`
