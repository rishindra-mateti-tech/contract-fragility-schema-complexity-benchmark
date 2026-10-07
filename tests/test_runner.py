import os
import json
import pytest
import subprocess
from src.stage_a_runner import run_stage_a

def test_selection_reproducibility():
    # Run the manifest generator
    subprocess.run(["python", "scripts/generate_pilot_manifest.py"], check=True)
    with open("data/pilot_manifest.json", "r") as f:
        manifest = json.load(f)
    
    assert manifest["metadata"]["random_seed"] == 42
    assert len(manifest["schemas"]) == 8
    
    expected_ids = ['k8s_scale_deployment', 'aws_create_s3_bucket', 'crm_update_lead', 'mailchimp_add_subscriber', 'database_execute_query', 'auth0_create_user', 'shipping_create_label', 'twilio_send_sms']
    actual_ids = [s["base_id"] for s in manifest["schemas"]]
    # check that they are deterministic
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
    if os.path.exists(out_file):
        os.remove(out_file)
        
    # Run 1: Dry run
    run_stage_a([("Gemini", "gemini-3.1-flash-lite-preview")], run_id=run_id, resume=False, dry_run=True, repeats=1)
    
    with open(out_file, "r") as f:
        results1 = json.load(f)
    
    assert len(results1) == 48 # 8 schemas * (4 Task1 + 2 Task2) * 1 repeat
    assert all(r["raw_text"] == "DRY_RUN" for r in results1)
    
    # Run 2: Resume (should skip all since they exist)
    run_stage_a([("Gemini", "gemini-3.1-flash-lite-preview")], run_id=run_id, resume=True, dry_run=True, repeats=1)
    
    with open(out_file, "r") as f:
        results2 = json.load(f)
        
    assert len(results2) == 48
    
    if os.path.exists(out_file):
        os.remove(out_file)
    manifest_file = os.path.join(results_dir, f"{run_id}_manifest.json")
    if os.path.exists(manifest_file):
        os.remove(manifest_file)
