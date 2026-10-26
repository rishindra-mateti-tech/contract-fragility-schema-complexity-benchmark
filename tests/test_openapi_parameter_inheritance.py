#!/usr/bin/env python3
"""Tests for OpenAPI Path-Item Parameter Inheritance Adapter under Policy 001."""

import pytest
from src.openapi_parameter_inheritance import (
    ParameterInheritanceAdapter,
    ParameterInheritanceError,
    POLICY_ID,
    ERR_UNRESOLVED_PARAM_REF,
    ERR_PARAM_MISSING_SCHEMA,
    ERR_PARAM_OVERRIDE_CONFLICT,
    ERR_PATH_PARAM_MISMATCH,
    ERR_DUPLICATE_OPERATION_PARAM,
)


@pytest.fixture
def base_doc():
    """Sample raw doc with reusable parameter components."""
    return {
        "openapi": "3.0.3",
        "components": {
            "parameters": {
                "AccountId": {
                    "name": "account_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"}
                },
                "QueryLimit": {
                    "name": "limit",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "default": 20}
                }
            }
        }
    }


def test_inherited_path_and_query_parameters(base_doc):
    """Test inheriting both path and query parameters from path-item level."""
    adapter = ParameterInheritanceAdapter()

    path_item = {
        "parameters": [
            {"$ref": "#/components/parameters/AccountId"},
            {"$ref": "#/components/parameters/QueryLimit"},
        ]
    }
    operation = {
        "operationId": "listUsers",
        "parameters": []
    }

    merged, decisions = adapter.merge_parameters(
        raw_doc=base_doc,
        path_item_node=path_item,
        operation_node=operation,
        path_template="/accounts/{account_id}/users",
        path_pointer="#/paths/~1accounts~1{account_id}~1users",
        op_pointer="#/paths/~1accounts~1{account_id}~1users/get",
    )

    assert len(merged) == 2
    assert len(decisions) == 2
    names = {p["name"] for p in merged}
    assert names == {"account_id", "limit"}

    account_dec = next(d for d in decisions if d["name"] == "account_id")
    assert account_dec["origin"] == "PATH_ITEM"
    assert account_dec["override_status"] == "INHERITED"
    assert account_dec["path_resolved_pointer"] == "#/components/parameters/AccountId"
    assert account_dec["required"] is True


def test_operation_level_override(base_doc):
    """Test operation-level parameter overriding an inherited path-item parameter."""
    adapter = ParameterInheritanceAdapter()

    path_item = {
        "parameters": [
            {"$ref": "#/components/parameters/AccountId"},
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 10}
            }
        ]
    }
    operation = {
        "operationId": "getSpecificUsers",
        "parameters": [
            {
                "name": "limit",
                "in": "query",
                "required": True,
                "description": "Overridden limit description",
                "schema": {"type": "integer", "maximum": 100}
            }
        ]
    }

    merged, decisions = adapter.merge_parameters(
        raw_doc=base_doc,
        path_item_node=path_item,
        operation_node=operation,
        path_template="/accounts/{account_id}/users",
        path_pointer="#/paths/~1accounts~1{account_id}~1users",
        op_pointer="#/paths/~1accounts~1{account_id}~1users/get",
    )

    assert len(merged) == 2
    limit_param = next(p for p in merged if p["name"] == "limit")
    assert limit_param["required"] is True
    assert limit_param["description"] == "Overridden limit description"

    limit_dec = next(d for d in decisions if d["name"] == "limit")
    assert limit_dec["origin"] == "OPERATION_OVERRIDE"
    assert limit_dec["override_status"] == "OVERRIDDEN"


def test_unresolved_parameter_reference_fails_closed(base_doc):
    """Test that referencing a missing parameter raises ERR_UNRESOLVED_PARAM_REF."""
    adapter = ParameterInheritanceAdapter()

    path_item = {
        "parameters": [
            {"$ref": "#/components/parameters/NonExistent"}
        ]
    }
    operation = {"parameters": []}

    with pytest.raises(ParameterInheritanceError) as exc_info:
        adapter.merge_parameters(
            raw_doc=base_doc,
            path_item_node=path_item,
            operation_node=operation,
            path_template="/test",
            path_pointer="#/paths/~1test",
            op_pointer="#/paths/~1test/get",
        )
    assert exc_info.value.code == ERR_UNRESOLVED_PARAM_REF


def test_duplicate_parameter_in_operation_fails_closed(base_doc):
    """Test declaring duplicates with the same (name, in) at operation level fails."""
    adapter = ParameterInheritanceAdapter()

    path_item = {"parameters": []}
    operation = {
        "parameters": [
            {"name": "tag", "in": "query", "schema": {"type": "string"}},
            {"name": "tag", "in": "query", "schema": {"type": "string"}},
        ]
    }

    with pytest.raises(ParameterInheritanceError) as exc_info:
        adapter.merge_parameters(
            raw_doc=base_doc,
            path_item_node=path_item,
            operation_node=operation,
            path_template="/test",
            path_pointer="#/paths/~1test",
            op_pointer="#/paths/~1test/get",
        )
    assert exc_info.value.code == ERR_DUPLICATE_OPERATION_PARAM


def test_path_template_missing_parameter_fails_closed(base_doc):
    """Test that a template variable with no matching path parameter fails."""
    adapter = ParameterInheritanceAdapter()

    path_item = {"parameters": []}
    operation = {"parameters": []}

    with pytest.raises(ParameterInheritanceError) as exc_info:
        adapter.merge_parameters(
            raw_doc=base_doc,
            path_item_node=path_item,
            operation_node=operation,
            path_template="/organizations/{org_id}/members",
            path_pointer="#/paths/~1organizations~1{org_id}~1members",
            op_pointer="#/paths/~1organizations~1{org_id}~1members/get",
        )
    assert exc_info.value.code == ERR_PATH_PARAM_MISMATCH


def test_path_parameter_not_in_template_fails_closed(base_doc):
    """Test that defining an in:path parameter not present in template fails."""
    adapter = ParameterInheritanceAdapter()

    path_item = {
        "parameters": [
            {"name": "extra_var", "in": "path", "required": True, "schema": {"type": "string"}}
        ]
    }
    operation = {"parameters": []}

    with pytest.raises(ParameterInheritanceError) as exc_info:
        adapter.merge_parameters(
            raw_doc=base_doc,
            path_item_node=path_item,
            operation_node=operation,
            path_template="/static/path",
            path_pointer="#/paths/~1static~1path",
            op_pointer="#/paths/~1static~1path/get",
        )
    assert exc_info.value.code == ERR_PATH_PARAM_MISMATCH


def test_path_parameter_without_required_true_fails_closed(base_doc):
    """Test that in:path parameter with required: False fails closed."""
    adapter = ParameterInheritanceAdapter()

    path_item = {
        "parameters": [
            {"name": "org_id", "in": "path", "required": False, "schema": {"type": "string"}}
        ]
    }
    operation = {"parameters": []}

    with pytest.raises(ParameterInheritanceError) as exc_info:
        adapter.merge_parameters(
            raw_doc=base_doc,
            path_item_node=path_item,
            operation_node=operation,
            path_template="/orgs/{org_id}",
            path_pointer="#/paths/~1orgs~1{org_id}",
            op_pointer="#/paths/~1orgs~1{org_id}/get",
        )
    assert exc_info.value.code == ERR_PARAM_MISSING_SCHEMA


def test_real_chatwoot_slots_merge_successfully():
    """Verify that real Chatwoot slots CAND-011 merge path parameters cleanly."""
    import json, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(root, "data_stage_b", "raw", "CAND-011", "b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589.json")
    with open(raw_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    adapter = ParameterInheritanceAdapter()

    # SLOT_CHATWOOT_02
    path_ptr = "#/paths/~1platform~1api~1v1~1accounts~1{account_id}~1account_users"
    path_item = doc["paths"]["/platform/api/v1/accounts/{account_id}/account_users"]
    op = path_item["post"]

    merged, decisions = adapter.merge_parameters(
        raw_doc=doc,
        path_item_node=path_item,
        operation_node=op,
        path_template="/platform/api/v1/accounts/{account_id}/account_users",
        path_pointer=path_ptr,
        op_pointer=f"{path_ptr}/post",
    )
    assert len(merged) == 1
    assert merged[0]["name"] == "account_id"
    assert merged[0]["in"] == "path"
    assert merged[0]["required"] is True
    assert decisions[0]["origin"] == "PATH_ITEM"
    assert decisions[0]["override_status"] == "INHERITED"

    # SLOT_CHATWOOT_03
    path_ptr_03 = "#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts~1{contact_identifier}~1conversations"
    path_item_03 = doc["paths"]["/public/api/v1/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations"]
    op_03 = path_item_03["post"]

    merged_03, decisions_03 = adapter.merge_parameters(
        raw_doc=doc,
        path_item_node=path_item_03,
        operation_node=op_03,
        path_template="/public/api/v1/inboxes/{inbox_identifier}/contacts/{contact_identifier}/conversations",
        path_pointer=path_ptr_03,
        op_pointer=f"{path_ptr_03}/post",
    )
    assert len(merged_03) == 2
    names_03 = {p["name"] for p in merged_03}
    assert names_03 == {"inbox_identifier", "contact_identifier"}
    assert all(p["required"] is True for p in merged_03)

