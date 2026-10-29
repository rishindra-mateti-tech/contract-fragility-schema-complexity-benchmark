"""Stage C Release 2 Model Execution Readiness and Release Gate Enforcer.

Evaluates the 11 mandatory Release 2 release gates required before any large language
model inference or benchmark evaluation may be executed.
Enforces the blocking state: MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
R2_TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
R2_MANIFEST_PATH = ROOT_DIR / "data_stage_c_release2" / "task_manifest.json"
R2_PACKAGES_DIR = ROOT_DIR / "data_stage_c_release2" / "reviewer_packages"
SUBMISSIONS_DIR = ROOT_DIR / "data_stage_c_release2" / "reviewer_submissions"

LEAKAGE_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_TASK_LEAKAGE_AUDIT.json"
DISTRACTOR_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_DISTRACTOR_QUALITY_AUDIT.json"
BALANCE_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_CORPUS_BALANCE_AUDIT.json"
DIVERSITY_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_PROMPT_DIVERSITY_AUDIT.json"

GATES_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_EXECUTION_READINESS_STATUS.json"
GATES_MD = ROOT_DIR / "results_stage_c" / "RELEASE2_EXECUTION_READINESS_GATES.md"


class StageCRelease2ExecutionReadinessEnforcer:
    """Evaluates the 11 Release 2 execution gates and blocks unauthorized model inference."""

    TOTAL_GATES = 11

    def evaluate_all_gates(self) -> Dict[str, Any]:
        """Runs checks across all 11 Release 2 release gates."""
        gate_evaluations: Dict[str, Dict[str, Any]] = {}

        # Gate 1: Release 2 Reproducibility Passes
        task_files = list(R2_TASKS_DIR.glob("TASK_R2_*.json"))
        g1_pass = len(task_files) == 300 and R2_MANIFEST_PATH.is_file()
        gate_evaluations["GATE_01_RELEASE2_REPRODUCIBILITY"] = {
            "gate_number": 1,
            "name": "Release 2 Suite Reproducibility",
            "status": "PASS" if g1_pass else "FAIL",
            "details": f"Found {len(task_files)} / 300 task instances and manifest on disk."
        }

        # Gate 2: Release 2 has Zero Invalid Tasks
        g2_pass = False
        invalid_cnt = 999
        if LEAKAGE_JSON.is_file():
            with open(LEAKAGE_JSON, "r", encoding="utf-8") as f:
                ldata = json.load(f)
            invalid_cnt = ldata.get("status_distribution", {}).get("INVALID", 999)
            g2_pass = (invalid_cnt == 0)
        gate_evaluations["GATE_02_ZERO_INVALID_TASKS"] = {
            "gate_number": 2,
            "name": "Zero Invalid Tasks",
            "status": "PASS" if g2_pass else "BLOCKED",
            "details": f"Release 2 contains {invalid_cnt} INVALID tasks (must be exactly 0)."
        }

        # Gate 3: Release 2 has Zero Unresolved Ambiguity
        g3_pass = False
        ambig_cnt = 999
        if DISTRACTOR_JSON.is_file():
            with open(DISTRACTOR_JSON, "r", encoding="utf-8") as f:
                ddata = json.load(f)
            ambig_cnt = ddata.get("ambiguity_items_count", 999)
            g3_pass = (ambig_cnt == 0)
        gate_evaluations["GATE_03_ZERO_UNRESOLVED_AMBIGUITY"] = {
            "gate_number": 3,
            "name": "Zero Unresolved Ambiguity",
            "status": "PASS" if g3_pass else "BLOCKED",
            "details": f"Release 2 contains {ambig_cnt} ambiguous distractor/abstention items (must be 0)."
        }

        # Gate 4: Release 2 Leakage Audit Passes
        g4_pass = LEAKAGE_JSON.is_file()
        gate_evaluations["GATE_04_LEAKAGE_AUDIT_PASSES"] = {
            "gate_number": 4,
            "name": "Release 2 Leakage Audit Complete and Clean",
            "status": "PASS" if (g4_pass and g2_pass) else "FAIL",
            "details": f"Report present and validated: {g4_pass and g2_pass}"
        }

        # Gate 5: Release 2 Distractor Audit Passes
        g5_pass = DISTRACTOR_JSON.is_file() and g3_pass
        gate_evaluations["GATE_05_DISTRACTOR_AUDIT_PASSES"] = {
            "gate_number": 5,
            "name": "Release 2 Distractor Quality Audit Complete",
            "status": "PASS" if g5_pass else "FAIL",
            "details": f"Distractor audit verified with zero collisions: {g5_pass}"
        }

        # Gate 6: Release 2 Corpus Balance Audit Passes
        g6_pass = False
        if BALANCE_JSON.is_file():
            with open(BALANCE_JSON, "r", encoding="utf-8") as f:
                bdata = json.load(f)
            g6_pass = bdata.get("balance_invariants_passed", False)
        gate_evaluations["GATE_06_CORPUS_BALANCE_AUDIT_PASSES"] = {
            "gate_number": 6,
            "name": "Corpus Balance and Diversity Audit Passes",
            "status": "PASS" if g6_pass else "FAIL",
            "details": f"Balance invariants verified (100/100/100): {g6_pass}"
        }

        # Gate 7: Release 2 Blind-Review Package Exists
        manifest_file = R2_PACKAGES_DIR / "blind_sample_manifest.json"
        key_file = R2_PACKAGES_DIR / "author_reconciliation_map.json"
        g7_pass = manifest_file.is_file() and key_file.is_file()
        gate_evaluations["GATE_07_BLIND_REVIEW_PACKAGE_EXISTS"] = {
            "gate_number": 7,
            "name": "Blinded Reviewer Packages Generated",
            "status": "PASS" if g7_pass else "FAIL",
            "details": f"Blinded sample manifest and reconciliation key present: {g7_pass}"
        }

        # Gate 8: Two Independent Review Submissions Required
        sub_files = list(SUBMISSIONS_DIR.glob("*.json")) if SUBMISSIONS_DIR.is_dir() else []
        g8_pass = len(sub_files) >= 2
        gate_evaluations["GATE_08_INDEPENDENT_REVIEW_SUBMISSIONS_REQUIRED"] = {
            "gate_number": 8,
            "name": "Two Independent Human Review Submissions Completed",
            "status": "PASS" if g8_pass else "BLOCKED",
            "details": f"Found {len(sub_files)} / 2 required independent reviewer submission files."
        }

        # Gate 9: Inter-Rater Agreement Threshold Required (kappa >= 0.70)
        g9_pass = False  # Blocked pending human validation
        gate_evaluations["GATE_09_INTER_RATER_AGREEMENT_REQUIRED"] = {
            "gate_number": 9,
            "name": "Inter-Rater Agreement Threshold Met (kappa >= 0.70)",
            "status": "BLOCKED",
            "details": "Requires at least 2 completed human review submissions."
        }

        # Gate 10: Adjudication Log Required
        g10_pass = False  # Blocked pending human validation
        gate_evaluations["GATE_10_ADJUDICATION_LOG_REQUIRED"] = {
            "gate_number": 10,
            "name": "Human Review Discordance Adjudication Log Completed",
            "status": "BLOCKED",
            "details": "Pending human review execution and discordance reconciliation."
        }

        # Gate 11: Final Reviewed Release 2 Manifest Frozen and Hashed
        g11_pass = False  # Blocked pending human validation
        gate_evaluations["GATE_11_FINAL_MANIFEST_FROZEN_AND_HASHED"] = {
            "gate_number": 11,
            "name": "Final Reviewed Manifest Frozen Post-Validation",
            "status": "BLOCKED",
            "details": "Final post-review manifest freeze pending completion of Gates 8-10."
        }

        passed_gates = sum(1 for g in gate_evaluations.values() if g["status"] == "PASS")
        blocked_gates = sum(1 for g in gate_evaluations.values() if g["status"] in ["BLOCKED", "FAIL"])

        operational_state = "MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION"
        model_execution_permitted = (passed_gates == self.TOTAL_GATES)

        summary = {
            "assessment_version": "2.0.0",
            "benchmark_release": "RELEASE_2",
            "total_gates_evaluated": self.TOTAL_GATES,
            "passed_gates_count": passed_gates,
            "blocked_gates_count": blocked_gates,
            "operational_state": operational_state,
            "model_execution_permitted": model_execution_permitted,
            "gates": gate_evaluations
        }

        # Write reports
        with open(GATES_JSON, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)

        self._generate_markdown_report(summary)

        return summary

    def _generate_markdown_report(self, summary: Dict[str, Any]) -> None:
        lines = [
            "# Stage C Release 2 Execution Readiness and Release Gate Report",
            "",
            "## 1. Executive Assessment",
            "",
            f"- **Operational State**: `{summary['operational_state']}`",
            f"- **Model Execution Permitted**: `{summary['model_execution_permitted']}`",
            f"- **Gates Evaluated**: `{summary['total_gates_evaluated']}`",
            f"- **Gates Passed**: `{summary['passed_gates_count']}`",
            f"- **Gates Blocked / Pending**: `{summary['blocked_gates_count']}`",
            "",
            "## 2. Release Gate Verification Matrix",
            "",
            "| Gate # | Release Gate Name | Status | Evaluation Evidence / Findings |",
            "| :---: | :--- | :---: | :--- |",
        ]

        for _, g in sorted(summary["gates"].items(), key=lambda x: x[1]["gate_number"]):
            lines.append(f"| Gate {g['gate_number']:02d} | **{g['name']}** | `{g['status']}` | {g['details']} |")

        lines.extend([
            "",
            "## 3. Operational State Invariants",
            "",
            "1. **Zero Model Execution Before Human Validation**: Model execution remains strictly prohibited",
            "   under state `MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION`.",
            "2. **Independent Review Defense (Pending)**: Heuristic audits do not constitute independent review and independent review remains pending",
            "   dual independent human review with verified inter-rater agreement (\\kappa \\ge 0.70).",
            "3. **Zero Empirical Claims**: Empirical benchmark state is explicitly certified as",
            "   `NO_EMPIRICAL_RESULTS_PRESENT`."
        ])

        with open(GATES_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def assert_model_execution_permitted(self) -> None:
        """Enforces execution blocking with a hard PermissionError exception."""
        status = self.evaluate_all_gates()
        if not status["model_execution_permitted"]:
            blocked_names = [g["name"] for g in status["gates"].values() if g["status"] != "PASS"]
            raise PermissionError(
                f"MODEL EXECUTION FORBIDDEN: Operational state is '{status['operational_state']}'. "
                f"{len(blocked_names)} gates remain blocked: {blocked_names}"
            )


def main():
    enforcer = StageCRelease2ExecutionReadinessEnforcer()
    status = enforcer.evaluate_all_gates()
    print(f"Execution readiness evaluated: {status['operational_state']}")
    print(f"Gates passed: {status['passed_gates_count']} / {status['total_gates_evaluated']}")
    print(f"Reports saved to {GATES_JSON} and {GATES_MD}")


if __name__ == "__main__":
    main()
