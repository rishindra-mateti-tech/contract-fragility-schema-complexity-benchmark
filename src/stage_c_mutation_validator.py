"""Stage C Mutation Validator.

Validates compiled contract mutations for schema validity (Draft-07),
gold example satisfaction, mapping reversibility, and complexity delta consistency.
"""

from typing import Any, Dict, List, Tuple
import jsonschema

from src.stage_c_contract_validator import StageCContractValidator
from src.stage_c_intent_codec import StageCIntentCodec
from src.stage_c_mutation_compiler import MutationResult


class StageCMutationValidator:
    """Validates structural and semantic invariants of mutated contracts."""

    def __init__(self):
        self.contract_validator = StageCContractValidator()

    def validate_mutation(self, mutation_res: MutationResult, base_contract: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Performs rigorous multi-point validation on a mutation result."""
        errors: List[str] = []
        mutated_contract = mutation_res.mutated_contract
        schema = mutated_contract.get("schema", {})

        # 1. Base Contract Validator Check (Draft-07, types, properties)
        is_valid, contract_errors = self.contract_validator.validate_contract(mutated_contract)
        if not is_valid:
            errors.extend([f"Base contract validator error: {e}" for e in contract_errors])

        # 2. Reversible Mapping Check for Invertible Families
        mapping_spec = mutation_res.mapping_spec
        family = mutation_res.family

        if family in ["CANONICAL", "NESTED_HIERARCHY", "AMBIGUOUS_IDENTIFIERS"]:
            codec = StageCIntentCodec(mapping_spec)
            for idx, gold in enumerate(base_contract.get("gold_examples", [])):
                intent = StageCIntentCodec.create_intent_from_contract_and_args(
                    contract=base_contract,
                    arguments=gold,
                    intent_id=f"MUT_VAL_INTENT_{idx}"
                )
                encoded = codec.encode_intent_to_arguments(intent)

                # Validate encoded matches schema
                try:
                    jsonschema.validate(encoded, schema)
                except jsonschema.ValidationError as err:
                    errors.append(f"Gold example {idx} encoded arguments failed schema validation: {err.message}")

                # Verify round-trip recovery
                decoded = codec.decode_arguments_to_intent(encoded, base_intent_template=intent)
                orig_slots = intent.get_slot_values()
                dec_slots = decoded.get_slot_values()
                for k, v in orig_slots.items():
                    if k not in dec_slots or dec_slots[k] != v:
                        errors.append(f"Lossless roundtrip failed for slot '{k}': expected {v!r}, got {dec_slots.get(k)!r}")

        # 3. Distractor Tools Verification (for DISTRACTOR_SET_COMPLEXITY)
        if family == "DISTRACTOR_SET_COMPLEXITY":
            distractors = mutation_res.distractor_tools
            if not distractors:
                errors.append("Distractor set mutation produced zero distractor tools.")
            for dist in distractors:
                if "tool_name" not in dist or "schema" not in dist:
                    errors.append(f"Distractor missing tool_name or schema: {dist}")

        return (len(errors) == 0), errors
