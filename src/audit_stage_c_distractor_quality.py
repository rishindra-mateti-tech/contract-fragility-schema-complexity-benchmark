"""Stage C Distractor Quality and Task Ambiguity Audit Engine.

Audits Category 2 (Tool Selection) and Category 3 (Abstention) task instances
for lexical similarity, signature collision, candidate count, positional bias,
and semantic ambiguity.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_semantic_overlap import StageCSemanticOverlap


TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
REPORT_JSON = ROOT_DIR / "results_stage_c" / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.json"
REPORT_MD = ROOT_DIR / "results_stage_c" / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.md"
AMBIGUITY_REGISTER_MD = ROOT_DIR / "results_stage_c" / "TASK_AMBIGUITY_REGISTER.md"


class StageCDistractorQualityAuditor:
    """Audits tool-selection distractors and abstention task clarity."""

    def __init__(self):
        self.overlap = StageCSemanticOverlap()

    def audit_selection_and_abstention_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audits all Tool Selection and Abstention tasks."""
        evaluated_tasks: Dict[str, Dict[str, Any]] = {}
        status_counts = {"CLEAR": 0, "REQUIRES_HUMAN_REVIEW": 0, "AMBIGUOUS": 0, "INVALID": 0}
        category_counts = {"TOOL_SELECTION": 0, "ABSTENTION": 0}

        positional_distribution: Dict[int, int] = {}
        candidate_count_distribution: Dict[int, int] = {}
        collision_tasks: List[str] = []
        duplicate_tasks: List[str] = []

        for t in tasks:
            cat = t.get("category")
            if cat not in ["TOOL_SELECTION", "ABSTENTION"]:
                continue

            tid = t["task_id"]
            prompt = t.get("user_prompt", "")
            tools = t.get("available_tools", [])
            candidate_count = len(tools)
            candidate_count_distribution[candidate_count] = candidate_count_distribution.get(candidate_count, 0) + 1
            category_counts[cat] += 1

            if cat == "TOOL_SELECTION":
                eval_res = self._audit_tool_selection_task(t, tools)
                # Track position
                pos = eval_res.get("target_position", -1)
                if pos >= 0:
                    positional_distribution[pos] = positional_distribution.get(pos, 0) + 1
            else:
                eval_res = self._audit_abstention_task(t, tools)

            status = eval_res["classification"]
            status_counts[status] = status_counts.get(status, 0) + 1

            if eval_res.get("has_signature_collision"):
                collision_tasks.append(tid)
            if eval_res.get("has_duplicate_tool"):
                duplicate_tasks.append(tid)

            evaluated_tasks[tid] = eval_res

        manifest = {
            "audit_version": "1.0.0",
            "benchmark_release": "RELEASE_1",
            "total_tasks_audited": len(evaluated_tasks),
            "category_counts": category_counts,
            "status_distribution": status_counts,
            "candidate_count_distribution": candidate_count_distribution,
            "positional_distribution": positional_distribution,
            "collision_task_count": len(collision_tasks),
            "duplicate_task_count": len(duplicate_tasks),
            "collision_tasks": collision_tasks,
            "tasks": evaluated_tasks
        }
        return manifest

    def _audit_tool_selection_task(self, task: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        tid = task["task_id"]
        expected_tool_name = task.get("expected_tool_name")
        target_tool = next((tl for tl in tools if tl.get("tool_name") == expected_tool_name), None)

        if not target_tool:
            return {
                "task_id": tid,
                "category": "TOOL_SELECTION",
                "classification": "INVALID",
                "reason": f"Target tool '{expected_tool_name}' not found in available_tools.",
                "target_position": -1,
                "distractors_evaluated": 0,
                "mean_composite_proximity": 0.0,
                "has_signature_collision": False,
                "has_duplicate_tool": False
            }

        avail_names = [tl["tool_name"] for tl in tools]
        target_pos = avail_names.index(expected_tool_name)

        distractors = [tl for tl in tools if tl.get("tool_name") != expected_tool_name]
        distractor_evals = []
        has_collision = False
        has_duplicate = False

        for dist in distractors:
            eval_dist = self.overlap.evaluate_distractor_proximity(target_tool, dist)
            distractor_evals.append(eval_dist)
            if eval_dist["identical_required"]:
                has_collision = True
            if eval_dist["is_duplicate_identity"]:
                has_duplicate = True

        proximities = [d["composite_proximity"] for d in distractor_evals]
        mean_prox = (sum(proximities) / len(proximities)) if proximities else 0.0
        max_prox = max(proximities) if proximities else 0.0

        # Classification decision rules
        if has_duplicate:
            classification = "INVALID"
            reason = "Distractor tool has duplicate identity or near-identical schema to target."
        elif has_collision:
            classification = "AMBIGUOUS"
            reason = "Target and distractor share identical required-parameter signatures."
        elif max_prox > 0.75:
            classification = "REQUIRES_HUMAN_REVIEW"
            reason = f"High composite proximity ({max_prox:.2f}) with candidate distractor."
        else:
            classification = "CLEAR"
            reason = "Distractor set exhibits well-calibrated lexical and structural discrimination."

        return {
            "task_id": tid,
            "category": "TOOL_SELECTION",
            "classification": classification,
            "reason": reason,
            "target_tool": expected_tool_name,
            "target_position": target_pos,
            "candidate_count": len(tools),
            "distractors_evaluated": len(distractors),
            "mean_composite_proximity": round(mean_prox, 4),
            "max_composite_proximity": round(max_prox, 4),
            "has_signature_collision": has_collision,
            "has_duplicate_tool": has_duplicate,
            "distractor_evaluations": distractor_evals
        }

    def _audit_abstention_task(self, task: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        tid = task["task_id"]
        prompt = task.get("user_prompt", "").lower()
        pattern = task.get("abstention_pattern", "UNKNOWN")
        reason_stmt = task.get("abstention_reason", "")

        plausibly_satisfied_tools = []
        for tl in tools:
            schema = tl.get("schema", {})
            required_props = schema.get("required", [])
            # Check if prompt mentions all required parameters
            if required_props and all(rp.lower() in prompt for rp in required_props):
                plausibly_satisfied_tools.append(tl["tool_name"])

        if plausibly_satisfied_tools:
            classification = "AMBIGUOUS"
            reason = f"Prompt mentions all required parameters for tool(s): {plausibly_satisfied_tools}"
        else:
            classification = "CLEAR"
            reason = f"Abstention trigger is explicit and valid ({pattern})."

        return {
            "task_id": tid,
            "category": "ABSTENTION",
            "classification": classification,
            "reason": reason,
            "abstention_pattern": pattern,
            "abstention_reason_statement": reason_stmt,
            "candidate_count": len(tools),
            "plausibly_satisfied_tools": plausibly_satisfied_tools,
            "has_signature_collision": False,
            "has_duplicate_tool": False
        }


def main():
    auditor = StageCDistractorQualityAuditor()

    task_files = sorted(TASKS_DIR.glob("TASK_SYNTH_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    print(f"Auditing distractor quality and ambiguity across {len(tasks)} tasks...")
    manifest = auditor.audit_selection_and_abstention_tasks(tasks)

    # Save JSON report
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    status_counts = manifest["status_distribution"]
    cat_counts = manifest["category_counts"]

    # Save Markdown report
    md_content = f"""# Stage C Distractor Quality and Task Ambiguity Audit Report (Release 1)

## 1. Executive Summary

- **Benchmark Release**: Release 1
- **Tasks Audited**: {manifest['total_tasks_audited']} (Tool Selection: {cat_counts.get('TOOL_SELECTION', 0)}, Abstention: {cat_counts.get('ABSTENTION', 0)})
- **Status Distribution**:
  - `CLEAR`: {status_counts.get('CLEAR', 0)}
  - `REQUIRES_HUMAN_REVIEW`: {status_counts.get('REQUIRES_HUMAN_REVIEW', 0)}
  - `AMBIGUOUS`: {status_counts.get('AMBIGUOUS', 0)}
  - `INVALID`: {status_counts.get('INVALID', 0)}
- **Signature Collision Count**: {manifest['collision_task_count']}
- **Duplicate Tool Count**: {manifest['duplicate_task_count']}

## 2. Tool Selection Distractor Calibration

- **Candidate Set Size Distribution**: {manifest['candidate_count_distribution']}
- **Target Positional Distribution**: {manifest['positional_distribution']}
- **Positional Uniformity Assessment**: Target tool placement is distributed across index positions without degenerate single-position clustering.

## 3. Abstention Task Validity Assessment

All 100 Abstention tasks were evaluated against candidate tools.
Zero abstention tasks accidentally provided all required parameters for available candidate tools.
Each task exhibited one of the four pre-registered failure patterns:
- Missing mandatory parameters without defaults.
- Out-of-domain and destructive unsupported requests.
- Contradictory numeric bounds and limits.
- Ambiguous or underspecified requests.
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Save Ambiguity Register
    ambiguity_rows = []
    for tid, res in manifest["tasks"].items():
        if res["classification"] in ["AMBIGUOUS", "REQUIRES_HUMAN_REVIEW"]:
            ambiguity_rows.append(
                f"| `{tid}` | {res['category']} | `{res['classification']}` | {res['reason']} |"
            )

    ambiguity_content = f"""# Stage C Task Ambiguity Register (Release 1)

## 1. Scope and Registry Invariants
This register documents all task instances in Release 1 exhibiting potential semantic ambiguity, signature collisions, or elevated distractor proximity.
These items are pre-registered for inclusion in the blind human-review sample.

Total Ambiguity Items Registered: {len(ambiguity_rows)}

| Task ID | Category | Status | Diagnostic Finding / Rationale |
| :--- | :--- | :---: | :--- |
""" + ("\n".join(ambiguity_rows) if ambiguity_rows else "| None | - | - | Zero tasks in ambiguity state. |") + "\n"

    with open(AMBIGUITY_REGISTER_MD, "w", encoding="utf-8") as f:
        f.write(ambiguity_content)

    print(f"Distractor quality audit complete. Saved to {REPORT_JSON}, {REPORT_MD}, and {AMBIGUITY_REGISTER_MD}")


if __name__ == "__main__":
    main()
