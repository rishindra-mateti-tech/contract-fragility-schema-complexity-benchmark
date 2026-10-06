"""
schema_mutator.py - Programmatically generates controlled structural variants
from base schemas to isolate causal schema properties.
"""

import copy
import json
import os

OPTIONAL_BLOAT_PROPERTIES = {
    "tags": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Optional arbitrary metadata labels."},
    "correlation_id": {"type": "STRING", "description": "Unique tracing span identifier for distributed telemetry."},
    "notify_on_completion": {"type": "BOOLEAN", "description": "Whether to publish an event hook upon completion."},
    "idempotency_key": {"type": "STRING", "description": "Header token preventing duplicate mutations."},
    "priority_level": {"type": "INTEGER", "description": "Execution queue priority ranking from 1 to 10."},
    "audit_comment": {"type": "STRING", "description": "Human-readable justification for security audit logs."},
    "dry_run": {"type": "BOOLEAN", "description": "If true, simulates the request without persisting changes."},
    "tenant_id": {"type": "STRING", "description": "UUID of the multi-tenant partition."},
    "api_version": {"type": "STRING", "description": "Override for the default API version (e.g., '2026-10-06')."},
    "strict_mode": {"type": "BOOLEAN", "description": "Fail immediately on warnings if true."},
    "callback_url": {"type": "STRING", "description": "Webhook URL for async status updates."},
    "timeout_ms": {"type": "INTEGER", "description": "Maximum execution time in milliseconds before aborting."},
    "metadata": {"type": "OBJECT", "description": "Key-value pairs for arbitrary extensions."},
    "session_token": {"type": "STRING", "description": "Ephemeral JWT for cross-service authorization."},
    "bypass_cache": {"type": "BOOLEAN", "description": "Force a fresh read/write bypassing Redis."}
}

AMBIGUOUS_NAME_MAPPINGS = {
    "charge_id": "target_id",
    "amount_cents": "qty",
    "reason": "spec",
    "owner": "ns",
    "repo": "entity",
    "title": "label",
    "body": "text_data",
    "channel_id": "dest",
    "message_text": "payload_str",
    "namespace": "env_scope",
    "deployment_name": "target_name",
    "replicas": "count_val",
    "bucket_name": "resource_id",
    "region": "loc",
    "database_name": "db",
    "sql_query": "raw_stmt",
    "lead_id": "ref_num",
    "pipeline_stage": "state_step",
    "deal_value_usd": "val",
    "carrier": "provider_code",
    "weight_lbs": "mass",
    "recipient_zip": "postal",
    "service_tier": "speed",
    "ticket_key": "id_code",
    "target_status": "next_state",
    "metric_name": "key_str",
    "critical_threshold": "cutoff",
    "evaluation_window_minutes": "window_dur",
    "recipient_number": "target_addr",
    "message_body": "msg_content",
    "subject": "headline",
    "requester_email": "user_contact",
    "priority": "urgency_flag",
    "description": "details_text",
    "list_id": "group_id",
    "email_address": "contact_addr",
    "subscription_status": "member_state",
    "zone_id": "domain_id",
    "purge_everything": "clear_all_flag",
    "service_id": "component_id",
    "incident_title": "alert_name",
    "urgency": "sev_level",
    "connection": "auth_realm",
    "email": "user_id_email",
    "email_verified": "is_confirmed",
    "index_name": "collection_name",
    "doc_id": "entry_id",
    "database_id": "parent_uuid",
    "title": "item_heading",
    "status": "workflow_phase",
    "image_name": "package_uri",
    "container_name": "instance_label",
    "restart_policy": "recovery_mode",
    "discount_code": "voucher_token",
    "discount_type": "promo_kind",
    "discount_value": "reduction_num"
}

def create_canonical_variant(base):
    return {
        "mutation_type": "canonical",
        "description": "Baseline canonical clean schema with flat properties.",
        "tool": {
            "name": base["name"],
            "description": base["description"],
            "parameters": copy.deepcopy(base["parameters"])
        },
        "expected_args": copy.deepcopy(base["ground_truth"])
    }

def create_nested_variant(base):
    orig_params = base["parameters"]
    nested_schema = {
        "type": "OBJECT",
        "properties": {
            "transaction_context": {
                "type": "OBJECT",
                "properties": {
                    "data": {
                        "type": "OBJECT",
                        "properties": {
                            "attributes": {
                                "type": "OBJECT",
                                "properties": copy.deepcopy(orig_params["properties"]),
                                "required": copy.deepcopy(orig_params.get("required", []))
                            }
                        },
                        "required": ["attributes"]
                    }
                },
                "required": ["data"]
            }
        },
        "required": ["transaction_context"]
    }
    return {
        "mutation_type": "nested_hierarchy",
        "description": "Structural depth mutation wrapping properties 3 levels deep.",
        "tool": {
            "name": base["name"],
            "description": base["description"],
            "parameters": nested_schema
        },
        "expected_args": {
            "transaction_context": {
                "data": {
                    "attributes": copy.deepcopy(base["ground_truth"])
                }
            }
        }
    }

def create_optionality_bloat_variant(base):
    params = copy.deepcopy(base["parameters"])
    for k, v in OPTIONAL_BLOAT_PROPERTIES.items():
        if k not in params["properties"]:
            params["properties"][k] = copy.deepcopy(v)
    return {
        "mutation_type": "optionality_bloat",
        "description": "Schema density mutation injecting 6 optional enterprise metadata fields.",
        "tool": {
            "name": base["name"],
            "description": base["description"],
            "parameters": params
        },
        "expected_args": copy.deepcopy(base["ground_truth"])
    }

def create_ambiguous_identifiers_variant(base):
    params = copy.deepcopy(base["parameters"])
    new_props = {}
    new_required = []
    new_expected = {}
    
    for old_name, old_prop in params["properties"].items():
        new_name = AMBIGUOUS_NAME_MAPPINGS.get(old_name, f"param_{old_name[:3]}_v2")
        # Strip the description entirely to make it harder
        new_prop = copy.deepcopy(old_prop)
        if "description" in new_prop:
            del new_prop["description"]
        new_props[new_name] = new_prop
        
        if old_name in params.get("required", []):
            new_required.append(new_name)
        if old_name in base["ground_truth"]:
            new_expected[new_name] = base["ground_truth"][old_name]
            
    params["properties"] = new_props
    params["required"] = new_required
    
    # Mutate tool name and docstring to test extreme identifier ambiguity
    verb_parts = base["name"].split("_")
    ambiguous_tool_name = f"system_op_0x{hash(base['name']) % 10000:04x}"
    ambiguous_description = "Internal operation endpoint."
    
    return {
        "mutation_type": "ambiguous_identifiers",
        "description": "Extreme semantic friction mutation removing all docstrings and using obfuscated names.",
        "tool": {
            "name": ambiguous_tool_name,
            "description": ambiguous_description,
            "parameters": params
        },
        "expected_args": new_expected
    }

def generate_all_mutations(base_schemas):
    mutated_dataset = []
    for base in base_schemas:
        schema_suite = {
            "base_id": base["id"],
            "domain": base["domain"],
            "query": base["query"],
            "variants": {
                "canonical": create_canonical_variant(base),
                "nested_hierarchy": create_nested_variant(base),
                "optionality_bloat": create_optionality_bloat_variant(base),
                "ambiguous_identifiers": create_ambiguous_identifiers_variant(base)
            }
        }
        mutated_dataset.append(schema_suite)
    return mutated_dataset

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_file = os.path.join(root_dir, "data", "base_schemas.json")
    with open(base_file, "r", encoding="utf-8") as f:
        base_schemas = json.load(f)
        
    mutated_dataset = generate_all_mutations(base_schemas)
    out_file = os.path.join(root_dir, "data", "mutated_schemas.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(mutated_dataset, f, indent=2)
    print(f"Generated {len(mutated_dataset)} schema suites with 4 variants each ({len(mutated_dataset) * 4} total schema conditions).")
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    main()
