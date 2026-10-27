# Stage C Reproducibility Audit Report

## 1. Reproducibility Assessment
- **Master Seed**: 42
- **Audit Status**: PASS
- **Verification Harness**: `scripts/verify_stage_c_reproducibility.py`

## 2. Invariant Reproducibility Checks

1. **Synthetic Base Contract Regeneration**:
   - Re-synthesizing all 40 contracts in memory from seed 42 matches on-disk JSON bit-for-bit.
   - Stratum balance verified: exactly 12 Simple Flat, 16 Medium Arrays/Enums, 12 Nested Objects/Surfaces.
   - Domain balance verified: exactly 8 contracts across each of 5 functional domains.

2. **Mutation Manifest Compilation**:
   - Compiling all 200 mutations across 5 families reproduces on-disk manifests bit-for-bit.
   - Invertible operators (Canonical, Nested Hierarchy, Ambiguous Identifiers) pass 100% in-process reversible round-trip decoding.

3. **Task Instance Integrity**:
   - All 300 task instance JSON files match declared SHA-256 digests in `TASK_SET_MANIFEST.json`.
   - Category distribution invariant: exactly 100 Argument Construction, 100 Tool Selection, 100 Abstention.

4. **Stage B Decoupling and Immutability**:
   - All Stage B raw specifications, canonical pilots, and historical candidates (V1-V4) remain untouched.
