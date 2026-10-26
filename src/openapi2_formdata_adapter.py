#!/usr/bin/env python3
"""OpenAPI 2.0 / Swagger formData to Tool Surface Adapter.

Implements dedicated, fail-closed adaptation of OpenAPI 2.0 `in: formData`
parameters to discrete `form` tool surface containers under
OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001.

Crucial Scientific Invariant:
- formData is NOT mapped to body or application/json.
- formData parameters are synthesized into a dedicated `form: {...}` container.
- Field types, enums, defaults, constraints, and descriptions are preserved.
- File uploads and binary payloads are rejected fail-closed.
- Dialect conversions are tracked as INTENTIONAL_REPRESENTATION_CHANGE.
"""

import copy
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Tuple

POLICY_ID = "OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001"

# Error Codes
ERR_FILE_UPLOAD_PROHIBITED = "ERR_FILE_UPLOAD_PROHIBITED"
ERR_BINARY_FIELD_PROHIBITED = "ERR_BINARY_FIELD_PROHIBITED"
ERR_BODY_FORMDATA_AMBIGUITY = "ERR_BODY_FORMDATA_AMBIGUITY"
ERR_UNSUPPORTED_COLLECTION_FORMAT = "ERR_UNSUPPORTED_COLLECTION_FORMAT"
ERR_UNSUPPORTED_FORM_TYPE = "ERR_UNSUPPORTED_FORM_TYPE"
ERR_UNRESOLVED_FORM_REF = "ERR_UNRESOLVED_FORM_REF"


class FormDataAdapterError(Exception):
    """Exception raised when OpenAPI 2.0 formData cannot be safely adapted."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


class OpenAPI2FormDataAdapter:
    """Adapter translating Swagger 2.0 formData parameters to Draft-07 form surface."""

    def __init__(self):
        self.adapter_decisions: List[Dict[str, Any]] = []
        self.transformations: List[Dict[str, Any]] = []

    def adapt_form_parameters(
        self,
        parameters: List[Dict[str, Any]],
        consumes: Optional[List[str]],
        op_pointer: str,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        """Synthesize a dedicated Draft-07 form surface object from formData parameters.

        Returns:
            Tuple of:
            - form_surface_schema: Draft-07 JSON Schema object for the form container
            - transport_metadata: Characterization of serialization and dialect origin
            - decisions_log: Detailed per-field decision and transformation records
        """
        form_params: List[Dict[str, Any]] = []
        body_params: List[Dict[str, Any]] = []

        for p in parameters:
            location = p.get("in")
            if location == "formData":
                form_params.append(p)
            elif location == "body":
                body_params.append(p)

        # Scientific Invariant: Ambiguity rejection
        if form_params and body_params:
            raise FormDataAdapterError(
                ERR_BODY_FORMDATA_AMBIGUITY,
                f"Operation at '{op_pointer}' declares both 'formData' and 'body' parameters.",
                {"op_pointer": op_pointer},
            )

        properties: Dict[str, Any] = {}
        required: List[str] = []
        decisions: List[Dict[str, Any]] = []

        supported_types = {"string", "number", "integer", "boolean", "array"}
        supported_collection_formats = {"csv", "ssv", "tsv", "pipes", "multi", None}

        for idx, p in enumerate(form_params):
            name = p.get("name")
            p_type = p.get("type")
            p_format = p.get("format")
            p_ptr = f"{op_pointer}/parameters/formData/{name}"

            # 1. Prohibit file uploads
            if p_type == "file":
                raise FormDataAdapterError(
                    ERR_FILE_UPLOAD_PROHIBITED,
                    f"Parameter '{name}' specifies 'type: file', which is prohibited in tool contracts.",
                    {"parameter": name, "pointer": p_ptr},
                )

            # 2. Prohibit binary payloads
            if p_format in ["binary", "byte"]:
                raise FormDataAdapterError(
                    ERR_BINARY_FIELD_PROHIBITED,
                    f"Parameter '{name}' specifies binary format '{p_format}', which is prohibited.",
                    {"parameter": name, "format": p_format, "pointer": p_ptr},
                )

            # 3. Validate supported type
            if p_type not in supported_types:
                raise FormDataAdapterError(
                    ERR_UNSUPPORTED_FORM_TYPE,
                    f"Parameter '{name}' specifies unsupported form data type '{p_type}'.",
                    {"parameter": name, "type": p_type, "pointer": p_ptr},
                )

            # 4. Validate collection format if array
            coll_format = p.get("collectionFormat")
            if p_type == "array" and coll_format not in supported_collection_formats:
                raise FormDataAdapterError(
                    ERR_UNSUPPORTED_COLLECTION_FORMAT,
                    f"Parameter '{name}' defines unsupported collectionFormat '{coll_format}'.",
                    {"parameter": name, "collectionFormat": coll_format, "pointer": p_ptr},
                )

            # Construct Draft-07 property schema
            prop_schema: Dict[str, Any] = {"type": p_type}

            # Copy standard validation keywords
            for kw in [
                "description", "default", "enum", "minimum", "maximum",
                "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems"
            ]:
                if kw in p:
                    prop_schema[kw] = copy.deepcopy(p[kw])

            # Handle array items
            if p_type == "array":
                items_def = p.get("items")
                if isinstance(items_def, dict):
                    item_type = items_def.get("type", "string")
                    prop_schema["items"] = {"type": item_type}
                    if "enum" in items_def:
                        prop_schema["items"]["enum"] = copy.deepcopy(items_def["enum"])
                else:
                    prop_schema["items"] = {"type": "string"}

            properties[name] = prop_schema

            if p.get("required") is True:
                required.append(name)

            decision = {
                "field_name": name,
                "source_dialect": "Swagger 2.0",
                "source_location": "formData",
                "target_surface": "form",
                "declared_pointer": p_ptr,
                "declared_type": p_type,
                "collection_format": coll_format,
                "required": p.get("required") is True,
                "transformation_category": "INTENTIONAL_REPRESENTATION_CHANGE",
                "rationale": "OpenAPI 2.0 formData parameter mapped to discrete Draft-07 'form' surface container.",
            }
            decisions.append(decision)

        form_surface_schema: Dict[str, Any] = {
            "type": "object",
            "additionalProperties": False,
            "properties": dict(sorted(properties.items())),
        }
        if required:
            form_surface_schema["required"] = sorted(required)

        transport_metadata = {
            "policy_id": POLICY_ID,
            "source_dialect": "Swagger 2.0",
            "source_surface": "formData",
            "target_surface": "form",
            "declared_consumes": consumes or ["application/x-www-form-urlencoded"],
            "inferred_serialization": "application/x-www-form-urlencoded",
            "fields_count": len(properties),
            "required_fields_count": len(required),
            "wire_conformance_claim": "HTTP_WIRE_CONFORMANCE_EXPLICITLY_UNVALIDATED",
            "server_acceptance_claim": "SERVER_ACCEPTANCE_EXPLICITLY_UNVALIDATED",
        }

        self.adapter_decisions = copy.deepcopy(decisions)
        return form_surface_schema, transport_metadata, decisions
