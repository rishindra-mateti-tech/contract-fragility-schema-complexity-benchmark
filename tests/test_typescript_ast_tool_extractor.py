#!/usr/bin/env python3
"""Tests for TypeScript AST Static Tool Extraction Adapter."""

import os
import pytest
from src.typescript_ast_tool_extractor import TypeScriptAstToolExtractor
from src.typescript_ast_source_normalizer import (
    TypeScriptAstExtractionError,
    ERR_UNKNOWN_SPREAD_REJECTED,
    ERR_COMPUTED_PROPERTY_REJECTED,
    ERR_RUNTIME_SCHEMA_BUILDER_REJECTED,
    ERR_IMPORTED_SCHEMA_REJECTED,
    ERR_FUNCTION_CALL_SCHEMA_REJECTED,
    ERR_DYNAMIC_EXPRESSION_REJECTED,
)

CAND_010_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data_stage_b",
    "raw",
    "CAND-010",
    "0676a34c85537e610f911fbd73a5a079f38be18e.ts",
)


def test_cand_010_dynamic_schema_fail_closed_rejections():
    """Verify that CAND-010 tools using zodToJsonSchema are rejected fail-closed."""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_file(CAND_010_FILE)
    assert res["tools_extracted_count"] == 0
    assert res["tools_rejected_count"] >= 3

    rej_map = {r["operation_id"]: r for r in res["tools_rejected"]}
    for op_id in ["search_repositories", "create_issue", "create_or_update_file"]:
        assert op_id in rej_map
        rej = rej_map[op_id]
        assert rej["rejection_code"] == ERR_RUNTIME_SCHEMA_BUILDER_REJECTED
        assert rej["rejection_category"] == "DYNAMIC_SCHEMA_CONSTRUCT"
        assert "zod" in rej["static_evidence"]["source_snippet"].lower()
        assert rej["static_evidence"]["span"]["lineno"] > 0
        assert len(rej["static_evidence"]["source_snippet_sha256"]) == 64


def test_literal_typescript_tool_extraction():
    """Verify that a tool declared with literal schema is extracted successfully."""
    ts_code = """
const tools = [
  {
    name: "literal_tool",
    description: "A tool with a statically literal input schema",
    inputSchema: {
      type: "object",
      properties: {
        repo: { type: "string", description: "Repository name" },
        count: { type: "number", default: 5 }
      },
      required: ["repo"]
    }
  }
];
"""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_source(ts_code, "test.ts")
    assert res["tools_extracted_count"] == 1
    assert res["tools_rejected_count"] == 0

    tool = res["tools_extracted"][0]
    assert tool["operation_id"] == "literal_tool"
    assert tool["source_dialect"] == "TypeScript AST"
    assert tool["input_surface"]["type"] == "object"
    assert tool["input_surface"]["additionalProperties"] is False
    assert tool["input_surface"]["required"] == ["repo"]
    assert "repo" in tool["input_surface"]["properties"]
    assert tool["input_surface"]["properties"]["count"]["default"] == 5

    evidence = tool["static_source_evidence"]
    assert evidence["ast_node_kind"] == "object"
    assert evidence["span"]["lineno"] > 0
    assert len(evidence["source_snippet_sha256"]) == 64


def test_reject_unknown_object_spread():
    """Verify rejection of object spread (...spread) in tool schema."""
    ts_code = """
const tools = [
  {
    name: "spread_tool",
    inputSchema: {
      type: "object",
      ...extraSchema
    }
  }
];
"""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_source(ts_code, "test.ts")
    assert res["tools_extracted_count"] == 0
    assert res["tools_rejected_count"] == 1
    assert res["tools_rejected"][0]["rejection_code"] == ERR_UNKNOWN_SPREAD_REJECTED


def test_reject_computed_property_key():
    """Verify rejection of computed property key ([computedKey]: val)."""
    ts_code = """
const tools = [
  {
    name: "computed_tool",
    inputSchema: {
      type: "object",
      properties: {
        [DYNAMIC_KEY]: { type: "string" }
      }
    }
  }
];
"""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_source(ts_code, "test.ts")
    assert res["tools_extracted_count"] == 0
    assert res["tools_rejected_count"] == 1
    assert res["tools_rejected"][0]["rejection_code"] == ERR_COMPUTED_PROPERTY_REJECTED


def test_reject_imported_variable_schema():
    """Verify rejection of direct identifier reference as schema."""
    ts_code = """
import { MySchema } from './schemas.js';
const tools = [
  {
    name: "imported_tool",
    inputSchema: MySchema
  }
];
"""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_source(ts_code, "test.ts")
    assert res["tools_extracted_count"] == 0
    assert res["tools_rejected_count"] == 1
    assert res["tools_rejected"][0]["rejection_code"] == ERR_IMPORTED_SCHEMA_REJECTED


def test_reject_arbitrary_function_call_schema():
    """Verify rejection of function-call-produced schemas."""
    ts_code = """
function buildSchema() { return { type: "object" }; }
const tools = [
  {
    name: "fn_call_tool",
    inputSchema: buildSchema()
  }
];
"""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_source(ts_code, "test.ts")
    assert res["tools_extracted_count"] == 0
    assert res["tools_rejected_count"] == 1
    assert res["tools_rejected"][0]["rejection_code"] == ERR_FUNCTION_CALL_SCHEMA_REJECTED


def test_preserve_nested_typescript_schema():
    """Verify nested objects and arrays are preserved in TypeScript AST."""
    ts_code = """
const tools = [
  {
    name: "nested_ts_tool",
    inputSchema: {
      type: "object",
      properties: {
        meta: {
          type: "object",
          properties: {
            tags: { type: "array", items: { type: "string" } }
          }
        }
      }
    }
  }
];
"""
    extractor = TypeScriptAstToolExtractor()
    res = extractor.extract_tools_from_source(ts_code, "test.ts")
    assert res["tools_extracted_count"] == 1
    tool = res["tools_extracted"][0]
    meta = tool["input_surface"]["properties"]["meta"]
    assert meta["type"] == "object"
    assert meta["properties"]["tags"]["type"] == "array"
