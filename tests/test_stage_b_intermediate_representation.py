#!/usr/bin/env python3
"""Tests for Stage B Intermediate Representation and Validator."""

import pytest
from src.stage_b_intermediate_representation import (
    build_intermediate_representation,
    compute_complexity_metrics,
    compute_schema_depth,
)
from src.validate_stage_b_intermediate_representation import IntermediateRepresentationValidator


def test_build_and_validate_openapi_ir():
    """Verify construction and validation of OpenAPI-derived IR."""
    ir = build_intermediate_representation(
        operation_id="floating_ips_create",
        slot_id="SLOT_DO_01",
        candidate_source_id="CAND-003",
        source_dialect="OpenAPI 3.0.0",
        primary_source_file="specification/DigitalOcean-public.v2.yaml",
        primary_source_file_blob_sha="a26d71aa637fd6c6241602e9862eae7fb3d1ed95",
        primary_source_file_sha256="e18ad525a336da3dd83776659d5b574e30748b1d59efc53a42c86115b290a76a",
        input_surface={
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Region slug"},
                "droplet_id": {"type": "integer", "description": "Droplet ID"},
            },
            "required": ["region"],
        },
        source_pointer="#/paths/~1v2~1floating_ips/post",
        closure_files_accessed=["resources/floating_ips/floatingIPs_create.yml"],
    )

    validator = IntermediateRepresentationValidator()
    is_valid, errors = validator.validate(ir)
    assert is_valid, f"Validation failed: {errors}"
    assert ir["schema_complexity_metrics"]["property_count"] == 2
    assert ir["schema_complexity_metrics"]["required_count"] == 1
    assert ir["input_surface"]["additionalProperties"] is False


def test_build_and_validate_python_ast_ir():
    """Verify construction and validation of Python AST-derived IR."""
    ir = build_intermediate_representation(
        operation_id="read_query",
        slot_id="SLOT_MCP_SQLITE_01",
        candidate_source_id="CAND-009",
        source_dialect="Python 3 AST",
        primary_source_file="src/sqlite/src/mcp_server_sqlite/server.py",
        primary_source_file_blob_sha="1b97a6a4903bd8961941cdff43df3b059e610e5f",
        primary_source_file_sha256="d3d58a605315e6bf360b43178d8a0a54a9098931bbc00974221ccf3d8e9ba863",
        input_surface={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SELECT SQL query to execute"},
            },
            "required": ["query"],
        },
        ast_span={"lineno": 235, "col_offset": 12, "end_lineno": 245, "end_col_offset": 14},
        ast_path="Module/main/handle_list_tools/Call[types.Tool:read-query]",
        source_snippet='types.Tool(name="read-query", ...)',
        source_snippet_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        parser_name="python:built-in:ast",
        parser_version="python-3.13.2:ast",
    )

    validator = IntermediateRepresentationValidator()
    is_valid, errors = validator.validate(ir)
    assert is_valid, f"Validation failed: {errors}"
    assert ir["operation_identity"]["source_dialect"] == "Python 3 AST"
    assert ir["status_and_confidence"]["lifecycle_status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"


def test_validator_rejects_missing_keys():
    """Verify validator flags missing mandatory top-level keys."""
    validator = IntermediateRepresentationValidator()
    is_valid, errors = validator.validate({"spec_id": "test"})
    assert not is_valid
    assert any("Missing required top-level key" in e for e in errors)


def test_validator_rejects_raw_nullable():
    """Verify validator rejects unhandled OpenAPI nullable keyword."""
    ir = build_intermediate_representation(
        operation_id="test_op",
        slot_id="SLOT_TEST_01",
        candidate_source_id="CAND-TEST",
        source_dialect="OpenAPI 3.0",
        primary_source_file="spec.yaml",
        primary_source_file_blob_sha="abc",
        primary_source_file_sha256="def",
        input_surface={
            "type": "object",
            "properties": {
                "name": {"type": "string", "nullable": True},
            },
        },
    )

    validator = IntermediateRepresentationValidator()
    is_valid, errors = validator.validate(ir)
    assert not is_valid
    assert any("nullable" in e for e in errors)


def test_validator_rejects_canonical_faithful():
    """Verify validator rejects forbidden CANONICAL_FAITHFUL designation."""
    ir = build_intermediate_representation(
        operation_id="test_op",
        slot_id="SLOT_TEST_01",
        candidate_source_id="CAND-TEST",
        source_dialect="OpenAPI 3.0",
        primary_source_file="spec.yaml",
        primary_source_file_blob_sha="abc",
        primary_source_file_sha256="def",
        input_surface={"type": "object", "properties": {}},
    )
    ir["status_and_confidence"]["lifecycle_status"] = "CANONICAL_FAITHFUL"

    validator = IntermediateRepresentationValidator()
    is_valid, errors = validator.validate(ir)
    assert not is_valid
    assert any("CANONICAL_FAITHFUL" in e for e in errors)
