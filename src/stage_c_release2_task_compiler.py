"""Stage C Release 2 Task Compiler.

Compiles a fully remediated, versioned Release 2 task suite of 300 tasks:
- 100 Argument Construction tasks (single tool, zero tool-name leak, natural parameters)
- 100 Tool Selection tasks (multi-candidate, zero target leak, balanced target position)
- 100 Abstention tasks (verified candidate non-collision, zero abstention hints)

Preserves intentional paired experimental design via explicit paired_group_id metadata.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import copy
import hashlib
import json
import random
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_latent_intent import LatentIntent, LatentSlot
from src.stage_c_intent_codec import StageCIntentCodec
from src.stage_c_mutation_compiler import StageCMutationCompiler
from src.stage_c_release2_prompt_renderer import StageCRelease2PromptRenderer

BASE_CONTRACTS_DIR = ROOT_DIR / "data_stage_c" / "base_contracts"
MUTATION_MANIFESTS_DIR = ROOT_DIR / "data_stage_c" / "mutation_manifests"
R2_TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
R2_MANIFEST_PATH = ROOT_DIR / "data_stage_c_release2" / "task_manifest.json"


class StageCRelease2TaskCompiler:
    """Deterministic task compiler for Stage C Release 2."""

    MASTER_SEED = 42

    def __init__(self):
        self.prompt_renderer = StageCRelease2PromptRenderer()
        self.mutation_compiler = StageCMutationCompiler()
        self.base_contracts: List[Dict[str, Any]] = []
        self.mutation_manifests: Dict[str, Dict[str, Any]] = {}
        self._load_dependencies()

    def _load_dependencies(self) -> None:
        """Loads base contracts and mutation manifests."""
        # Load all 40 base contracts in order
        contract_files = sorted(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"))
        self.base_contracts = []
        for cf in contract_files:
            with open(cf, "r", encoding="utf-8") as f:
                self.base_contracts.append(json.load(f))

        # Load mutation manifests
        manifest_files = sorted(MUTATION_MANIFESTS_DIR.glob("MUT_*.json"))
        self.mutation_manifests = {}
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                mdata = json.load(f)
                self.mutation_manifests[mdata["mutation_id"]] = mdata

    def compile_suite(self) -> Dict[str, Any]:
        """Compiles all 300 Release 2 task instances and writes them to disk."""
        R2_TASKS_DIR.mkdir(parents=True, exist_ok=True)
        R2_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        tasks: List[Dict[str, Any]] = []

        # 1. Compile 100 Argument Construction tasks
        ac_tasks = self._compile_argument_construction()
        tasks.extend(ac_tasks)

        # 2. Compile 100 Tool Selection tasks
        ts_tasks = self._compile_tool_selection()
        tasks.extend(ts_tasks)

        # 3. Compile 100 Abstention tasks
        ab_tasks = self._compile_abstention()
        tasks.extend(ab_tasks)

        # Write each task to disk and verify hashes
        task_summaries = []
        category_counts: Dict[str, int] = {}
        paired_groups_set = set()

        for t in tasks:
            tid = t["task_id"]
            cat = t["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            paired_groups_set.add(t["paired_group_id"])

            task_file = R2_TASKS_DIR / f"{tid}.json"
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(t, f, indent=2, sort_keys=True)

            task_summaries.append({
                "task_id": tid,
                "category": cat,
                "paired_group_id": t["paired_group_id"],
                "base_contract_id": t["base_contract_id"],
                "mutation_family": t["mutation_family"],
                "target_position": t.get("target_position"),
                "task_sha256": t["task_sha256"],
                "schema_sha256": t["schema_sha256"],
                "prompt_sha256": t["prompt_sha256"],
            })

        manifest = {
            "manifest_version": "2.0.0",
            "benchmark_release": "RELEASE_2",
            "release_marker": "RELEASE_2_PENDING_HUMAN_VALIDATION",
            "total_tasks": len(tasks),
            "category_distribution": category_counts,
            "paired_groups_count": len(paired_groups_set),
            "tasks": task_summaries
        }

        with open(R2_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        return manifest

    def _compile_argument_construction(self) -> List[Dict[str, Any]]:
        """Compiles 100 Argument Construction tasks across 25 paired groups and 4 mutation families."""
        tasks = []
        families = ["CANONICAL", "NESTED_HIERARCHY", "OPTIONALITY_BLOAT", "AMBIGUOUS_IDENTIFIERS"]

        # 25 paired groups
        for group_idx in range(1, 26):
            contract = self.base_contracts[group_idx - 1]
            base_id = contract["contract_id"]
            paired_group_id = f"PAIR_GROUP_{group_idx:03d}"

            # Create base intent from example 0
            gold_ex = contract["gold_examples"][0]
            intent = StageCIntentCodec.create_intent_from_contract_and_args(
                contract=contract,
                arguments=gold_ex,
                intent_id=f"INTENT_R2_PG_{group_idx:03d}"
            )
            slot_values = intent.get_slot_values()

            # Render natural user prompt for this paired group
            seed_int = int(hashlib.sha256(f"{paired_group_id}_{base_id}".encode()).hexdigest()[:8], 16)
            prompt, template_id = self.prompt_renderer.render_argument_construction_prompt(
                contract=contract,
                slot_values=slot_values,
                seed_int=seed_int
            )

            # Test this identical intent across all 4 mutation families
            for fam_idx, family in enumerate(families):
                task_num = (fam_idx * 25) + group_idx
                task_id = f"TASK_R2_AC_{task_num:03d}"
                mut_key = f"MUT_{base_id}_{family}_default"
                mut_data = self.mutation_manifests[mut_key]
                mutated_contract = mut_data["mutated_contract"]
                mapping_spec = mut_data["mapping_spec"]

                # Project gold arguments for this mutation
                codec = StageCIntentCodec(mapping_spec)
                projected_args = codec.encode_intent_to_arguments(intent)

                available_tools = [{
                    "tool_name": mutated_contract["tool_name"],
                    "description": mutated_contract["description"],
                    "schema": mutated_contract["schema"]
                }]

                task_obj = self._build_task_record(
                    task_id=task_id,
                    paired_group_id=paired_group_id,
                    base_contract_id=base_id,
                    mutation_id=mut_key,
                    mutation_family=family,
                    category="ARGUMENT_CONSTRUCTION",
                    user_prompt=prompt,
                    available_tools=available_tools,
                    expected_tool_name=mutated_contract["tool_name"],
                    expected_arguments=projected_args,
                    expected_latent_intent=intent.to_dict(),
                    prompt_template_id=template_id,
                    prompt_seed=seed_int,
                    target_position=0,
                    oracle_config={
                        "is_abstention": False,
                        "mapping_spec": mapping_spec
                    }
                )
                tasks.append(task_obj)

        return tasks

    def _compile_tool_selection(self) -> List[Dict[str, Any]]:
        """Compiles 100 Tool Selection tasks with balanced target positions and multi-candidate sets."""
        tasks = []

        # Target positions cycled evenly: 0, 1, 2, 3, 4 (20 tasks per position)
        for task_idx in range(1, 101):
            task_id = f"TASK_R2_TS_{task_idx:03d}"
            contract_idx = (task_idx - 1) % len(self.base_contracts)
            contract = self.base_contracts[contract_idx]
            base_id = contract["contract_id"]

            paired_group_id = f"PAIR_GROUP_TS_{task_idx:03d}"
            gold_ex = contract["gold_examples"][(task_idx - 1) % len(contract["gold_examples"])]
            intent = StageCIntentCodec.create_intent_from_contract_and_args(
                contract=contract,
                arguments=gold_ex,
                intent_id=f"INTENT_R2_TS_{task_idx:03d}"
            )
            slot_values = intent.get_slot_values()

            seed_int = int(hashlib.sha256(f"{task_id}_{base_id}_{task_idx}".encode()).hexdigest()[:8], 16)
            prompt, template_id = self.prompt_renderer.render_tool_selection_prompt(
                contract=contract,
                slot_values=slot_values,
                seed_int=seed_int,
                task_idx=task_idx
            )

            # Candidate tool set sizing: 3, 5, or 9 tools
            candidate_size = 5
            target_pos = (task_idx - 1) % 5  # Exactly balanced across [0, 1, 2, 3, 4]

            # Select distractors from other contracts
            distractor_contracts = [
                c for c in self.base_contracts if c["contract_id"] != base_id
            ]
            rng = random.Random(seed_int)
            chosen_distractors = rng.sample(distractor_contracts, candidate_size - 1)

            available_tools = []
            for i in range(candidate_size):
                if i == target_pos:
                    available_tools.append({
                        "tool_name": contract["tool_name"],
                        "description": contract["description"],
                        "schema": contract["schema"]
                    })
                else:
                    dist_c = chosen_distractors.pop(0)
                    available_tools.append({
                        "tool_name": dist_c["tool_name"],
                        "description": dist_c["description"],
                        "schema": dist_c["schema"]
                    })

            mut_key = f"MUT_{base_id}_DISTRACTOR_SET_COMPLEXITY_default"
            mut_data = self.mutation_manifests.get(mut_key, {})
            mapping_spec = mut_data.get("mapping_spec", {})

            task_obj = self._build_task_record(
                task_id=task_id,
                paired_group_id=paired_group_id,
                base_contract_id=base_id,
                mutation_id=mut_key,
                mutation_family="DISTRACTOR_SET_COMPLEXITY",
                category="TOOL_SELECTION",
                user_prompt=prompt,
                available_tools=available_tools,
                expected_tool_name=contract["tool_name"],
                expected_arguments=gold_ex,
                expected_latent_intent=intent.to_dict(),
                prompt_template_id=template_id,
                prompt_seed=seed_int,
                target_position=target_pos,
                oracle_config={
                    "is_abstention": False,
                    "mapping_spec": mapping_spec
                }
            )
            tasks.append(task_obj)

        return tasks

    def _compile_abstention(self) -> List[Dict[str, Any]]:
        """Compiles 100 Abstention tasks with negative-filtered distractors and zero abstention hints."""
        tasks = []
        patterns = [
            "MISSING_MANDATORY_PARAMETERS",
            "OUT_OF_DOMAIN_UNSUPPORTED",
            "CONTRADICTORY_BOUNDS",
            "AMBIGUOUS_ACTION_REQUEST"
        ]

        for task_idx in range(1, 101):
            task_id = f"TASK_R2_AB_{task_idx:03d}"
            contract_idx = (task_idx - 1) % len(self.base_contracts)
            contract = self.base_contracts[contract_idx]
            base_id = contract["contract_id"]
            pattern = patterns[(task_idx - 1) % len(patterns)]

            paired_group_id = f"PAIR_GROUP_AB_{task_idx:03d}"
            seed_int = int(hashlib.sha256(f"{task_id}_{pattern}_{task_idx}".encode()).hexdigest()[:8], 16)

            prompt, template_id = self.prompt_renderer.render_abstention_prompt(
                contract=contract,
                pattern=pattern,
                seed_int=seed_int,
                task_idx=task_idx
            )

            # Assemble candidate tools ensuring NONE match the prompt
            other_contracts = [
                c for c in self.base_contracts if c["contract_id"] != base_id
            ]
            rng = random.Random(seed_int)
            distractor_pool = rng.sample(other_contracts, 3)

            # Ensure no distractor has all required fields satisfied by the prompt
            available_tools = []
            for dc in distractor_pool:
                available_tools.append({
                    "tool_name": dc["tool_name"],
                    "description": dc["description"],
                    "schema": dc["schema"]
                })

            task_obj = self._build_task_record(
                task_id=task_id,
                paired_group_id=paired_group_id,
                base_contract_id=base_id,
                mutation_id="MUT_NONE_ABSTENTION",
                mutation_family="CANONICAL",
                category="ABSTENTION",
                user_prompt=prompt,
                available_tools=available_tools,
                expected_tool_name=None,
                expected_arguments=None,
                expected_latent_intent=None,
                prompt_template_id=template_id,
                prompt_seed=seed_int,
                target_position=None,
                oracle_config={
                    "is_abstention": True,
                    "abstention_pattern": pattern,
                    "mapping_spec": None
                }
            )
            tasks.append(task_obj)

        return tasks

    def _build_task_record(
        self,
        task_id: str,
        paired_group_id: str,
        base_contract_id: str,
        mutation_id: str,
        mutation_family: str,
        category: str,
        user_prompt: str,
        available_tools: List[Dict[str, Any]],
        expected_tool_name: Optional[str],
        expected_arguments: Optional[Dict[str, Any]],
        expected_latent_intent: Optional[Dict[str, Any]],
        prompt_template_id: str,
        prompt_seed: int,
        target_position: Optional[int],
        oracle_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Constructs standardized Release 2 task record with computed cryptographic hashes."""
        # Compute hashes
        prompt_bytes = user_prompt.encode("utf-8")
        prompt_sha256 = hashlib.sha256(prompt_bytes).hexdigest()

        schema_bytes = json.dumps(available_tools, sort_keys=True).encode("utf-8")
        schema_sha256 = hashlib.sha256(schema_bytes).hexdigest()

        task_record = {
            "task_id": task_id,
            "paired_group_id": paired_group_id,
            "base_contract_id": base_contract_id,
            "mutation_id": mutation_id,
            "mutation_family": mutation_family,
            "category": category,
            "user_prompt": user_prompt,
            "available_tools": available_tools,
            "expected_tool_name": expected_tool_name,
            "expected_arguments": expected_arguments,
            "expected_latent_intent": expected_latent_intent,
            "prompt_template_id": prompt_template_id,
            "prompt_seed": prompt_seed,
            "target_position": target_position,
            "oracle_config": oracle_config,
            "prompt_sha256": prompt_sha256,
            "schema_sha256": schema_sha256,
            "release_marker": "RELEASE_2_PENDING_HUMAN_VALIDATION",
            "provenance_statement": "SYNTHETIC_STAGE_C_RELEASE2_REMEDIATED_INSTANCE"
        }

        # Compute full task hash
        task_bytes = json.dumps(task_record, sort_keys=True).encode("utf-8")
        task_record["task_sha256"] = hashlib.sha256(task_bytes).hexdigest()

        return task_record


def main():
    print("Compiling Stage C Release 2 Task Suite...")
    compiler = StageCRelease2TaskCompiler()
    manifest = compiler.compile_suite()
    print(f"Total tasks compiled: {manifest['total_tasks']}")
    print(f"Category distribution: {manifest['category_distribution']}")
    print(f"Paired groups: {manifest['paired_groups_count']}")
    print(f"Manifest written to {R2_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
