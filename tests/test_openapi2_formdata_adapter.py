#!/usr/bin/env python3
"""Tests for OpenAPI 2.0 FormData to Tool Surface Adapter under Policy 001."""

import json
import os
import pytest

from src.openapi2_formdata_adapter import (
    OpenAPI2FormDataAdapter,
    FormDataAdapterError,
    POLICY_ID,
    ERR_FILE_UPLOAD_PROHIBITED,
    ERR_BINARY_FIELD_PROHIBITED,
    ERR_BODY_FORMDATA_AMBIGUITY,
    ERR_UNSUPPORTED_COLLECTION_FORMAT,
    ERR_UNSUPPORTED_FORM_TYPE,
)


@pytest.fixture
def adapter():
    return OpenAPI2FormDataAdapter()


def test_valid_formdata_adaptation(adapter):
    """Test standard adaptation of formData parameters into form container."""
    parameters = [
        {
            "name": "title",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Post title",
            "maxLength": 100
        },
        {
            "name": "priority",
            "in": "formData",
            "type": "integer",
            "required": False,
            "default": 1,
            "minimum": 1,
            "maximum": 5
        },
        {
            "name": "tags",
            "in": "formData",
            "type": "array",
            "items": {"type": "string"},
            "collectionFormat": "csv",
            "required": False
        }
    ]

    form_schema, transport, decisions = adapter.adapt_form_parameters(
        parameters=parameters,
        consumes=["application/x-www-form-urlencoded"],
        op_pointer="#/paths/~1posts/post",
    )

    assert form_schema["type"] == "object"
    assert form_schema["additionalProperties"] is False
    assert form_schema["required"] == ["title"]
    assert len(form_schema["properties"]) == 3
    assert form_schema["properties"]["title"]["maxLength"] == 100
    assert form_schema["properties"]["priority"]["minimum"] == 1
    assert form_schema["properties"]["tags"]["type"] == "array"

    assert transport["target_surface"] == "form"
    assert transport["fields_count"] == 3
    assert transport["required_fields_count"] == 1

    assert len(decisions) == 3
    assert all(d["transformation_category"] == "INTENTIONAL_REPRESENTATION_CHANGE" for d in decisions)


def test_file_upload_rejected_fail_closed(adapter):
    """Test that type: file parameters are rejected fail-closed."""
    parameters = [
        {"name": "avatar", "in": "formData", "type": "file", "required": True}
    ]

    with pytest.raises(FormDataAdapterError) as exc_info:
        adapter.adapt_form_parameters(parameters, ["multipart/form-data"], "#/paths/~1upload/post")
    assert exc_info.value.code == ERR_FILE_UPLOAD_PROHIBITED


def test_binary_field_rejected_fail_closed(adapter):
    """Test that binary format fields are rejected fail-closed."""
    parameters = [
        {"name": "payload", "in": "formData", "type": "string", "format": "binary"}
    ]

    with pytest.raises(FormDataAdapterError) as exc_info:
        adapter.adapt_form_parameters(parameters, ["application/x-www-form-urlencoded"], "#/paths/~1data/post")
    assert exc_info.value.code == ERR_BINARY_FIELD_PROHIBITED


def test_body_and_formdata_ambiguity_rejected(adapter):
    """Test that mixing body and formData parameters fails closed."""
    parameters = [
        {"name": "field1", "in": "formData", "type": "string"},
        {"name": "bodyPayload", "in": "body", "schema": {"type": "object"}}
    ]

    with pytest.raises(FormDataAdapterError) as exc_info:
        adapter.adapt_form_parameters(parameters, ["application/json"], "#/paths/~1mixed/post")
    assert exc_info.value.code == ERR_BODY_FORMDATA_AMBIGUITY


def test_unsupported_collection_format_rejected(adapter):
    """Test that unknown collectionFormat values fail closed."""
    parameters = [
        {
            "name": "values",
            "in": "formData",
            "type": "array",
            "items": {"type": "string"},
            "collectionFormat": "unsupported_format"
        }
    ]

    with pytest.raises(FormDataAdapterError) as exc_info:
        adapter.adapt_form_parameters(parameters, ["application/x-www-form-urlencoded"], "#/paths/~1arr/post")
    assert exc_info.value.code == ERR_UNSUPPORTED_COLLECTION_FORMAT


def test_real_slack_operations_from_candidate_source(adapter):
    """Verify that real Slack operations in CAND-006 adapt cleanly into form containers."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(root, "data_stage_b", "raw", "CAND-006", "f7b1affd1fb34f9473cd87980428883019b29c07.json")
    with open(raw_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    # 1. conversations.create
    op1 = doc["paths"]["/conversations.create"]["post"]
    form1, trans1, dec1 = adapter.adapt_form_parameters(
        parameters=op1.get("parameters", []),
        consumes=op1.get("consumes"),
        op_pointer="#/paths/~1conversations.create/post"
    )
    assert form1["type"] == "object"
    assert form1["additionalProperties"] is False
    assert set(form1["properties"].keys()) == {"name", "is_private"}
    assert form1["properties"]["name"]["type"] == "string"
    assert form1["properties"]["is_private"]["type"] == "boolean"

    # 2. users.profile.set
    op2 = doc["paths"]["/users.profile.set"]["post"]
    form2, trans2, dec2 = adapter.adapt_form_parameters(
        parameters=op2.get("parameters", []),
        consumes=op2.get("consumes"),
        op_pointer="#/paths/~1users.profile.set/post"
    )
    assert form2["type"] == "object"
    assert set(form2["properties"].keys()) == {"name", "profile", "user", "value"}

    # 3. reminders.add
    op3 = doc["paths"]["/reminders.add"]["post"]
    form3, trans3, dec3 = adapter.adapt_form_parameters(
        parameters=op3.get("parameters", []),
        consumes=op3.get("consumes"),
        op_pointer="#/paths/~1reminders.add/post"
    )
    assert form3["type"] == "object"
    assert set(form3["properties"].keys()) == {"text", "time", "user"}
    assert sorted(form3["required"]) == ["text", "time"]
