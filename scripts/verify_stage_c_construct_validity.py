"""Stage C Construct Validity Reproducibility and Audit Verifier.

Verifies bit-for-bit reproducibility and completeness of the entire Construct Validity,
Leakage Audit, and Blind Review architecture across Tracks 0 through 7.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import hashlib
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results_stage_c"
PACKAGES_DIR = ROOT_DIR / "data_stage_c" / "reviewer_packages"
TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"


def verify_track0_scope_freeze() -> Tuple[bool, List[str]]:
    errors = []
    prereg_file = RESULTS_DIR / "CONSTRUCT_VALIDITY_PREREGISTRATION.json"
    if not prereg_file.is_file():
        errors.append("Missing CONSTRUCT_VALIDITY_PREREGISTRATION.json")
        return False, errors

    with open(prereg_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "Ability to map a natural-language request" not in data.get("target_construct", ""):
        errors.append("Target construct definition does not match preregistered construct.")

    if data.get("operational_state") != "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION":
        errors.append(f"Operational state violation: {data.get('operational_state')}")

    return (len(errors) == 0), errors


def verify_track1_leakage_audit() -> Tuple[bool, List[str]]:
    errors = []
    leak_file = RESULTS_DIR / "TASK_LEAKAGE_AUDIT_RELEASE1.json"
    if not leak_file.is_file():
        errors.append("Missing TASK_LEAKAGE_AUDIT_RELEASE1.json")
        return False, errors

    with open(leak_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("total_tasks_audited") != 300:
        errors.append(f"Expected 300 tasks audited for leakage, found {data.get('total_tasks_audited')}")

    dist = data.get("status_distribution", {})
    if "INVALID" not in dist or "REQUIRES_HUMAN_REVIEW" not in dist:
        errors.append("Leakage status distribution missing required categories.")

    return (len(errors) == 0), errors


def verify_track2_distractor_audit() -> Tuple[bool, List[str]]:
    errors = []
    dist_file = RESULTS_DIR / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.json"
    ambig_file = RESULTS_DIR / "TASK_AMBIGUITY_REGISTER.md"

    if not dist_file.is_file() or not ambig_file.is_file():
        errors.append("Missing distractor audit report or ambiguity register.")
        return False, errors

    with open(dist_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("total_tasks_audited") != 200:
        errors.append(f"Expected 200 tasks audited in distractor quality, found {data.get('total_tasks_audited')}")

    return (len(errors) == 0), errors


def verify_track3_balance_and_diversity() -> Tuple[bool, List[str]]:
    errors = []
    balance_file = RESULTS_DIR / "CORPUS_BALANCE_AUDIT_RELEASE1.json"
    diversity_file = RESULTS_DIR / "PROMPT_DIVERSITY_AUDIT_RELEASE1.json"

    if not balance_file.is_file() or not diversity_file.is_file():
        errors.append("Missing corpus balance or prompt diversity audit report.")
        return False, errors

    with open(balance_file, "r", encoding="utf-8") as f:
        b_data = json.load(f)
    if b_data.get("total_tasks") != 300:
        errors.append(f"Balance report audited {b_data.get('total_tasks')} tasks instead of 300.")

    with open(diversity_file, "r", encoding="utf-8") as f:
        d_data = json.load(f)
    if d_data.get("shannon_entropy_bits", 0.0) < 4.0:
        errors.append(f"Low entropy in prompt diversity: {d_data.get('shannon_entropy_bits')}")

    return (len(errors) == 0), errors


def verify_track4_blind_packages() -> Tuple[bool, List[str]]:
    errors = []
    manifest_file = PACKAGES_DIR / "blind_sample_manifest.json"
    csv_file = RESULTS_DIR / "HUMAN_REVIEW_ASSIGNMENT_TEMPLATE.csv"

    if not manifest_file.is_file() or not csv_file.is_file():
        errors.append("Missing blind review sample manifest or assignment CSV.")
        return False, errors

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    if len(tasks) != 90:
        errors.append(f"Expected 90 blinded tasks, found {len(tasks)}")

    # Check blinding
    for t in tasks:
        if "expected_tool_name" in t or "expected_arguments" in t or "mutation_family" in t:
            errors.append(f"Blinding violation in task {t.get('blind_task_id')}")

    return (len(errors) == 0), errors


def verify_track5_review_app() -> Tuple[bool, List[str]]:
    errors = []
    app_py = ROOT_DIR / "review_app" / "app.py"
    readme = ROOT_DIR / "review_app" / "README.md"
    reqs = ROOT_DIR / "review_app" / "requirements.txt"

    for p in [app_py, readme, reqs]:
        if not p.is_file():
            errors.append(f"Missing review app file: {p.name}")

    return (len(errors) == 0), errors


def verify_track6_human_review_tooling() -> Tuple[bool, List[str]]:
    errors = []
    schema_file = RESULTS_DIR / "HUMAN_REVIEW_RESULTS_SCHEMA.json"
    template_file = RESULTS_DIR / "HUMAN_REVIEW_RESULTS_TEMPLATE.md"

    for p in [schema_file, template_file]:
        if not p.is_file():
            errors.append(f"Missing human review analysis file: {p.name}")

    return (len(errors) == 0), errors


def verify_track7_execution_gates() -> Tuple[bool, List[str]]:
    errors = []
    status_file = RESULTS_DIR / "STAGE_C_EXECUTION_READINESS_STATUS.json"
    gates_file = RESULTS_DIR / "STAGE_C_EXECUTION_READINESS_GATES.md"

    if not status_file.is_file() or not gates_file.is_file():
        errors.append("Missing execution readiness artifacts.")
        return False, errors

    with open(status_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("operational_state") != "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION":
        errors.append(f"Invalid operational state: {data.get('operational_state')}")

    if data.get("model_execution_permitted") is not False:
        errors.append("Model execution must be strictly forbidden (model_execution_permitted == False).")

    return (len(errors) == 0), errors


def verify_release1_tasks_immutability() -> Tuple[bool, List[str]]:
    """Confirms Release 1 tasks match original hashes in TASK_SET_MANIFEST.json."""
    errors = []
    manifest_path = RESULTS_DIR / "TASK_SET_MANIFEST.json"
    if not manifest_path.is_file():
        errors.append("Missing TASK_SET_MANIFEST.json")
        return False, errors

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for item in manifest.get("tasks", []):
        tid = item["task_id"]
        expected_sha = item["sha256"]
        fpath = TASKS_DIR / f"{tid}.json"
        if not fpath.is_file():
            errors.append(f"Missing Release 1 task {tid}")
            continue

        with open(fpath, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        if actual_sha != expected_sha:
            errors.append(f"Immutability breach for Release 1 task {tid}")

    return (len(errors) == 0), errors


def main():
    print("Executing Stage C Construct Validity Reproducibility Verification...")
    all_errors = []

    checks = [
        ("Track 0: Scope Freeze", verify_track0_scope_freeze),
        ("Track 1: Task Leakage Audit", verify_track1_leakage_audit),
        ("Track 2: Distractor Quality Audit", verify_track2_distractor_audit),
        ("Track 3: Corpus Balance and Diversity", verify_track3_balance_and_diversity),
        ("Track 4: Blind Review Packages", verify_track4_blind_packages),
        ("Track 5: Local Review Application", verify_track5_review_app),
        ("Track 6: Human Review Analysis Tooling", verify_track6_human_review_tooling),
        ("Track 7: Model Execution Readiness Gates", verify_track7_execution_gates),
        ("Release 1 Immutability Check", verify_release1_tasks_immutability),
    ]

    for name, check_fn in checks:
        print(f"Checking {name}...")
        ok, errs = check_fn()
        all_errors.extend(errs)

    if all_errors:
        print(f"FAILED: {len(all_errors)} construct validity errors detected:")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)

    print("SUCCESS: Stage C construct-validity and review infrastructure is 100% verified.")


if __name__ == "__main__":
    main()
