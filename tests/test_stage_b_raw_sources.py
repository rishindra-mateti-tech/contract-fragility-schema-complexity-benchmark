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
    
    for s in registry["sources"]:
        cid = s["candidate_source_id"]
        blob_sha = s["source_file_blob_sha"]
        ext = os.path.splitext(s["source_file_path"])[1]
        raw_path = os.path.join(RAW_BASE_DIR, cid, f"{blob_sha}{ext}")
        
        assert os.path.exists(raw_path), f"Raw source file missing: {raw_path}"
        with open(raw_path, "rb") as f:
            content = f.read()
        
        # Verify Git blob SHA identity
        actual_blob_sha = git_blob_sha(content)
        assert actual_blob_sha == blob_sha, f"Git blob SHA mismatch for {cid}: expected {blob_sha}, got {actual_blob_sha}"
        
        # Verify SHA-256 identity
        actual_sha256 = hashlib.sha256(content).hexdigest()
        assert actual_sha256 == s["downloaded_file_sha256"], f"SHA-256 mismatch for {cid}"

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
    
    for s in registry["sources"]:
        cid = s["candidate_source_id"]
        blob_sha = s["source_file_blob_sha"]
        sidecar_path = os.path.join(RAW_BASE_DIR, cid, f"{blob_sha}.provenance.json")
        
        assert os.path.exists(sidecar_path), f"Sidecar provenance missing: {sidecar_path}"
        with open(sidecar_path, "r", encoding="utf-8") as f:
            sidecar = json.load(f)
            
        for rf in required_fields:
            assert rf in sidecar, f"Missing field {rf} in {sidecar_path}"
        assert sidecar["blob_sha_verified"] is True
        assert len(sidecar["associated_operation_ids"]) >= 1

def test_all_30_operations_resolve_deterministic_pointers():
    assert os.path.exists(MANIFEST_PATH), "Operation manifest must exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
        
    assert len(manifest["operations"]) == 30, "Expected exactly 30 approved operations"
    
    for op in manifest["operations"]:
        cid = op["candidate_source_id"]
        op_id = op["operation_id"]
        blob_sha = op["source_file_blob_sha"]
        path = op["source_file_path"]
        ext = os.path.splitext(path)[1]
        raw_path = os.path.join(RAW_BASE_DIR, cid, f"{blob_sha}{ext}")
        pointer = op["source_spec_pointer"]
        
        assert os.path.exists(raw_path), f"Raw source missing for {op_id}: {raw_path}"
        
        if ext in [".json", ".yaml", ".yml"]:
            if ext == ".json":
                with open(raw_path, "r", encoding="utf-8") as f:
                    doc = json.load(f)
            else:
                with open(raw_path, "r", encoding="utf-8") as f:
                    doc = yaml.safe_load(f)
            resolved = resolve_json_pointer(doc, pointer)
            assert resolved is not None, f"JSON Pointer {pointer} for {op_id} failed to resolve in {raw_path}"
            assert isinstance(resolved, dict), f"Resolved target for {op_id} must be a dict"
        elif ext in [".py", ".ts"]:
            with open(raw_path, "r", encoding="utf-8") as f:
                content = f.read()
            matched = resolve_mcp_pointer(content, pointer)
            assert matched is not None, f"MCP Pointer {pointer} for {op_id} failed to resolve in {raw_path}"
        else:
            pytest.fail(f"Unsupported file extension {ext} for {op_id}")
