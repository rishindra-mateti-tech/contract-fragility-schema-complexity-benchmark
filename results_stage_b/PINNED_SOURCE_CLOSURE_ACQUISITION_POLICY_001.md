# Pinned Source-Closure Acquisition Policy for DigitalOcean Multi-File OpenAPI

**Policy ID:** `PINNED_SOURCE_CLOSURE_ACQUISITION_POLICY_001`  
**Status:** `ENFORCED`  
**Effective Date:** October 26, 2026  
**Governing Candidate Source:** `CAND-003` (DigitalOcean `digitalocean/openapi`)  
**Pinned Immutable Commit SHA:** `e326f5060794769b6835084e48be7ce4db062d39`  
**Cryptographic Policy Hash (JSON):** `66dee7f12536da047799c55803a13a3ec4a7286a75edcea8e8a6c5c0039b526c`  

---

## 1. Purpose and Scope

This policy governs the bounded, fail-closed, cryptographic acquisition and local storage of missing multi-file references required by the DigitalOcean OpenAPI 3.0.0 root specification (`specification/DigitalOcean-public.v2.yaml`).

During Batch Extraction V3, operations `SLOT_DO_01` (`floating_ips_create`), `SLOT_DO_02` (`domains_create`), and `SLOT_DO_03` (`droplets_create`) were rejected fail-closed under `ERR_LOCAL_REF_FILE_NOT_FOUND` because the single-file root spec in the raw corpus referenced external local files that were omitted from the initial repository retrieval.

This policy establishes the exact rules under which transitive closure files may be acquired, verified, and quarantined to enable offline reference resolution without modifying existing raw files or compromising scientific provenance.

---

## 2. Pinned Upstream Basis

Acquisition is strictly restricted to the immutable upstream basis recorded in the Stage B Candidate Manifest and Provenance Registry:

- **Source Project:** DigitalOcean OpenAPI
- **Repository URL:** `https://github.com/digitalocean/openapi`
- **Immutable Commit SHA:** `e326f5060794769b6835084e48be7ce4db062d39`
- **Root Specification Relative Path:** `specification/DigitalOcean-public.v2.yaml`
- **Root Specification Git Blob SHA:** `a26d71aa637fd6c6241602e9862eae7fb3d1ed95`
- **Root Specification File SHA-256:** `e18ad525a336da3dd83776659d5b574e30748b1d59efc53a42c86115b290a76a`
- **License File Git Blob SHA:** `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64` (MIT License)

---

## 3. Strict Acquisition Invariants

1. **Immutable Commit Constraint:** All acquired files must be fetched exclusively from the immutable commit `e326f5060794769b6835084e48be7ce4db062d39`. Fetches targeting floating branches (`main`, `master`), latest tags, or unspecified revisions are strictly prohibited.
2. **Transitive Dependency Constraint:** Only files transitively referenced by the root specification for admitted operations (`floating_ips_create`, `domains_create`, `droplets_create`) may be downloaded. Unrelated files in the repository must not be acquired.
3. **No Overwrite of Raw Corpus:** Acquired files must NEVER be written into `data_stage_b/raw/`. The raw corpus remains byte-for-byte read-only and immutable.
4. **Dedicated Closure Storage:** Acquired files must be stored in `data_stage_b/source_closures/CAND-003/` matching their upstream relative hierarchy under `specification/`.
5. **Path Traversal Prevention:** Any reference attempting to navigate outside the boundary of `specification/` using escaping relative paths (`..`) is rejected fail-closed under `ERR_PATH_TRAVERSAL_DETECTED`.
6. **Remote Scheme Prohibition:** Any reference containing network schemes (`http://`, `https://`, `ftp://`) is rejected fail-closed under `ERR_REMOTE_REF_PROHIBITED`.
7. **Offline Guarantee:** Once acquired and audited, all pipeline steps, candidate extractions, tests, and reproducibility checks must run 100% offline with zero live network calls.

---

## 4. Metadata and Provenance Accounting

For every acquired closure file, the acquisition pipeline must record:
- Relative path within closure directory.
- Upstream source repository URL.
- Immutable commit SHA.
- Retrieval URL.
- File size in bytes.
- SHA-256 cryptographic checksum.
- Git blob SHA-1 checksum.
- Reference depth from root specification.
- Parent file referencing this dependency.
- License inheritance affirmation (MIT license, blob `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`).

All metadata must be serialized to `data_stage_b/source_closures/CAND-003/closure_manifest.json`.

---

## 5. Audit and Verification Protocol

A dedicated audit script (`src/audit_pinned_source_closure.py`) must verify:
1. Every file recorded in `closure_manifest.json` exists on disk.
2. Cryptographic SHA-256 and Git blob SHA match the manifest record bit-for-bit.
3. Offline resolution of all 3 target operations succeeds with zero missing reference targets.
4. Clean directory hygiene: no extra, untracked, or non-specification files exist in the closure directory.
