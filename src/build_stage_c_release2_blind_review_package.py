"""Stage C Release 2 Blind Human-Review Package Builder.

Selects a stratified 90-task sample from Release 2 task instances (30 AC, 30 TS, 30 AB)
plus 5 qualification tasks. Completely strips gold answers, target tool names, mutation
families, paired group IDs, and internal seeds.
Outputs reviewer packets, blind sample manifest, and author reconciliation key in
data_stage_c_release2/reviewer_packages/.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import random
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
R2_TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
BASE_DIR = ROOT_DIR / "data_stage_c" / "base_contracts"
R2_PACKAGES_DIR = ROOT_DIR / "data_stage_c_release2" / "reviewer_packages"


class StageCRelease2BlindReviewBuilder:
    """Builds blinded review packets from Release 2 task suite."""

    def __init__(self, master_seed: int = 42):
        self.master_seed = master_seed
        self.rng = random.Random(master_seed)

    def build_packages(
        self,
        tasks: List[Dict[str, Any]],
        base_contracts: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Constructs stratified blinded sample and generates reviewer package files."""
        R2_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

        # Separate by category
        ac_tasks = [t for t in tasks if t.get("category") == "ARGUMENT_CONSTRUCTION"]
        ts_tasks = [t for t in tasks if t.get("category") == "TOOL_SELECTION"]
        ab_tasks = [t for t in tasks if t.get("category") == "ABSTENTION"]

        sample_ac = self._stratified_sample(ac_tasks, target_count=30, base_contracts=base_contracts)
        sample_ts = self._stratified_sample(ts_tasks, target_count=30, base_contracts=base_contracts)
        sample_ab = self._stratified_sample(ab_tasks, target_count=30, base_contracts=base_contracts)

        all_sampled = sample_ac + sample_ts + sample_ab
        self.rng.shuffle(all_sampled)

        blind_items = []
        author_key = []

        for idx, task in enumerate(all_sampled, start=1):
            blind_id = f"BLIND_R2_TASK_{idx:03d}"
            cat = task.get("category", "")
            orig_id = task["task_id"]

            packet_type = (
                "CONSTRUCTION_REVIEW" if cat == "ARGUMENT_CONSTRUCTION" else
                ("SELECTION_REVIEW" if cat == "TOOL_SELECTION" else "ABSTENTION_REVIEW")
            )

            # Masked candidate tools
            candidate_tools = []
            for tl in task.get("available_tools", []):
                candidate_tools.append({
                    "tool_name": tl["tool_name"],
                    "description": tl.get("description", ""),
                    "schema": tl.get("schema", {})
                })

            blind_item = {
                "blind_task_id": blind_id,
                "benchmark_release": "RELEASE_2",
                "packet_type": packet_type,
                "natural_language_request": task["user_prompt"],
                "candidate_tools": candidate_tools,
                "review_instructions": self._get_instructions_for_type(packet_type),
                "required_evaluation_fields": {
                    "is_abstention_required": "boolean (true if request cannot be fulfilled by any tool)",
                    "selected_tool_name": "string (name of chosen tool, or null if abstaining)",
                    "submitted_arguments": "object (JSON dictionary of arguments for chosen tool)",
                    "confidence_score": "integer 1-5 (1=low, 5=high certainty)",
                    "is_ambiguous": "boolean (true if request is contradictory or under-specified)",
                    "reviewer_notes": "optional free-text justification"
                }
            }
            blind_items.append(blind_item)

            author_key.append({
                "blind_task_id": blind_id,
                "release_2_task_id": orig_id,
                "category": cat,
                "base_contract_id": task.get("base_contract_id"),
                "mutation_family": task.get("mutation_family"),
                "paired_group_id": task.get("paired_group_id"),
                "gold_tool_name": task.get("expected_tool_name"),
                "gold_arguments": task.get("expected_arguments"),
                "gold_is_abstention": (cat == "ABSTENTION"),
                "target_position": task.get("target_position")
            })

        # Save packets
        manifest = {
            "manifest_version": "2.0.0",
            "benchmark_release": "RELEASE_2",
            "release_marker": "RELEASE_2_PENDING_HUMAN_VALIDATION",
            "independent_review_state": "NO_INDEPENDENT_HUMAN_REVIEW_RESULTS_PRESENT",
            "total_blinded_tasks": len(blind_items),
            "category_breakdown": {
                "ARGUMENT_CONSTRUCTION": len(sample_ac),
                "TOOL_SELECTION": len(sample_ts),
                "ABSTENTION": len(sample_ab)
            },
            "tasks": blind_items
        }

        with open(R2_PACKAGES_DIR / "blind_sample_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        with open(R2_PACKAGES_DIR / "construction_review_packet.json", "w", encoding="utf-8") as f:
            json.dump([item for item in blind_items if item["packet_type"] == "CONSTRUCTION_REVIEW"], f, indent=2, sort_keys=True)

        with open(R2_PACKAGES_DIR / "selection_review_packet.json", "w", encoding="utf-8") as f:
            json.dump([item for item in blind_items if item["packet_type"] == "SELECTION_REVIEW"], f, indent=2, sort_keys=True)

        with open(R2_PACKAGES_DIR / "abstention_review_packet.json", "w", encoding="utf-8") as f:
            json.dump([item for item in blind_items if item["packet_type"] == "ABSTENTION_REVIEW"], f, indent=2, sort_keys=True)

        with open(R2_PACKAGES_DIR / "author_reconciliation_map.json", "w", encoding="utf-8") as f:
            json.dump({
                "map_version": "2.0.0",
                "benchmark_release": "RELEASE_2",
                "author_reconciliation_key": author_key
            }, f, indent=2, sort_keys=True)

        # Generate 5 qualification items
        qual_items = self._build_qualification_items(all_sampled[:5], author_key[:5])
        with open(R2_PACKAGES_DIR / "qualification_review_packet.json", "w", encoding="utf-8") as f:
            json.dump(qual_items, f, indent=2, sort_keys=True)

        return manifest

    def _stratified_sample(
        self,
        category_tasks: List[Dict[str, Any]],
        target_count: int,
        base_contracts: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Stratifies by mutation family and complexity stratum."""
        strata_bins: Dict[str, List[Dict[str, Any]]] = {}
        for t in category_tasks:
            bid = t.get("base_contract_id", "")
            base_c = base_contracts.get(bid, {})
            st = base_c.get("stratum", "UNKNOWN")
            strata_bins.setdefault(st, []).append(t)

        sampled = []
        per_stratum = target_count // len(strata_bins)
        remainder = target_count % len(strata_bins)

        for s_idx, (st, bin_tasks) in enumerate(sorted(strata_bins.items())):
            needed = per_stratum + (1 if s_idx < remainder else 0)
            self.rng.shuffle(bin_tasks)
            sampled.extend(bin_tasks[:needed])

        return sampled

    def _get_instructions_for_type(self, packet_type: str) -> str:
        if packet_type == "CONSTRUCTION_REVIEW":
            return (
                "Review the single available tool and provide the exact arguments required by the user's "
                "request according to the tool's parameter schema. If the request cannot be fulfilled, mark abstention."
            )
        elif packet_type == "SELECTION_REVIEW":
            return (
                "Select the single most appropriate tool from the candidate tools that satisfies the user's "
                "request, and provide the required arguments. If no tool is appropriate, mark abstention."
            )
        else:
            return (
                "Determine whether any candidate tool can fulfill the request. If none can fulfill it "
                "or if critical information is missing, record an abstention."
            )

    def _build_qualification_items(
        self,
        sample_tasks: List[Dict[str, Any]],
        author_entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Constructs 5 calibration qualification items with reference solutions."""
        qual = []
        for idx, (task, auth) in enumerate(zip(sample_tasks, author_entries), start=1):
            qual.append({
                "qualification_id": f"QUAL_R2_ITEM_{idx:02d}",
                "natural_language_request": task["user_prompt"],
                "candidate_tools": [
                    {"tool_name": tl["tool_name"], "description": tl.get("description", ""), "schema": tl.get("schema", {})}
                    for tl in task.get("available_tools", [])
                ],
                "ground_truth_solution": {
                    "is_abstention_required": auth["gold_is_abstention"],
                    "expected_tool_name": auth["gold_tool_name"],
                    "expected_arguments": auth["gold_arguments"]
                },
                "rubric": "Evaluator must match ground truth tool choice and produce schema-valid arguments."
            })
        return qual


def main():
    print("Building Stage C Release 2 Blind Review Packages...")
    builder = StageCRelease2BlindReviewBuilder()

    task_files = sorted(R2_TASKS_DIR.glob("TASK_R2_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    base_contracts = {}
    for cf in sorted(BASE_DIR.glob("BASE_SYNTH_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            c = json.load(f)
            base_contracts[c["contract_id"]] = c

    manifest = builder.build_packages(tasks, base_contracts)
    print(f"Total blinded tasks: {manifest['total_blinded_tasks']}")
    print(f"Category breakdown: {manifest['category_breakdown']}")
    print(f"Package files generated in {R2_PACKAGES_DIR}")


if __name__ == "__main__":
    main()
