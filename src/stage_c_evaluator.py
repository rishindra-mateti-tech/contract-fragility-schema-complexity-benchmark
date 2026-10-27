"""Stage C Offline Evaluator.

Executes deterministic offline evaluation of candidate model responses against
gold task instances using StageCResponseParser, StageCSemanticOracle, and StageCMetrics.
"""

from typing import Any, Dict, List, Optional
import json

from src.stage_c_response_parser import StageCResponseParser
from src.stage_c_semantic_oracle import StageCSemanticOracle
from src.stage_c_intent_codec import StageCIntentCodec
from src.stage_c_latent_intent import LatentIntent
from src.stage_c_metrics import StageCMetrics


class StageCEvaluator:
    """Offline evaluation runner."""

    def __init__(self):
        self.parser = StageCResponseParser()
        self.oracle = StageCSemanticOracle()

    def evaluate_task_response(
        self,
        task: Dict[str, Any],
        raw_response: Any
    ) -> Dict[str, Any]:
        """Evaluates a single raw model response against a task instance."""
        parsed = self.parser.parse_response(raw_response)
        oracle_cfg = task.get("oracle_config", {})
        is_abstention_task = oracle_cfg.get("is_abstention", False)

        mapping_spec = oracle_cfg.get("mapping_spec")
        codec = StageCIntentCodec(mapping_spec) if mapping_spec else None

        expected_intent = None
        if task.get("expected_latent_intent"):
            expected_intent = LatentIntent.from_dict(task["expected_latent_intent"])

        # Match target contract declaration
        expected_tool_name = task.get("expected_tool_name")
        target_contract = None
        if expected_tool_name:
            target_decl = next((t for t in task.get("available_tools", []) if t.get("tool_name") == expected_tool_name), None)
            if target_decl:
                target_contract = {
                    "tool_name": expected_tool_name,
                    "schema": target_decl.get("schema", {})
                }

        candidate_tool = parsed.tool_name
        candidate_args = parsed.arguments

        # If parser detected abstention
        if parsed.is_abstention:
            candidate_tool = None
            candidate_args = None

        oracle_res = self.oracle.evaluate_invocation(
            expected_intent=expected_intent,
            target_contract=target_contract,
            candidate_tool_name=candidate_tool,
            candidate_arguments=candidate_args,
            codec=codec,
            is_abstention_task=is_abstention_task
        )

        res_dict = oracle_res.to_dict()
        res_dict["task_id"] = task["task_id"]
        res_dict["category"] = task.get("category")
        res_dict["base_contract_id"] = task.get("base_contract_id")
        res_dict["mutation_family"] = task.get("mutation_family")
        res_dict["is_abstention_task"] = is_abstention_task
        res_dict["raw_response"] = parsed.raw_response
        res_dict["parse_errors"] = parsed.parse_errors

        return res_dict

    def evaluate_batch(
        self,
        tasks: List[Dict[str, Any]],
        responses_by_task_id: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluates a batch of tasks against candidate responses."""
        if not responses_by_task_id:
            return {
                "evaluation_status": "NO_EMPIRICAL_RESULTS_PRESENT",
                "reason": "Pre-registered benchmark foundation; model evaluations not executed.",
                "total_tasks_registered": len(tasks),
                "tasks_evaluated": 0,
                "metrics": {}
            }

        evaluated = []
        for task in tasks:
            tid = task["task_id"]
            if tid in responses_by_task_id:
                eval_res = self.evaluate_task_response(task, responses_by_task_id[tid])
                evaluated.append(eval_res)

        metrics = StageCMetrics.compute_evaluation_metrics(evaluated)

        return {
            "evaluation_status": "COMPLETED",
            "total_tasks_registered": len(tasks),
            "tasks_evaluated": len(evaluated),
            "metrics": metrics,
            "individual_evaluations": evaluated
        }
