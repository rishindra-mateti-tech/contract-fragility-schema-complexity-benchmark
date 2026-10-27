#!/usr/bin/env python3
"""Python AST Source Normalizer.

Statically normalizes literal AST constructs into pure Python primitive
data structures under PYTHON_AST_STATIC_TOOL_EXTRACTION_POLICY_001.

Enforces:
1. Pure literal evaluation without code execution or importing.
2. Fail-closed rejection of dynamic variables, function calls, spreads,
   f-strings, string concatenations, comprehensions, and attribute accesses.
3. Accurate source line/column span extraction and snippet slicing.
"""

import ast
import hashlib
from typing import Any, Dict, List, Optional, Tuple

POLICY_ID = "PYTHON_AST_STATIC_TOOL_EXTRACTION_POLICY_001"

# Pinned Policy Error Codes
ERR_DYNAMIC_VARIABLE_REJECTED = "ERR_DYNAMIC_VARIABLE_REJECTED"
ERR_COMPUTED_SCHEMA_CONSTRUCTION = "ERR_COMPUTED_SCHEMA_CONSTRUCTION"
ERR_STRING_CONCATENATION_REJECTED = "ERR_STRING_CONCATENATION_REJECTED"
ERR_FSTRING_REJECTED = "ERR_FSTRING_REJECTED"
ERR_NON_LITERAL_SPREAD = "ERR_NON_LITERAL_SPREAD"
ERR_DYNAMIC_ATTRIBUTE_REJECTED = "ERR_DYNAMIC_ATTRIBUTE_REJECTED"
ERR_COMPREHENSION_REJECTED = "ERR_COMPREHENSION_REJECTED"
ERR_UNSUPPORTED_AST_CONSTRUCT = "ERR_UNSUPPORTED_AST_CONSTRUCT"


class PythonAstExtractionError(Exception):
    """Exception raised when Python AST extraction encounters prohibited constructs."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


def get_node_span(node: ast.AST) -> Dict[str, int]:
    """Extract line and column boundaries from an AST node."""
    return {
        "lineno": getattr(node, "lineno", 0),
        "col_offset": getattr(node, "col_offset", 0),
        "end_lineno": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
        "end_col_offset": getattr(node, "end_col_offset", getattr(node, "col_offset", 0)),
    }


def extract_source_snippet(source_text: str, span: Dict[str, int]) -> str:
    """Extract exact substring from source text based on AST line/col span."""
    lines = source_text.splitlines(keepends=True)
    start_line = span["lineno"] - 1
    end_line = span["end_lineno"] - 1

    if start_line < 0 or start_line >= len(lines):
        return ""

    if start_line == end_line:
        line = lines[start_line]
        return line[span["col_offset"] : span["end_col_offset"]]

    parts = []
    parts.append(lines[start_line][span["col_offset"] :])
    for l_idx in range(start_line + 1, end_line):
        parts.append(lines[l_idx])
    if end_line < len(lines):
        parts.append(lines[end_line][: span["end_col_offset"]])

    return "".join(parts)


def normalize_ast_literal(node: ast.AST, source_text: str = "") -> Any:
    """Statically and recursively convert an AST node to a primitive literal.
    
    Rejects any dynamic, computed, or non-literal construct fail-closed.
    """
    span = get_node_span(node)

    # 1. Constant literals (str, int, float, bool, None)
    if isinstance(node, ast.Constant):
        return node.value

    # 2. Literal Dictionaries
    elif isinstance(node, ast.Dict):
        result_dict = {}
        for key_node, val_node in zip(node.keys, node.values):
            # Check for dict unpacking (**kwargs)
            if key_node is None:
                raise PythonAstExtractionError(
                    ERR_NON_LITERAL_SPREAD,
                    "Dictionary unpacking (**spread) is prohibited in literal tool schemas",
                    {"span": span},
                )
            # Keys must be string constants
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                raise PythonAstExtractionError(
                    ERR_UNSUPPORTED_AST_CONSTRUCT,
                    f"Dictionary keys must be literal strings, found: {type(key_node).__name__}",
                    {"span": get_node_span(key_node)},
                )
            key_str = key_node.value
            val_lit = normalize_ast_literal(val_node, source_text)
            result_dict[key_str] = val_lit
        return result_dict

    # 3. Literal Lists and Tuples
    elif isinstance(node, (ast.List, ast.Tuple)):
        result_list = []
        for elt in node.elts:
            if isinstance(elt, ast.Starred):
                raise PythonAstExtractionError(
                    ERR_NON_LITERAL_SPREAD,
                    "List unpacking (*spread) is prohibited in literal tool schemas",
                    {"span": get_node_span(elt)},
                )
            result_list.append(normalize_ast_literal(elt, source_text))
        return result_list

    # 4. Literal Unary operations (e.g. -1)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
        if isinstance(node.operand.value, (int, float)):
            return -node.operand.value
        raise PythonAstExtractionError(
            ERR_UNSUPPORTED_AST_CONSTRUCT,
            "Unary operator USub applied to non-numeric constant",
            {"span": span},
        )

    # 5. Fail-Closed Rejections for Dynamic Constructs
    elif isinstance(node, ast.Name):
        raise PythonAstExtractionError(
            ERR_DYNAMIC_VARIABLE_REJECTED,
            f"Dynamic variable reference '{node.id}' is prohibited in literal tool schema",
            {"variable_name": node.id, "span": span},
        )

    elif isinstance(node, ast.Call):
        raise PythonAstExtractionError(
            ERR_COMPUTED_SCHEMA_CONSTRUCTION,
            "Function calls producing schema values are prohibited",
            {"span": span},
        )

    elif isinstance(node, ast.BinOp):
        raise PythonAstExtractionError(
            ERR_STRING_CONCATENATION_REJECTED,
            "Dynamic string concatenation or binary operators are prohibited in literal tool schemas",
            {"span": span},
        )

    elif isinstance(node, ast.JoinedStr):
        raise PythonAstExtractionError(
            ERR_FSTRING_REJECTED,
            "f-string formatting (JoinedStr) is prohibited in literal tool schemas",
            {"span": span},
        )

    elif isinstance(node, ast.Attribute):
        raise PythonAstExtractionError(
            ERR_DYNAMIC_ATTRIBUTE_REJECTED,
            f"Dynamic attribute access '{node.attr}' is prohibited in literal tool schemas",
            {"attribute": node.attr, "span": span},
        )

    elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
        raise PythonAstExtractionError(
            ERR_COMPREHENSION_REJECTED,
            "Comprehensions are prohibited in literal tool schemas",
            {"span": span},
        )

    else:
        raise PythonAstExtractionError(
            ERR_UNSUPPORTED_AST_CONSTRUCT,
            f"Unsupported AST construct '{type(node).__name__}' in literal schema",
            {"node_type": type(node).__name__, "span": span},
        )
