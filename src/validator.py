"""
validator.py - Strict deterministic syntactic and semantic validation
for LLM function-calling outputs.
"""

import copy
import jsonschema
from jsonschema import Draft7Validator

def convert_to_json_schema(schema_dict):
    """
    Converts Gemini/OpenAPI parameter format to standard JSON Schema Draft-07.
    Maps uppercase types (STRING, OBJECT, etc.) to lowercase (string, object, etc.).
    """
    if not isinstance(schema_dict, dict):
        return schema_dict
        
    res = {}
    type_map = {
        "STRING": "string",
        "INTEGER": "integer",
        "NUMBER": "number",
        "BOOLEAN": "boolean",
        "ARRAY": "array",
        "OBJECT": "object"
    }
    
    for k, v in schema_dict.items():
        if k == "type" and isinstance(v, str):
            res["type"] = type_map.get(v.upper(), v.lower())
        elif k == "properties" and isinstance(v, dict):
            res["properties"] = {pk: convert_to_json_schema(pv) for pk, pv in v.items()}
        elif k == "items" and isinstance(v, dict):
            res["items"] = convert_to_json_schema(v)
        else:
            res[k] = copy.deepcopy(v)
            
    return res

def validate_syntax(generated_args, parameters_schema):
    """
    Validates whether generated_args adheres to parameters_schema.
    Returns: (is_valid: bool, error_category: str | None, error_message: str | None)
    """
    if not isinstance(generated_args, dict):
        return False, "NON_OBJECT_PAYLOAD", f"Expected dict, got {type(generated_args).__name__}"
        
    json_schema = convert_to_json_schema(parameters_schema)
    validator = Draft7Validator(json_schema)
    errors = sorted(validator.iter_errors(generated_args), key=lambda e: e.path)
    
    if not errors:
        return True, None, None
        
    first_error = errors[0]
    validator_name = first_error.validator
    
    category = "SCHEMA_VIOLATION"
    if validator_name == "required":
        category = "MISSING_REQUIRED_FIELD"
    elif validator_name == "type":
        category = "TYPE_MISMATCH"
    elif validator_name == "enum":
        category = "ENUM_VIOLATION"
    elif validator_name == "additionalProperties":
        category = "UNEXPECTED_FIELD"
        
    return False, category, first_error.message

def validate_semantics(generated_args, expected_args):
    """
    Evaluates grounding and execution semantics against ground truth.
    Returns: (exact_match: bool, field_precision: float, field_recall: float, details: dict)
    """
    if not isinstance(generated_args, dict) or not isinstance(expected_args, dict):
        return False, 0.0, 0.0, {"error": "Invalid argument types"}
        
    expected_keys = set(expected_args.keys())
    generated_keys = set(generated_args.keys())
    
    matched_keys = []
    mismatched_values = {}
    
    for k, v_exp in expected_args.items():
        if k in generated_args:
            v_gen = generated_args[k]
            # Handle nested dicts recursively
            if isinstance(v_exp, dict) and isinstance(v_gen, dict):
                sub_em, _, _, _ = validate_semantics(v_gen, v_exp)
                if sub_em:
                    matched_keys.append(k)
                else:
                    mismatched_values[k] = {"expected": v_exp, "generated": v_gen}
            else:
                # String normalization
                if isinstance(v_exp, str) and isinstance(v_gen, str):
                    if v_exp.strip().lower() == v_gen.strip().lower():
                        matched_keys.append(k)
                    else:
                        mismatched_values[k] = {"expected": v_exp, "generated": v_gen}
                elif v_exp == v_gen:
                    matched_keys.append(k)
                else:
                    mismatched_values[k] = {"expected": v_exp, "generated": v_gen}
        else:
            mismatched_values[k] = {"expected": v_exp, "generated": "<MISSING>"}
            
    recall = len(matched_keys) / len(expected_keys) if expected_keys else 1.0
    precision = len(matched_keys) / len(generated_keys) if generated_keys else 1.0
    exact_match = (len(matched_keys) == len(expected_keys) and len(mismatched_values) == 0)
    
    return exact_match, precision, recall, {
        "matched_keys": matched_keys,
        "mismatches": mismatched_values,
        "unsolicited_keys": list(generated_keys - expected_keys)
    }
