# OpenAPI Local Reference Resolution and Closure Policy

**Policy Identifier:** `OPENAPI_REFERENCE_RESOLUTION_POLICY_001`  
**Policy Version:** `1.0.0`  
**Effective Date:** October 26, 2026  
**Status:** `FROZEN_AND_ENFORCED`  
**Target Output Artifact:** `source_reference_closure.json`  

---

## 1. Epistemic Mandate and Scientific Rationale

In real-world OpenAPI specifications, operations and schema objects frequently declare references (`$ref`) to external files or sibling definitions. Uncontrolled reference resolution presents significant risks to scientific reproducibility and benchmark integrity:

1. **Remote Scheme Hazards:** Dereferencing HTTP/HTTPS URIs introduces network nondeterminism, potential data mutability, and network dependency in benchmark execution.
2. **Filesystem Traversal Hazards:** Unbounded relative paths (`../`) may escape the pinned specification directory, reading host system files or arbitrary workspace contents.
3. **Reference Cycle Hazards:** Circular schema definitions can cause infinite recursion loops in static analysis and extraction pipelines.
4. **Silent Dereference Loss:** Resolving a reference without recording both the original reference path and the resolved destination file obscures contract provenance.

This policy establishes strict, fail-closed, and cryptographically verifiable rules for local multi-file reference resolution in Stage B benchmark candidate extraction.

---

## 2. Core Operational Principles

### Principle 1: Strict Local Confinement
All references must resolve to files located strictly within the designated candidate source root directory (`bundle_root_dir`).
- Absolute canonical paths are computed for both target files and the bundle root.
- Any reference that resolves outside `bundle_root_dir` is rejected immediately under `ERR_PATH_TRAVERSAL_DETECTED`.

### Principle 2: Zero Remote Network Calls
Any reference beginning with a URI scheme prefix (e.g., `http://`, `https://`, `ftp://`, `file://`) is rejected immediately under `ERR_REMOTE_REF_PROHIBITED`. No remote fetching is permitted at any stage of benchmark execution.

### Principle 3: Prohibition of Absolute Filesystem Paths
References declaring absolute paths (e.g., `/etc/...` or `C:\...`) are prohibited under `ERR_ABSOLUTE_PATH_PROHIBITED` to ensure cross-platform reproducibility and repository isolation.

### Principle 4: Cycle Safety and Loop Detection
The resolver tracks the active resolution call stack as a sequence of `(target_file, json_pointer)` tuples. If a tuple is encountered that already exists in the active call stack, resolution aborts with `ERR_REFERENCE_CYCLE_DETECTED`.

### Principle 5: Bounded Traversal Depth
Transitive reference resolution chains are bounded by a configurable maximum depth ($d \le 8$). Exceeding this bound triggers `ERR_REF_DEPTH_EXCEEDED`.

### Principle 6: Fail-Closed on Missing Targets
If a referenced local file or fragment pointer does not exist on disk in the pinned source bundle, extraction fails closed immediately with `ERR_LOCAL_REF_FILE_NOT_FOUND` or `ERR_FRAGMENT_NOT_FOUND`. Missing local files must never be synthesized, mocked, or bypassed.

---

## 3. Required Closure Manifest (`source_reference_closure.json`)

Every extracted candidate bundle utilizing multi-file resolution must emit `source_reference_closure.json` containing:

1. `policy_id`: Must equal `OPENAPI_REFERENCE_RESOLUTION_POLICY_001`.
2. `bundle_root_dir`: Normalized absolute path to the pinned bundle root.
3. `closure_sha256`: Cryptographic hash over all accessed files (`path:sha256;` concatenation).
4. `accessed_files_count`: Total number of distinct local files accessed.
5. `accessed_files`: Array of records containing:
   - `relative_path`: Normalized POSIX relative path from bundle root.
   - `file_sha256`: Hex-encoded SHA-256 hash of file content.
   - `git_blob_sha`: Git blob SHA-1 hash of file content.
   - `file_size_bytes`: Integer byte size of file on disk.
6. `resolution_steps_count`: Total number of resolution steps executed.
7. `resolution_log`: Chronological record of reference resolutions mapping `declared_ref` to `resolved_file` and `resolved_pointer`.

---

## 4. Error Code Reference

| Error Code | Category | Operational Action |
| :--- | :--- | :--- |
| `ERR_REMOTE_REF_PROHIBITED` | Security / Determinism | Reject slot fail-closed. |
| `ERR_ABSOLUTE_PATH_PROHIBITED` | Portability / Isolation | Reject slot fail-closed. |
| `ERR_PATH_TRAVERSAL_DETECTED` | Security / Confinement | Reject slot fail-closed. |
| `ERR_LOCAL_REF_FILE_NOT_FOUND` | Spec Completeness | Reject slot fail-closed; document missing target file in rejection register. |
| `ERR_REFERENCE_CYCLE_DETECTED` | Graph Topology | Reject slot fail-closed. |
| `ERR_REF_DEPTH_EXCEEDED` | Complexity Limit | Reject slot fail-closed. |
| `ERR_FRAGMENT_NOT_FOUND` | Pointer Resolution | Reject slot fail-closed. |
| `ERR_UNSUPPORTED_DOC_FORMAT` | Format Compatibility | Reject slot fail-closed. |
