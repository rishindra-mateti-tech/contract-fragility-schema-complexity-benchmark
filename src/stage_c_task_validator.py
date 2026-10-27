"""Stage C Task Validator.

Validates integrity, schema adherence, lack of gold leakage, and correctness
of Stage C benchmark task instances.
"""

from typing import Any, Dict, List, Tuple
import jsonschema

from src.stage_c_prompt_renderer import StageCPromptRenderer


class StageCTaskValidator:
    """Validates structural and adversarial integrity of task instances."""

    VALID_CATEGORIES = ["ARGUMENT_CONSTRUCTION", "TOOL_SELECTION", "ABSTENTION"]

    def __init__(self):
        self.draft7_validator_cls = jsonschema.Draft7Validator

    def validate_task(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Performs multi-point validation on a single task instance."""
        errors: List[str] = []

        # 1. Structural Field Checks
        required_fields = [
            "task_id", "category", "base_contract_id", "mutation_id",
            "user_prompt", "available_tools", "oracle_config", "provenance_statement"
        ]
        for f in required_fields:
            if f not in task:
                errors.append(f"Missing required task field: '{f}'")

        category = task.get("category")
        if category not in self.VALID_CATEGORIES:
            errors.append(f"Invalid category '{category}'. Must be in {self.VALID_CATEGORIES}")

        # 2. Available Tools Schema Validation
        tools = task.get("available_tools", [])
        if not tools:
            errors.append("Task defines zero available tools.")

        tool_names = set()
        for idx, t in enumerate(tools):
            name = t.get("tool_name")
            if not name:
                errors.append(f"Tool at index {idx} has missing or empty tool_name.")
            tool_names.add(name)

            schema = t.get("schema", {})
            try:
                self.draft7_validator_cls.check_schema(schema)
            except jsonschema.SchemaError as err:
                errors.append(f"Tool '{name}' schema is not valid Draft-07: {err.message}")

        # 3. Category-Specific Validation
        prompt = task.get("user_prompt", "")
        oracle_cfg = task.get("oracle_config", {})

        if category in ["ARGUMENT_CONSTRUCTION", "TOOL_SELECTION"]:
            expected_tool = task.get("expected_tool_name")
            expected_args = task.get("expected_arguments")

            if expected_tool not in tool_names:
                errors.append(f"Expected tool '{expected_tool}' is not in available_tools: {tool_names}")

            if expected_args is None or not isinstance(expected_args, dict):
                errors.append(f"Task category '{category}' requires non-null expected_arguments dictionary.")
            else:
                # Find target tool schema and validate expected_args
                target_decl = next((t for t in tools if t.get("tool_name") == expected_tool), None)
                if target_decl:
                    try:
                        jsonschema.validate(expected_args, target_decl.get("schema", {}))
                    except jsonschema.ValidationError as val_err:
                        errors.append(f"expected_arguments failed schema validation for tool '{expected_tool}': {val_err.message}")

            # Check prompt leakage
            leakages = StageCPromptRenderer.check_for_gold_leakage(prompt, expected_args)
            if leakages:
                errors.extend(leakages)

            if oracle_cfg.get("is_abstention") is not False:
                errors.append(f"Task category '{category}' must have oracle_config.is_abstention == False")

        elif category == "ABSTENTION":
            if task.get("expected_tool_name") is not None:
                errors.append("ABSTENTION task must have expected_tool_name == None")
            if task.get("expected_arguments") is not None:
                errors.append("ABSTENTION task must have expected_arguments == None")
            if oracle_cfg.get("is_abstention") is not True:
                errors.append("ABSTENTION task must have oracle_config.is_abstention == True")
            if not task.get("abstention_pattern"):
                errors.append("ABSTENTION task missing 'abstention_pattern'")

        return (len(errors) == 0), errors
