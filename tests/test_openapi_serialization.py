#!/usr/bin/env python3
"""Tests for OpenAPI Serialization Conformance Layer.

Validates RFC 8259 JSON, RFC 1866 application/x-www-form-urlencoded, deepObject
parameter serialization, explode semantics, deterministic key sorting, and
bidirectional round-trip reversibility against the SLOT_STRIPE_02 canonical contract.
"""

import json
import os
import pytest

from src.openapi_serialization import (
    coerce_value_by_schema,
    deserialize_form_urlencoded,
    deserialize_json,
    round_trip_form_urlencoded,
    serialize_form_urlencoded,
    serialize_json,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRIPE_CANONICAL_PATH = os.path.join(
    ROOT_DIR, "data_stage_b", "canonical", "SLOT_STRIPE_02", "canonical_contract.json"
)


# =============================================================================
# 1. RFC 8259 JSON SERIALIZATION TESTS
# =============================================================================

def test_json_serialization_deterministic_and_round_trip():
    """Verify JSON serialization is deterministic and in-process reversible."""
    payload = {
        "title": "Fix memory leak",
        "head": "feature/cache",
        "base": "main",
        "draft": False,
        "reviewers": ["alice", "bob"],
        "metadata": {"priority": 1, "score": 98.6},
    }
    s1 = serialize_json(payload, sort_keys=True)
    s2 = serialize_json(payload, sort_keys=True)
    assert s1 == s2
    assert deserialize_json(s1) == payload


# =============================================================================
# 2. APPLICATION/X-WWW-FORM-URLENCODED & DEEPOBJECT SERIALIZATION
# =============================================================================

def test_form_urlencoded_flat_scalars():
    """Verify flat primitives serialize to URL-encoded query pairs with deterministic sorting."""
    payload = {
        "name": "Standard Shipping",
        "active": True,
        "amount": 500,
        "rate": 4.5,
    }
    encoded = serialize_form_urlencoded(payload, sort_keys=True)
    # Sorted order: active, amount, name, rate
    assert encoded == "active=true&amount=500&name=Standard+Shipping&rate=4.5"


def test_form_urlencoded_deep_object_nesting():
    """Verify deepObject style serializes nested dictionaries as bracketed keys."""
    payload = {
        "fixed_amount": {
            "amount": 1200,
            "currency": "usd",
        },
        "metadata": {
            "department": "fulfillment",
            "tier": "gold",
        },
    }
    encoded = serialize_form_urlencoded(payload, style="deepObject", sort_keys=True)
    expected = (
        "fixed_amount%5Bamount%5D=1200&"
        "fixed_amount%5Bcurrency%5D=usd&"
        "metadata%5Bdepartment%5D=fulfillment&"
        "metadata%5Btier%5D=gold"
    )
    assert encoded == expected


def test_form_urlencoded_multilevel_deep_object():
    """Verify 3-level deep nesting is correctly bracketed."""
    payload = {
        "delivery_estimate": {
            "minimum": {
                "unit": "business_day",
                "value": 3,
            }
        }
    }
    encoded = serialize_form_urlencoded(payload, style="deepObject", sort_keys=True)
    expected = (
        "delivery_estimate%5Bminimum%5D%5Bunit%5D=business_day&"
        "delivery_estimate%5Bminimum%5D%5Bvalue%5D=3"
    )
    assert encoded == expected


def test_form_urlencoded_array_styles():
    """Verify array serialization with bracket indexing, repeated keys, and comma separation."""
    payload = {"tags": ["fast", "insured"]}

    # 1. Bracket indexing (default Stripe convention)
    encoded_bracket = serialize_form_urlencoded(payload, explode=True, items_indexing="bracket")
    assert encoded_bracket == "tags%5B0%5D=fast&tags%5B1%5D=insured"

    # 2. Repeated keys (standard OpenAPI explode=true)
    encoded_repeat = serialize_form_urlencoded(payload, explode=True, items_indexing="repeat")
    assert encoded_repeat == "tags=fast&tags=insured"

    # 3. Comma-separated (explode=false)
    encoded_comma = serialize_form_urlencoded(payload, explode=False)
    assert encoded_comma == "tags=fast%2Cinsured"


# =============================================================================
# 3. DESERIALIZATION AND SCHEMA-GUIDED TYPE COERCION
# =============================================================================

def test_deserialization_bracket_nested_structure():
    """Verify deserializing bracketed keys reconstructs nested dicts and lists."""
    raw = "fixed_amount%5Bamount%5D=1500&fixed_amount%5Bcurrency%5D=eur&expand%5B0%5D=rates"
    deserialized = deserialize_form_urlencoded(raw)

    assert deserialized == {
        "fixed_amount": {
            "amount": "1500",
            "currency": "eur",
        },
        "expand": ["rates"],
    }


def test_schema_guided_coercion():
    """Verify schema-guided deserialization restores primitive scalar types."""
    schema = {
        "type": "object",
        "properties": {
            "amount": {"type": "integer"},
            "active": {"type": "boolean"},
            "rate": {"type": "number"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "config": {
                "type": "object",
                "properties": {
                    "retries": {"type": "integer"},
                },
            },
        },
    }
    raw = "active=true&amount=250&config%5Bretries%5D=3&rate=9.99&tags=a%2Cb"
    deserialized = deserialize_form_urlencoded(raw, schema=schema)

    assert deserialized["amount"] == 250
    assert isinstance(deserialized["amount"], int)
    assert deserialized["active"] is True
    assert isinstance(deserialized["active"], bool)
    assert deserialized["rate"] == 9.99
    assert isinstance(deserialized["rate"], float)
    assert deserialized["config"]["retries"] == 3
    assert deserialized["tags"] == ["a", "b"]


# =============================================================================
# 4. READ-ONLY VALIDATION AGAINST SLOT_STRIPE_02 CANONICAL CONTRACT
# =============================================================================

def test_stripe_shipping_rate_payload_round_trip():
    """Validate full bidirectional round-trip serialization against SLOT_STRIPE_02 canonical body schema."""
    assert os.path.exists(STRIPE_CANONICAL_PATH), f"Canonical contract missing: {STRIPE_CANONICAL_PATH}"
    with open(STRIPE_CANONICAL_PATH, "r", encoding="utf-8") as f:
        contract = json.load(f)

    body_schema = contract["properties"]["body"]

    # Construct rich payload matching Stripe PostShippingRates canonical schema
    payload = {
        "display_name": "Next Day Express",
        "type": "fixed_amount",
        "fixed_amount": {
            "amount": 2500,
            "currency": "usd",
            "currency_options": {
                "eur": {
                    "amount": 2300,
                    "tax_behavior": "inclusive",
                }
            },
        },
        "delivery_estimate": {
            "minimum": {
                "unit": "day",
                "value": 1,
            },
            "maximum": {
                "unit": "day",
                "value": 2,
            },
        },
        "metadata": {
            "carrier": "fedex",
            "warehouse": "dfw_01",
        },
        "expand": ["data", "customer"],
        "tax_behavior": "exclusive",
        "tax_code": "txcd_92010001",
    }

    is_equivalent, serialized, round_tripped = round_trip_form_urlencoded(
        payload,
        schema=body_schema,
        style="deepObject",
        explode=True,
        items_indexing="bracket",
    )

    # Prove deterministic in-process round-trip under declared representation and encoding policy
    assert is_equivalent is True
    assert round_tripped == payload

    # Verify expected wire substrings
    assert "display_name=Next+Day+Express" in serialized
    assert "fixed_amount%5Bamount%5D=2500" in serialized
    assert "fixed_amount%5Bcurrency%5D=usd" in serialized
    assert "delivery_estimate%5Bminimum%5D%5Bvalue%5D=1" in serialized
    assert "metadata%5Bcarrier%5D=fedex" in serialized
    assert "expand%5B0%5D=data" in serialized
    assert "expand%5B1%5D=customer" in serialized
