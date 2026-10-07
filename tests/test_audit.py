import os
import json
import pytest
from src.audit_stage_a import generate_audit

def test_audit_failures(tmp_path):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Setup mock data dir inside tmp_path
    
    # 1. We mock the pilot_manifest
    pilot = {"schemas": [{"base_id": "test_schema"}]}
    os.makedirs(os.path.join(tmp_path, "data"), exist_ok=True)
    with open(os.path.join(tmp_path, "data", "pilot_manifest.json"), "w") as f:
        json.dump(pilot, f)
        
    # We need a mock target document to hash.
    with open(os.path.join(tmp_path, "PROTOCOL.md"), "w") as f:
        f.write("mock protocol content")
        
    import hashlib
    real_hash = hashlib.sha256(b"mock protocol content").hexdigest()
    fake_hash = "1234567890abcdef"
    
    run_id = "test_audit"
    manifest = {
        "providers_models": [("MockProv", "mock-mod")],
        "repeats": 1,
        "git_sha": "abcd",
        "document_hashes": {
            "PROTOCOL.md": fake_hash # Intentional mismatch
        }
    }
    with open(os.path.join(tmp_path, f"{run_id}_manifest.json"), "w") as f:
        json.dump(manifest, f)
        
    # We will only provide 1 actual record, but expected keys will be task1 (4 variants) + task2 (2 variants) = 6 keys
    records = [{
        "provider": "MockProv", "model": "mock-mod", "track": "Track A",
        "task": 1, "base_id": "test_schema", "variant": "canonical", "repeat": 0,
        "git_sha": "abcd"
    }]
    with open(os.path.join(tmp_path, f"{run_id}_results.json"), "w") as f:
        json.dump(records, f)
        
    analysis = {"results": []}
    with open(os.path.join(tmp_path, f"{run_id}_analysis.json"), "w") as f:
        json.dump(analysis, f)
        
    # Run audit
    res = generate_audit(run_id=run_id, data_dir=str(tmp_path), root_dir=str(tmp_path))
    
    # Assert missing keys detected
    assert len(res["missing_keys"]) == 5 # 6 expected - 1 provided
    assert "MockProv_mock-mod_1_test_schema_nested_hierarchy_0" in res["missing_keys"]
    
    # Assert document hash mismatch detected
    assert "PROTOCOL.md" in res["mismatched_hashes"]
    
    # verify md output
    with open(os.path.join(tmp_path, "POST_RUN_AUDIT.md"), "r") as f:
        content = f.read()
        assert "Missing Conditions**: 5" in content
        assert "PROTOCOL.md`: MISMATCH" in content
