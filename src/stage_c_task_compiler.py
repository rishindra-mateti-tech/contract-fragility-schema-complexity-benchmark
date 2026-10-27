"""Stage C Task Compiler.

Compiles at least 300 standardized benchmark task instances across three categories:
1. ARGUMENT_CONSTRUCTION (100 instances)
2. TOOL_SELECTION (100 instances with distractor tools)
3. ABSTENTION (100 instances with unfulfillable / missing parameter requests)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import copy
import hashlib
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_latent_intent import LatentIntent, LatentSlot
from src.stage_c_intent_codec import StageCIntentCodec
from src.stage_c_mutation_compiler import StageCMutationCompiler
from src.stage_c_prompt_renderer import StageCPromptRenderer


TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
MANIFEST_PATH = ROOT_DIR / "results_stage_c" / "TASK_SET_MANIFEST.json"


class StageCTaskCompiler:
    """Compiles gold task instances for the Stage C evaluation harness."""

    def __init__(self):
        self.prompt_renderer = StageCPromptRenderer()
        self.mutation_compiler = StageCMutationCompiler()

    def compile_all_tasks(
        self,
        base_contracts: List[Dict[str, Any]],
        mutation_manifests: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compiles 300 task instances (100 AC, 100 TS, 100 AB) and writes to disk."""
        TASKS_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        task_records = []
        category_counts = {
            "ARGUMENT_CONSTRUCTION": 0,
            "TOOL_SELECTION": 0,
            "ABSTENTION": 0
        }

        # 1. Compile 100 Argument Construction Tasks
        ac_tasks = self._compile_argument_construction_tasks(base_contracts, mutation_manifests)
        for t in ac_tasks:
            self._save_task(t)
            task_records.append(self._summarize_task(t))
            category_counts["ARGUMENT_CONSTRUCTION"] += 1

        # 2. Compile 100 Tool Selection Tasks
        ts_tasks = self._compile_tool_selection_tasks(base_contracts, mutation_manifests)
        for t in ts_tasks:
            self._save_task(t)
            task_records.append(self._summarize_task(t))
            category_counts["TOOL_SELECTION"] += 1

        # 3. Compile 100 Abstention Tasks
        ab_tasks = self._compile_abstention_tasks(base_contracts, mutation_manifests)
        for t in ab_tasks:
            self._save_task(t)
            task_records.append(self._summarize_task(t))
            category_counts["ABSTENTION"] += 1

        manifest = {
            "manifest_version": "1.0.0",
            "total_tasks": len(task_records),
            "category_distribution": category_counts,
            "tasks": task_records
        }

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        return manifest

    def _compile_argument_construction_tasks(
        self,
        base_contracts: List[Dict[str, Any]],
        mutation_manifests: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generates 100 Argument Construction tasks testing argument formatting under schema variants."""
        tasks = []
        task_idx = 1

        # Loop through base contracts with varying mutations
        mutation_rotation = ["CANONICAL", "NESTED_HIERARCHY", "OPTIONALITY_BLOAT", "AMBIGUOUS_IDENTIFIERS"]

        while len(tasks) < 100:
            contract_idx = (task_idx - 1) % len(base_contracts)
            contract = base_contracts[contract_idx]
            base_id = contract["contract_id"]

            mut_family = mutation_rotation[(task_idx - 1) % len(mutation_rotation)]
            mut_key = f"MUT_{base_id}_{mut_family}_default"
            mut_data = mutation_manifests.get(mut_key)

            if not mut_data:
                continue

            mutated_contract = mut_data["mutated_contract"]
            mapping_spec = mut_data["mapping_spec"]
            gold_examples = mutated_contract.get("gold_examples", [])
            gold_args = gold_examples[(task_idx - 1) % len(gold_examples)]

            # Construct intent
            intent = StageCIntentCodec.create_intent_from_contract_and_args(
                contract=contract,
                arguments=contract["gold_examples"][(task_idx - 1) % len(contract["gold_examples"])],
                intent_id=f"INTENT_AC_{task_idx:03d}"
            )

            # Generate natural language prompt
            slot_descriptions = [f"{k} set to {v!r}" for k, v in intent.get_slot_values().items()]
            prompt = (
                f"Please execute the {contract['tool_name']} operation for {contract['title']}. "
                f"Specific parameters required: {', '.join(slot_descriptions)}."
            )

            task = {
                "task_id": f"TASK_SYNTH_AC_{task_idx:03d}",
                "category": "ARGUMENT_CONSTRUCTION",
                "base_contract_id": base_id,
                "mutation_id": mut_key,
                "mutation_family": mut_family,
                "user_prompt": prompt,
                "expected_tool_name": contract["tool_name"],
                "expected_arguments": gold_args,
                "expected_latent_intent": intent.to_dict(),
                "available_tools": [{
                    "tool_name": mutated_contract["tool_name"],
                    "description": mutated_contract["description"],
                    "schema": mutated_contract["schema"]
                }],
                "oracle_config": {
                    "is_abstention": False,
                    "mapping_spec": mapping_spec
                },
                "provenance_statement": "SYNTHETIC_STAGE_C_GOLD_TASK_INSTANCE"
            }
            tasks.append(task)
            task_idx += 1

        return tasks

    def _compile_tool_selection_tasks(
        self,
        base_contracts: List[Dict[str, Any]],
        mutation_manifests: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generates 100 Tool Selection tasks testing target tool discrimination amidst distractors."""
        tasks = []
        task_idx = 1

        while len(tasks) < 100:
            contract_idx = (task_idx - 1) % len(base_contracts)
            contract = base_contracts[contract_idx]
            base_id = contract["contract_id"]

            mut_key = f"MUT_{base_id}_DISTRACTOR_SET_COMPLEXITY_default"
            mut_data = mutation_manifests.get(mut_key)

            if not mut_data:
                continue

            mutated_contract = mut_data["mutated_contract"]
            distractors = mut_data.get("distractor_tools", [])
            gold_args = mutated_contract["gold_examples"][(task_idx - 1) % len(mutated_contract["gold_examples"])]

            intent = StageCIntentCodec.create_intent_from_contract_and_args(
                contract=contract,
                arguments=contract["gold_examples"][(task_idx - 1) % len(contract["gold_examples"])],
                intent_id=f"INTENT_TS_{task_idx:03d}"
            )

            # Assemble candidate tool set (target tool + distractors)
            target_tool_decl = {
                "tool_name": mutated_contract["tool_name"],
                "description": mutated_contract["description"],
                "schema": mutated_contract["schema"]
            }
            available_tools = [target_tool_decl] + distractors
            # Sort deterministically by tool name to prevent positional bias
            available_tools.sort(key=lambda x: x["tool_name"])

            slot_descriptions = [f"{k} as {v!r}" for k, v in intent.get_slot_values().items()]
            prompt = (
                f"We need to perform the following action: {contract['description']}. "
                f"Configure the action with: {', '.join(slot_descriptions)}."
            )

            task = {
                "task_id": f"TASK_SYNTH_TS_{task_idx:03d}",
                "category": "TOOL_SELECTION",
                "base_contract_id": base_id,
                "mutation_id": mut_key,
                "mutation_family": "DISTRACTOR_SET_COMPLEXITY",
                "user_prompt": prompt,
                "expected_tool_name": contract["tool_name"],
                "expected_arguments": gold_args,
                "expected_latent_intent": intent.to_dict(),
                "available_tools": available_tools,
                "oracle_config": {
                    "is_abstention": False,
                    "mapping_spec": mut_data["mapping_spec"]
                },
                "provenance_statement": "SYNTHETIC_STAGE_C_GOLD_TASK_INSTANCE"
            }
            tasks.append(task)
            task_idx += 1

        return tasks

    def _compile_abstention_tasks(
        self,
        base_contracts: List[Dict[str, Any]],
        mutation_manifests: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generates 100 Abstention tasks testing model restraint when requests are unfulfillable."""
        tasks = []
        task_idx = 1

        abstention_patterns = [
            "MISSING_MANDATORY_PARAMETERS",
            "OUT_OF_DOMAIN_UNSUPPORTED",
            "CONTRADICTORY_BOUNDS",
            "AMBIGUOUS_ACTION_REQUEST"
        ]

        while len(tasks) < 100:
            contract_idx = (task_idx - 1) % len(base_contracts)
            contract = base_contracts[contract_idx]
            base_id = contract["contract_id"]

            pattern = abstention_patterns[(task_idx - 1) % len(abstention_patterns)]
            required_fields = contract.get("schema", {}).get("required", [])

            if pattern == "MISSING_MANDATORY_PARAMETERS":
                # Prompt requests operation but omits required fields
                prompt = (
                    f"Perform {contract['tool_name']} immediately. "
                    f"Do not ask any clarifying questions, but no parameter details are provided."
                )
                reason = f"Request lacks mandatory parameters: {required_fields}"
            elif pattern == "OUT_OF_DOMAIN_UNSUPPORTED":
                # Prompt requests an unsupported operation
                prompt = (
                    f"Purge and permanently drop all underlying system databases and raw storage partitions "
                    f"associated with {contract['title']}."
                )
                reason = "Requested destructive action is not supported by available tool definitions."
            elif pattern == "CONTRADICTORY_BOUNDS":
                # Request violates mathematical limits
                prompt = (
                    f"Execute {contract['tool_name']} with negative count -99999 and infinite retries."
                )
                reason = "Requested parameters violate schema numeric constraints and boundary checks."
            else:
                # Ambiguous
                prompt = (
                    f"Modify the configuration for {contract['title']} to match unknown legacy system settings."
                )
                reason = "Instruction is completely ambiguous with no actionable parameter data."

            tool_decl = {
                "tool_name": contract["tool_name"],
                "description": contract["description"],
                "schema": contract["schema"]
            }

            task = {
                "task_id": f"TASK_SYNTH_AB_{task_idx:03d}",
                "category": "ABSTENTION",
                "base_contract_id": base_id,
                "mutation_id": f"MUT_{base_id}_CANONICAL_default",
                "mutation_family": "CANONICAL",
                "abstention_pattern": pattern,
                "abstention_reason": reason,
                "user_prompt": prompt,
                "expected_tool_name": None,
                "expected_arguments": None,
                "expected_latent_intent": None,
                "available_tools": [tool_decl],
                "oracle_config": {
                    "is_abstention": True
                },
                "provenance_statement": "SYNTHETIC_STAGE_C_GOLD_TASK_INSTANCE"
            }
            tasks.append(task)
            task_idx += 1

        return tasks

    def _save_task(self, task: Dict[str, Any]) -> None:
        task_id = task["task_id"]
        filepath = TASKS_DIR / f"{task_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2, sort_keys=True)

    def _summarize_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task["task_id"]
        filepath = TASKS_DIR / f"{task_id}.json"
        with open(filepath, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()

        return {
            "task_id": task_id,
            "category": task["category"],
            "base_contract_id": task["base_contract_id"],
            "mutation_id": task["mutation_id"],
            "relative_path": f"data_stage_c/task_instances/{task_id}.json",
            "sha256": digest,
            "tool_count": len(task["available_tools"]),
            "is_abstention": task["oracle_config"]["is_abstention"],
            "provenance_statement": task["provenance_statement"]
        }


def main():
    compiler = StageCTaskCompiler()

    # Load base contracts
    base_contracts = []
    for cf in sorted((ROOT_DIR / "data_stage_c" / "base_contracts").glob("BASE_SYNTH_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            base_contracts.append(json.load(f))

    # Load mutation manifests
    mutation_manifests = {}
    for mf in sorted((ROOT_DIR / "data_stage_c" / "mutation_manifests").glob("MUT_*.json")):
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)
            mutation_manifests[data["mutation_id"]] = data

    manifest = compiler.compile_all_tasks(base_contracts, mutation_manifests)
    print(f"Compiled and saved {manifest['total_tasks']} tasks.")
    print(f"Manifest written to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
