"""Stage C Release 2 Distractor Quality and Ambiguity Audit Engine.

Audits all 100 Tool Selection tasks and 100 Abstention tasks in Release 2:
- Evaluates candidate set sizes and target positional uniformity.
- Checks lexical and structural proximity between target tool and distractors.
- Verifies zero signature collisions and zero duplicate tool identities.
- Verifies that zero abstention tasks have candidate tools matching prompt parameters.
- Generates RELEASE2_DISTRACTOR_QUALITY_AUDIT.json and RELEASE2_AMBIGUITY_REGISTER.md.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
REPORT_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_DISTRACTOR_QUALITY_AUDIT.json"
AMBIGUITY_REGISTER_MD = ROOT_DIR / "results_stage_c" / "RELEASE2_AMBIGUITY_REGISTER.md"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_semantic_overlap import StageCSemanticOverlap


class StageCRelease2DistractorAuditor:
    """Audits distractor quality and candidate calibration for Release 2."""

    def __init__(self):
        self.overlap = StageCSemanticOverlap()

    def audit_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs distractor calibration and ambiguity audit across TS and AB tasks."""
        evaluated_tasks: Dict[str, Dict[str, Any]] = {}
        status_counts = {"CLEAR": 0, "REQUIRES_HUMAN_REVIEW": 0, "AMBIGUOUS": 0, "INVALID": 0}
        category_counts = {"TOOL_SELECTION": 0, "ABSTENTION": 0}

        positional_distribution: Dict[int, int] = {}
        candidate_count_distribution: Dict[int, int] = {}
        ambiguity_items: List[Dict[str, Any]] = []

        for t in tasks:
            cat = t.get("category")
            if cat not in ["TOOL_SELECTION", "ABSTENTION"]:
                continue

            tid = t["task_id"]
            tools = t.get("available_tools", [])
            cand_count = len(tools)
            candidate_count_distribution[cand_count] = candidate_count_distribution.get(cand_count, 0) + 1
            category_counts[cat] += 1

            if cat == "TOOL_SELECTION":
                eval_res = self._audit_selection_task(t, tools)
                pos = eval_res.get("target_position", -1)
                if pos >= 0:
                    positional_distribution[pos] = positional_distribution.get(pos, 0) + 1
            else:  # ABSTENTION
                eval_res = self._audit_abstention_task(t, tools)

            stat = eval_res["classification"]
            status_counts[stat] += 1
            evaluated_tasks[tid] = eval_res

            if stat in ["AMBIGUOUS", "INVALID"]:
                ambiguity_items.append({
                    "task_id": tid,
                    "category": cat,
                    "status": stat,
                    "rationale": eval_res["reason"]
                })

        report = {
            "audit_version": "2.0.0",
            "benchmark_release": "RELEASE_2",
            "total_tasks_audited": len(evaluated_tasks),
            "category_distribution": category_counts,
            "status_distribution": status_counts,
            "positional_distribution": {str(k): v for k, v in sorted(positional_distribution.items())},
            "candidate_count_distribution": {str(k): v for k, v in sorted(candidate_count_distribution.items())},
            "ambiguity_items_count": len(ambiguity_items),
            "ambiguity_items": ambiguity_items,
            "evaluated_tasks": evaluated_tasks
        }

        with open(REPORT_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)

        self._generate_ambiguity_register(ambiguity_items)

        return report

    def _audit_selection_task(self, task: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        tid = task["task_id"]
        expected_tool_name = task.get("expected_tool_name")
        target_pos = task.get("target_position")

        target_tool = next((tl for tl in tools if tl.get("tool_name") == expected_tool_name), None)
        if not target_tool:
            return {
                "task_id": tid,
                "category": "TOOL_SELECTION",
                "classification": "INVALID",
                "reason": f"Expected tool '{expected_tool_name}' not found in candidate tools.",
                "target_position": target_pos
            }

        distractors = [tl for tl in tools if tl.get("tool_name") != expected_tool_name]
        distractor_evals = []
        has_collision = False
        has_duplicate = False

        for dist in distractors:
            eval_dist = self.overlap.evaluate_distractor_proximity(target_tool, dist)
            distractor_evals.append(eval_dist)
            if eval_dist.get("identical_required"):
                has_collision = True
            if eval_dist.get("is_duplicate_identity"):
                has_duplicate = True

        proximities = [d.get("composite_proximity", 0.0) for d in distractor_evals]
        mean_prox = (sum(proximities) / len(proximities)) if proximities else 0.0
        max_prox = max(proximities) if proximities else 0.0

        if has_duplicate:
            classification = "INVALID"
            reason = "Distractor tool has duplicate identity or schema to target tool."
        elif has_collision:
            classification = "AMBIGUOUS"
            reason = "Target and distractor share identical required-parameter signatures."
        elif max_prox > 0.85:
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
            "mean_composite_proximity": round(mean_prox, 4),
            "max_composite_proximity": round(max_prox, 4),
            "has_signature_collision": has_collision,
            "has_duplicate_tool": has_duplicate
        }

    def _audit_abstention_task(self, task: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        tid = task["task_id"]
        prompt = task.get("user_prompt", "").lower()
        oracle_conf = task.get("oracle_config", {})
        pattern = oracle_conf.get("abstention_pattern", "UNKNOWN")

        plausibly_satisfied = []
        for tl in tools:
            schema = tl.get("schema", {})
            req_props = schema.get("required", [])
            if req_props and all(re.search(r"\b" + re.escape(rp.lower()) + r"\b", prompt) for rp in req_props):
                plausibly_satisfied.append(tl["tool_name"])

        if plausibly_satisfied:
            classification = "AMBIGUOUS"
            reason = f"Prompt mentions all required parameters for candidate tool(s): {plausibly_satisfied}"
        else:
            classification = "CLEAR"
            reason = f"Abstention trigger is explicit and valid ({pattern})."

        return {
            "task_id": tid,
            "category": "ABSTENTION",
            "classification": classification,
            "reason": reason,
            "abstention_pattern": pattern,
            "candidate_count": len(tools),
            "plausibly_satisfied_tools": plausibly_satisfied,
            "has_signature_collision": False,
            "has_duplicate_tool": False
        }

    def _generate_ambiguity_register(self, ambiguity_items: List[Dict[str, Any]]) -> None:
        """Generates markdown ambiguity register for Release 2."""
        lines = [
            "# Stage C Release 2 Task Ambiguity Register",
            "",
            "## 1. Scope and Registry Invariants",
            "",
            "This register records any task instances in Release 2 exhibiting potential semantic ambiguity,",
            "signature collisions, or elevated distractor proximity. Release 2 quality gates require zero",
            "unresolved invalid or ambiguous items.",
            "",
            f"Total Ambiguity Items Registered: `{len(ambiguity_items)}`",
            "",
        ]

        if ambiguity_items:
            lines.extend([
                "| Task ID | Category | Status | Diagnostic Finding / Rationale |",
                "| :--- | :--- | :---: | :--- |",
            ])
            for item in ambiguity_items:
                lines.append(f"| `{item['task_id']}` | {item['category']} | `{item['status']}` | {item['rationale']} |")
        else:
            lines.extend([
                "Zero ambiguous or invalid distractor tasks detected in Release 2.",
                "All 100 Tool Selection tasks possess clean distractor separation without signature collisions.",
                "All 100 Abstention tasks possess verified negative candidate toolsets without accidental validity."
            ])

        with open(AMBIGUITY_REGISTER_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def main():
    print("Running Stage C Release 2 Distractor Quality and Ambiguity Audit...")
    auditor = StageCRelease2DistractorAuditor()
    task_files = sorted(TASKS_DIR.glob("TASK_R2_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    report = auditor.audit_tasks(tasks)
    dist = report["status_distribution"]
    print(f"Audited {report['total_tasks_audited']} tasks across TS and AB:")
    print(f"  CLEAR: {dist.get('CLEAR', 0)}")
    print(f"  REQUIRES_HUMAN_REVIEW: {dist.get('REQUIRES_HUMAN_REVIEW', 0)}")
    print(f"  AMBIGUOUS: {dist.get('AMBIGUOUS', 0)}")
    print(f"  INVALID: {dist.get('INVALID', 0)}")
    print(f"Positional distribution: {report['positional_distribution']}")
    print(f"Reports written to {REPORT_JSON} and {AMBIGUITY_REGISTER_MD}")


if __name__ == "__main__":
    main()
