import os
import json
import hashlib
import pytest
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_sources_provenance_registry.json")
MANIFEST_PATH = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")
RAW_BASE_DIR = os.path.join(ROOT_DIR, "data_stage_b", "raw")

def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode('utf-8')
    return hashlib.sha1(header + data).hexdigest()

def resolve_json_pointer(doc, pointer):
    if pointer.startswith("#/"):
        pointer = pointer[2:]
    elif pointer.startswith("/"):
        pointer = pointer[1:]
    tokens = pointer.split("/")
    curr = doc
    for tok in tokens:
        unescaped = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(curr, dict) and unescaped in curr:
            curr = curr[unescaped]
        elif isinstance(curr, list) and unescaped.isdigit():
            curr = curr[int(unescaped)]
        else:
            return None
    return curr

def resolve_mcp_pointer(file_content, pointer):
    parts = pointer.split(":")
    tool_name = parts[-1]
    patterns = [
        f'name="{tool_name}"',
        f"name='{tool_name}'",
        f'name: "{tool_name}"',
        f"name: '{tool_name}'",
        f'Tool(\n        name="{tool_name}"',
        f'"{tool_name}"',
    ]
    for pat in patterns:
        if pat in file_content:
            return pat
    return None

def test_registry_exists_and_contains_approved_sources():
    assert os.path.exists(REGISTRY_PATH), "Provenance registry must exist"
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    assert registry["total_sources_retrieved"] == 10
    assert len(registry["sources"]) == 10

def test_raw_source_files_exist_and_match_blob_sha():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    mismatches = []
    for s in registry["sources"]:
        cid = s["candidate_source_id"]
        expected_blob_sha = s["source_file_blob_sha"]
        ext = os.path.splitext(s["source_file_path"])[1]
        raw_path = os.path.join(RAW_BASE_DIR, cid, f"{expected_blob_sha}{ext}")
        
        if not os.path.exists(raw_path):
            mismatches.append(f"[{cid}] Raw source file missing on disk: {raw_path}")
            continue
            
        with open(raw_path, "rb") as f:
            content = f.read()
        
        # Verify Git blob SHA identity
        actual_blob_sha = git_blob_sha(content)
        if actual_blob_sha != expected_blob_sha:
            mismatches.append(
                f"[{cid}] Git blob SHA mismatch: expected {expected_blob_sha}, got {actual_blob_sha} "
                f"(file_size={len(content)} bytes, path={raw_path})"
            )
        
        # Verify SHA-256 identity
        actual_sha256 = hashlib.sha256(content).hexdigest()
        if actual_sha256 != s["downloaded_file_sha256"]:
            mismatches.append(
                f"[{cid}] SHA-256 mismatch: recorded {s['downloaded_file_sha256']}, got {actual_sha256}"
            )
            
    if mismatches:
        pytest.fail(f"Raw source integrity check failed with {len(mismatches)} errors:\n" + "\n".join(mismatches))

def test_sidecar_provenance_files():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
        
    required_fields = [
        "candidate_source_id", "source_project", "source_repository_url",
        "immutable_commit_sha", "source_file_path", "source_file_blob_sha",
        "retrieved_file_size_bytes", "downloaded_file_sha256",
        "retrieval_timestamp", "raw_source_url", "license_file_url",
        "license_file_blob_sha", "associated_operation_ids", "blob_sha_verified"
    ]
    
    errors = []
    for s in registry["sources"]:
        cid = s["candidate_source_id"]
        blob_sha = s["source_file_blob_sha"]
        sidecar_path = os.path.join(RAW_BASE_DIR, cid, f"{blob_sha}.provenance.json")
        
        if not os.path.exists(sidecar_path):
            errors.append(f"[{cid}] Sidecar provenance missing: {sidecar_path}")
            continue
            
        with open(sidecar_path, "r", encoding="utf-8") as f:
            sidecar = json.load(f)
            
        for rf in required_fields:
            if rf not in sidecar:
                errors.append(f"[{cid}] Missing required provenance field '{rf}' in {sidecar_path}")
                
        if sidecar.get("blob_sha_verified") is not True:
            errors.append(f"[{cid}] blob_sha_verified is not True in {sidecar_path}")
            
        if len(sidecar.get("associated_operation_ids", [])) < 1:
            errors.append(f"[{cid}] associated_operation_ids is empty in {sidecar_path}")
            
    if errors:
        pytest.fail(f"Sidecar provenance check failed with {len(errors)} errors:\n" + "\n".join(errors))

def test_all_30_operations_resolve_deterministic_pointers():
    assert os.path.exists(MANIFEST_PATH), "Operation manifest must exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
        
    assert len(manifest["operations"]) == 30, "Expected exactly 30 approved operations"
    
    errors = []
    for op in manifest["operations"]:
        cid = op["candidate_source_id"]
        op_id = op["operation_id"]
        blob_sha = op["source_file_blob_sha"]
        path = op["source_file_path"]
        ext = os.path.splitext(path)[1]
        raw_path = os.path.join(RAW_BASE_DIR, cid, f"{blob_sha}{ext}")
        pointer = op["source_spec_pointer"]
        
        if not os.path.exists(raw_path):
            errors.append(f"[{op_id}] Raw source missing: {raw_path}")
            continue
            
        if ext in [".json", ".yaml", ".yml"]:
            if ext == ".json":
                with open(raw_path, "r", encoding="utf-8") as f:
                    doc = json.load(f)
            else:
                with open(raw_path, "r", encoding="utf-8") as f:
                    doc = yaml.safe_load(f)
            resolved = resolve_json_pointer(doc, pointer)
            if resolved is None:
                errors.append(f"[{op_id}] JSON Pointer '{pointer}' failed to resolve in {raw_path}")
            elif not isinstance(resolved, dict):
                errors.append(f"[{op_id}] Resolved target for '{pointer}' is not a dict (got {type(resolved)})")
        elif ext in [".py", ".ts"]:
            with open(raw_path, "r", encoding="utf-8") as f:
                content = f.read()
            matched = resolve_mcp_pointer(content, pointer)
            if matched is None:
                errors.append(f"[{op_id}] MCP Pointer '{pointer}' failed to resolve in {raw_path}")
        else:
            errors.append(f"[{op_id}] Unsupported file extension {ext}")
            
    if errors:
        pytest.fail(f"Operation pointer resolution failed with {len(errors)} errors:\n" + "\n".join(errors))
