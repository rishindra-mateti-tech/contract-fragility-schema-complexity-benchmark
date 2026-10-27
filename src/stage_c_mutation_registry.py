"""Stage C Mutation Registry.

Compiles, validates, persists, and indexes all controlled mutations derived
from the synthetic base contract corpus.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_mutation_compiler import StageCMutationCompiler, MutationResult
from src.stage_c_mutation_validator import StageCMutationValidator


ROOT_DIR = Path(__file__).resolve().parent.parent
BASE_CONTRACTS_DIR = ROOT_DIR / "data_stage_c" / "base_contracts"
MUTATIONS_DIR = ROOT_DIR / "data_stage_c" / "mutation_manifests"
REGISTRY_PATH = ROOT_DIR / "results_stage_c" / "MUTATION_REGISTRY.json"


class StageCMutationRegistry:
    """Registry managing compiled mutations and cataloging them."""

    def __init__(self):
        self.compiler = StageCMutationCompiler()
        self.validator = StageCMutationValidator()
        self.mutations: Dict[str, MutationResult] = {}

    def build_registry(self) -> Dict[str, Any]:
        """Compiles and validates mutations across all base contracts."""
        MUTATIONS_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

        contract_files = sorted(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"))
        base_contracts = []
        for cf in contract_files:
            with open(cf, "r", encoding="utf-8") as f:
                base_contracts.append(json.load(f))

        registry_entries = []
        family_counts = {fam: 0 for fam in self.compiler.MUTATION_FAMILIES}

        for base_contract in base_contracts:
            for family in self.compiler.MUTATION_FAMILIES:
                res = self.compiler.compile_mutation(
                    base_contract=base_contract,
                    family=family,
                    variant="default",
                    all_contracts=base_contracts
                )

                is_valid, errors = self.validator.validate_mutation(res, base_contract)
                if not is_valid:
                    raise ValueError(f"Mutation {res.mutation_id} validation failed: {errors}")

                # Save individual mutation manifest
                mutation_file = MUTATIONS_DIR / f"{res.mutation_id}.json"
                with open(mutation_file, "w", encoding="utf-8") as f:
                    json.dump(res.to_dict(), f, indent=2, sort_keys=True)

                self.mutations[res.mutation_id] = res
                family_counts[family] += 1

                registry_entries.append({
                    "mutation_id": res.mutation_id,
                    "base_contract_id": res.base_contract_id,
                    "family": res.family,
                    "variant": res.variant,
                    "relative_path": f"data_stage_c/mutation_manifests/{res.mutation_id}.json",
                    "distractor_count": len(res.distractor_tools),
                    "provenance_statement": res.provenance_statement,
                })

        manifest = {
            "registry_version": "1.0.0",
            "total_mutations": len(registry_entries),
            "base_contracts_covered": len(base_contracts),
            "family_distribution": family_counts,
            "mutations": registry_entries
        }

        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        return manifest


def main():
    registry = StageCMutationRegistry()
    manifest = registry.build_registry()
    print(f"Compiled and validated {manifest['total_mutations']} mutations.")
    print(f"Registry written to {REGISTRY_PATH}")


if __name__ == "__main__":
    main()
