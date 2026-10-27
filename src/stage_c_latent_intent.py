"""Stage C Latent Intent Data Model.

Defines the abstract, canonical intent representation that decouples what an agent
is instructed to do from how a specific JSON schema formats the parameters.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import json
import hashlib


@dataclass
class LatentSlot:
    """Represents a single abstract slot in a user's latent intent."""
    name: str
    value: Any
    data_type: str
    is_required: bool = True
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LatentSlot":
        return cls(
            name=data["name"],
            value=data["value"],
            data_type=data.get("data_type", "string"),
            is_required=data.get("is_required", True),
            description=data.get("description", "")
        )


@dataclass
class LatentIntent:
    """Abstract intent representing the semantic goal of a tool invocation.
    
    Decoupled from concrete schema representation (flat, nested, aliased).
    """
    intent_id: str
    domain: str
    action: str
    target_entity: str
    slots: Dict[str, LatentSlot] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    epistemic_provenance: str = "SYNTHETIC_LATENT_INTENT_REPRESENTATION"

    def add_slot(self, name: str, value: Any, data_type: str, is_required: bool = True, description: str = "") -> None:
        self.slots[name] = LatentSlot(
            name=name,
            value=value,
            data_type=data_type,
            is_required=is_required,
            description=description
        )

    def get_slot_values(self) -> Dict[str, Any]:
        return {k: slot.value for k, slot in self.slots.items()}

    def get_required_slot_names(self) -> List[str]:
        return [k for k, slot in self.slots.items() if slot.is_required]

    def compute_intent_hash(self) -> str:
        serialized = json.dumps({
            "domain": self.domain,
            "action": self.action,
            "target_entity": self.target_entity,
            "slots": {k: self.slots[k].to_dict() for k in sorted(self.slots.keys())},
            "constraints": self.constraints
        }, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "domain": self.domain,
            "action": self.action,
            "target_entity": self.target_entity,
            "slots": {k: slot.to_dict() for k, slot in self.slots.items()},
            "constraints": self.constraints,
            "metadata": self.metadata,
            "epistemic_provenance": self.epistemic_provenance,
            "intent_hash": self.compute_intent_hash()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LatentIntent":
        slots = {}
        for k, v in data.get("slots", {}).items():
            slots[k] = LatentSlot.from_dict(v)
        return cls(
            intent_id=data["intent_id"],
            domain=data["domain"],
            action=data["action"],
            target_entity=data["target_entity"],
            slots=slots,
            constraints=data.get("constraints", {}),
            metadata=data.get("metadata", {}),
            epistemic_provenance=data.get("epistemic_provenance", "SYNTHETIC_LATENT_INTENT_REPRESENTATION")
        )
