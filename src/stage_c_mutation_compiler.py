"""Stage C Controlled Mutation Compiler.

Compiles controlled schema transformations across 5 mutation families:
1. CANONICAL (Identity baseline)
2. NESTED_HIERARCHY (Container nesting with reversible mappings)
3. OPTIONALITY_BLOAT (Injection of optional parameters and defaults)
4. AMBIGUOUS_IDENTIFIERS (Semantic near-synonym renaming)
5. DISTRACTOR_SET_COMPLEXITY (Controlled distractor tool sets)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import copy
import hashlib
import json

from src.stage_c_contract_validator import compute_contract_complexity_metrics
from src.stage_c_intent_codec import StageCIntentCodec


@dataclass
class MutationResult:
    """Output bundle for a compiled contract mutation."""
    mutation_id: str
    base_contract_id: str
    family: str
    variant: str
    mutated_contract: Dict[str, Any]
    mapping_spec: Dict[str, Any]
    distractor_tools: List[Dict[str, Any]] = field(default_factory=list)
    complexity_delta: Dict[str, Any] = field(default_factory=dict)
    provenance_statement: str = "SYNTHETIC_MUTATION_DERIVED_FROM_BASE_CONTRACT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "base_contract_id": self.base_contract_id,
            "family": self.family,
            "variant": self.variant,
            "mutated_contract": self.mutated_contract,
            "mapping_spec": self.mapping_spec,
            "distractor_tools": self.distractor_tools,
            "complexity_delta": self.complexity_delta,
            "provenance_statement": self.provenance_statement,
        }


class StageCMutationCompiler:
    """Compiles controlled mutations against Stage C synthetic base contracts."""

    MUTATION_FAMILIES = [
        "CANONICAL",
        "NESTED_HIERARCHY",
        "OPTIONALITY_BLOAT",
        "AMBIGUOUS_IDENTIFIERS",
        "DISTRACTOR_SET_COMPLEXITY",
    ]

    # Deterministic alias dictionary for AMBIGUOUS_IDENTIFIERS
    ALIAS_MAP = {
        "key": "entry_identifier",
        "value": "payload_content",
        "ttl_seconds": "expiry_duration_sec",
        "overwrite": "replace_existing_flag",
        "record_id": "item_reference",
        "user_id": "account_identifier",
        "cluster_id": "node_group_ref",
        "email": "recipient_address",
        "channel": "broadcast_destination",
        "message": "content_body",
        "title": "display_headline",
        "description": "summary_text",
        "status": "lifecycle_state",
        "limit": "max_records_count",
        "offset": "starting_cursor_index",
        "tags": "metadata_labels",
        "metric_name": "telemetry_indicator",
        "threshold": "trigger_boundary_val",
        "priority": "dispatch_urgency_tier",
        "created_at": "timestamp_epoch",
        "role": "permission_profile",
        "query": "search_expression",
        "enabled": "active_status",
    }

    # Bloat parameters pool for OPTIONALITY_BLOAT
    BLOAT_POOL = [
        ("client_request_id", {"type": "string", "maxLength": 64, "description": "Client correlation identifier."}),
        ("dry_run", {"type": "boolean", "default": False, "description": "Validate request without committing changes."}),
        ("notify_on_completion", {"type": "boolean", "default": False, "description": "Trigger alert upon operation completion."}),
        ("trace_context", {"type": "string", "maxLength": 128, "description": "Distributed tracing baggage header."}),
        ("audit_reason", {"type": "string", "maxLength": 120, "description": "Operator justification for compliance log."}),
        ("priority_override", {"type": "string", "enum": ["low", "standard", "high"], "default": "standard", "description": "Execution priority tier."}),
        ("timeout_ms", {"type": "integer", "minimum": 100, "maximum": 60000, "default": 5000, "description": "Request timeout in milliseconds."}),
        ("idempotency_key", {"type": "string", "maxLength": 36, "description": "Unique key to ensure safe idempotency."}),
    ]

    def compile_mutation(
        self,
        base_contract: Dict[str, Any],
        family: str,
        variant: str = "default",
        all_contracts: Optional[List[Dict[str, Any]]] = None
    ) -> MutationResult:
        """Dispatches compilation to the requested mutation operator family."""
        if family not in self.MUTATION_FAMILIES:
            raise ValueError(f"Unknown mutation family '{family}'. Must be one of {self.MUTATION_FAMILIES}")

        base_id = base_contract["contract_id"]
        mutation_id = f"MUT_{base_id}_{family}_{variant}"

        if family == "CANONICAL":
            return self._compile_canonical(base_contract, mutation_id, variant)
        elif family == "NESTED_HIERARCHY":
            return self._compile_nested_hierarchy(base_contract, mutation_id, variant)
        elif family == "OPTIONALITY_BLOAT":
            return self._compile_optionality_bloat(base_contract, mutation_id, variant)
        elif family == "AMBIGUOUS_IDENTIFIERS":
            return self._compile_ambiguous_identifiers(base_contract, mutation_id, variant)
        elif family == "DISTRACTOR_SET_COMPLEXITY":
            return self._compile_distractor_complexity(base_contract, mutation_id, variant, all_contracts or [])
        else:
            raise NotImplementedError(f"Operator {family} not implemented")

    def _compile_canonical(
        self,
        base_contract: Dict[str, Any],
        mutation_id: str,
        variant: str
    ) -> MutationResult:
        """Identity baseline mutation."""
        mutated = copy.deepcopy(base_contract)
        mutated["mutation_id"] = mutation_id
        mutated["mutation_family"] = "CANONICAL"
        mutated["mutation_variant"] = variant

        # Identity mappings
        properties = mutated.get("schema", {}).get("properties", {})
        mapping_spec = {
            "intent_to_arg_path": {k: k for k in properties.keys()},
            "arg_to_intent_slot": {k: k for k in properties.keys()}
        }

        return MutationResult(
            mutation_id=mutation_id,
            base_contract_id=base_contract["contract_id"],
            family="CANONICAL",
            variant=variant,
            mutated_contract=mutated,
            mapping_spec=mapping_spec,
            complexity_delta={"depth_delta": 0, "properties_delta": 0}
        )

    def _compile_nested_hierarchy(
        self,
        base_contract: Dict[str, Any],
        mutation_id: str,
        variant: str
    ) -> MutationResult:
        """Wraps selected properties into a structured container object."""
        mutated = copy.deepcopy(base_contract)
        mutated["mutation_id"] = mutation_id
        mutated["mutation_family"] = "NESTED_HIERARCHY"
        mutated["mutation_variant"] = variant

        schema = mutated["schema"]
        orig_properties = schema.get("properties", {})
        orig_required = set(schema.get("required", []))

        # Select grouping: if 3 or more properties, group all but the first into 'payload_details'
        # or 'execution_parameters'
        prop_names = list(orig_properties.keys())
        container_name = "payload_parameters" if variant == "default" else f"container_{variant}"

        grouped_props = prop_names[1:] if len(prop_names) > 1 else prop_names
        kept_top_props = prop_names[:1] if len(prop_names) > 1 else []

        container_properties = {k: orig_properties[k] for k in grouped_props}
        container_required = [k for k in grouped_props if k in orig_required]

        new_properties: Dict[str, Any] = {}
        for k in kept_top_props:
            new_properties[k] = orig_properties[k]

        new_properties[container_name] = {
            "type": "object",
            "properties": container_properties,
            "required": container_required,
            "additionalProperties": False,
            "description": f"Structured container encapsulating {len(grouped_props)} parameters."
        }

        new_required = [k for k in kept_top_props if k in orig_required]
        if container_required:
            new_required.append(container_name)

        schema["properties"] = new_properties
        schema["required"] = new_required

        # Build bidirectional mapping spec
        intent_to_arg: Dict[str, str] = {}
        arg_to_intent: Dict[str, str] = {}

        for k in kept_top_props:
            intent_to_arg[k] = k
            arg_to_intent[k] = k

        for k in grouped_props:
            path = f"{container_name}.{k}"
            intent_to_arg[k] = path
            arg_to_intent[path] = k

        mapping_spec = {
            "intent_to_arg_path": intent_to_arg,
            "arg_to_intent_slot": arg_to_intent
        }

        # Project gold examples
        codec = StageCIntentCodec(mapping_spec)
        new_golds = []
        for gold in base_contract.get("gold_examples", []):
            intent = StageCIntentCodec.create_intent_from_contract_and_args(base_contract, gold)
            new_golds.append(codec.encode_intent_to_arguments(intent))
        mutated["gold_examples"] = new_golds

        # Recalculate metrics
        new_metrics = compute_contract_complexity_metrics(schema)
        mutated["complexity_metrics"] = new_metrics

        depth_delta = new_metrics["max_nesting_depth"] - base_contract["complexity_metrics"]["max_nesting_depth"]
        return MutationResult(
            mutation_id=mutation_id,
            base_contract_id=base_contract["contract_id"],
            family="NESTED_HIERARCHY",
            variant=variant,
            mutated_contract=mutated,
            mapping_spec=mapping_spec,
            complexity_delta={"depth_delta": depth_delta, "properties_delta": 0}
        )

    def _compile_optionality_bloat(
        self,
        base_contract: Dict[str, Any],
        mutation_id: str,
        variant: str
    ) -> MutationResult:
        """Injects extraneous optional parameters and default values into schema."""
        mutated = copy.deepcopy(base_contract)
        mutated["mutation_id"] = mutation_id
        mutated["mutation_family"] = "OPTIONALITY_BLOAT"
        mutated["mutation_variant"] = variant

        schema = mutated["schema"]
        properties = schema.get("properties", {})

        # Determine count of bloat properties (e.g. 3 or 5 depending on variant)
        num_bloat = 5 if variant == "high" else 3
        existing_keys = set(properties.keys())

        injected_keys = []
        for name, spec in self.BLOAT_POOL:
            if name not in existing_keys:
                properties[name] = copy.deepcopy(spec)
                injected_keys.append(name)
                if len(injected_keys) >= num_bloat:
                    break

        # Required fields remain unchanged! Optional fields are added.
        schema["properties"] = properties

        # Mapping retains identity for original slots, ignores optional bloat slots
        intent_to_arg = {k: k for k in base_contract.get("schema", {}).get("properties", {}).keys()}
        arg_to_intent = {k: k for k in intent_to_arg.keys()}

        mapping_spec = {
            "intent_to_arg_path": intent_to_arg,
            "arg_to_intent_slot": arg_to_intent,
            "injected_optional_properties": injected_keys
        }

        new_metrics = compute_contract_complexity_metrics(schema)
        mutated["complexity_metrics"] = new_metrics

        return MutationResult(
            mutation_id=mutation_id,
            base_contract_id=base_contract["contract_id"],
            family="OPTIONALITY_BLOAT",
            variant=variant,
            mutated_contract=mutated,
            mapping_spec=mapping_spec,
            complexity_delta={"properties_delta": len(injected_keys)}
        )

    def _compile_ambiguous_identifiers(
        self,
        base_contract: Dict[str, Any],
        mutation_id: str,
        variant: str
    ) -> MutationResult:
        """Renames properties to semantically close near-synonyms."""
        mutated = copy.deepcopy(base_contract)
        mutated["mutation_id"] = mutation_id
        mutated["mutation_family"] = "AMBIGUOUS_IDENTIFIERS"
        mutated["mutation_variant"] = variant

        schema = mutated["schema"]
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        new_properties: Dict[str, Any] = {}
        intent_to_arg: Dict[str, str] = {}
        arg_to_intent: Dict[str, str] = {}
        new_required: List[str] = []

        for prop_name, prop_spec in properties.items():
            if prop_name in self.ALIAS_MAP:
                alias = self.ALIAS_MAP[prop_name]
            else:
                alias = f"{prop_name}_param"

            new_properties[alias] = copy.deepcopy(prop_spec)
            intent_to_arg[prop_name] = alias
            arg_to_intent[alias] = prop_name

            if prop_name in required:
                new_required.append(alias)

        schema["properties"] = new_properties
        schema["required"] = new_required

        mapping_spec = {
            "intent_to_arg_path": intent_to_arg,
            "arg_to_intent_slot": arg_to_intent
        }

        # Project gold examples
        new_golds = []
        for gold in base_contract.get("gold_examples", []):
            new_gold = {}
            for k, v in gold.items():
                target_key = intent_to_arg.get(k, k)
                new_gold[target_key] = copy.deepcopy(v)
            new_golds.append(new_gold)
        mutated["gold_examples"] = new_golds

        new_metrics = compute_contract_complexity_metrics(schema)
        mutated["complexity_metrics"] = new_metrics

        return MutationResult(
            mutation_id=mutation_id,
            base_contract_id=base_contract["contract_id"],
            family="AMBIGUOUS_IDENTIFIERS",
            variant=variant,
            mutated_contract=mutated,
            mapping_spec=mapping_spec,
            complexity_delta={"renamed_properties": len(intent_to_arg)}
        )

    def _compile_distractor_complexity(
        self,
        base_contract: Dict[str, Any],
        mutation_id: str,
        variant: str,
        all_contracts: List[Dict[str, Any]]
    ) -> MutationResult:
        """Injects controlled distractor tool definitions alongside the target tool."""
        mutated = copy.deepcopy(base_contract)
        mutated["mutation_id"] = mutation_id
        mutated["mutation_family"] = "DISTRACTOR_SET_COMPLEXITY"
        mutated["mutation_variant"] = variant

        # Target tool schema remains unchanged
        mapping_spec = {
            "intent_to_arg_path": {k: k for k in mutated.get("schema", {}).get("properties", {}).keys()},
            "arg_to_intent_slot": {k: k for k in mutated.get("schema", {}).get("properties", {}).keys()}
        }

        # Determine distractor count: 2 (low), 4 (medium), 8 (high)
        target_count = 2 if variant == "low" else (8 if variant == "high" else 4)

        base_id = base_contract["contract_id"]
        base_domain = base_contract.get("domain", "")

        # Same-domain candidates preferred first, then other domains
        same_domain = [c for c in all_contracts if c["contract_id"] != base_id and c.get("domain") == base_domain]
        other_domain = [c for c in all_contracts if c["contract_id"] != base_id and c.get("domain") != base_domain]

        selected_candidates = (same_domain + other_domain)[:target_count]
        distractors = []
        for cand in selected_candidates:
            distractors.append({
                "contract_id": cand["contract_id"],
                "tool_name": cand["tool_name"],
                "title": cand["title"],
                "description": cand["description"],
                "schema": cand["schema"],
                "domain": cand.get("domain")
            })

        return MutationResult(
            mutation_id=mutation_id,
            base_contract_id=base_contract["contract_id"],
            family="DISTRACTOR_SET_COMPLEXITY",
            variant=variant,
            mutated_contract=mutated,
            mapping_spec=mapping_spec,
            distractor_tools=distractors,
            complexity_delta={"distractor_count": len(distractors)}
        )
