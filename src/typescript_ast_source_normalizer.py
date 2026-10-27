#!/usr/bin/env python3
"""TypeScript AST Source Normalizer.

Statically normalizes literal Tree-sitter TypeScript AST nodes into
pure Python primitive data structures under TYPESCRIPT_AST_STATIC_TOOL_EXTRACTION_POLICY_001.

Strict Invariants:
1. Pure static AST traversal via Tree-sitter without Node.js runtime execution.
2. Fail-closed rejection of runtime schema builders (zodToJsonSchema),
   function calls, object spreads, computed property names, and imported variables.
3. Accurate source line/column span extraction and snippet hashing.
"""

import hashlib
from typing import Any, Dict, List, Optional
import tree_sitter

POLICY_ID = "TYPESCRIPT_AST_STATIC_TOOL_EXTRACTION_POLICY_001"

# Pinned Policy Error Codes
ERR_DYNAMIC_EXPRESSION_REJECTED = "ERR_DYNAMIC_EXPRESSION_REJECTED"
ERR_UNKNOWN_SPREAD_REJECTED = "ERR_UNKNOWN_SPREAD_REJECTED"
ERR_COMPUTED_PROPERTY_REJECTED = "ERR_COMPUTED_PROPERTY_REJECTED"
ERR_RUNTIME_SCHEMA_BUILDER_REJECTED = "ERR_RUNTIME_SCHEMA_BUILDER_REJECTED"
ERR_IMPORTED_SCHEMA_REJECTED = "ERR_IMPORTED_SCHEMA_REJECTED"
ERR_FUNCTION_CALL_SCHEMA_REJECTED = "ERR_FUNCTION_CALL_SCHEMA_REJECTED"
ERR_UNRESOLVED_ALIAS_REJECTED = "ERR_UNRESOLVED_ALIAS_REJECTED"
ERR_UNSUPPORTED_TS_AST_CONSTRUCT = "ERR_UNSUPPORTED_TS_AST_CONSTRUCT"


class TypeScriptAstExtractionError(Exception):
    """Exception raised when TypeScript AST extraction encounters prohibited constructs."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


def get_ts_node_span(node: tree_sitter.Node) -> Dict[str, int]:
    """Extract 1-indexed line and 0-indexed column span from a Tree-sitter node."""
    return {
        "lineno": node.start_point.row + 1,
        "col_offset": node.start_point.column,
        "end_lineno": node.end_point.row + 1,
        "end_col_offset": node.end_point.column,
    }


def extract_ts_source_snippet(source_bytes: bytes, node: tree_sitter.Node) -> str:
    """Extract raw snippet text from source bytes for a node."""
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def normalize_ts_literal(node: tree_sitter.Node, source_bytes: bytes) -> Any:
    """Statically and recursively convert a Tree-sitter node to a primitive literal.
    
    Rejects any dynamic, computed, or non-literal construct fail-closed.
    """
    span = get_ts_node_span(node)
    node_type = node.type

    # 1. String Literals
    if node_type == "string":
        raw = extract_ts_source_snippet(source_bytes, node)
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            return raw[1:-1]
        return raw

    elif node_type == "string_fragment":
        return extract_ts_source_snippet(source_bytes, node)

    # 2. Number Literals
    elif node_type == "number":
        raw = extract_ts_source_snippet(source_bytes, node).strip()
        try:
            if "." in raw or "e" in raw.lower():
                return float(raw)
            return int(raw)
        except ValueError:
            raise TypeScriptAstExtractionError(
                ERR_UNSUPPORTED_TS_AST_CONSTRUCT,
                f"Invalid numeric literal: {raw}",
                {"span": span},
            )

    # 3. Boolean Literals
    elif node_type == "true":
        return True
    elif node_type == "false":
        return False

    # 4. Null / Undefined
    elif node_type in ["null", "undefined"]:
        return None

    # 5. Object Literals
    elif node_type == "object":
        result_dict = {}
        for child in node.children:
            if child.type == "pair":
                key_node = child.child_by_field_name("key")
                val_node = child.child_by_field_name("value")

                if not key_node or not val_node:
                    continue

                # Check for computed property name ([key]: val)
                if key_node.type == "computed_property_name":
                    raise TypeScriptAstExtractionError(
                        ERR_COMPUTED_PROPERTY_REJECTED,
                        "Computed property names are prohibited in literal tool schemas",
                        {"span": get_ts_node_span(key_node)},
                    )

                # Extract key string
                key_text = extract_ts_source_snippet(source_bytes, key_node).strip()
                if (key_text.startswith('"') and key_text.endswith('"')) or (key_text.startswith("'") and key_text.endswith("'")):
                    key_text = key_text[1:-1]

                val_lit = normalize_ts_literal(val_node, source_bytes)
                result_dict[key_text] = val_lit

            elif child.type == "spread_element":
                raise TypeScriptAstExtractionError(
                    ERR_UNKNOWN_SPREAD_REJECTED,
                    "Object spread elements (...spread) are prohibited in literal tool schemas",
                    {"span": get_ts_node_span(child)},
                )

        return result_dict

    # 6. Array Literals
    elif node_type == "array":
        result_list = []
        for child in node.children:
            if child.type in ["[", "]", ","]:
                continue
            if child.type == "spread_element":
                raise TypeScriptAstExtractionError(
                    ERR_UNKNOWN_SPREAD_REJECTED,
                    "Array spread elements (...spread) are prohibited in literal tool schemas",
                    {"span": get_ts_node_span(child)},
                )
            result_list.append(normalize_ts_literal(child, source_bytes))
        return result_list

    # 7. Unary Expression (e.g. -1)
    elif node_type == "unary_expression":
        op_node = child_by_field = node.children[0] if node.children else None
        arg_node = node.child_by_field_name("argument")
        if op_node and op_node.type == "-" and arg_node and arg_node.type == "number":
            val = normalize_ts_literal(arg_node, source_bytes)
            return -val
        raise TypeScriptAstExtractionError(
            ERR_UNSUPPORTED_TS_AST_CONSTRUCT,
            "Unary expression other than negative number literal is prohibited",
            {"span": span},
        )

    # 8. Dynamic Function Calls and Runtime Schema Builders
    elif node_type == "call_expression":
        fn_node = node.child_by_field_name("function")
        fn_name = extract_ts_source_snippet(source_bytes, fn_node) if fn_node else ""
        if "zod" in fn_name.lower():
            raise TypeScriptAstExtractionError(
                ERR_RUNTIME_SCHEMA_BUILDER_REJECTED,
                f"Dynamic runtime schema builder '{fn_name}' cannot be resolved statically without code execution",
                {"function_name": fn_name, "span": span},
            )
        raise TypeScriptAstExtractionError(
            ERR_FUNCTION_CALL_SCHEMA_REJECTED,
            f"Function call '{fn_name}' producing schema is prohibited",
            {"function_name": fn_name, "span": span},
        )

    # 9. Dynamic Identifiers / Imported Variables
    elif node_type == "identifier":
        ident_name = extract_ts_source_snippet(source_bytes, node).strip()
        raise TypeScriptAstExtractionError(
            ERR_IMPORTED_SCHEMA_REJECTED,
            f"Dynamic variable or imported schema identifier '{ident_name}' cannot be resolved statically",
            {"identifier": ident_name, "span": span},
        )

    # 10. Template Strings and Binary Expressions
    elif node_type in ["template_string", "binary_expression"]:
        raise TypeScriptAstExtractionError(
            ERR_DYNAMIC_EXPRESSION_REJECTED,
            f"Dynamic string template or expression of type '{node_type}' is prohibited",
            {"span": span},
        )

    else:
        raise TypeScriptAstExtractionError(
            ERR_UNSUPPORTED_TS_AST_CONSTRUCT,
            f"Unsupported TypeScript AST construct '{node_type}' in literal schema",
            {"node_type": node_type, "span": span},
        )
