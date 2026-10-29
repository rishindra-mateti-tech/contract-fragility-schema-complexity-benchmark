"""Stage C Release 2 Task Validator.

Validates the structural integrity, cryptographic consistency, and experimental
invariants of all 300 Release 2 benchmark tasks.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import json
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
R2_TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
R2_MANIFEST_PATH = ROOT_DIR / "data_stage_c_release2" / "task_manifest.json"


class StageCRelease2TaskValidator:
    """Rigorous validator for Release 2 task instances."""

    REQUIRED_FIELDS = [
        "task_id",
        "paired_group_id",
        "base_contract_id",
        "mutation_id",
        "mutation_family",
        "category",
        "user_prompt",
        "available_tools",
        "expected_tool_name",
        "expected_arguments",
        "expected_latent_intent",
        "prompt_template_id",
        "prompt_seed",
        "target_position",
        "oracle_config",
        "prompt_sha256",
        "schema_sha256",
        "task_sha256",
        "release_marker",
        "provenance_statement"
    ]

    FORBIDDEN_ABSTENTION_WORDS = [
        "none of these", "cannot fulfill", "unavailable", "abstain", "no tool matches"
    ]

    def validate_all(self) -> Tuple[bool, List[str]]:
        """Validates all Release 2 tasks on disk against preregistered criteria."""
        errors: List[str] = []

        if not R2_MANIFEST_PATH.is_file():
            errors.append(f"Missing Release 2 manifest at {R2_MANIFEST_PATH}")
            return False, errors

        with open(R2_MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if manifest.get("total_tasks") != 300:
            errors.append(f"Expected 300 tasks in manifest, found {manifest.get('total_tasks')}")

        dist = manifest.get("category_distribution", {})
        if dist.get("ARGUMENT_CONSTRUCTION") != 100 or dist.get("TOOL_SELECTION") != 100 or dist.get("ABSTENTION") != 100:
            errors.append(f"Invalid category distribution: {dist}")

        # Load all tasks
        task_files = sorted(R2_TASKS_DIR.glob("TASK_R2_*.json"))
        if len(task_files) != 300:
            errors.append(f"Expected 300 task files on disk, found {len(task_files)}")

        tasks: List[Dict[str, Any]] = []
        for tf in task_files:
            with open(tf, "r", encoding="utf-8") as f:
                tasks.append(json.load(f))

        # Check per-task properties
        paired_intents: Dict[str, Any] = {}
        cell_prompts: Dict[Tuple[str, str], Set[str]] = {}
        ts_positions: Dict[int, int] = {}

        for t in tasks:
            tid = t.get("task_id", "")
            cat = t.get("category", "")
            mut_fam = t.get("mutation_family", "")
            pg_id = t.get("paired_group_id", "")
            prompt = t.get("user_prompt", "")
            tools = t.get("available_tools", [])
            target = t.get("expected_tool_name")
            target_pos = t.get("target_position")

            # 1. Required fields
            for rf in self.REQUIRED_FIELDS:
                if rf not in t:
                    errors.append(f"Task {tid} missing field '{rf}'")

            # 2. Release marker
            if t.get("release_marker") != "RELEASE_2_PENDING_HUMAN_VALIDATION":
                errors.append(f"Task {tid} invalid release marker: {t.get('release_marker')}")

            # 3. Hash integrity
            prompt_bytes = prompt.encode("utf-8")
            if hashlib.sha256(prompt_bytes).hexdigest() != t.get("prompt_sha256"):
                errors.append(f"Task {tid} prompt_sha256 mismatch")

            schema_bytes = json.dumps(tools, sort_keys=True).encode("utf-8")
            if hashlib.sha256(schema_bytes).hexdigest() != t.get("schema_sha256"):
                errors.append(f"Task {tid} schema_sha256 mismatch")

            task_copy = dict(t)
            orig_task_sha = task_copy.pop("task_sha256", None)
            recomputed_task_sha = hashlib.sha256(json.dumps(task_copy, sort_keys=True).encode("utf-8")).hexdigest()
            if orig_task_sha != recomputed_task_sha:
                errors.append(f"Task {tid} task_sha256 mismatch")

            # 4. Intra-cell uniqueness
            cell_key = (cat, mut_fam)
            seen_prompts = cell_prompts.setdefault(cell_key, set())
            if prompt in seen_prompts:
                errors.append(f"Task {tid} has duplicate prompt inside cell {cell_key}")
            seen_prompts.add(prompt)

            # 5. Paired group intent consistency
            if pg_id and t.get("expected_latent_intent"):
                intent_hash = t["expected_latent_intent"].get("intent_hash")
                if pg_id in paired_intents:
                    if paired_intents[pg_id] != intent_hash:
                        errors.append(f"Task {tid} in paired group {pg_id} has conflicting intent hash")
                else:
                    paired_intents[pg_id] = intent_hash

            # 6. Category-specific validations
            if cat == "ARGUMENT_CONSTRUCTION":
                if len(tools) != 1:
                    errors.append(f"Task {tid} (AC) should have exactly 1 available tool, found {len(tools)}")
                # Tool name omission
                if target and target.lower() in prompt.lower():
                    errors.append(f"Task {tid} (AC) prompt leaks tool name '{target}'")
                # Verbatim snake_case keys omission
                tool_schema = tools[0].get("schema", {}) if tools else {}
                for k in tool_schema.get("properties", {}).keys():
                    if "_" in k and len(k) > 4:
                        if re.search(r"\b" + re.escape(k.lower()) + r"\b", prompt.lower()):
                            errors.append(f"Task {tid} (AC) leaks snake_case key '{k}'")

            elif cat == "TOOL_SELECTION":
                if len(tools) < 3:
                    errors.append(f"Task {tid} (TS) should have >= 3 candidate tools, found {len(tools)}")
                if target and target.lower() in prompt.lower():
                    errors.append(f"Task {tid} (TS) prompt leaks target tool name '{target}'")
                avail_names = [tl["tool_name"] for tl in tools]
                if target not in avail_names:
                    errors.append(f"Task {tid} (TS) target '{target}' not in candidate tools")
                elif target_pos is not None and avail_names.index(target) != target_pos:
                    errors.append(f"Task {tid} (TS) target position mismatch: {avail_names.index(target)} vs {target_pos}")
                if target_pos is not None:
                    ts_positions[target_pos] = ts_positions.get(target_pos, 0) + 1

            elif cat == "ABSTENTION":
                if t.get("expected_tool_name") is not None or t.get("expected_arguments") is not None:
                    errors.append(f"Task {tid} (AB) should have null expected tool and arguments")
                if not t.get("oracle_config", {}).get("is_abstention"):
                    errors.append(f"Task {tid} (AB) oracle_config.is_abstention must be True")
                for fw in self.FORBIDDEN_ABSTENTION_WORDS:
                    if fw in prompt.lower():
                        errors.append(f"Task {tid} (AB) prompt contains forbidden abstention word '{fw}'")

        # 7. Positional uniformity check across Tool Selection
        if len(ts_positions) > 0:
            counts = list(ts_positions.values())
            max_c = max(counts)
            min_c = min(counts)
            if max_c - min_c > 10:
                errors.append(f"Tool Selection target positions skewed: {ts_positions}")

        return (len(errors) == 0), errors


def main():
    print("Validating Stage C Release 2 Task Suite...")
    validator = StageCRelease2TaskValidator()
    ok, errors = validator.validate_all()
    if not ok:
        print(f"FAILED: {len(errors)} validation errors found:")
        for e in errors[:10]:
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more.")
        sys.exit(1)
    print("SUCCESS: All 300 Release 2 tasks pass all validation checks.")


if __name__ == "__main__":
    main()
