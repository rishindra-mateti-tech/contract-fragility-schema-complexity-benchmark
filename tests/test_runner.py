import os
import json
import pytest
import subprocess
from src.stage_a_runner import run_stage_a
from src.validator import validate_syntax, validate_semantics
from src.analyze_stage_a import analyze

def test_selection_reproducibility():
    # DO NOT mutate pilot_manifest.json during tests.
    with open("data/pilot_manifest.json", "r") as f:
        manifest = json.load(f)
    expected_ids = ['k8s_scale_deployment', 'aws_create_s3_bucket', 'crm_update_lead', 'mailchimp_add_subscriber', 'database_execute_query', 'auth0_create_user', 'shipping_create_label', 'twilio_send_sms']
    actual_ids = [s["base_id"] for s in manifest["schemas"]]
    assert set(actual_ids) == set(expected_ids)

def test_task2_randomization():
    import random
    pool = ["A", "B", "C", "D"]
    rng1 = random.Random("test_seed_1")
    pool1 = list(pool)
    rng1.shuffle(pool1)
    
    rng2 = random.Random("test_seed_1")
    pool2 = list(pool)
    rng2.shuffle(pool2)
    
    rng3 = random.Random("test_seed_2")
    pool3 = list(pool)
    rng3.shuffle(pool3)
    
    assert pool1 == pool2
    assert pool1 != pool3

def test_dry_run_and_resume(tmp_path):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(root_dir, "results")
    
    run_id = "test_dry_run"
    out_file = os.path.join(results_dir, f"{run_id}_results.json")
    if os.path.exists(out_file): os.remove(out_file)
        
    results1 = run_stage_a([("Gemini", "gemini-3.1-flash-lite-preview")], run_id=run_id, resume=False, dry_run=True, repeats=1)
    
    assert len(results1) == 48 
    
    task1_records = [r for r in results1 if r["task"] == 1]
    assert len(task1_records) == 32 # 8 schemas * 4 variants
    for r in task1_records:
        assert r["syntax_valid"] is True
        assert r["semantics_valid"] is True
        assert r["tool_name_valid"] is True
        assert "rendered_prompt_hash" in r
        assert "query_hash" in r

    task2_records = [r for r in results1 if r["task"] == 2]
    assert len(task2_records) == 16 # 8 schemas * 2 variants
    for r in task2_records:
        assert r["selection_valid"] is True
        assert "target_position" in r
        assert "candidate_tool_names" in r
        assert "shuffle_seed" in r
    
    run_stage_a([("Gemini", "gemini-3.1-flash-lite-preview")], run_id=run_id, resume=True, dry_run=True, repeats=1)
    with open(out_file, "r") as f:
        results2 = json.load(f)
    assert len(results2) == 48
    
    # Test analyze functionality
    analysis = analyze(run_id, results_dir)
    assert analysis["metadata"]["total_records"] == 48
    assert len(analysis["results"]) == 1
    summary = analysis["results"][0]
    assert summary["provider"] == "Gemini"
    assert summary["track"] == "Track A"
    assert summary["task1"]["canonical"]["syntax_rate"] == 1.0
    
    # Verify no cross-track comparisons in McNemar
    mcnemar = summary["mcnemar_tests"]
    assert "canonical_vs_nested_hierarchy" in mcnemar["task1_semantics"]
    assert mcnemar["task1_semantics"]["canonical_vs_nested_hierarchy"]["discordant_b"] == 0
    assert mcnemar["task1_semantics"]["canonical_vs_nested_hierarchy"]["discordant_c"] == 0
    assert mcnemar["task1_semantics"]["canonical_vs_nested_hierarchy"]["p_value"] == 1.0
    
    if os.path.exists(out_file): os.remove(out_file)
    analysis_out = os.path.join(results_dir, f"{run_id}_analysis.json")
    if os.path.exists(analysis_out): os.remove(analysis_out)
    manifest_out = os.path.join(results_dir, f"{run_id}_manifest.json")
    if os.path.exists(manifest_out): os.remove(manifest_out)

def test_scoring_logic_mutations():
    # Test valid and invalid mocking logic for exact validator signatures
    from src.validator import validate_syntax, validate_semantics
    
    # Example Canonical
    params_can = {"type": "object", "properties": {"amount": {"type": "integer"}}, "required": ["amount"]}
    exp_can = {"amount": 500}
    
    # 1. Valid Canonical
    syn_ok, cat, msg = validate_syntax({"amount": 500}, params_can)
    assert syn_ok and cat is None
    sem_ok, prec, rec, dets = validate_semantics({"amount": 500}, exp_can)
    assert sem_ok and prec == 1.0 and rec == 1.0
    
    # 2. Nested Hierarchy
    params_nest = {"type": "object", "properties": {"request_payload": {"type": "object", "properties": {"amount": {"type": "integer"}}, "required": ["amount"]}}, "required": ["request_payload"]}
    exp_nest = {"request_payload": {"amount": 500}}
    
    syn_ok, cat, msg = validate_syntax({"request_payload": {"amount": 500}}, params_nest)
    assert syn_ok
    sem_ok, prec, rec, dets = validate_semantics({"request_payload": {"amount": 500}}, exp_nest)
    assert sem_ok
    
    # 3. Optionality Bloat
    params_opt = {"type": "object", "properties": {"amount": {"type": "integer"}, "tags": {"type": "string"}}, "required": ["amount"]}
    exp_opt = {"amount": 500} # ground truth only requires amount
    
    # If model hallucinates optional field:
    syn_ok, cat, msg = validate_syntax({"amount": 500, "tags": "hallucinated"}, params_opt)
    assert syn_ok # Valid structurally
    sem_ok, prec, rec, dets = validate_semantics({"amount": 500, "tags": "hallucinated"}, exp_opt)
    assert prec < 1.0 # Precision drops due to hallucinated argument
    
    # 4. Ambiguous Identifier (missing field)
    syn_ok, cat, msg = validate_syntax({}, params_can)
    assert not syn_ok
    assert cat == "MISSING_REQUIRED_FIELD"

def test_malformed_lists():
    params = {"type": "object", "properties": {"foo": {"type": "string"}}}
    syn_ok, cat, msg = validate_syntax([{"foo": "bar"}], params)
    assert not syn_ok
    assert cat == "NON_OBJECT_PAYLOAD"

def test_analyzer_denominators(tmp_path):
    # Create a mock results JSON containing 1 success, 1 rate-limit, and 1 syntax error
    mock_records = [
        # 1. Success
        {
            "provider": "MockProvider", "model": "mock-model", "track": "Track B",
            "task": 1, "variant": "canonical", "base_id": "b1", "repeat": 0,
            "api_error_category": None, "syntax_valid": True, "semantics_valid": True
        },
        # 2. API Error (Rate Limit)
        {
            "provider": "MockProvider", "model": "mock-model", "track": "Track B",
            "task": 1, "variant": "canonical", "base_id": "b2", "repeat": 0,
            "api_error_category": "rate_limit", "syntax_valid": False, "semantics_valid": False
        },
        # 3. Syntax Error (Evaluated)
        {
            "provider": "MockProvider", "model": "mock-model", "track": "Track B",
            "task": 1, "variant": "canonical", "base_id": "b3", "repeat": 0,
            "api_error_category": None, "syntax_valid": False, "semantics_valid": False
        }
    ]
    run_id = "test_denominators"
    out_file = tmp_path / f"{run_id}_results.json"
    with open(out_file, "w") as f:
        json.dump(mock_records, f)
        
    analysis = analyze(run_id, data_dir=str(tmp_path))
    res = analysis["results"][0]
    
    assert res["task1"]["canonical"]["attempted"] == 3
    assert res["task1"]["canonical"]["excluded_api_error"] == 1
    assert res["task1"]["canonical"]["evaluated"] == 2
    assert res["task1"]["canonical"]["n"] == 2
    
    assert res["task1"]["canonical"]["syntax_pass"] == 1
    assert res["task1"]["canonical"]["semantic_pass"] == 1
    
    assert res["error_categories"]["rate_limit"] == 1
