#!/usr/bin/env python3
"""OpenAPI Serialization Conformance Layer.

Implements standalone RFC 8259 JSON and RFC 1866 application/x-www-form-urlencoded
serialization and deserialization conforming to OpenAPI 3.0 parameter style guidelines:
- deepObject style for nested objects (e.g. fixed_amount[currency]=usd)
- form style with explode=true (separate key=value or bracket-indexed pairs)
- form style with explode=false (comma-separated values)
- Deterministic key sorting across all emitted URL-encoded query/body strings
- Schema-guided type coercion and bidirectional round-trip reversibility
"""

import json
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple, Union


def serialize_json(payload: Any, sort_keys: bool = True) -> str:
    """Serialize payload to deterministic RFC 8259 JSON string."""
    return json.dumps(payload, indent=None, sort_keys=sort_keys, separators=(",", ":"))


def deserialize_json(raw: str) -> Any:
    """Deserialize RFC 8259 JSON string into Python objects."""
    return json.loads(raw)


def _flatten_form_data(
    prefix: str,
    value: Any,
    style: str = "deepObject",
    explode: bool = True,
    items_indexing: str = "bracket",  # "bracket" e.g. arr[0]=x, "repeat" e.g. arr=x
) -> List[Tuple[str, str]]:
    """Recursively flatten complex nested data structures into key-value pairs."""
    pairs: List[Tuple[str, str]] = []

    if value is None:
        # None/null is represented as empty string or omitted in form-urlencoded
        pairs.append((prefix, ""))
        return pairs

    if isinstance(value, bool):
        pairs.append((prefix, "true" if value else "false"))
        return pairs

    if isinstance(value, (int, float, str)):
        pairs.append((prefix, str(value)))
        return pairs

    if isinstance(value, list):
        if not value:
            return pairs

        if not explode:
            # Comma-separated form values
            joined = ",".join(str(item) for item in value)
            pairs.append((prefix, joined))
            return pairs

        for idx, item in enumerate(value):
            if items_indexing == "bracket":
                elem_key = f"{prefix}[{idx}]"
            elif items_indexing == "empty_bracket":
                elem_key = f"{prefix}[]"
            else:
                elem_key = prefix

            if isinstance(item, (dict, list)):
                pairs.extend(_flatten_form_data(elem_key, item, style, explode, items_indexing))
            else:
                val_str = "true" if isinstance(item, bool) else str(item)
                pairs.append((elem_key, val_str))
        return pairs

    if isinstance(value, dict):
        if not value:
            return pairs

        for k in sorted(value.keys()):
            sub_val = value[k]
            if not prefix:
                sub_key = str(k)
            else:
                if style == "deepObject":
                    sub_key = f"{prefix}[{k}]"
                else:
                    sub_key = f"{prefix}.{k}"
            pairs.extend(_flatten_form_data(sub_key, sub_val, style, explode, items_indexing))
        return pairs

    pairs.append((prefix, str(value)))
    return pairs


def serialize_form_urlencoded(
    payload: Dict[str, Any],
    style: str = "deepObject",
    explode: bool = True,
    sort_keys: bool = True,
    items_indexing: str = "bracket",
) -> str:
    """Serialize dictionary to RFC 1866 application/x-www-form-urlencoded string.

    Supports:
    - style="deepObject" (OpenAPI default for nested objects in Stripe and modern APIs)
    - explode=True vs explode=False
    - Deterministic alphabetical sorting of keys
    """
    pairs: List[Tuple[str, str]] = []
    keys_to_process = sorted(payload.keys()) if sort_keys else payload.keys()

    for key in keys_to_process:
        val = payload[key]
        pairs.extend(_flatten_form_data(key, val, style=style, explode=explode, items_indexing=items_indexing))

    if sort_keys:
        pairs.sort(key=lambda x: (x[0], x[1]))

    return urllib.parse.urlencode(pairs, doseq=False)


def _parse_bracket_path(key: str) -> List[Union[str, int]]:
    """Parse a bracketed key into path tokens: 'fixed_amount[currency]' -> ['fixed_amount', 'currency']."""
    tokens: List[Union[str, int]] = []
    # Match root identifier followed by zero or more bracketed terms [term]
    m = re.match(r"^([^\[]+)(.*)$", key)
    if not m:
        return [key]
    root = m.group(1)
    rest = m.group(2)
    tokens.append(root)

    bracket_pattern = re.findall(r"\[(.*?)\]", rest)
    for b in bracket_pattern:
        if b.isdigit():
            tokens.append(int(b))
        else:
            tokens.append(b)
    return tokens


def _assign_nested_token(target: Any, tokens: List[Union[str, int]], value: str) -> None:
    """Assign a value into a nested dict/list structure following parsed tokens."""
    cur = target
    for i, token in enumerate(tokens[:-1]):
        next_token = tokens[i + 1]

        if isinstance(token, str):
            if token not in cur:
                # If next token is an integer, initialize list or dict
                if isinstance(next_token, int):
                    cur[token] = []
                else:
                    cur[token] = {}
            # If cur[token] is a list and next_token is str, upgrade to dict if needed
            cur = cur[token]
        elif isinstance(token, int):
            # Target is a list
            while len(cur) <= token:
                cur.append({} if isinstance(next_token, str) else [])
            cur = cur[token]

    last_token = tokens[-1]
    if isinstance(last_token, str):
        if isinstance(cur, dict):
            if last_token in cur and isinstance(cur[last_token], list):
                cur[last_token].append(value)
            elif last_token in cur and not isinstance(cur[last_token], list):
                cur[last_token] = [cur[last_token], value]
            else:
                cur[last_token] = value
    elif isinstance(last_token, int):
        while len(cur) <= last_token:
            cur.append(None)
        cur[last_token] = value


def deserialize_form_urlencoded(
    raw: str,
    schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Deserialize application/x-www-form-urlencoded string into nested Python dictionary.

    Optionally coerces types using a Draft-07 / OpenAPI JSON Schema.
    """
    if not raw:
        return {}

    parsed_qs = urllib.parse.parse_qs(raw, keep_blank_values=True)
    result: Dict[str, Any] = {}

    for raw_key, raw_values in sorted(parsed_qs.items()):
        tokens = _parse_bracket_path(raw_key)

        for val in raw_values:
            _assign_nested_token(result, tokens, val)

    if schema is not None:
        result = coerce_value_by_schema(result, schema)

    return result


def coerce_value_by_schema(val: Any, schema: Optional[Dict[str, Any]]) -> Any:
    """Recursively coerce deserialized string scalars into types defined by the schema."""
    if schema is None or val is None:
        return val

    # Resolve local $ref if present
    # (Schema is assumed inlined/dereferenced in canonical Draft-07 contracts)

    expected_type = schema.get("type")

    # Boolean coercion
    if expected_type == "boolean":
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            lower = val.lower()
            if lower == "true":
                return True
            if lower == "false":
                return False
        return bool(val)

    # Integer coercion
    if expected_type == "integer":
        if isinstance(val, int) and not isinstance(val, bool):
            return val
        try:
            return int(val)
        except (ValueError, TypeError):
            return val

    # Number / float coercion
    if expected_type == "number":
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val)
        try:
            return float(val)
        except (ValueError, TypeError):
            return val

    # String coercion
    if expected_type == "string":
        return str(val) if not isinstance(val, str) else val

    # Array coercion
    if expected_type == "array":
        items_schema = schema.get("items", {})
        if isinstance(val, str):
            # Explode=false comma-separated case
            items = val.split(",") if val else []
            return [coerce_value_by_schema(item, items_schema) for item in items]
        if isinstance(val, list):
            return [coerce_value_by_schema(item, items_schema) for item in val if item is not None]
        return [coerce_value_by_schema(val, items_schema)]

    # Object coercion
    if expected_type == "object" or isinstance(val, dict):
        if not isinstance(val, dict):
            return val

        coerced_obj: Dict[str, Any] = {}
        props_schema = schema.get("properties", {})
        add_props = schema.get("additionalProperties")

        for k, v in val.items():
            if k in props_schema:
                coerced_obj[k] = coerce_value_by_schema(v, props_schema[k])
            elif isinstance(add_props, dict):
                coerced_obj[k] = coerce_value_by_schema(v, add_props)
            else:
                coerced_obj[k] = v

        return coerced_obj

    return val


def round_trip_form_urlencoded(
    payload: Dict[str, Any],
    schema: Optional[Dict[str, Any]] = None,
    style: str = "deepObject",
    explode: bool = True,
    items_indexing: str = "bracket",
) -> Tuple[bool, str, Dict[str, Any]]:
    """Perform an in-process serialize -> deserialize round trip under declared encoding policy.

    Evaluates in-process representation equivalence (Tier 2).
    Does NOT assert HTTP wire conformance (Tier 3) or server-side acceptance (Tier 4).

    Returns (is_equivalent, serialized_str, deserialized_payload).
    """
    serialized = serialize_form_urlencoded(
        payload,
        style=style,
        explode=explode,
        sort_keys=True,
        items_indexing=items_indexing,
    )
    deserialized = deserialize_form_urlencoded(serialized, schema=schema)
    is_equivalent = (deserialized == payload)
    return is_equivalent, serialized, deserialized
