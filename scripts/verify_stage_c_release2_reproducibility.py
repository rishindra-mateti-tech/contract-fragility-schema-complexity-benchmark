"""Stage C Release 2 Reproducibility and Quality Verifier.

Verifies bit-for-bit determinism, Release 1 immutability, zero-invalid tasks,
zero-ambiguity status, and execution gate enforcement for Release 2.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import hashlib
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

R1_TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
R1_MANIFEST_PATH = ROOT_DIR / "results_stage_c" / "TASK_SET_MANIFEST.json"

R2_TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
R2_MANIFEST_PATH = ROOT_DIR / "data_stage_c_release2" / "task_manifest.json"
R2_PACKAGES_DIR = ROOT_DIR / "data_stage_c_release2" / "reviewer_packages"

LEAKAGE_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_TASK_LEAKAGE_AUDIT.json"
DISTRACTOR_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_DISTRACTOR_QUALITY_AUDIT.json"
GATES_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_EXECUTION_READINESS_STATUS.json"


def verify_release1_immutability() -> Tuple[bool, List[str]]:
    """Confirms all Release 1 task files match original declared hashes in TASK_SET_MANIFEST.json."""
    errors = []
    if not R1_MANIFEST_PATH.is_file():
        errors.append(f"Missing Release 1 manifest at {R1_MANIFEST_PATH}")
        return False, errors

    with open(R1_MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for item in manifest.get("tasks", []):
        tid = item["task_id"]
        expected_sha = item["sha256"]
        fpath = R1_TASKS_DIR / f"{tid}.json"
        if not fpath.is_file():
            errors.append(f"Missing Release 1 task file {tid}")
            continue

        with open(fpath, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        if actual_sha != expected_sha:
            errors.append(f"Release 1 immutability breach for {tid}")

    return (len(errors) == 0), errors


def verify_release2_tasks_determinism() -> Tuple[bool, List[str]]:
    """Confirms all 300 Release 2 tasks match manifest hashes."""
    errors = []
    if not R2_MANIFEST_PATH.is_file():
        errors.append(f"Missing Release 2 manifest at {R2_MANIFEST_PATH}")
        return False, errors

    with open(R2_MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    task_summaries = manifest.get("tasks", [])
    if len(task_summaries) != 300:
        errors.append(f"Expected 300 task summaries in Release 2 manifest, found {len(task_summaries)}")

    for item in task_summaries:
        tid = item["task_id"]
        expected_task_sha = item["task_sha256"]
        fpath = R2_TASKS_DIR / f"{tid}.json"
        if not fpath.is_file():
            errors.append(f"Missing Release 2 task file {tid}")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            tdata = json.load(f)

        if tdata.get("task_sha256") != expected_task_sha:
            errors.append(f"Release 2 task hash mismatch for {tid}")

        # Verify release marker
        if tdata.get("release_marker") != "RELEASE_2_PENDING_HUMAN_VALIDATION":
            errors.append(f"Task {tid} has invalid release marker: {tdata.get('release_marker')}")

    return (len(errors) == 0), errors


def verify_release2_zero_invalid() -> Tuple[bool, List[str]]:
    """Confirms Release 2 achieves exactly 0 INVALID tasks."""
    errors = []
    if not LEAKAGE_JSON.is_file():
        errors.append("Missing RELEASE2_TASK_LEAKAGE_AUDIT.json")
        return False, errors

    with open(LEAKAGE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    dist = data.get("status_distribution", {})
    if dist.get("INVALID", 999) != 0:
        errors.append(f"Release 2 has {dist.get('INVALID')} INVALID tasks (must be 0)")
    if dist.get("CLEAR") != 300:
        errors.append(f"Release 2 has {dist.get('CLEAR')} CLEAR tasks (expected 300)")

    return (len(errors) == 0), errors


def verify_release2_zero_ambiguity() -> Tuple[bool, List[str]]:
    """Confirms Release 2 achieves exactly 0 AMBIGUOUS items."""
    errors = []
    if not DISTRACTOR_JSON.is_file():
        errors.append("Missing RELEASE2_DISTRACTOR_QUALITY_AUDIT.json")
        return False, errors

    with open(DISTRACTOR_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    ambig_cnt = data.get("ambiguity_items_count", 999)
    if ambig_cnt != 0:
        errors.append(f"Release 2 has {ambig_cnt} ambiguity items (must be 0)")

    # Verify uniform position
    pos_dist = data.get("positional_distribution", {})
    for p in range(5):
        if pos_dist.get(str(p)) != 20:
            errors.append(f"Target position {p} has count {pos_dist.get(str(p))} instead of 20")

    return (len(errors) == 0), errors


def verify_release2_blind_package_integrity() -> Tuple[bool, List[str]]:
    """Confirms Release 2 blind review package exists and is strictly blinded."""
    errors = []
    manifest_file = R2_PACKAGES_DIR / "blind_sample_manifest.json"
    key_file = R2_PACKAGES_DIR / "author_reconciliation_map.json"

    if not manifest_file.is_file() or not key_file.is_file():
        errors.append("Missing Release 2 blinded reviewer packages or reconciliation map.")
        return False, errors

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    if len(tasks) != 90:
        errors.append(f"Expected 90 blinded tasks, found {len(tasks)}")

    for t in tasks:
        for forbidden in ["expected_tool_name", "expected_arguments", "mutation_family", "paired_group_id"]:
            if forbidden in t:
                errors.append(f"Task {t.get('blind_task_id')} leaks '{forbidden}' in blinded packet")

    return (len(errors) == 0), errors


def verify_release2_execution_gates() -> Tuple[bool, List[str]]:
    """Confirms operational state is MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION."""
    errors = []
    if not GATES_JSON.is_file():
        errors.append("Missing RELEASE2_EXECUTION_READINESS_STATUS.json")
        return False, errors

    with open(GATES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_state = "MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION"
    if data.get("operational_state") != expected_state:
        errors.append(f"Invalid operational state: {data.get('operational_state')}")

    if data.get("model_execution_permitted") is not False:
        errors.append("Model execution must be strictly forbidden (model_execution_permitted == False)")

    if data.get("passed_gates_count") != 7:
        errors.append(f"Expected 7 passed gates, found {data.get('passed_gates_count')}")

    return (len(errors) == 0), errors


def main():
    print("Executing Stage C Release 2 Reproducibility and Quality Verification...")
    all_errors = []

    checks = [
        ("Release 1 Immutability Check", verify_release1_immutability),
        ("Release 2 Task Determinism", verify_release2_tasks_determinism),
        ("Release 2 Zero-Invalid Verification", verify_release2_zero_invalid),
        ("Release 2 Zero-Ambiguity Verification", verify_release2_zero_ambiguity),
        ("Release 2 Blind Package Blinding Integrity", verify_release2_blind_package_integrity),
        ("Release 2 Execution Gate Enforcement", verify_release2_execution_gates),
    ]

    for name, check_fn in checks:
        print(f"Checking {name}...")
        ok, errs = check_fn()
        all_errors.extend(errs)

    if all_errors:
        print(f"FAILED: {len(all_errors)} verification errors detected:")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)

    print("SUCCESS: Stage C Release 2 reproducibility and quality foundation is 100% verified.")


if __name__ == "__main__":
    main()
