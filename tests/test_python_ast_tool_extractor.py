#!/usr/bin/env python3
"""Tests for Python AST Static Tool Extraction Adapter."""

import os
import pytest
from src.python_ast_tool_extractor import PythonAstToolExtractor
from src.python_ast_source_normalizer import (
    PythonAstExtractionError,
    ERR_DYNAMIC_VARIABLE_REJECTED,
    ERR_COMPUTED_SCHEMA_CONSTRUCTION,
    ERR_STRING_CONCATENATION_REJECTED,
    ERR_FSTRING_REJECTED,
    ERR_NON_LITERAL_SPREAD,
    ERR_DYNAMIC_ATTRIBUTE_REJECTED,
    ERR_COMPREHENSION_REJECTED,
)

CAND_009_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data_stage_b",
    "raw",
    "CAND-009",
    "1b97a6a4903bd8961941cdff43df3b059e610e5f.py",
)


def test_extract_tools_from_real_cand_009():
    """Verify static extraction from real CAND-009 sqlite server.py."""
    extractor = PythonAstToolExtractor()
    tools = extractor.extract_tools_from_file(CAND_009_FILE)
    assert len(tools) >= 3

    tool_map = {t["operation_id"]: t for t in tools}
    for op_id in ["read_query", "describe_table", "write_query"]:
        assert op_id in tool_map
        t = tool_map[op_id]
        assert t["source_dialect"] == "Python 3 AST"
        assert t["lifecycle_status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
        assert t["input_surface"]["type"] == "object"
        assert t["input_surface"]["additionalProperties"] is False
        assert len(t["input_surface"]["required"]) >= 1

        evidence = t["static_source_evidence"]
        assert evidence["ast_node_kind"] == "ast.Call"
        assert evidence["span"]["lineno"] > 0
        assert evidence["span"]["end_lineno"] >= evidence["span"]["lineno"]
        assert len(evidence["source_snippet"]) > 0
        assert len(evidence["source_snippet_sha256"]) == 64
        assert "Call[types.Tool:" in evidence["ast_path"]


def test_reject_dynamic_variable():
    """Verify rejection when schema references an unresolved variable."""
    code = """
import mcp.types as types
schema = {"type": "object", "properties": {"x": {"type": "string"}}}
t = types.Tool(name="test-tool", inputSchema=schema)
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_DYNAMIC_VARIABLE_REJECTED


def test_reject_computed_function_call():
    """Verify rejection when schema is produced by a function call."""
    code = """
import mcp.types as types
def make_schema(): return {"type": "object"}
t = types.Tool(name="test-tool", inputSchema=make_schema())
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_COMPUTED_SCHEMA_CONSTRUCTION


def test_reject_string_concatenation():
    """Verify rejection when schema property uses binary addition."""
    code = """
import mcp.types as types
t = types.Tool(
    name="test-tool",
    inputSchema={
        "type": "object",
        "description": "Prefix " + "Suffix"
    }
)
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_STRING_CONCATENATION_REJECTED


def test_reject_fstring():
    """Verify rejection when schema property uses an f-string."""
    code = """
import mcp.types as types
val = "test"
t = types.Tool(
    name="test-tool",
    inputSchema={
        "type": "object",
        "description": f"Formatted {val}"
    }
)
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_FSTRING_REJECTED


def test_reject_dictionary_spread():
    """Verify rejection when schema uses **kwargs dictionary unpacking."""
    code = """
import mcp.types as types
extra = {"x": {"type": "string"}}
t = types.Tool(
    name="test-tool",
    inputSchema={
        "type": "object",
        **extra
    }
)
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_NON_LITERAL_SPREAD


def test_reject_dynamic_attribute():
    """Verify rejection when schema uses dynamic attribute lookup."""
    code = """
import mcp.types as types
class Config:
    type_name = "string"
t = types.Tool(
    name="test-tool",
    inputSchema={
        "type": "object",
        "properties": {"val": {"type": Config.type_name}}
    }
)
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_DYNAMIC_ATTRIBUTE_REJECTED


def test_reject_comprehension():
    """Verify rejection when schema uses list or dict comprehensions."""
    code = """
import mcp.types as types
t = types.Tool(
    name="test-tool",
    inputSchema={
        "type": "object",
        "properties": {k: {"type": "string"} for k in ["a", "b"]}
    }
)
"""
    extractor = PythonAstToolExtractor()
    with pytest.raises(PythonAstExtractionError) as exc_info:
        extractor.extract_tools_from_source(code)
    assert exc_info.value.code == ERR_COMPREHENSION_REJECTED


def test_preserve_nested_literal_schema():
    """Verify that deeply nested literal structures are correctly preserved."""
    code = """
import mcp.types as types
t = types.Tool(
    name="nested-tool",
    description="Tool with nested literal properties",
    inputSchema={
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["limit"]
            }
        },
        "required": ["filter"]
    }
)
"""
    extractor = PythonAstToolExtractor()
    tools = extractor.extract_tools_from_source(code)
    assert len(tools) == 1
    tool = tools[0]
    assert tool["operation_id"] == "nested_tool"
    assert "filter" in tool["input_surface"]["properties"]
    nested = tool["input_surface"]["properties"]["filter"]
    assert nested["properties"]["limit"]["default"] == 10
    assert nested["properties"]["tags"]["items"]["type"] == "string"
