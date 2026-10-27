#!/usr/bin/env python3
"""Python AST Tool Extractor.

Statically extracts Model Context Protocol (MCP) tool declarations
from Python source files under PYTHON_AST_STATIC_TOOL_EXTRACTION_POLICY_001.

Strict Invariants:
1. Pure static AST parsing via Python built-in `ast` module.
2. Zero runtime execution, importing, or dynamic evaluation.
3. Zero regex parsing.
4. Generates an intermediate source-neutral tool operation record.
5. Captures exact line/column spans, source snippet SHA-256, and AST path.
"""

import ast
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.python_ast_source_normalizer import (
    POLICY_ID,
    PythonAstExtractionError,
    get_node_span,
    extract_source_snippet,
    normalize_ast_literal,
    ERR_UNSUPPORTED_AST_CONSTRUCT,
)
from src.stage_b_candidate_manifest import (
    sha256_file,
    git_blob_sha,
)


class PythonAstToolExtractor:
    """Deterministic, static extractor for Python MCP tool definitions."""

    def __init__(self, policy_id: str = POLICY_ID):
        self.policy_id = policy_id
        self.parser_version = f"python-{sys.version.split()[0]}:ast"

    def extract_tools_from_source(
        self,
        source_code: str,
        source_file_path: str = "server.py",
        source_file_blob_sha: Optional[str] = None,
        source_file_sha256: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Parse source code statically and extract all valid literal MCP tools."""
        raw_bytes = source_code.encode("utf-8")
        if source_file_sha256 is None:
            source_file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        if source_file_blob_sha is None:
            header = f"blob {len(raw_bytes)}\0".encode("utf-8")
            source_file_blob_sha = hashlib.sha1(header + raw_bytes).hexdigest()

        try:
            tree = ast.parse(source_code, filename=source_file_path)
        except SyntaxError as e:
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                f"Syntax error parsing Python source {source_file_path}: {e}",
                {"line": e.lineno, "offset": e.offset},
            )

        extracted_tools: List[Dict[str, Any]] = []

        # Walk AST tracking parent hierarchy for AST path construction
        parent_map: Dict[ast.AST, Tuple[ast.AST, str]] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parent_map[child] = (parent, type(parent).__name__)

        def build_ast_path(node: ast.AST) -> str:
            path_segments = []
            curr: Optional[ast.AST] = node
            while curr is not None:
                seg_name = type(curr).__name__
                if isinstance(curr, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    seg_name += f"[{curr.name}]"
                elif isinstance(curr, ast.ClassDef):
                    seg_name += f"[{curr.name}]"
                path_segments.append(seg_name)
                curr_parent = parent_map.get(curr)
                curr = curr_parent[0] if curr_parent else None
            return "/".join(reversed(path_segments))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = f"{ast.unparse(node.func.value)}.{node.func.attr}"
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id

                # Match types.Tool(...) or Tool(...)
                if func_name in ["types.Tool", "Tool"] or func_name.endswith(".Tool"):
                    tool_record = self._extract_single_tool(
                        node=node,
                        source_code=source_code,
                        source_file_path=source_file_path,
                        source_file_blob_sha=source_file_blob_sha,
                        source_file_sha256=source_file_sha256,
                        ast_path=build_ast_path(node),
                    )
                    extracted_tools.append(tool_record)

        return extracted_tools

    def _extract_single_tool(
        self,
        node: ast.Call,
        source_code: str,
        source_file_path: str,
        source_file_blob_sha: str,
        source_file_sha256: str,
        ast_path: str,
    ) -> Dict[str, Any]:
        """Extract tool properties and argument schema from a single Tool call node."""
        span = get_node_span(node)
        raw_snippet = extract_source_snippet(source_code, span)
        snippet_sha256 = hashlib.sha256(raw_snippet.encode("utf-8")).hexdigest()

        # Parse kwargs
        kwargs: Dict[str, ast.AST] = {k.arg: k.value for k in node.keywords if k.arg is not None}

        # 1. Tool Name
        if "name" not in kwargs:
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                "Tool call missing mandatory 'name' keyword argument",
                {"span": span},
            )
        raw_name = normalize_ast_literal(kwargs["name"], source_code)
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                f"Tool name must be a non-empty string literal, got {raw_name}",
                {"span": span},
            )

        # Normalize name for operation id (hyphens to underscores)
        normalized_op_id = raw_name.replace("-", "_")

        # 2. Tool Description
        description = ""
        if "description" in kwargs:
            desc_val = normalize_ast_literal(kwargs["description"], source_code)
            if isinstance(desc_val, str):
                description = desc_val

        # 3. Input Schema
        if "inputSchema" not in kwargs:
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                f"Tool '{raw_name}' missing mandatory 'inputSchema' keyword argument",
                {"span": span},
            )

        raw_input_schema = normalize_ast_literal(kwargs["inputSchema"], source_code)
        if not isinstance(raw_input_schema, dict):
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                f"Tool '{raw_name}' inputSchema must be a dictionary literal, got {type(raw_input_schema).__name__}",
                {"span": span},
            )

        schema_type = raw_input_schema.get("type", "object")
        properties = raw_input_schema.get("properties", {})
        required = raw_input_schema.get("required", [])

        if not isinstance(properties, dict):
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                f"Tool '{raw_name}' properties must be a dictionary literal",
                {"span": span},
            )
        if not isinstance(required, list):
            raise PythonAstExtractionError(
                ERR_UNSUPPORTED_AST_CONSTRUCT,
                f"Tool '{raw_name}' required must be a list literal",
                {"span": span},
            )

        # Build intermediate representation
        return {
            "operation_id": normalized_op_id,
            "raw_tool_name": raw_name,
            "description": description,
            "source_dialect": "Python 3 AST",
            "source_file_path": source_file_path.replace("\\", "/"),
            "source_file_blob_sha": source_file_blob_sha,
            "source_file_sha256": source_file_sha256,
            "source_spec_pointer": f"{os.path.basename(source_file_path)}:list_tools:{raw_name}",
            "input_surface": {
                "type": schema_type,
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
            "static_source_evidence": {
                "ast_node_kind": "ast.Call",
                "ast_path": f"{ast_path}/Call[types.Tool:{raw_name}]",
                "span": span,
                "source_snippet": raw_snippet.strip(),
                "source_snippet_sha256": snippet_sha256,
                "parser_name": "python:built-in:ast",
                "parser_version": self.parser_version,
            },
            "adapter_decisions": [
                {
                    "adapter_name": "PythonAstToolExtractor",
                    "action": "STATIC_LITERAL_EXTRACTION",
                    "reason": "Statically extracted literal Tool call schema from Python AST without code execution.",
                },
                {
                    "adapter_name": "PythonAstToolExtractor",
                    "action": "TOOL_SURFACE_SYNTHESIS",
                    "reason": "Normalized inputSchema dictionary into closed object container (additionalProperties: false).",
                },
            ],
            "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "governing_policy_id": self.policy_id,
        }

    def extract_tools_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract all tools from a Python file on disk."""
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        return self.extract_tools_from_source(
            source_code=src,
            source_file_path=file_path,
        )
