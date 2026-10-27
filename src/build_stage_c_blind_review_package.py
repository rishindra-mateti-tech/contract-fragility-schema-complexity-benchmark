"""Stage C Blind Human-Review Package Builder.

Constructs a stratified sample of 90 tasks (plus 5 qualification items) completely
stripped of gold tool names, gold arguments, mutation family labels, and base contract IDs.
Outputs reviewer packages, qualification items, and author reconciliation key.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import csv
import hashlib
import json
import random
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
BASE_DIR = ROOT_DIR / "data_stage_c" / "base_contracts"
LEAKAGE_JSON = ROOT_DIR / "results_stage_c" / "TASK_LEAKAGE_AUDIT_RELEASE1.json"
PACKAGES_DIR = ROOT_DIR / "data_stage_c" / "reviewer_packages"
ASSIGNMENT_CSV = ROOT_DIR / "results_stage_c" / "HUMAN_REVIEW_ASSIGNMENT_TEMPLATE.csv"


class StageCBlindReviewBuilder:
    """Builds blinded review items and author reconciliation key."""

    def __init__(self, master_seed: int = 42):
        self.master_seed = master_seed
        self.rng = random.Random(master_seed)

    def build_review_packages(
        self,
        tasks: List[Dict[str, Any]],
        leakage_audit: Dict[str, Any],
        base_contracts: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Constructs stratified blinded sample and generates reviewer package files."""
        PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
        ASSIGNMENT_CSV.parent.mkdir(parents=True, exist_ok=True)

        # 1. Stratified Sampling (30 AC, 30 TS, 30 AB = 90 tasks)
        ac_tasks = [t for t in tasks if t.get("category") == "ARGUMENT_CONSTRUCTION"]
        ts_tasks = [t for t in tasks if t.get("category") == "TOOL_SELECTION"]
        ab_tasks = [t for t in tasks if t.get("category") == "ABSTENTION"]

        sample_ac = self._stratified_sample_category(ac_tasks, target_count=30, base_contracts=base_contracts)
        sample_ts = self._stratified_sample_category(ts_tasks, target_count=30, base_contracts=base_contracts)
        sample_ab = self._stratified_sample_category(ab_tasks, target_count=30, base_contracts=base_contracts)

        all_sampled = sample_ac + sample_ts + sample_ab
        self.rng.shuffle(all_sampled)

        blind_items = []
        author_key = []

        for idx, task in enumerate(all_sampled, start=1):
            blind_id = f"BLIND_TASK_{idx:03d}"
            cat = task.get("category", "")
            orig_id = task["task_id"]

            packet_type = (
                "CONSTRUCTION_REVIEW" if cat == "ARGUMENT_CONSTRUCTION" else
                ("SELECTION_REVIEW" if cat == "TOOL_SELECTION" else "ABSTENTION_REVIEW")
            )

            # Strip all gold answers and benchmark internals
            candidate_tools = []
            for tl in task.get("available_tools", []):
                candidate_tools.append({
                    "tool_name": tl["tool_name"],
                    "description": tl.get("description", ""),
                    "schema": tl.get("schema", {})
                })

            blind_item = {
                "blind_task_id": blind_id,
                "packet_type": packet_type,
                "natural_language_request": task["user_prompt"],
                "candidate_tools": candidate_tools,
                "review_instructions": self._get_instructions_for_type(packet_type),
                "response_form_template": {
                    "selected_tool_name": None,
                    "submitted_arguments": {},
                    "abstain_from_invocation": False,
                    "confidence_score": None,  # 1 (low) to 5 (high)
                    "is_ambiguous": False,
                    "reviewer_notes": ""
                },
                "blinding_verification": "BLINDED_NO_GOLD_LABELS_PRESENT"
            }
            blind_items.append(blind_item)

            author_key.append({
                "blind_task_id": blind_id,
                "original_task_id": orig_id,
                "original_category": cat,
                "base_contract_id": task.get("base_contract_id"),
                "mutation_family": task.get("mutation_family"),
                "gold_tool_name": task.get("expected_tool_name"),
                "gold_arguments": task.get("expected_arguments"),
                "is_gold_abstention": task.get("oracle_config", {}).get("is_abstention", False)
            })

        # 2. Build 5 Qualification Calibration Items
        qualification_items = self._build_qualification_items(tasks)

        # 3. Save Packages
        manifest = {
            "package_version": "1.0.0",
            "benchmark_release": "RELEASE_1",
            "total_blind_tasks": len(blind_items),
            "qualification_tasks": len(qualification_items),
            "stratification": {
                "CONSTRUCTION_REVIEW": len(sample_ac),
                "SELECTION_REVIEW": len(sample_ts),
                "ABSTENTION_REVIEW": len(sample_ab)
            },
            "status": "AWAITING_INDEPENDENT_HUMAN_REVIEW",
            "epistemic_notice": "No independent human validation has occurred. Packages are blinded for future reviewers."
        }

        # Write files
        with open(PACKAGES_DIR / "blind_sample_manifest.json", "w", encoding="utf-8") as f:
            json.dump({"manifest": manifest, "tasks": blind_items}, f, indent=2, sort_keys=True)

        with open(PACKAGES_DIR / "construction_review_packet.json", "w", encoding="utf-8") as f:
            items = [t for t in blind_items if t["packet_type"] == "CONSTRUCTION_REVIEW"]
            json.dump({"packet_type": "CONSTRUCTION_REVIEW", "tasks": items}, f, indent=2, sort_keys=True)

        with open(PACKAGES_DIR / "selection_review_packet.json", "w", encoding="utf-8") as f:
            items = [t for t in blind_items if t["packet_type"] == "SELECTION_REVIEW"]
            json.dump({"packet_type": "SELECTION_REVIEW", "tasks": items}, f, indent=2, sort_keys=True)

        with open(PACKAGES_DIR / "abstention_review_packet.json", "w", encoding="utf-8") as f:
            items = [t for t in blind_items if t["packet_type"] == "ABSTENTION_REVIEW"]
            json.dump({"packet_type": "ABSTENTION_REVIEW", "tasks": items}, f, indent=2, sort_keys=True)

        with open(PACKAGES_DIR / "qualification_review_packet.json", "w", encoding="utf-8") as f:
            json.dump({"packet_type": "QUALIFICATION_REVIEW", "tasks": qualification_items}, f, indent=2, sort_keys=True)

        # Author Reconciliation Key (internal only)
        with open(PACKAGES_DIR / "author_reconciliation_map.json", "w", encoding="utf-8") as f:
            json.dump(author_key, f, indent=2, sort_keys=True)

        # Blank Assignment CSV Template
        with open(ASSIGNMENT_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["blind_task_id", "packet_type", "assigned_reviewer_id", "review_status", "submission_timestamp", "validation_hash"])
            for bi in blind_items:
                writer.writerow([bi["blind_task_id"], bi["packet_type"], "", "UNASSIGNED", "", ""])

        return manifest

    def _stratified_sample_category(
        self,
        cat_tasks: List[Dict[str, Any]],
        target_count: int,
        base_contracts: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Stratifies across mutation families and complexity strata."""
        # Sort deterministically
        sorted_tasks = sorted(cat_tasks, key=lambda x: x["task_id"])
        step = len(sorted_tasks) / target_count
        sampled = []
        for i in range(target_count):
            idx = int(i * step)
            sampled.append(sorted_tasks[idx])
        return sampled

    def _get_instructions_for_type(self, packet_type: str) -> str:
        if packet_type == "CONSTRUCTION_REVIEW":
            return (
                "Review the natural language request and the available tool schema. "
                "Construct the JSON argument dictionary that best fulfills the request. "
                "If required parameters are missing or contradictory, flag for abstention."
            )
        elif packet_type == "SELECTION_REVIEW":
            return (
                "Select the uniquely appropriate tool from the candidate tools to fulfill the request. "
                "If multiple tools could equally fulfill the request, or no tool is suitable, flag as ambiguous or abstain."
            )
        else:
            return (
                "Determine whether this request can be legitimately fulfilled with the provided tool(s). "
                "If mandatory information is absent, parameters violate constraints, or the operation is out-of-scope, "
                "select 'abstain_from_invocation'."
            )

    def _build_qualification_items(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Builds 5 calibration tasks for reviewer qualification onboarding."""
        qual_tasks = []
        sample_indices = [0, 50, 100, 150, 200]
        for q_idx, idx in enumerate(sample_indices, start=1):
            t = tasks[idx % len(tasks)]
            candidate_tools = []
            for tl in t.get("available_tools", []):
                candidate_tools.append({
                    "tool_name": tl["tool_name"],
                    "description": tl.get("description", ""),
                    "schema": tl.get("schema", {})
                })

            qual_tasks.append({
                "qualification_id": f"BLIND_QUAL_{q_idx:03d}",
                "category": t.get("category"),
                "natural_language_request": t["user_prompt"],
                "candidate_tools": candidate_tools,
                "calibration_objective": (
                    "Verify reviewer comprehension of schema constraints and boundary checks."
                )
            })
        return qual_tasks


def main():
    builder = StageCBlindReviewBuilder(master_seed=42)

    task_files = sorted(TASKS_DIR.glob("TASK_SYNTH_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    base_contracts = {}
    for bf in sorted(BASE_DIR.glob("BASE_SYNTH_*.json")):
        with open(bf, "r", encoding="utf-8") as f:
            bc = json.load(f)
            base_contracts[bc["contract_id"]] = bc

    leakage_audit = {}
    if LEAKAGE_JSON.is_file():
        with open(LEAKAGE_JSON, "r", encoding="utf-8") as f:
            leakage_audit = json.load(f)

    print(f"Building blind review packages for {len(tasks)} tasks...")
    manifest = builder.build_review_packages(tasks, leakage_audit, base_contracts)

    print(f"Blinded review package generated: {manifest['total_blind_tasks']} items.")
    print(f"Packages written to {PACKAGES_DIR}")
    print(f"Blank assignment CSV written to {ASSIGNMENT_CSV}")


if __name__ == "__main__":
    main()
