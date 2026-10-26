#!/usr/bin/env python3
"""OpenAPI Path-Item Parameter Inheritance Adapter.

Implements generic parameter inheritance between Path Item Object and Operation
Object under OPENAPI_PARAMETER_INHERITANCE_POLICY_001.

OpenAPI Specification Rule (Section 4.7.9 & 4.7.10):
- Parameters defined at the Path Item level apply to all operations under that path.
- An operation may override a path-level parameter by declaring a parameter with the
  identical (name, in) unique key.
- Operation-level parameters cannot remove inherited parameters.
- Inherited parameters must retain complete provenance (origin pointer, resolved pointer,
  override status, requiredness, schema representation).
"""

import copy
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple

POLICY_ID = "OPENAPI_PARAMETER_INHERITANCE_POLICY_001"

# Error Codes
ERR_UNRESOLVED_PARAM_REF = "ERR_UNRESOLVED_PARAM_REF"
ERR_PARAM_MISSING_SCHEMA = "ERR_PARAM_MISSING_SCHEMA"
ERR_PARAM_OVERRIDE_CONFLICT = "ERR_PARAM_OVERRIDE_CONFLICT"
ERR_PATH_PARAM_MISMATCH = "ERR_PATH_PARAM_MISMATCH"
ERR_DUPLICATE_OPERATION_PARAM = "ERR_DUPLICATE_OPERATION_PARAM"


class ParameterInheritanceError(Exception):
    """Exception raised when parameter inheritance fails validation."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


def resolve_pointer_in_doc(doc: Any, pointer: str) -> Any:
    """Resolve JSON pointer within an in-memory document."""
    if not pointer or pointer in ("#", "#/"):
        return doc
    clean = pointer[2:] if pointer.startswith("#/") else (pointer[1:] if pointer.startswith(("#", "/")) else pointer)
    curr = doc
    for tok in clean.split("/"):
        key = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(curr, dict) and key in curr:
            curr = curr[key]
        elif isinstance(curr, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(curr):
                curr = curr[idx]
            else:
                return None
        else:
            return None
    return curr


class ParameterInheritanceAdapter:
    """Generic adapter for merging Path-Item and Operation-level parameters."""

    def __init__(self):
        self.adapter_decisions: List[Dict[str, Any]] = []

    def _resolve_param_def(
        self,
        param_item: Any,
        raw_doc: Any,
        declared_ptr: str,
    ) -> Tuple[Dict[str, Any], str]:
        """Resolve parameter node and track resolved pointer."""
        if not isinstance(param_item, dict):
            raise ParameterInheritanceError(
                ERR_PARAM_MISSING_SCHEMA,
                f"Parameter at '{declared_ptr}' is not a valid object node.",
                {"declared_pointer": declared_ptr},
            )

        if "$ref" in param_item:
            ref_val = param_item["$ref"]
            resolved = resolve_pointer_in_doc(raw_doc, ref_val)
            if resolved is None:
                raise ParameterInheritanceError(
                    ERR_UNRESOLVED_PARAM_REF,
                    f"Parameter reference '{ref_val}' at '{declared_ptr}' failed to resolve.",
                    {"declared_pointer": declared_ptr, "ref": ref_val},
                )
            if not isinstance(resolved, dict):
                raise ParameterInheritanceError(
                    ERR_PARAM_MISSING_SCHEMA,
                    f"Resolved parameter at '{ref_val}' is not an object node.",
                    {"ref": ref_val},
                )
            return copy.deepcopy(resolved), ref_val

        return copy.deepcopy(param_item), declared_ptr

    def merge_parameters(
        self,
        raw_doc: Any,
        path_item_node: Dict[str, Any],
        operation_node: Dict[str, Any],
        path_template: str,
        path_pointer: str,
        op_pointer: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Merge Path Item and Operation parameters with complete provenance tracking.

        Returns:
            Tuple of:
            - merged_parameters: List of fully resolved parameter dicts
            - decisions_log: Detailed provenance and decision records for each parameter
        """
        raw_path_params = path_item_node.get("parameters") or []
        raw_op_params = operation_node.get("parameters") or []

        # Map by unique key (name, in)
        path_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for idx, p in enumerate(raw_path_params):
            p_ptr = f"{path_pointer}/parameters/{idx}"
            resolved_p, resolved_ptr = self._resolve_param_def(p, raw_doc, p_ptr)
            
            name = resolved_p.get("name")
            location = resolved_p.get("in")
            if not name or not location:
                raise ParameterInheritanceError(
                    ERR_PARAM_MISSING_SCHEMA,
                    f"Parameter at '{p_ptr}' missing required 'name' or 'in' field.",
                    {"declared_pointer": p_ptr, "param": resolved_p},
                )

            key = (name, location)
            if key in path_map:
                raise ParameterInheritanceError(
                    ERR_PARAM_OVERRIDE_CONFLICT,
                    f"Duplicate parameter '{name}' in '{location}' at Path-Item level '{p_ptr}'.",
                    {"key": key, "path_pointer": path_pointer},
                )

            path_map[key] = {
                "resolved_param": resolved_p,
                "declared_pointer": p_ptr,
                "resolved_pointer": resolved_ptr,
            }

        # Process Operation-level parameters and overrides
        op_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for idx, p in enumerate(raw_op_params):
            p_ptr = f"{op_pointer}/parameters/{idx}"
            resolved_p, resolved_ptr = self._resolve_param_def(p, raw_doc, p_ptr)

            name = resolved_p.get("name")
            location = resolved_p.get("in")
            if not name or not location:
                raise ParameterInheritanceError(
                    ERR_PARAM_MISSING_SCHEMA,
                    f"Parameter at '{p_ptr}' missing required 'name' or 'in' field.",
                    {"declared_pointer": p_ptr, "param": resolved_p},
                )

            key = (name, location)
            if key in op_map:
                raise ParameterInheritanceError(
                    ERR_DUPLICATE_OPERATION_PARAM,
                    f"Duplicate parameter '{name}' in '{location}' at Operation level '{p_ptr}'.",
                    {"key": key, "op_pointer": op_pointer},
                )

            op_map[key] = {
                "resolved_param": resolved_p,
                "declared_pointer": p_ptr,
                "resolved_pointer": resolved_ptr,
            }

        merged_parameters: List[Dict[str, Any]] = []
        decisions: List[Dict[str, Any]] = []

        # 1. Process Path-Item parameters (inherited or overridden)
        for key, p_data in sorted(path_map.items()):
            name, location = key
            if key in op_map:
                # Overridden by operation level
                op_data = op_map[key]
                merged_parameters.append(op_data["resolved_param"])
                decisions.append({
                    "name": name,
                    "in": location,
                    "origin": "OPERATION_OVERRIDE",
                    "override_status": "OVERRIDDEN",
                    "path_declared_pointer": p_data["declared_pointer"],
                    "path_resolved_pointer": p_data["resolved_pointer"],
                    "op_declared_pointer": op_data["declared_pointer"],
                    "op_resolved_pointer": op_data["resolved_pointer"],
                    "required": op_data["resolved_param"].get("required", False),
                    "schema": op_data["resolved_param"].get("schema"),
                })
            else:
                # Inherited as-is
                merged_parameters.append(p_data["resolved_param"])
                decisions.append({
                    "name": name,
                    "in": location,
                    "origin": "PATH_ITEM",
                    "override_status": "INHERITED",
                    "path_declared_pointer": p_data["declared_pointer"],
                    "path_resolved_pointer": p_data["resolved_pointer"],
                    "op_declared_pointer": None,
                    "op_resolved_pointer": None,
                    "required": p_data["resolved_param"].get("required", False),
                    "schema": p_data["resolved_param"].get("schema"),
                })

        # 2. Add operation-only parameters
        for key, op_data in sorted(op_map.items()):
            if key not in path_map:
                name, location = key
                merged_parameters.append(op_data["resolved_param"])
                decisions.append({
                    "name": name,
                    "in": location,
                    "origin": "OPERATION",
                    "override_status": "OPERATION_LEVEL",
                    "path_declared_pointer": None,
                    "path_resolved_pointer": None,
                    "op_declared_pointer": op_data["declared_pointer"],
                    "op_resolved_pointer": op_data["resolved_pointer"],
                    "required": op_data["resolved_param"].get("required", False),
                    "schema": op_data["resolved_param"].get("schema"),
                })

        # 3. Path parameter template consistency validation
        # Find all {var} in path_template
        template_vars = set(re.findall(r"\{([a-zA-Z0-9_]+)\}", path_template))
        path_param_names = {p["name"] for p in merged_parameters if p.get("in") == "path"}

        missing_in_params = template_vars - path_param_names
        missing_in_template = path_param_names - template_vars

        if missing_in_params:
            raise ParameterInheritanceError(
                ERR_PATH_PARAM_MISMATCH,
                f"Path template '{path_template}' defines variables {missing_in_params} with no corresponding path parameter.",
                {"path_template": path_template, "missing_in_params": list(missing_in_params)},
            )

        if missing_in_template:
            raise ParameterInheritanceError(
                ERR_PATH_PARAM_MISMATCH,
                f"Merged parameters define path parameters {missing_in_template} not present in template '{path_template}'.",
                {"path_template": path_template, "missing_in_template": list(missing_in_template)},
            )

        # All path parameters must have required: true
        for p in merged_parameters:
            if p.get("in") == "path" and p.get("required") is not True:
                raise ParameterInheritanceError(
                    ERR_PARAM_MISSING_SCHEMA,
                    f"Path parameter '{p.get('name')}' must have 'required: true'.",
                    {"param": p},
                )

        self.adapter_decisions = copy.deepcopy(decisions)
        return merged_parameters, decisions

    def get_adapter_decisions(self) -> List[Dict[str, Any]]:
        """Return the list of decisions made during parameter merge."""
        return copy.deepcopy(self.adapter_decisions)
