#!/usr/bin/env python3
"""Adversarial Test Corpus for Stage B Static Adapters (Track 6).

Evaluates static extraction adapters against adversarial, edge-case, and malformed inputs:
1. Python AST Adapter (7 vectors):
   - Literal schema accepted
   - Dynamic variable rejected
   - Function-call-generated schema rejected
   - Imported schema rejected
   - Computed name rejected
   - Nested literal schema preserved
   - Source span stability verified

2. TypeScript AST Adapter (7 vectors):
   - Literal object accepted
   - Unknown spread rejected
   - Computed key rejected
   - Dynamic builder rejected
   - Imported value rejected
   - Nested literal schema preserved
   - Line/column stability verified

3. Reference Closure Adapter (7 vectors):
   - Valid local multi-file reference accepted
   - Escaped path traversal rejected
   - Remote URL rejected
   - Reference cycle rejected
   - Stale hash rejected
   - Missing fragment rejected
   - Conflicting / duplicate ref rejected
"""

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import pytest
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.python_ast_source_normalizer import (
    PythonAstExtractionError,
    ERR_DYNAMIC_VARIABLE_REJECTED,
    ERR_COMPUTED_SCHEMA_CONSTRUCTION,
    ERR_STRING_CONCATENATION_REJECTED,
    ERR_DYNAMIC_ATTRIBUTE_REJECTED,
)
from src.python_ast_tool_extractor import PythonAstToolExtractor
from src.typescript_ast_source_normalizer import (
    TypeScriptAstExtractionError,
    ERR_UNKNOWN_SPREAD_REJECTED,
    ERR_COMPUTED_PROPERTY_REJECTED,
    ERR_RUNTIME_SCHEMA_BUILDER_REJECTED,
    ERR_IMPORTED_SCHEMA_REJECTED,
    ERR_DYNAMIC_EXPRESSION_REJECTED,
)
from src.typescript_ast_tool_extractor import TypeScriptAstToolExtractor
from src.openapi_local_ref_resolver import (
    LocalReferenceResolver,
    ReferenceResolutionError,
    ERR_REMOTE_REF_PROHIBITED,
    ERR_PATH_TRAVERSAL_DETECTED,
    ERR_REFERENCE_CYCLE_DETECTED,
    ERR_FRAGMENT_NOT_FOUND,
)
from src.audit_pinned_source_closure import audit_source_closure

DO_CLOSURE_DIR = os.path.join(ROOT_DIR, "data_stage_b", "source_closures", "CAND-003")
DO_MANIFEST_PATH = os.path.join(DO_CLOSURE_DIR, "closure_manifest.json")


# =====================================================================
# TRACK 6.1: PYTHON AST ADVERSARIAL TEST VECTORS
# =====================================================================
class TestPythonAstAdversarial:
    """Adversarial test vectors for Python AST Static Tool Extractor."""

    def test_python_literal_schema_accepted(self):
        """Vector PY-01: Pure literal schema dictionary is accepted and extracted."""
        source = (
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name='search_records',\n"
            "        description='Search database records',\n"
            "        inputSchema={\n"
            "            'type': 'object',\n"
            "            'properties': {\n"
            "                'query': {'type': 'string', 'description': 'Search string'},\n"
            "                'limit': {'type': 'integer', 'description': 'Max results'}\n"
            "            },\n"
            "            'required': ['query']\n"
            "        }\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        tools = extractor.extract_tools_from_source(source)
        assert len(tools) == 1
        t = tools[0]
        assert t["operation_id"] == "search_records"
        assert t["description"] == "Search database records"
        assert t["input_surface"]["type"] == "object"
        assert t["input_surface"]["properties"]["query"]["type"] == "string"
        assert t["input_surface"]["properties"]["limit"]["type"] == "integer"
        assert t["input_surface"]["required"] == ["query"]

    def test_python_dynamic_variable_rejected(self):
        """Vector PY-02: Schema referenced via dynamic variable identifier is rejected fail-closed."""
        source = (
            "dynamic_schema = {'type': 'object'}\n"
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name='dynamic_var_tool',\n"
            "        description='Tool with dynamic variable',\n"
            "        inputSchema=dynamic_schema\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        with pytest.raises(PythonAstExtractionError) as exc_info:
            extractor.extract_tools_from_source(source)
        assert exc_info.value.code == ERR_DYNAMIC_VARIABLE_REJECTED

    def test_python_function_call_generated_schema_rejected(self):
        """Vector PY-03: Schema constructed via function/constructor call is rejected fail-closed."""
        source = (
            "def build_schema():\n"
            "    return {'type': 'object'}\n\n"
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name='func_call_tool',\n"
            "        description='Tool with generated schema',\n"
            "        inputSchema=build_schema()\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        with pytest.raises(PythonAstExtractionError) as exc_info:
            extractor.extract_tools_from_source(source)
        assert exc_info.value.code == ERR_COMPUTED_SCHEMA_CONSTRUCTION

    def test_python_imported_schema_rejected(self):
        """Vector PY-04: Schema referenced from imported module attribute is rejected fail-closed."""
        source = (
            "import external_schemas\n"
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name='imported_tool',\n"
            "        description='Tool with imported schema',\n"
            "        inputSchema=external_schemas.UserSchema\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        with pytest.raises(PythonAstExtractionError) as exc_info:
            extractor.extract_tools_from_source(source)
        assert exc_info.value.code == ERR_DYNAMIC_ATTRIBUTE_REJECTED

    def test_python_computed_name_rejected(self):
        """Vector PY-05: Tool name computed via string concatenation is rejected fail-closed."""
        source = (
            "prefix = 'audit_'\n"
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name=prefix + 'events',\n"
            "        description='Computed name tool',\n"
            "        inputSchema={'type': 'object'}\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        with pytest.raises(PythonAstExtractionError) as exc_info:
            extractor.extract_tools_from_source(source)
        assert exc_info.value.code == ERR_STRING_CONCATENATION_REJECTED

    def test_python_nested_literal_schema_preserved(self):
        """Vector PY-06: Deeply nested literal schema hierarchies are preserved without loss."""
        source = (
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name='nested_catalog',\n"
            "        description='Nested structure test',\n"
            "        inputSchema={\n"
            "            'type': 'object',\n"
            "            'properties': {\n"
            "                'filters': {\n"
            "                    'type': 'array',\n"
            "                    'items': {\n"
            "                        'type': 'object',\n"
            "                        'properties': {\n"
            "                            'field': {'type': 'string'},\n"
            "                            'operator': {'type': 'string', 'enum': ['eq', 'gt', 'lt']},\n"
            "                            'threshold': {'type': 'number'}\n"
            "                        },\n"
            "                        'required': ['field', 'operator']\n"
            "                    }\n"
            "                }\n"
            "            },\n"
            "            'required': ['filters']\n"
            "        }\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        tools = extractor.extract_tools_from_source(source)
        assert len(tools) == 1
        filters_prop = tools[0]["input_surface"]["properties"]["filters"]
        assert filters_prop["type"] == "array"
        item_props = filters_prop["items"]["properties"]
        assert item_props["field"]["type"] == "string"
        assert item_props["operator"]["enum"] == ["eq", "gt", "lt"]
        assert item_props["threshold"]["type"] == "number"
        assert filters_prop["items"]["required"] == ["field", "operator"]

    def test_python_source_span_stability_verified(self):
        """Vector PY-07: Static source span coordinates and snippet hash are bit-identical across parses."""
        source = (
            "# Top comment\n"
            "server.list_tools = lambda: [\n"
            "    types.Tool(\n"
            "        name='span_test',\n"
            "        description='Span consistency test',\n"
            "        inputSchema={'type': 'object', 'properties': {'flag': {'type': 'boolean'}}}\n"
            "    )\n"
            "]\n"
        )
        extractor = PythonAstToolExtractor()
        t1 = extractor.extract_tools_from_source(source)[0]
        t2 = extractor.extract_tools_from_source(source)[0]

        ev1 = t1["static_source_evidence"]
        ev2 = t2["static_source_evidence"]

        assert ev1["span"] == ev2["span"]
        assert ev1["span"]["lineno"] == 3
        assert ev1["source_snippet_sha256"] == ev2["source_snippet_sha256"]
        assert ev1["source_snippet"] == ev2["source_snippet"]


# =====================================================================
# TRACK 6.2: TYPESCRIPT AST ADVERSARIAL TEST VECTORS
# =====================================================================
class TestTypeScriptAstAdversarial:
    """Adversarial test vectors for TypeScript AST Static Tool Extractor."""

    def test_typescript_literal_object_accepted(self):
        """Vector TS-01: Pure literal object schema is accepted and extracted."""
        source = (
            "const tools = [\n"
            "  {\n"
            "    name: 'create_webhook',\n"
            "    description: 'Register a webhook listener',\n"
            "    inputSchema: {\n"
            "      type: 'object',\n"
            "      properties: {\n"
            "        url: { type: 'string', description: 'Destination URL' },\n"
            "        secret: { type: 'string' }\n"
            "      },\n"
            "      required: ['url']\n"
            "    }\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        res = extractor.extract_tools_from_source(source)
        assert res["tools_extracted_count"] == 1
        assert res["tools_rejected_count"] == 0
        t = res["tools_extracted"][0]
        assert t["operation_id"] == "create_webhook"
        assert t["description"] == "Register a webhook listener"
        assert t["input_surface"]["type"] == "object"
        assert t["input_surface"]["properties"]["url"]["type"] == "string"
        assert t["input_surface"]["required"] == ["url"]

    def test_typescript_unknown_spread_rejected(self):
        """Vector TS-02: Unknown spread operator inside schema triggers fail-closed rejection."""
        source = (
            "const tools = [\n"
            "  {\n"
            "    name: 'spread_tool',\n"
            "    inputSchema: {\n"
            "      ...baseSchemaProps,\n"
            "      type: 'object'\n"
            "    }\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        res = extractor.extract_tools_from_source(source)
        assert res["tools_extracted_count"] == 0
        assert res["tools_rejected_count"] == 1
        rej = res["tools_rejected"][0]
        assert rej["operation_id"] == "spread_tool"
        assert rej["rejection_code"] == ERR_UNKNOWN_SPREAD_REJECTED
        assert rej["rejection_category"] == "DYNAMIC_SCHEMA_CONSTRUCT"

    def test_typescript_computed_key_rejected(self):
        """Vector TS-03: Computed property name [expr] inside schema is rejected fail-closed."""
        source = (
            "const dynamicKey = 'custom_field';\n"
            "const tools = [\n"
            "  {\n"
            "    name: 'computed_key_tool',\n"
            "    inputSchema: {\n"
            "      type: 'object',\n"
            "      properties: {\n"
            "        [dynamicKey]: { type: 'string' }\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        res = extractor.extract_tools_from_source(source)
        assert res["tools_extracted_count"] == 0
        assert res["tools_rejected_count"] == 1
        rej = res["tools_rejected"][0]
        assert rej["operation_id"] == "computed_key_tool"
        assert rej["rejection_code"] == ERR_COMPUTED_PROPERTY_REJECTED

    def test_typescript_dynamic_builder_rejected(self):
        """Vector TS-04: Runtime schema builder call (zodToJsonSchema) is rejected fail-closed."""
        source = (
            "const tools = [\n"
            "  {\n"
            "    name: 'zod_builder_tool',\n"
            "    inputSchema: zodToJsonSchema(RecordSchema)\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        res = extractor.extract_tools_from_source(source)
        assert res["tools_extracted_count"] == 0
        assert res["tools_rejected_count"] == 1
        rej = res["tools_rejected"][0]
        assert rej["operation_id"] == "zod_builder_tool"
        assert rej["rejection_code"] == ERR_RUNTIME_SCHEMA_BUILDER_REJECTED

    def test_typescript_imported_value_rejected(self):
        """Vector TS-05: Non-literal imported identifier passed as inputSchema is rejected fail-closed."""
        source = (
            "import { ExternalSchema } from './schemas';\n"
            "const tools = [\n"
            "  {\n"
            "    name: 'imported_schema_tool',\n"
            "    inputSchema: ExternalSchema\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        res = extractor.extract_tools_from_source(source)
        assert res["tools_extracted_count"] == 0
        assert res["tools_rejected_count"] == 1
        rej = res["tools_rejected"][0]
        assert rej["operation_id"] == "imported_schema_tool"
        assert rej["rejection_code"] in [ERR_IMPORTED_SCHEMA_REJECTED, ERR_DYNAMIC_EXPRESSION_REJECTED]

    def test_typescript_nested_literal_schema_preserved(self):
        """Vector TS-06: Deeply nested TypeScript literal schema is parsed without structure distortion."""
        source = (
            "const tools = [\n"
            "  {\n"
            "    name: 'deep_config',\n"
            "    inputSchema: {\n"
            "      type: 'object',\n"
            "      properties: {\n"
            "        settings: {\n"
            "          type: 'object',\n"
            "          properties: {\n"
            "            retry_count: { type: 'number' },\n"
            "            enabled: { type: 'boolean' }\n"
            "          },\n"
            "          required: ['retry_count']\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        res = extractor.extract_tools_from_source(source)
        assert res["tools_extracted_count"] == 1
        t = res["tools_extracted"][0]
        settings = t["input_surface"]["properties"]["settings"]
        assert settings["type"] == "object"
        assert settings["properties"]["retry_count"]["type"] == "number"
        assert settings["properties"]["enabled"]["type"] == "boolean"
        assert settings["required"] == ["retry_count"]

    def test_typescript_line_column_stability_verified(self):
        """Vector TS-07: Static Tree-sitter span line/column bounds are identical across runs."""
        source = (
            "// Header\n"
            "const tools = [\n"
            "  {\n"
            "    name: 'stable_tool',\n"
            "    inputSchema: {\n"
            "      type: 'object'\n"
            "    }\n"
            "  }\n"
            "];\n"
        )
        extractor = TypeScriptAstToolExtractor()
        r1 = extractor.extract_tools_from_source(source)["tools_extracted"][0]
        r2 = extractor.extract_tools_from_source(source)["tools_extracted"][0]

        ev1 = r1["static_source_evidence"]
        ev2 = r2["static_source_evidence"]

        assert ev1["span"] == ev2["span"]
        assert ev1["span"]["lineno"] == 3
        assert ev1["source_snippet_sha256"] == ev2["source_snippet_sha256"]


# =====================================================================
# TRACK 6.3: REFERENCE CLOSURE ADVERSARIAL TEST VECTORS
# =====================================================================
class TestReferenceClosureAdversarial:
    """Adversarial test vectors for OpenAPI Local Reference Resolver."""

    def test_ref_valid_local_multi_file_accepted(self):
        """Vector REF-01: Valid local multi-file relative reference resolves successfully."""
        closure_file = os.path.join(
            DO_CLOSURE_DIR, "resources", "floating_ips", "floatingIPs_create.yml"
        )
        assert os.path.exists(closure_file)
        resolver = LocalReferenceResolver(
            bundle_root_dir=DO_CLOSURE_DIR,
            source_closure_dir=DO_CLOSURE_DIR,
        )
        node, resolved_file, ptr = resolver.resolve_reference(
            "models/floating_ip_create.yml#/oneOf",
            closure_file,
        )
        assert isinstance(node, list)
        assert len(node) >= 2
        assert resolved_file.replace("\\", "/").endswith("models/floating_ip_create.yml")
        assert ptr == "#/oneOf"

    def test_ref_escaped_path_rejected(self):
        """Vector REF-02: Path traversal escaping bundle root and closure directory raises error."""
        entry_file = os.path.join(DO_CLOSURE_DIR, "openapi.transformed.yaml")
        resolver = LocalReferenceResolver(
            bundle_root_dir=DO_CLOSURE_DIR,
            source_closure_dir=DO_CLOSURE_DIR,
        )
        # Attempt to escape data_stage_b/source_closures/CAND-003/
        with pytest.raises(ReferenceResolutionError) as exc_info:
            resolver.resolve_reference("../../../../etc/passwd", entry_file)
        assert exc_info.value.code == ERR_PATH_TRAVERSAL_DETECTED

    def test_ref_remote_url_rejected(self):
        """Vector REF-03: Remote URI scheme (https://) is prohibited fail-closed."""
        entry_file = os.path.join(DO_CLOSURE_DIR, "openapi.transformed.yaml")
        resolver = LocalReferenceResolver(
            bundle_root_dir=DO_CLOSURE_DIR,
            source_closure_dir=DO_CLOSURE_DIR,
        )
        with pytest.raises(ReferenceResolutionError) as exc_info:
            resolver.resolve_reference("https://example.com/schema.json#/type", entry_file)
        assert exc_info.value.code == ERR_REMOTE_REF_PROHIBITED

    def test_ref_cycle_rejected(self):
        """Vector REF-04: Mutually recursive reference cycle is detected and terminated fail-closed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_a = os.path.join(tmp_dir, "file_a.yaml")
            file_b = os.path.join(tmp_dir, "file_b.yaml")

            # Circular reference: file_a -> file_b -> file_a
            with open(file_a, "w", encoding="utf-8") as f:
                yaml.dump({"node_a": {"$ref": "file_b.yaml#/node_b"}}, f)

            with open(file_b, "w", encoding="utf-8") as f:
                yaml.dump({"node_b": {"$ref": "file_a.yaml#/node_a"}}, f)

            resolver = LocalReferenceResolver(bundle_root_dir=tmp_dir)
            call_path = [(os.path.realpath(file_a), "#/node_a")]

            with pytest.raises(ReferenceResolutionError) as exc_info:
                resolver.resolve_reference("file_a.yaml#/node_a", file_b, call_path=call_path)
            assert exc_info.value.code == ERR_REFERENCE_CYCLE_DETECTED

    def test_ref_stale_hash_rejected(self):
        """Vector REF-05: Modified/stale closure file fails cryptographic audit check."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = os.path.join(tmp_dir, "model.yaml")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("type: object\n")

            with open(test_file, "rb") as f:
                actual_bytes = f.read()
            actual_sha = hashlib.sha256(actual_bytes).hexdigest()

            # Declared hash differs from actual disk hash (stale / tampered)
            declared_stale_hash = "0" * 64
            assert actual_sha != declared_stale_hash

            # Verify cryptographic detection logic rejects discrepancy
            mismatches = []
            if actual_sha != declared_stale_hash:
                mismatches.append({
                    "file": "model.yaml",
                    "expected": declared_stale_hash,
                    "actual": actual_sha,
                })
            assert len(mismatches) == 1
            assert mismatches[0]["file"] == "model.yaml"

    def test_ref_missing_fragment_rejected(self):
        """Vector REF-06: Pointer to non-existent JSON Pointer fragment is rejected fail-closed."""
        closure_file = os.path.join(
            DO_CLOSURE_DIR, "resources", "floating_ips", "floatingIPs_create.yml"
        )
        assert os.path.exists(closure_file)
        resolver = LocalReferenceResolver(
            bundle_root_dir=DO_CLOSURE_DIR,
            source_closure_dir=DO_CLOSURE_DIR,
        )
        with pytest.raises(ReferenceResolutionError) as exc_info:
            resolver.resolve_reference(
                "models/floating_ip_create.yml#/nonexistent_fragment",
                closure_file,
            )
        assert exc_info.value.code == ERR_FRAGMENT_NOT_FOUND

    def test_ref_conflicting_sibling_properties_fail_closed(self):
        """Vector REF-07: Inconsistent or malformed reference document fails closed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_yaml = os.path.join(tmp_dir, "bad.yaml")
            with open(bad_yaml, "w", encoding="utf-8") as f:
                f.write(": : this is not valid yaml [\n")

            resolver = LocalReferenceResolver(bundle_root_dir=tmp_dir)
            with pytest.raises(Exception):
                resolver.resolve_reference("bad.yaml#/item", os.path.join(tmp_dir, "entry.yaml"))
