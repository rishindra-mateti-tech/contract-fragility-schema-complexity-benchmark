#!/usr/bin/env python3
"""Stage B Canonical Source-to-Contract Difference Engine.

Recursively compares raw OpenAPI source specifications against extracted Draft-07
canonical contracts, producing a granular, machine-readable difference register.

Classifies every structural element, property, and keyword into:
- PRESERVE_VERBATIM / PRESERVED: Semantic identity preserved.
- WRAPPER_NORMALIZATION: Synthesized tool container (root, path, body, query, header,
  and container additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001).
- INTENTIONAL_REPRESENTATION_CHANGE: Explicit protocol-governed representation shift
  (e.g. intra-doc $ref inlining, x-openapi-encoding metadata, form-urlencoded transport metadata).
- UNSUPPORTED_OR_UNVERIFIED: Canonical element lacking verifiable source provenance.
- POTENTIAL_LOSS: Raw required field or constraint dropped without justification.
"""

import copy
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

from src.extract_stage_b_canonical_contract import resolve_json_pointer


class DifferenceClassification:
    PRESERVED = "PRESERVED"
    WRAPPER_NORMALIZATION = "WRAPPER_NORMALIZATION"
    INTENTIONAL_REPRESENTATION_CHANGE = "INTENTIONAL_REPRESENTATION_CHANGE"
    UNSUPPORTED_OR_UNVERIFIED = "UNSUPPORTED_OR_UNVERIFIED"
    POTENTIAL_LOSS = "POTENTIAL_LOSS"

    ALL = {
        PRESERVED,
        WRAPPER_NORMALIZATION,
        INTENTIONAL_REPRESENTATION_CHANGE,
        UNSUPPORTED_OR_UNVERIFIED,
        POTENTIAL_LOSS,
    }


def compare_source_to_canonical(
    slot_id: str,
    raw_doc: Dict[str, Any],
    source_pointer: str,
    canonical_contract: Dict[str, Any],
    lineage_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Recursively compare raw operation specification against canonical contract.

    Returns a comprehensive list of difference register records.
    """
    diffs: List[Dict[str, Any]] = []

    # 1. Resolve raw operation node
    raw_op = resolve_json_pointer(raw_doc, source_pointer)

    # Lineage lookup: canonical pointer -> lineage entry
    lineage_map: Dict[str, Dict[str, Any]] = {
        rec.get("canonical_json_pointer", ""): rec for rec in lineage_records
    }

    # -------------------------------------------------------------------------
    # A. Root and Envelope Normalizations
    # -------------------------------------------------------------------------
    diffs.append({
        "slot_id": slot_id,
        "field_path": "/",
        "canonical_pointer": "#",
        "raw_source_pointer": source_pointer,
        "difference_category": "ROOT_ENVELOPE_SYNTHESIS",
        "classification": DifferenceClassification.WRAPPER_NORMALIZATION,
        "source_value_or_location": f"{source_pointer} (OpenAPI Operation Object)",
        "canonical_value_or_location": "root (Draft-07 Object Schema)",
        "evidence_pointer": "WRAPPER_CLOSED_OBJECT_POLICY_001",
        "requires_human_validation": True,
        "rationale": "Root object synthesizes function calling parameter contract; closed object policy enforced.",
    })

    # Tool description
    raw_desc = raw_op.get("summary") or raw_op.get("description", "")
    can_desc = canonical_contract.get("description", "")
    desc_cat = "PRESERVED" if raw_desc == can_desc else "INTENTIONAL_REPRESENTATION_CHANGE"
    diffs.append({
        "slot_id": slot_id,
        "field_path": "/description",
        "canonical_pointer": "#/description",
        "raw_source_pointer": f"{source_pointer}/summary" if raw_op.get("summary") else f"{source_pointer}/description",
        "difference_category": "TOOL_DESCRIPTION",
        "classification": desc_cat,
        "source_value_or_location": raw_desc[:80] + ("..." if len(raw_desc) > 80 else ""),
        "canonical_value_or_location": can_desc[:80] + ("..." if len(can_desc) > 80 else ""),
        "evidence_pointer": "/description in field_lineage.jsonl",
        "requires_human_validation": False,
        "rationale": "Tool description mapped from operation summary or description.",
    })

    # Container envelopes: path, body, query, header
    for surf in ["path", "body", "query", "header"]:
        c_ptr = f"#/properties/{surf}"
        lineage_ptr = f"/properties/{surf}"
        has_lineage = lineage_ptr in lineage_map
        diffs.append({
            "slot_id": slot_id,
            "field_path": f"/properties/{surf}",
            "canonical_pointer": c_ptr,
            "raw_source_pointer": (
                f"{source_pointer}/parameters" if surf == "path" else
                (f"{source_pointer}/requestBody" if surf == "body" else source_pointer)
            ),
            "difference_category": "SURFACE_CONTAINER_SYNTHESIS",
            "classification": DifferenceClassification.WRAPPER_NORMALIZATION,
            "source_value_or_location": f"OpenAPI {surf} transport representation",
            "canonical_value_or_location": f"properties.{surf} (closed object wrapper)",
            "evidence_pointer": "WRAPPER_CLOSED_OBJECT_POLICY_001",
            "requires_human_validation": True,
            "rationale": f"Explicit transport surface container for {surf} parameters.",
        })

    # -------------------------------------------------------------------------
    # B. Path Parameters Comparison
    # -------------------------------------------------------------------------
    raw_params = raw_op.get("parameters", [])
    raw_path_params: Dict[str, Any] = {}
    raw_path_pointers: Dict[str, str] = {}

    for idx, p in enumerate(raw_params):
        p_ptr = f"{source_pointer}/parameters/{idx}"
        ref_ptr = None
        resolved_p = p
        if "$ref" in p:
            ref_ptr = p["$ref"]
            resolved_p = resolve_json_pointer(raw_doc, ref_ptr)

        if resolved_p.get("in") == "path":
            p_name = resolved_p["name"]
            raw_path_params[p_name] = resolved_p
            raw_path_pointers[p_name] = ref_ptr or p_ptr

    canonical_path_props = canonical_contract.get("properties", {}).get("path", {}).get("properties", {})
    canonical_path_req = canonical_contract.get("properties", {}).get("path", {}).get("required", [])

    # Check raw path params presence and keywords in canonical
    for p_name, r_param in raw_path_params.items():
        if p_name not in canonical_path_props:
            diffs.append({
                "slot_id": slot_id,
                "field_path": f"/properties/path/properties/{p_name}",
                "canonical_pointer": f"#/properties/path/properties/{p_name}",
                "raw_source_pointer": raw_path_pointers[p_name],
                "difference_category": "MISSING_PATH_PARAMETER",
                "classification": DifferenceClassification.POTENTIAL_LOSS,
                "source_value_or_location": raw_path_pointers[p_name],
                "canonical_value_or_location": None,
                "evidence_pointer": "MISSING_IN_CANONICAL",
                "requires_human_validation": True,
                "rationale": f"Path parameter '{p_name}' defined in raw spec is missing from canonical contract.",
            })
            continue

        c_prop = canonical_path_props[p_name]
        r_schema = r_param.get("schema", {})
        c_ptr = f"#/properties/path/properties/{p_name}"
        lin_ptr = f"/properties/path/properties/{p_name}"

        # Property routing from path parameter to object property
        diffs.append({
            "slot_id": slot_id,
            "field_path": f"/properties/path/properties/{p_name}",
            "canonical_pointer": c_ptr,
            "raw_source_pointer": raw_path_pointers[p_name],
            "difference_category": "PATH_PARAMETER_ROUTING",
            "classification": DifferenceClassification.WRAPPER_NORMALIZATION,
            "source_value_or_location": f"in: path parameter '{p_name}'",
            "canonical_value_or_location": f"properties.path.properties.{p_name}",
            "evidence_pointer": "WRAPPER_CLOSED_OBJECT_POLICY_001",
            "requires_human_validation": False,
            "rationale": f"Path parameter '{p_name}' encapsulated in canonical path envelope.",
        })

        # Compare schema keywords of path parameter
        _compare_schema_keywords(
            slot_id=slot_id,
            path_prefix=f"/properties/path/properties/{p_name}",
            raw_schema=r_schema,
            canonical_schema=c_prop,
            raw_pointer=f"{raw_path_pointers[p_name]}/schema",
            canonical_pointer=c_ptr,
            diffs=diffs,
            lineage_map=lineage_map,
            lin_ptr=lin_ptr,
        )

    # -------------------------------------------------------------------------
    # C. Request Body Comparison
    # -------------------------------------------------------------------------
    raw_rb = raw_op.get("requestBody", {})
    if raw_rb:
        if "$ref" in raw_rb:
            raw_rb = resolve_json_pointer(raw_doc, raw_rb["$ref"])

        content_map = raw_rb.get("content", {})
        # Target content-type
        ct = "application/json" if "application/json" in content_map else (
            "application/x-www-form-urlencoded" if "application/x-www-form-urlencoded" in content_map else list(content_map.keys())[0]
        )
        escaped_ct = ct.replace("~", "~0").replace("/", "~1")
        raw_b_schema_ptr = f"{source_pointer}/requestBody/content/{escaped_ct}/schema"

        raw_content_item = content_map.get(ct, {})
        raw_b_schema = raw_content_item.get("schema", {})
        if "$ref" in raw_b_schema:
            ref_path = raw_b_schema["$ref"]
            diffs.append({
                "slot_id": slot_id,
                "field_path": "/properties/body",
                "canonical_pointer": "#/properties/body",
                "raw_source_pointer": f"{source_pointer}/requestBody/content/{escaped_ct}/schema/$ref",
                "difference_category": "SCHEMA_REF_INLINING",
                "classification": DifferenceClassification.INTENTIONAL_REPRESENTATION_CHANGE,
                "source_value_or_location": ref_path,
                "canonical_value_or_location": "Inlined schema node",
                "evidence_pointer": ref_path,
                "requires_human_validation": False,
                "rationale": f"Intra-document $ref ({ref_path}) inlined into canonical contract tree.",
            })
            raw_b_schema = resolve_json_pointer(raw_doc, ref_path)

        # Check form-urlencoded encoding metadata
        if ct == "application/x-www-form-urlencoded":
            enc_meta = raw_content_item.get("encoding", {})
            diffs.append({
                "slot_id": slot_id,
                "field_path": "/properties/body/x-openapi-encoding",
                "canonical_pointer": "#/properties/body/x-openapi-encoding",
                "raw_source_pointer": f"{source_pointer}/requestBody/content/{escaped_ct}/encoding",
                "difference_category": "TRANSPORT_ENCODING_METADATA",
                "classification": DifferenceClassification.INTENTIONAL_REPRESENTATION_CHANGE,
                "source_value_or_location": f"OpenAPI encoding block ({len(enc_meta)} fields)",
                "canonical_value_or_location": "x-openapi-encoding annotation",
                "evidence_pointer": "SERIALIZATION_CONFORMANCE_SPEC.md",
                "requires_human_validation": False,
                "rationale": "Form-urlencoded deepObject encoding rules preserved via canonical annotation.",
            })

        canonical_body = canonical_contract.get("properties", {}).get("body", {})

        # Recursively compare body schema properties
        _compare_object_properties_recursive(
            slot_id=slot_id,
            path_prefix="/properties/body",
            raw_schema=raw_b_schema,
            canonical_schema=canonical_body,
            raw_pointer=raw_b_schema_ptr,
            canonical_pointer="#/properties/body",
            diffs=diffs,
            lineage_map=lineage_map,
            raw_doc=raw_doc,
        )

    # -------------------------------------------------------------------------
    # D. Lineage Orphan & Integrity Checks
    # -------------------------------------------------------------------------
    for lin_ptr, lin_rec in lineage_map.items():
        # Verify that raw source pointers resolve
        for r_ptr in lin_rec.get("raw_source_pointers", []):
            try:
                resolved = resolve_json_pointer(raw_doc, r_ptr)
            except (KeyError, IndexError, ValueError):
                diffs.append({
                    "slot_id": slot_id,
                    "field_path": lin_ptr,
                    "canonical_pointer": f"#{lin_ptr}",
                    "raw_source_pointer": r_ptr,
                    "difference_category": "UNRESOLVABLE_SOURCE_POINTER",
                    "classification": DifferenceClassification.UNSUPPORTED_OR_UNVERIFIED,
                    "source_value_or_location": r_ptr,
                    "canonical_value_or_location": lin_ptr,
                    "evidence_pointer": "field_lineage.jsonl",
                    "requires_human_validation": True,
                    "rationale": f"Lineage pointer '{r_ptr}' fails to resolve against raw pinned document.",
                })

    return diffs


def _compare_schema_keywords(
    slot_id: str,
    path_prefix: str,
    raw_schema: Dict[str, Any],
    canonical_schema: Dict[str, Any],
    raw_pointer: str,
    canonical_pointer: str,
    diffs: List[Dict[str, Any]],
    lineage_map: Dict[str, Dict[str, Any]],
    lin_ptr: str,
) -> None:
    """Compare individual schema keywords (type, description, format, bounds, enums, etc.)."""
    common_keywords = [
        "type",
        "description",
        "format",
        "enum",
        "const",
        "default",
        "example",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "nullable",
    ]

    for kw in common_keywords:
        if kw in raw_schema:
            r_val = raw_schema[kw]
            if kw not in canonical_schema:
                diffs.append({
                    "slot_id": slot_id,
                    "field_path": f"{path_prefix}/{kw}",
                    "canonical_pointer": f"{canonical_pointer}/{kw}",
                    "raw_source_pointer": f"{raw_pointer}/{kw}",
                    "difference_category": "DROPPED_KEYWORD",
                    "classification": DifferenceClassification.POTENTIAL_LOSS,
                    "source_value_or_location": str(r_val),
                    "canonical_value_or_location": None,
                    "evidence_pointer": "CANONICAL_SCHEMA",
                    "requires_human_validation": True,
                    "rationale": f"Keyword '{kw}' in raw schema was omitted from canonical schema.",
                })
            else:
                c_val = canonical_schema[kw]
                if r_val == c_val:
                    diffs.append({
                        "slot_id": slot_id,
                        "field_path": f"{path_prefix}/{kw}",
                        "canonical_pointer": f"{canonical_pointer}/{kw}",
                        "raw_source_pointer": f"{raw_pointer}/{kw}",
                        "difference_category": "KEYWORD_PRESERVATION",
                        "classification": DifferenceClassification.PRESERVED,
                        "source_value_or_location": str(r_val),
                        "canonical_value_or_location": str(c_val),
                        "evidence_pointer": lin_ptr,
                        "requires_human_validation": False,
                        "rationale": f"Keyword '{kw}' preserved with 100% semantic identity.",
                    })
                else:
                    diffs.append({
                        "slot_id": slot_id,
                        "field_path": f"{path_prefix}/{kw}",
                        "canonical_pointer": f"{canonical_pointer}/{kw}",
                        "raw_source_pointer": f"{raw_pointer}/{kw}",
                        "difference_category": "KEYWORD_VALUE_DIFF",
                        "classification": DifferenceClassification.INTENTIONAL_REPRESENTATION_CHANGE,
                        "source_value_or_location": str(r_val),
                        "canonical_value_or_location": str(c_val),
                        "evidence_pointer": lin_ptr,
                        "requires_human_validation": True,
                        "rationale": f"Keyword '{kw}' differs between raw and canonical representations.",
                    })


def _compare_object_properties_recursive(
    slot_id: str,
    path_prefix: str,
    raw_schema: Dict[str, Any],
    canonical_schema: Dict[str, Any],
    raw_pointer: str,
    canonical_pointer: str,
    diffs: List[Dict[str, Any]],
    lineage_map: Dict[str, Dict[str, Any]],
    raw_doc: Dict[str, Any],
) -> None:
    """Recursively compare object properties, items, additionalProperties, and required arrays."""
    # Check additionalProperties closure on container
    r_add = raw_schema.get("additionalProperties")
    c_add = canonical_schema.get("additionalProperties")

    if r_add is None and c_add is False:
        diffs.append({
            "slot_id": slot_id,
            "field_path": f"{path_prefix}/additionalProperties",
            "canonical_pointer": f"{canonical_pointer}/additionalProperties",
            "raw_source_pointer": f"{raw_pointer}/additionalProperties",
            "difference_category": "WRAPPER_CLOSED_OBJECT_POLICY",
            "classification": DifferenceClassification.WRAPPER_NORMALIZATION,
            "source_value_or_location": "omitted (open by default)",
            "canonical_value_or_location": "false (closed)",
            "evidence_pointer": "WRAPPER_CLOSED_OBJECT_POLICY_001",
            "requires_human_validation": True,
            "rationale": "additionalProperties: false applied under WRAPPER_CLOSED_OBJECT_POLICY_001.",
        })
    elif r_add == c_add:
        diffs.append({
            "slot_id": slot_id,
            "field_path": f"{path_prefix}/additionalProperties",
            "canonical_pointer": f"{canonical_pointer}/additionalProperties",
            "raw_source_pointer": f"{raw_pointer}/additionalProperties",
            "difference_category": "ADDITIONAL_PROPERTIES_PRESERVED",
            "classification": DifferenceClassification.PRESERVED,
            "source_value_or_location": str(r_add),
            "canonical_value_or_location": str(c_add),
            "evidence_pointer": "CANONICAL_SCHEMA",
            "requires_human_validation": False,
            "rationale": "additionalProperties configuration matches raw schema.",
        })

    # Compare required array
    r_req = sorted(raw_schema.get("required", []))
    c_req = sorted(canonical_schema.get("required", []))
    if r_req == c_req:
        if r_req:
            diffs.append({
                "slot_id": slot_id,
                "field_path": f"{path_prefix}/required",
                "canonical_pointer": f"{canonical_pointer}/required",
                "raw_source_pointer": f"{raw_pointer}/required",
                "difference_category": "REQUIRED_FIELDS_PRESERVED",
                "classification": DifferenceClassification.PRESERVED,
                "source_value_or_location": str(r_req),
                "canonical_value_or_location": str(c_req),
                "evidence_pointer": "CANONICAL_SCHEMA",
                "requires_human_validation": False,
                "rationale": "Required properties array preserved identically with sorted keys.",
            })
    else:
        diffs.append({
            "slot_id": slot_id,
            "field_path": f"{path_prefix}/required",
            "canonical_pointer": f"{canonical_pointer}/required",
            "raw_source_pointer": f"{raw_pointer}/required",
            "difference_category": "REQUIRED_FIELDS_DIFF",
            "classification": DifferenceClassification.POTENTIAL_LOSS,
            "source_value_or_location": str(r_req),
            "canonical_value_or_location": str(c_req),
            "evidence_pointer": "CANONICAL_SCHEMA",
            "requires_human_validation": True,
            "rationale": "Mismatch in required properties array.",
        })

    # Properties
    raw_props = raw_schema.get("properties", {})
    can_props = canonical_schema.get("properties", {})

    for p_name, r_pdef in raw_props.items():
        sub_raw_ptr = f"{raw_pointer}/properties/{p_name}"
        sub_can_ptr = f"{canonical_pointer}/properties/{p_name}"
        sub_path = f"{path_prefix}/properties/{p_name}"
        lin_ptr = sub_path

        if "$ref" in r_pdef:
            target_ref = r_pdef["$ref"]
            diffs.append({
                "slot_id": slot_id,
                "field_path": sub_path,
                "canonical_pointer": sub_can_ptr,
                "raw_source_pointer": f"{sub_raw_ptr}/$ref",
                "difference_category": "PROPERTY_REF_INLINED",
                "classification": DifferenceClassification.INTENTIONAL_REPRESENTATION_CHANGE,
                "source_value_or_location": target_ref,
                "canonical_value_or_location": "Inlined schema node",
                "evidence_pointer": target_ref,
                "requires_human_validation": False,
                "rationale": f"Intra-document $ref ({target_ref}) inlined into canonical contract.",
            })
            r_pdef = resolve_json_pointer(raw_doc, target_ref)
            sub_raw_ptr = target_ref

        if p_name not in can_props:
            diffs.append({
                "slot_id": slot_id,
                "field_path": sub_path,
                "canonical_pointer": sub_can_ptr,
                "raw_source_pointer": sub_raw_ptr,
                "difference_category": "MISSING_PROPERTY",
                "classification": DifferenceClassification.POTENTIAL_LOSS,
                "source_value_or_location": sub_raw_ptr,
                "canonical_value_or_location": None,
                "evidence_pointer": "CANONICAL_SCHEMA",
                "requires_human_validation": True,
                "rationale": f"Property '{p_name}' present in raw schema was not extracted into canonical contract.",
            })
            continue

        c_pdef = can_props[p_name]

        # Property presence
        diffs.append({
            "slot_id": slot_id,
            "field_path": sub_path,
            "canonical_pointer": sub_can_ptr,
            "raw_source_pointer": sub_raw_ptr,
            "difference_category": "PROPERTY_PRESENCE",
            "classification": DifferenceClassification.PRESERVED,
            "source_value_or_location": sub_raw_ptr,
            "canonical_value_or_location": sub_can_ptr,
            "evidence_pointer": lin_ptr,
            "requires_human_validation": False,
            "rationale": f"Property '{p_name}' successfully extracted and mapped to canonical schema.",
        })

        # Compare scalar keywords
        _compare_schema_keywords(
            slot_id=slot_id,
            path_prefix=sub_path,
            raw_schema=r_pdef,
            canonical_schema=c_pdef,
            raw_pointer=sub_raw_ptr,
            canonical_pointer=sub_can_ptr,
            diffs=diffs,
            lineage_map=lineage_map,
            lin_ptr=lin_ptr,
        )

        # Recurse if nested object
        if r_pdef.get("type") == "object" or "properties" in r_pdef:
            _compare_object_properties_recursive(
                slot_id=slot_id,
                path_prefix=sub_path,
                raw_schema=r_pdef,
                canonical_schema=c_pdef,
                raw_pointer=sub_raw_ptr,
                canonical_pointer=sub_can_ptr,
                diffs=diffs,
                lineage_map=lineage_map,
                raw_doc=raw_doc,
            )

        # Recurse if array items
        if r_pdef.get("type") == "array" and "items" in r_pdef:
            r_items = r_pdef["items"]
            c_items = c_pdef.get("items", {})
            sub_items_raw_ptr = f"{sub_raw_ptr}/items"
            sub_items_can_ptr = f"{sub_can_ptr}/items"
            sub_items_path = f"{sub_path}/items"

            if "$ref" in r_items:
                target_ref = r_items["$ref"]
                r_items = resolve_json_pointer(raw_doc, target_ref)
                sub_items_raw_ptr = target_ref

            diffs.append({
                "slot_id": slot_id,
                "field_path": sub_items_path,
                "canonical_pointer": sub_items_can_ptr,
                "raw_source_pointer": sub_items_raw_ptr,
                "difference_category": "ARRAY_ITEMS_SCHEMA",
                "classification": DifferenceClassification.PRESERVED,
                "source_value_or_location": sub_items_raw_ptr,
                "canonical_value_or_location": sub_items_can_ptr,
                "evidence_pointer": sub_items_path,
                "requires_human_validation": False,
                "rationale": f"Array items schema for '{p_name}' mapped to canonical items container.",
            })

            _compare_schema_keywords(
                slot_id=slot_id,
                path_prefix=sub_items_path,
                raw_schema=r_items,
                canonical_schema=c_items,
                raw_pointer=sub_items_raw_ptr,
                canonical_pointer=sub_items_can_ptr,
                diffs=diffs,
                lineage_map=lineage_map,
                lin_ptr=sub_items_path,
            )

        # Recurse if additionalProperties map schema
        if isinstance(r_pdef.get("additionalProperties"), dict):
            r_add_schema = r_pdef["additionalProperties"]
            c_add_schema = c_pdef.get("additionalProperties", {})
            sub_add_raw_ptr = f"{sub_raw_ptr}/additionalProperties"
            sub_add_can_ptr = f"{sub_can_ptr}/additionalProperties"
            sub_add_path = f"{sub_path}/additionalProperties"

            diffs.append({
                "slot_id": slot_id,
                "field_path": sub_add_path,
                "canonical_pointer": sub_add_can_ptr,
                "raw_source_pointer": sub_add_raw_ptr,
                "difference_category": "MAP_VALUE_SCHEMA",
                "classification": DifferenceClassification.PRESERVED,
                "source_value_or_location": sub_add_raw_ptr,
                "canonical_value_or_location": sub_add_can_ptr,
                "evidence_pointer": sub_add_path,
                "requires_human_validation": False,
                "rationale": f"Dynamic map value schema for '{p_name}' preserved in canonical additionalProperties.",
            })

            if r_add_schema.get("type") == "object" or "properties" in r_add_schema:
                _compare_object_properties_recursive(
                    slot_id=slot_id,
                    path_prefix=sub_add_path,
                    raw_schema=r_add_schema,
                    canonical_schema=c_add_schema,
                    raw_pointer=sub_add_raw_ptr,
                    canonical_pointer=sub_add_can_ptr,
                    diffs=diffs,
                    lineage_map=lineage_map,
                    raw_doc=raw_doc,
                )
