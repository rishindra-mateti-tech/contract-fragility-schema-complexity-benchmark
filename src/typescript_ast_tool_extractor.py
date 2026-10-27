#!/usr/bin/env python3
"""TypeScript AST Tool Extractor.

Statically extracts Model Context Protocol (MCP) tool declarations
from TypeScript source files under TYPESCRIPT_AST_STATIC_TOOL_EXTRACTION_POLICY_001.

Strict Invariants:
1. Static Tree-sitter AST parsing via tree-sitter and tree-sitter-typescript.
2. Zero runtime execution (no Node.js, Bun, or Deno runtime execution).
3. Zero regex parsing.
4. Generates an intermediate source-neutral tool operation record for literal schemas.
5. Emits structured fail-closed rejections for tools using dynamic schema builders or imports.
"""

import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
import tree_sitter
import tree_sitter_typescript

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.typescript_ast_source_normalizer import (
    POLICY_ID,
    TypeScriptAstExtractionError,
    get_ts_node_span,
    extract_ts_source_snippet,
    normalize_ts_literal,
    ERR_UNSUPPORTED_TS_AST_CONSTRUCT,
    ERR_RUNTIME_SCHEMA_BUILDER_REJECTED,
)

PARSER_VERSION = "tree-sitter:0.25.2:tree-sitter-typescript:0.23.2"


class TypeScriptAstToolExtractor:
    """Deterministic, static extractor for TypeScript MCP tool definitions."""

    def __init__(self, policy_id: str = POLICY_ID):
        self.policy_id = policy_id
        self.parser_version = PARSER_VERSION
        self.language = tree_sitter.Language(tree_sitter_typescript.language_typescript())
        self.parser = tree_sitter.Parser(self.language)

    def extract_tools_from_source(
        self,
        source_code: str,
        source_file_path: str = "index.ts",
        source_file_blob_sha: Optional[str] = None,
        source_file_sha256: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse source code statically and extract literal tools or record fail-closed rejections."""
        source_bytes = source_code.encode("utf-8")
        if source_file_sha256 is None:
            source_file_sha256 = hashlib.sha256(source_bytes).hexdigest()
        if source_file_blob_sha is None:
            header = f"blob {len(source_bytes)}\0".encode("utf-8")
            source_file_blob_sha = hashlib.sha1(header + source_bytes).hexdigest()

        tree = self.parser.parse(source_bytes)

        extracted_tools: List[Dict[str, Any]] = []
        rejected_tools: List[Dict[str, Any]] = []

        # Find tool object literals: { name: "...", inputSchema: ... }
        def walk_for_tools(node: tree_sitter.Node, ast_path: str = "Program"):
            if node.type == "object":
                pairs = {}
                for child in node.children:
                    if child.type == "pair":
                        k_node = child.child_by_field_name("key")
                        v_node = child.child_by_field_name("value")
                        if k_node and v_node:
                            k_text = extract_ts_source_snippet(source_bytes, k_node).strip().strip("\"'")
                            pairs[k_text] = (k_node, v_node)

                if "name" in pairs and "inputSchema" in pairs:
                    name_k_node, name_v_node = pairs["name"]
                    schema_k_node, schema_v_node = pairs["inputSchema"]

                    # Extract name string
                    name_raw = extract_ts_source_snippet(source_bytes, name_v_node).strip().strip("\"'")
                    tool_ast_path = f"{ast_path}/Object[Tool:{name_raw}]"
                    tool_span = get_ts_node_span(node)
                    tool_snippet = extract_ts_source_snippet(source_bytes, node)
                    tool_snippet_sha256 = hashlib.sha256(tool_snippet.encode("utf-8")).hexdigest()

                    # Extract optional description
                    desc_text = ""
                    if "description" in pairs:
                        desc_text = extract_ts_source_snippet(source_bytes, pairs["description"][1]).strip().strip("\"'")

                    # Attempt literal schema normalization
                    try:
                        normalized_schema = normalize_ts_literal(schema_v_node, source_bytes)
                        if not isinstance(normalized_schema, dict):
                            raise TypeScriptAstExtractionError(
                                ERR_UNSUPPORTED_TS_AST_CONSTRUCT,
                                f"Tool '{name_raw}' inputSchema must be a dictionary literal, got {type(normalized_schema).__name__}",
                                {"span": get_ts_node_span(schema_v_node)},
                            )

                        schema_type = normalized_schema.get("type", "object")
                        properties = normalized_schema.get("properties", {})
                        required = normalized_schema.get("required", [])

                        extracted_tools.append({
                            "operation_id": name_raw,
                            "raw_tool_name": name_raw,
                            "description": desc_text,
                            "source_dialect": "TypeScript AST",
                            "source_file_path": source_file_path.replace("\\", "/"),
                            "source_file_blob_sha": source_file_blob_sha,
                            "source_file_sha256": source_file_sha256,
                            "source_spec_pointer": f"{source_file_path.replace('\\', '/')}:{name_raw}",
                            "input_surface": {
                                "type": schema_type,
                                "properties": properties,
                                "required": required,
                                "additionalProperties": False,
                            },
                            "static_source_evidence": {
                                "ast_node_kind": "object",
                                "ast_path": tool_ast_path,
                                "span": tool_span,
                                "source_snippet": tool_snippet.strip(),
                                "source_snippet_sha256": tool_snippet_sha256,
                                "parser_name": "tree-sitter:typescript",
                                "parser_version": self.parser_version,
                            },
                            "adapter_decisions": [
                                {
                                    "adapter_name": "TypeScriptAstToolExtractor",
                                    "action": "STATIC_LITERAL_EXTRACTION",
                                    "reason": "Statically extracted literal tool schema from TypeScript AST without runtime execution.",
                                },
                            ],
                            "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
                            "governing_policy_id": self.policy_id,
                        })

                    except TypeScriptAstExtractionError as e:
                        schema_span = get_ts_node_span(schema_v_node)
                        schema_snippet = extract_ts_source_snippet(source_bytes, schema_v_node).strip()
                        rejected_tools.append({
                            "operation_id": name_raw,
                            "raw_tool_name": name_raw,
                            "source_file_path": source_file_path.replace("\\", "/"),
                            "rejection_code": e.code,
                            "rejection_category": "DYNAMIC_SCHEMA_CONSTRUCT",
                            "rationale": e.message,
                            "static_evidence": {
                                "ast_node_kind": schema_v_node.type,
                                "ast_path": f"{tool_ast_path}/inputSchema:{schema_v_node.type}",
                                "span": schema_span,
                                "source_snippet": schema_snippet,
                                "source_snippet_sha256": hashlib.sha256(schema_snippet.encode("utf-8")).hexdigest(),
                            },
                        })

            # Recurse children
            for child in node.children:
                child_path = f"{ast_path}/{node.type}"
                walk_for_tools(child, child_path)

        walk_for_tools(tree.root_node)

        return {
            "source_file_path": source_file_path.replace("\\", "/"),
            "source_file_blob_sha": source_file_blob_sha,
            "source_file_sha256": source_file_sha256,
            "tools_extracted_count": len(extracted_tools),
            "tools_rejected_count": len(rejected_tools),
            "tools_extracted": extracted_tools,
            "tools_rejected": rejected_tools,
        }

    def extract_tools_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract tools from a TypeScript source file on disk."""
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        return self.extract_tools_from_source(
            source_code=src,
            source_file_path=file_path,
        )
