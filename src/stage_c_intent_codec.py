"""Stage C Latent Intent Codec.

Encodes abstract latent intents into concrete tool invocation arguments and
decodes concrete arguments back into latent intent slot values.
Supports identity mapping (canonical), nested container mapping, and identifier aliasing.
"""

from typing import Any, Dict, List, Optional, Tuple
import copy
from src.stage_c_latent_intent import LatentIntent, LatentSlot


class StageCIntentCodec:
    """Bidirectional codec between abstract LatentIntent and schema arguments."""

    def __init__(self, mapping_spec: Optional[Dict[str, Any]] = None):
        """Initializes codec with an optional mapping specification.
        
        mapping_spec can contain:
          - "intent_to_arg_path": Dict[slot_name, dot_separated_arg_path]
          - "arg_to_intent_slot": Dict[dot_separated_arg_path, slot_name]
          - "value_transformers": Dict[slot_name, {"encode": func_name, "decode": func_name}]
        """
        self.mapping_spec = mapping_spec or {}
        self.intent_to_arg_path = self.mapping_spec.get("intent_to_arg_path", {})
        self.arg_to_intent_slot = self.mapping_spec.get("arg_to_intent_slot", {})

    @staticmethod
    def create_intent_from_contract_and_args(
        contract: Dict[str, Any],
        arguments: Dict[str, Any],
        intent_id: str = "INTENT_AUTO_001"
    ) -> LatentIntent:
        """Constructs a canonical LatentIntent from a base contract and argument dict."""
        domain = contract.get("domain", "general")
        action = contract.get("tool_name", "tool")
        target_entity = contract.get("contract_id", "CONTRACT_001")
        schema = contract.get("schema", {})
        properties = schema.get("properties", {})
        required_props = set(schema.get("required", []))
        latent_schema = contract.get("latent_intent_schema", {})

        intent = LatentIntent(
            intent_id=intent_id,
            domain=domain,
            action=action,
            target_entity=target_entity,
            constraints={"required": sorted(list(required_props))}
        )

        for prop_name, prop_val in arguments.items():
            data_type = latent_schema.get(prop_name, "string")
            is_req = prop_name in required_props
            doc_desc = properties.get(prop_name, {}).get("description", "")
            intent.add_slot(
                name=prop_name,
                value=copy.deepcopy(prop_val),
                data_type=data_type,
                is_required=is_req,
                description=doc_desc
            )

        return intent

    def encode_intent_to_arguments(self, intent: LatentIntent) -> Dict[str, Any]:
        """Encodes an abstract LatentIntent into concrete schema arguments."""
        args: Dict[str, Any] = {}
        slot_values = intent.get_slot_values()

        for slot_name, slot_value in slot_values.items():
            target_path = self.intent_to_arg_path.get(slot_name, slot_name)
            self._set_nested_value(args, target_path, copy.deepcopy(slot_value))

        return args

    def decode_arguments_to_intent(
        self,
        arguments: Dict[str, Any],
        base_intent_template: Optional[LatentIntent] = None
    ) -> LatentIntent:
        """Decodes concrete schema arguments into an abstract LatentIntent."""
        if base_intent_template:
            intent = LatentIntent(
                intent_id=base_intent_template.intent_id,
                domain=base_intent_template.domain,
                action=base_intent_template.action,
                target_entity=base_intent_template.target_entity,
                constraints=copy.deepcopy(base_intent_template.constraints),
                metadata=copy.deepcopy(base_intent_template.metadata)
            )
        else:
            intent = LatentIntent(
                intent_id="INTENT_DECODED_001",
                domain="unknown",
                action="unknown",
                target_entity="unknown"
            )

        # 1. Custom path mapping defined
        if self.arg_to_intent_slot:
            for arg_path, slot_name in self.arg_to_intent_slot.items():
                found, val = self._get_nested_value(arguments, arg_path)
                if found:
                    data_type = "string"
                    if base_intent_template and slot_name in base_intent_template.slots:
                        data_type = base_intent_template.slots[slot_name].data_type
                    intent.add_slot(slot_name, val, data_type=data_type)
        elif base_intent_template:
            # 2. Base template provided: extract slots according to expected template
            for slot_name, slot_def in base_intent_template.slots.items():
                if slot_name in arguments:
                    intent.add_slot(
                        slot_name,
                        copy.deepcopy(arguments[slot_name]),
                        data_type=slot_def.data_type,
                        is_required=slot_def.is_required,
                        description=slot_def.description
                    )
                else:
                    found, val = self._get_nested_value(arguments, slot_name)
                    if found:
                        intent.add_slot(
                            slot_name,
                            copy.deepcopy(val),
                            data_type=slot_def.data_type,
                            is_required=slot_def.is_required,
                            description=slot_def.description
                        )
            # Capture any extra arguments not in template
            for arg_k, arg_v in arguments.items():
                if arg_k not in base_intent_template.slots and arg_k not in intent.slots:
                    intent.add_slot(arg_k, copy.deepcopy(arg_v), data_type="any")
        else:
            # 3. Direct shallow copy
            for k, v in arguments.items():
                intent.add_slot(k, copy.deepcopy(v), data_type="any")

        return intent

    def verify_lossless_roundtrip(self, intent: LatentIntent) -> Tuple[bool, List[str]]:
        """Verifies that encoding intent and decoding it preserves all slots and values."""
        errors = []
        encoded = self.encode_intent_to_arguments(intent)
        decoded = self.decode_arguments_to_intent(encoded, base_intent_template=intent)

        original_slots = intent.get_slot_values()
        decoded_slots = decoded.get_slot_values()

        if set(original_slots.keys()) != set(decoded_slots.keys()):
            errors.append(
                f"Slot set mismatch: expected {sorted(original_slots.keys())}, got {sorted(decoded_slots.keys())}"
            )
            return False, errors

        for k, v in original_slots.items():
            dec_v = decoded_slots.get(k)
            if v != dec_v:
                errors.append(f"Value mismatch for slot '{k}': expected {v!r}, got {dec_v!r}")

        return (len(errors) == 0), errors

    @staticmethod
    def _set_nested_value(d: Dict[str, Any], path: str, value: Any) -> None:
        parts = path.split(".")
        current = d
        for p in parts[:-1]:
            if p not in current or not isinstance(current[p], dict):
                current[p] = {}
            current = current[p]
        current[parts[-1]] = value

    @staticmethod
    def _get_nested_value(d: Dict[str, Any], path: str) -> Tuple[bool, Any]:
        parts = path.split(".")
        current = d
        for p in parts:
            if not isinstance(current, dict) or p not in current:
                return False, None
            current = current[p]
        return True, current
