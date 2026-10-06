"""
validator.py - Strict deterministic syntactic and semantic validation
for LLM function-calling outputs.
"""

import copy
import jsonschema
from jsonschema import Draft7Validator

def convert_to_json_schema(schema_dict):
    """
    Converts OpenAPI parameter format to standard JSON Schema Draft-07.
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

def _values_are_equivalent(val_gen, val_exp):
    """Robust value comparison handling types, whitespace, case, and numbers."""
    if val_gen is None and val_exp is None:
        return True
    if val_gen is None or val_exp is None:
        return False
        
    # Numeric equivalence (e.g. 4500 == 4500.0 or '4500' vs 4500)
    try:
        num_gen = float(val_gen)
        num_exp = float(val_exp)
        if abs(num_gen - num_exp) < 1e-5:
            return True
    except (ValueError, TypeError):
        pass
        
    # String equivalence with case and whitespace stripping
    if isinstance(val_gen, str) and isinstance(val_exp, str):
        return " ".join(val_gen.strip().lower().split()) == " ".join(val_exp.strip().lower().split())
        
    return val_gen == val_exp

def flatten_dict(d, parent_key="", sep="."):
    """Recursively flattens a nested dictionary into dot-separated paths."""
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
    return dict(items)

def validate_semantics(generated_args, expected_args):
    """
    Evaluates grounding and execution semantics with recursive field-by-field scoring.
    Returns: (exact_match: bool, field_precision: float, field_recall: float, details: dict)
    """
    if not isinstance(generated_args, dict) or not isinstance(expected_args, dict):
        return False, 0.0, 0.0, {"error": "Invalid argument types"}
        
    flat_exp = flatten_dict(expected_args)
    flat_gen = flatten_dict(generated_args)
    
    matched_paths = []
    mismatched_paths = {}
    
    for path, exp_val in flat_exp.items():
        if path in flat_gen:
            gen_val = flat_gen[path]
            if _values_are_equivalent(gen_val, exp_val):
                matched_paths.append(path)
            else:
                mismatched_paths[path] = {"expected": exp_val, "generated": gen_val}
        else:
            mismatched_paths[path] = {"expected": exp_val, "generated": "<MISSING>"}
            
    total_expected = len(flat_exp)
    total_generated = len(flat_gen)
    
    recall = len(matched_paths) / total_expected if total_expected > 0 else 1.0
    precision = len(matched_paths) / total_generated if total_generated > 0 else 1.0
    exact_match = (len(matched_paths) == total_expected and len(mismatched_paths) == 0)
    
    return exact_match, precision, recall, {
        "matched_fields": matched_paths,
        "mismatches": mismatched_paths,
        "unsolicited_fields": list(set(flat_gen.keys()) - set(flat_exp.keys()))
    }
