"""Stage C Semantic Oracle.

Deterministic semantic evaluation oracle that scores candidate tool invocations
against latent intent definitions and schema constraints.
Classifies outcomes into exact match, semantic equivalent, schema violation,
missing required slot, value corruption, hallucinated slot, or tool selection error.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import copy
import jsonschema

from src.stage_c_latent_intent import LatentIntent
from src.stage_c_intent_codec import StageCIntentCodec


@dataclass
class OracleEvaluationResult:
    """Detailed result of semantic oracle evaluation."""
    is_success: bool
    classification: str
    tool_correct: bool
    schema_valid: bool
    slot_precision: float
    slot_recall: float
    slot_f1: float
    matched_slots: List[str] = field(default_factory=list)
    missing_slots: List[str] = field(default_factory=list)
    corrupted_slots: List[str] = field(default_factory=list)
    hallucinated_slots: List[str] = field(default_factory=list)
    schema_errors: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_success": self.is_success,
            "classification": self.classification,
            "tool_correct": self.tool_correct,
            "schema_valid": self.schema_valid,
            "slot_precision": round(self.slot_precision, 4),
            "slot_recall": round(self.slot_recall, 4),
            "slot_f1": round(self.slot_f1, 4),
            "matched_slots": self.matched_slots,
            "missing_slots": self.missing_slots,
            "corrupted_slots": self.corrupted_slots,
            "hallucinated_slots": self.hallucinated_slots,
            "schema_errors": self.schema_errors,
            "details": self.details,
        }


class StageCSemanticOracle:
    """Deterministic semantic evaluator for tool invocation correctness."""

    VALID_CLASSIFICATIONS = [
        "EXACT_MATCH",
        "SEMANTIC_EQUIVALENT",
        "SCHEMA_VIOLATION",
        "MISSING_REQUIRED_SLOT",
        "VALUE_CORRUPTION",
        "HALLUCINATED_SLOT",
        "TOOL_SELECTION_ERROR",
        "MALFORMED_INVOCATION",
        "CORRECT_ABSTENTION",
        "FALSE_EXECUTION_UNWARRANTED",
        "FALSE_ABSTENTION",
    ]

    def __init__(self):
        self.draft7_validator_cls = jsonschema.Draft7Validator

    def evaluate_invocation(
        self,
        expected_intent: Optional[LatentIntent],
        target_contract: Optional[Dict[str, Any]],
        candidate_tool_name: Optional[str],
        candidate_arguments: Optional[Dict[str, Any]],
        codec: Optional[StageCIntentCodec] = None,
        is_abstention_task: bool = False
    ) -> OracleEvaluationResult:
        """Evaluates a candidate tool invocation against expected intent and schema.
        
        Handles standard execution tasks as well as abstention tasks.
        """
        # Case A: Abstention Task Handling
        if is_abstention_task:
            return self._evaluate_abstention(candidate_tool_name, candidate_arguments)

        # Case B: Standard Tool Invocation Task
        if expected_intent is None or target_contract is None:
            raise ValueError("Standard execution tasks require expected_intent and target_contract.")

        expected_tool_name = target_contract.get("tool_name", "")
        schema = target_contract.get("schema", {})

        # 1. Tool Selection Check
        tool_correct = (candidate_tool_name == expected_tool_name)
        if not tool_correct:
            return OracleEvaluationResult(
                is_success=False,
                classification="TOOL_SELECTION_ERROR",
                tool_correct=False,
                schema_valid=False,
                slot_precision=0.0,
                slot_recall=0.0,
                slot_f1=0.0,
                details={
                    "expected_tool": expected_tool_name,
                    "candidate_tool": candidate_tool_name
                }
            )

        # 2. Argument Well-Formedness Check
        if candidate_arguments is None or not isinstance(candidate_arguments, dict):
            return OracleEvaluationResult(
                is_success=False,
                classification="MALFORMED_INVOCATION",
                tool_correct=True,
                schema_valid=False,
                slot_precision=0.0,
                slot_recall=0.0,
                slot_f1=0.0,
                details={"reason": "candidate_arguments is None or not a dict"}
            )

        # 3. JSON Schema Validation Check
        schema_errors = []
        try:
            validator = self.draft7_validator_cls(schema)
            for err in sorted(validator.iter_errors(candidate_arguments), key=lambda e: e.message):
                schema_errors.append(f"{err.path}: {err.message}")
        except Exception as exc:
            schema_errors.append(f"Validator failure: {str(exc)}")

        schema_valid = (len(schema_errors) == 0)

        # 4. Intent Slot Recovery and Analysis
        effective_codec = codec or StageCIntentCodec()
        decoded_intent = effective_codec.decode_arguments_to_intent(
            candidate_arguments,
            base_intent_template=expected_intent
        )

        expected_slots = expected_intent.get_slot_values()
        decoded_slots = decoded_intent.get_slot_values()
        required_slot_names = expected_intent.get_required_slot_names()

        matched_slots = []
        missing_slots = []
        corrupted_slots = []
        hallucinated_slots = []

        for req_name in required_slot_names:
            if req_name not in decoded_slots or decoded_slots[req_name] is None:
                missing_slots.append(req_name)

        for slot_name, expected_val in expected_slots.items():
            if slot_name in decoded_slots:
                cand_val = decoded_slots[slot_name]
                if self._values_equal(expected_val, cand_val):
                    matched_slots.append(slot_name)
                else:
                    corrupted_slots.append(slot_name)
            else:
                if slot_name not in missing_slots:
                    missing_slots.append(slot_name)

        for cand_slot_name in decoded_slots:
            if cand_slot_name not in expected_slots:
                hallucinated_slots.append(cand_slot_name)

        # Calculate metrics
        num_expected = len(expected_slots)
        num_candidate = len(decoded_slots)
        num_matched = len(matched_slots)

        slot_precision = (num_matched / num_candidate) if num_candidate > 0 else 0.0
        slot_recall = (num_matched / num_expected) if num_expected > 0 else 0.0
        slot_f1 = (2 * slot_precision * slot_recall / (slot_precision + slot_recall)) if (slot_precision + slot_recall) > 0 else 0.0

        # 5. Outcome Classification
        if not schema_valid:
            classification = "SCHEMA_VIOLATION"
            is_success = False
        elif missing_slots:
            classification = "MISSING_REQUIRED_SLOT"
            is_success = False
        elif corrupted_slots:
            classification = "VALUE_CORRUPTION"
            is_success = False
        elif hallucinated_slots:
            classification = "HALLUCINATED_SLOT"
            is_success = False
        else:
            # All slots match, schema valid
            expected_args = effective_codec.encode_intent_to_arguments(expected_intent)
            if candidate_arguments == expected_args:
                classification = "EXACT_MATCH"
            else:
                classification = "SEMANTIC_EQUIVALENT"
            is_success = True

        return OracleEvaluationResult(
            is_success=is_success,
            classification=classification,
            tool_correct=True,
            schema_valid=schema_valid,
            slot_precision=slot_precision,
            slot_recall=slot_recall,
            slot_f1=slot_f1,
            matched_slots=matched_slots,
            missing_slots=missing_slots,
            corrupted_slots=corrupted_slots,
            hallucinated_slots=hallucinated_slots,
            schema_errors=schema_errors,
            details={
                "expected_slots": list(expected_slots.keys()),
                "decoded_slots": list(decoded_slots.keys())
            }
        )

    def _evaluate_abstention(
        self,
        candidate_tool_name: Optional[str],
        candidate_arguments: Optional[Dict[str, Any]]
    ) -> OracleEvaluationResult:
        """Evaluates an abstention task where the correct behavior is not to invoke any tool."""
        if candidate_tool_name is None or candidate_tool_name == "" or candidate_tool_name == "ABSTAIN":
            return OracleEvaluationResult(
                is_success=True,
                classification="CORRECT_ABSTENTION",
                tool_correct=True,
                schema_valid=True,
                slot_precision=1.0,
                slot_recall=1.0,
                slot_f1=1.0,
                details={"reason": "Model correctly abstained from unfulfillable request"}
            )
        else:
            return OracleEvaluationResult(
                is_success=False,
                classification="FALSE_EXECUTION_UNWARRANTED",
                tool_correct=False,
                schema_valid=False,
                slot_precision=0.0,
                slot_recall=0.0,
                slot_f1=0.0,
                details={
                    "invoked_tool": candidate_tool_name,
                    "arguments": candidate_arguments
                }
            )

    @staticmethod
    def _values_equal(val1: Any, val2: Any) -> bool:
        """Normalized value comparison."""
        if val1 == val2:
            return True
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return abs(val1 - val2) < 1e-9
        if isinstance(val1, str) and isinstance(val2, str):
            return val1.strip() == val2.strip()
        if isinstance(val1, list) and isinstance(val2, list):
            if len(val1) != len(val2):
                return False
            return all(StageCSemanticOracle._values_equal(a, b) for a, b in zip(val1, val2))
        if isinstance(val1, dict) and isinstance(val2, dict):
            if set(val1.keys()) != set(val2.keys()):
                return False
            return all(StageCSemanticOracle._values_equal(val1[k], val2[k]) for k in val1)
        return False
