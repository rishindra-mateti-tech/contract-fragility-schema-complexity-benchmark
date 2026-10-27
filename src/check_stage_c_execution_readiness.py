"""Stage C Model Execution Readiness and Release Gate Enforcer.

Evaluates the 12 mandatory release gates required before any large language model
inference or benchmark evaluation may be executed.
Enforces the blocking state: MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PACKAGES_DIR = ROOT_DIR / "data_stage_c" / "reviewer_packages"
SUBMISSIONS_DIR = ROOT_DIR / "data_stage_c" / "reviewer_submissions"
BASE_DIR = ROOT_DIR / "data_stage_c" / "base_contracts"
MUTATIONS_DIR = ROOT_DIR / "data_stage_c" / "mutation_manifests"
TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
LEAKAGE_JSON = ROOT_DIR / "results_stage_c" / "TASK_LEAKAGE_AUDIT_RELEASE1.json"
DISTRACTOR_JSON = ROOT_DIR / "results_stage_c" / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.json"
BALANCE_JSON = ROOT_DIR / "results_stage_c" / "CORPUS_BALANCE_AUDIT_RELEASE1.json"

GATES_JSON = ROOT_DIR / "results_stage_c" / "STAGE_C_EXECUTION_READINESS_STATUS.json"
GATES_MD = ROOT_DIR / "results_stage_c" / "STAGE_C_EXECUTION_READINESS_GATES.md"


class StageCExecutionReadinessEnforcer:
    """Evaluates the 12 mandatory execution gates and blocks unauthorized model runs."""

    TOTAL_GATES = 12

    def evaluate_all_gates(self) -> Dict[str, Any]:
        """Runs checks across all 12 pre-registered release gates."""
        gate_evaluations: Dict[str, Dict[str, Any]] = {}

        # Gate 1: Synthetic Base Corpus Reproducibility
        base_files = list(BASE_DIR.glob("BASE_SYNTH_*.json"))
        g1_pass = len(base_files) == 40
        gate_evaluations["GATE_01_BASE_CORPUS_REPRODUCIBILITY"] = {
            "gate_number": 1,
            "name": "Synthetic Base Corpus Reproducibility",
            "status": "PASS" if g1_pass else "FAIL",
            "details": f"Found {len(base_files)} / 40 base contracts on disk."
        }

        # Gate 2: Mutation Registry Reproducibility
        mut_files = list(MUTATIONS_DIR.glob("MUT_*.json"))
        g2_pass = len(mut_files) == 200
        gate_evaluations["GATE_02_MUTATION_REPRODUCIBILITY"] = {
            "gate_number": 2,
            "name": "Mutation Registry Reproducibility",
            "status": "PASS" if g2_pass else "FAIL",
            "details": f"Found {len(mut_files)} / 200 mutation manifests on disk."
        }

        # Gate 3: Task Suite Reproducibility
        task_files = list(TASKS_DIR.glob("TASK_SYNTH_*.json"))
        g3_pass = len(task_files) == 300
        gate_evaluations["GATE_03_TASK_SUITE_REPRODUCIBILITY"] = {
            "gate_number": 3,
            "name": "Task Suite Reproducibility",
            "status": "PASS" if g3_pass else "FAIL",
            "details": f"Found {len(task_files)} / 300 task instances on disk."
        }

        # Gate 4: Leakage Audit Complete
        g4_pass = LEAKAGE_JSON.is_file()
        gate_evaluations["GATE_04_LEAKAGE_AUDIT_COMPLETE"] = {
            "gate_number": 4,
            "name": "Leakage and Shortcut Audit Complete",
            "status": "PASS" if g4_pass else "FAIL",
            "details": f"Leakage audit report present: {g4_pass}"
        }

        # Gate 5: Distractor Quality Audit Complete
        g5_pass = DISTRACTOR_JSON.is_file()
        gate_evaluations["GATE_05_DISTRACTOR_AUDIT_COMPLETE"] = {
            "gate_number": 5,
            "name": "Distractor Quality Audit Complete",
            "status": "PASS" if g5_pass else "FAIL",
            "details": f"Distractor audit report present: {g5_pass}"
        }

        # Gate 6: Corpus Balance Audit Complete
        g6_pass = BALANCE_JSON.is_file()
        gate_evaluations["GATE_06_CORPUS_BALANCE_COMPLETE"] = {
            "gate_number": 6,
            "name": "Corpus Balance and Diversity Audit Complete",
            "status": "PASS" if g6_pass else "FAIL",
            "details": f"Corpus balance report present: {g6_pass}"
        }

        # Gate 7: Zero Unresolved INVALID Tasks
        # In Release 1, 100 tasks are diagnosed as INVALID; they must be versioned into Release 2
        invalid_count = 0
        if LEAKAGE_JSON.is_file():
            with open(LEAKAGE_JSON, "r", encoding="utf-8") as f:
                leak_data = json.load(f)
                invalid_count = leak_data.get("status_distribution", {}).get("INVALID", 0)

        g7_pass = (invalid_count == 0)
        gate_evaluations["GATE_07_ZERO_UNRESOLVED_INVALID_TASKS"] = {
            "gate_number": 7,
            "name": "Zero Unresolved INVALID Tasks in Active Suite",
            "status": "PASS" if g7_pass else "BLOCKED_PENDING_RELEASE_2_REMEDIATION",
            "details": f"{invalid_count} tasks in Release 1 diagnosed with INVALID leakage findings."
        }

        # Gate 8: Blind Human-Review Package Exists
        blind_manifest = PACKAGES_DIR / "blind_sample_manifest.json"
        g8_pass = blind_manifest.is_file()
        gate_evaluations["GATE_08_HUMAN_REVIEW_PACKAGE_BUILT"] = {
            "gate_number": 8,
            "name": "Blinded Human Review Package Generation",
            "status": "PASS" if g8_pass else "FAIL",
            "details": f"Blind review package present: {g8_pass}"
        }

        # Gate 9: Dual Independent Human Reviews Completed
        sub_files = list(SUBMISSIONS_DIR.glob("*.json")) if SUBMISSIONS_DIR.exists() else []
        g9_pass = len(sub_files) >= 2
        gate_evaluations["GATE_09_DUAL_HUMAN_REVIEWS_COMPLETED"] = {
            "gate_number": 9,
            "name": "Dual Independent Reviews on Pre-Registered Sample",
            "status": "PASS" if g9_pass else "BLOCKED_PENDING_INDEPENDENT_HUMAN_REVIEW",
            "details": f"Found {len(sub_files)} reviewer submissions (minimum 2 required)."
        }

        # Gate 10: Inter-Rater Agreement Thresholds Satisfied (kappa >= 0.70)
        gate_evaluations["GATE_10_AGREEMENT_THRESHOLDS_SATISFIED"] = {
            "gate_number": 10,
            "name": "Inter-Rater Agreement Thresholds Satisfied",
            "status": "BLOCKED_PENDING_INDEPENDENT_HUMAN_REVIEW",
            "details": "Requires at least two validated human reviewer submissions."
        }

        # Gate 11: Reviewer Outcomes and Exclusions Logged
        gate_evaluations["GATE_11_REVIEWER_OUTCOMES_LOGGED"] = {
            "gate_number": 11,
            "name": "Reviewer Outcomes and Exclusion Registry Logged",
            "status": "BLOCKED_PENDING_INDEPENDENT_HUMAN_REVIEW",
            "details": "Requires finalized human review adjudications."
        }

        # Gate 12: Final Task Suite Frozen and Hashed
        gate_evaluations["GATE_12_FINAL_SUITE_FROZEN_AND_HASHED"] = {
            "gate_number": 12,
            "name": "Final Benchmark Task Suite Frozen and Hashed",
            "status": "BLOCKED_PENDING_POST_REVIEW_FREEZE",
            "details": "Final benchmark freeze follows successful human review adjudication."
        }

        passed_gates = sum(1 for g in gate_evaluations.values() if g["status"] == "PASS")
        all_passed = (passed_gates == self.TOTAL_GATES)

        overall_state = (
            "MODEL_EXECUTION_PERMITTED" if all_passed else
            "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION"
        )

        manifest = {
            "schema_version": "1.0.0",
            "benchmark_stage": "STAGE_C",
            "operational_state": overall_state,
            "model_execution_permitted": all_passed,
            "total_gates": self.TOTAL_GATES,
            "gates_passed": passed_gates,
            "gates_blocked": self.TOTAL_GATES - passed_gates,
            "gates": gate_evaluations,
            "enforcement_notice": (
                "Hard execution gate: Model inference, evaluation scripts, or token calls "
                "must not be invoked while operational_state is MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION."
            )
        }
        return manifest

    def assert_execution_permitted(self) -> None:
        """Raises PermissionError if model execution is currently blocked."""
        manifest = self.evaluate_all_gates()
        if not manifest["model_execution_permitted"]:
            raise PermissionError(
                f"Model execution is strictly BLOCKED. State: {manifest['operational_state']}. "
                f"Gates passed: {manifest['gates_passed']} / {manifest['total_gates']}."
            )


def main():
    enforcer = StageCExecutionReadinessEnforcer()
    manifest = enforcer.evaluate_all_gates()

    GATES_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(GATES_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # Format Markdown Report
    rows = []
    for gid, g in manifest["gates"].items():
        rows.append(f"| {g['gate_number']} | {g['name']} | `{g['status']}` | {g['details']} |")

    md_content = fr"""# Stage C Model Execution Readiness Gates

## 1. Executive Summary

- **Operational State**: `{manifest['operational_state']}`
- **Model Execution Permitted**: `{manifest['model_execution_permitted']}`
- **Gates Satisfied**: {manifest['gates_passed']} of {manifest['total_gates']} passed
- **Gates Blocked**: {manifest['gates_blocked']} pending independent human review and remediation

## 2. Gate Verification Matrix

| Gate # | Gate Name | Current Status | Verification Findings / Blocker |
| :---: | :--- | :---: | :--- |
""" + "\n".join(rows) + f"""

## 3. Enforcement Notice and Scientific Guardrails

Model evaluation is strictly blocked until independent human evaluators complete review of the pre-registered sample, inter-rater reliability is certified (\\kappa \\ge 0.70), and any identified leakage tasks are addressed via a versioned Release 2 corpus.
"""

    with open(GATES_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Execution readiness evaluated: {manifest['operational_state']}")
    print(f"Gates passed: {manifest['gates_passed']} / {manifest['total_gates']}")
    print(f"Reports saved to {GATES_JSON} and {GATES_MD}")


if __name__ == "__main__":
    main()
