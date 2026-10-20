# Stage B Benchmark Reproducibility and Verification Protocol

## 1. Overview and Engineering Objectives

This guide provides an end-to-end protocol for verifying the reproducibility, cryptographic integrity, and deterministic execution of the Stage B Contract Fragility and Schema Complexity Benchmark from a clean repository clone.

Every benchmark artifact, canonical contract, and provenance record is subject to:
1. Pinned dependencies: Verified execution under Python 3.10+ with exact pinned packages in `requirements.txt`.
2. Raw specification immutability: Cryptographic SHA-256 and Git blob SHA checks against `results_stage_b/raw_sources_provenance_registry.json`.
3. Deterministic re-extraction: Bit-for-bit byte identity when extracting canonical contracts under identical timestamps.
4. Fail-closed schema enforcement: Strict rejection of unsupported OpenAPI/JSON Schema constructs.
5. Strict status invariants: Non-elevation of unvalidated slots; `SLOT_STRIPE_02` remains held strictly at `EXTRACTED_PENDING_HUMAN_VALIDATION`, with zero claims of `CANONICAL_FAITHFUL`.
6. Adversarial red-team resilience: Continuous verification that hostile perturbations actively trigger fail-closed stops.

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
The repository provides a single executable script that verifies environment sanity, raw source hashes, full pytest execution, deterministic pilot re-extraction, artifact integrity, directory cleanliness, status invariants, and batch candidate extraction determinism:
```bash
python scripts/verify_reproducibility.py
```

Expected output:
```text
======================================================================
Stage B Benchmark - Reproducibility & Integrity Verification
======================================================================
[PASS] Check 1: Environment Sanity
[PASS] Check 2: Raw Pinned Source Integrity
[PASS] Check 3: Full Pytest Suite
[PASS] Check 4: Deterministic Re-Extraction Byte Identity
[PASS] Check 5: Canonical Artifact Cryptographic Integrity
[PASS] Check 6: Canonical Directory Cleanliness
[PASS] Check 7: Lifecycle Status Invariants & Boundaries
[PASS] Check 8: Batch Candidate Re-Extraction Determinism
======================================================================
RESULT: ALL 8 REPRODUCIBILITY CHECKS PASSED SUCCESSFULLY.
======================================================================
```

### Step 4: Run the Complete Pytest Suite
To execute the comprehensive automated test suite (including Stage A, prescreen audits, mutations, schema feature registry, adversarial feature corpus, serialization, and pilots):
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

### Step 5b: Verify Deterministic Re-Extraction of Quarantined Batch Candidates
To manually verify that the generic batch extraction candidate pipeline produces bit-for-bit identical outputs for all 13 quarantined candidates:
```bash
# Re-extract all candidates into temporary directory
python src/extract_stage_b_batch_candidates.py --all --output-dir /tmp/candidates_reextract

# Verify byte identity for any candidate slot (e.g. SLOT_GITHUB_02)
diff -r /tmp/candidates_reextract/SLOT_GITHUB_02 data_stage_b/extraction_candidates/SLOT_GITHUB_02
```

### Step 6: Run Adversarial Red-Team Verification
To verify that the verification pipeline actively rejects tampered hashes, mutated contracts, broken lineage pointers, and unauthorized status elevations:
```bash
python scripts/red_team_reproducibility.py
```

### Step 7: Run Epistemic Research Claim Linter
To verify that no un-scoped absolutist statements or premature status promotions exist in repository documentation:
```bash
python src/lint_research_claims.py
```

---

## 4. Cryptographic Provenance Reference

Authoritative artifact hashes on disk:

| Artifact Path | SHA-256 Digest | Role & Evidentiary Standard |
| :--- | :--- | :--- |
| `data_stage_b/canonical/SLOT_GITHUB_01/canonical_contract.json` | `43c7a75070e310e13499f8128d6d3a061b46de94238cb5c8ca7044ca103b23b9` | Admitted pilot contract (`pulls/create`) |
| `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json` | `c7e2a3a33078a892ca861684ca963dd00a3ea7cdbd0a9cb2e215b2912547cdbc` | Admitted pilot contract (`PostShippingRates`) |
| `results_stage_b/CANONICAL_PROVENANCE_AUDIT.json` | `b1479bbef50ecb8702797c649fa7ed29bc08e86b046b0f3d685986afcd2df729` | Recursive provenance difference audit |
| `results_stage_b/CLAIM_EVIDENCE_LEDGER.json` | `7546a7c08646bbbe9d35e5c2ebb8ab24c498d92cfbad3b840542253f45bedae5` | Epistemic claim inventory |
| `results_stage_b/SOURCE_ADMISSION_FORENSIC_AUDIT.json` | `e048be53790b053890f51fb3958371a1eb6e4f6d9cc53b14b4433aa2f8b6a631` | Forensic source admission accounting |
| `results_stage_b/FEATURE_REGISTRY_COVERAGE_MATRIX.json` | `700f2bb994e1f9672c6ddc7315b6b04e49f6b6f37947ef3ece6e8fdac0114dc7` | 60-feature red-team test matrix |
| `results_stage_b/BATCH_EXTRACTION_RUN_MANIFEST.json` | `1183129d0b09685545eb96eb83814ebb5bca0623b42810a9a58cf6dd46632c9b` | Batch extraction run manifest and artifact hashes |
| `results_stage_b/SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml` | `65c8ad76a778c7c0f6fd87e608f9806706c19743147684b8738f9a482538ceef` | Schema feature behavior definitions |
| `results_stage_b/stage_b_operation_manifest.yaml` | `117b301a4287cdf8458d6c7a34af33342786d5d4113506e8895767764f005326` | 30-operation admitted manifest |

Raw source specification hashes:
- `CAND-001` (GitHub OpenAPI JSON): `ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194`
- `CAND-002` (Stripe OpenAPI JSON): `19614457e5e347ba07e15e8b4e7b8979c52220ea1901a88bb3e81bfb3e15fba2`

---

## 5. Epistemic Certification and Invariants

1. **Deterministic Byte Identity:** Re-extracting any admitted canonical contract under its pinned timestamp yields an exact byte-for-byte SHA-256 match.
2. **Fail-Closed Continuous Integration:** Any missing file, altered SHA, unhandled schema keyword, or un-scoped claim causes CI to fail.
3. **No Claimed Independent Review:** All current human reviews are documented as `AUTHOR_MANUAL_REVIEW`. Zero independent validations are claimed.
