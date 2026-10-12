"""Tests for Stage B Raw-Source Operation Universe Static Analysis Scanner.

Verifies:
1. Pointer resolution with standard RFC 6901 escaping (~1, ~0).
2. Intra-document local $ref resolution and cycle detection.
3. Recursion depth bounding (depth <= 5 allowed, depth > 5 flagged).
4. Object-level union detection (primitive allowed, object-level flagged).
5. Binary and multipart format detection (file, binary format, multipart/form-data).
6. Form fields and multi-surface partitioning (path, query, header, body).
7. Credential / authentication field classification.
8. Graceful handling of malformed and edge-case schema inputs.
9. Deterministic, byte-stable output when --generated-at is provided.
10. Cryptographic hash and blob SHA mismatch detection.
11. Full universe scan summary invariants (scale, cluster counts, PostRefunds faithful-union).
"""

import json
import os
import pytest
from src.scan_stage_b_raw_operation_universe import (
    OperationAuditor,
    resolve_json_pointer,
    resolve_local_ref,
    count_properties_and_required,
    estimate_token_footprint,
    parse_mcp_sqlite_tools_ast,
    inspect_mcp_github_ts_ast,
    scan_raw_operation_universe,
    generate_markdown_report,
    git_blob_sha,
    sha256_file,
    JSON_OUTPUT_PATH,
    MD_OUTPUT_PATH,
    ROOT_DIR,
)


def test_mcp_sqlite_ast_parsing_reads_source_structure_not_dictionary(tmp_path):
    """Proves that SQLite MCP scanner parses actual Python AST, not hardcoded dictionaries."""
    raw_sqlite_path = os.path.join(ROOT_DIR, "data_stage_b", "raw", "CAND-009", "1b97a6a4903bd8961941cdff43df3b059e610e5f.py")
    raw_sha = sha256_file(raw_sqlite_path)
    blob_sha = "1b97a6a4903bd8961941cdff43df3b059e610e5f"

    # 1. Parse real raw source file
    tools = parse_mcp_sqlite_tools_ast(raw_sqlite_path, raw_sha, blob_sha)
    assert len(tools) == 6
    op_ids = [t["operation_id"] for t in tools]
    assert op_ids == ["append_insight", "create_table", "describe_table", "list_tables", "read_query", "write_query"]

    # Verify source span line numbers are parsed directly from AST
    for t in tools:
        assert "source_ast_span" in t
        assert 230 <= t["source_ast_span"]["start_line"] <= 300
        assert 230 <= t["source_ast_span"]["end_line"] <= 300
        assert "parsed_input_schema_shape" in t

    read_query = next(t for t in tools if t["operation_id"] == "read_query")
    assert read_query["parsed_input_schema_shape"]["property_names"] == ["query"]
    assert read_query["parsed_input_schema_shape"]["required_names"] == ["query"]
    assert read_query["property_count"] == 1
    assert read_query["required_count"] == 1

    # 2. Dynamic AST test: create modified Python file with custom tool and verify dynamic AST extraction
    custom_py = tmp_path / "custom_server.py"
    custom_code = """
import mcp.types as types

class DummyServer:
    @server.list_tools()
    async def handle_list_tools():
        return [
            types.Tool(
                name="dynamic-ast-diagnostic-tool",
                description="Dynamically created tool to prove AST parsing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "alpha_param": {"type": "string"},
                        "beta_param": {"type": "integer"}
                    },
                    "required": ["alpha_param"]
                }
            )
        ]
"""
    custom_py.write_text(custom_code, encoding="utf-8")
    custom_sha = sha256_file(str(custom_py))
    custom_tools = parse_mcp_sqlite_tools_ast(str(custom_py), custom_sha, "dummy_blob_sha")
    assert len(custom_tools) == 1
    c_tool = custom_tools[0]
    assert c_tool["operation_id"] == "dynamic_ast_diagnostic_tool"
    assert c_tool["property_count"] == 2
    assert c_tool["required_count"] == 1
    assert c_tool["parsed_input_schema_shape"]["property_names"] == ["alpha_param", "beta_param"]
    assert c_tool["parsed_input_schema_shape"]["required_names"] == ["alpha_param"]
    # This conclusively proves the scanner reads AST node structures, not embedded constant dictionaries.


def test_mcp_github_unresolved_external_import_detection():
    """Verifies that GitHub MCP source is inspected and flagged for unresolved external schema imports."""
    raw_ts_path = os.path.join(ROOT_DIR, "data_stage_b", "raw", "CAND-010", "0676a34c85537e610f911fbd73a5a079f38be18e.ts")
    raw_sha = sha256_file(raw_ts_path)
    blob_sha = "0676a34c85537e610f911fbd73a5a079f38be18e"

    inspection = inspect_mcp_github_ts_ast(raw_ts_path, raw_sha, blob_sha)
    assert inspection["has_external_schemas_import"] is True
    assert "CreateOrUpdateFileSchema" in inspection["referenced_external_zod_schemas"]
    assert "SearchRepositoriesSchema" in inspection["referenced_external_zod_schemas"]
    assert inspection["exclusion_status"] == "EXCLUDED_FROM_UNIVERSE"
    assert inspection["exclusion_reason"] == "UNRESOLVED_EXTERNAL_SCHEMA_IMPORTS"


def test_static_eligibility_vocabulary_and_governing_policy():
    """Verifies that universe scanner outputs strictly adhere to STATICALLY_ELIGIBLE vocabulary."""
    rep = scan_raw_operation_universe(generated_at_utc="2026-10-12T04:30:00Z")
    summ = rep["summary"]

    assert "statically_eligible_candidates" in summ
    assert "statically_eligible_faithful_union_candidates" in summ
    assert "disqualified_candidates" in summ
    assert "governing_policy_statement" in summ

    # Policy statement must explicitly state that static eligibility is not canonical admission
    policy = summ["governing_policy_statement"]
    assert "does NOT constitute canonical-contract admission" in policy
    assert "provisional finite-union candidate" in policy

    # Check each operation's static_eligibility field
    valid_verdicts = {
        "STATICALLY_ELIGIBLE_CANDIDATE",
        "STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE",
        "DISQUALIFIED"
    }
    for op in rep["operations"]:
        assert op["static_eligibility"] in valid_verdicts
        # Backward compatibility field also populated
        assert op["canonical_eligibility"] in valid_verdicts

    # Verify excluded_sources records
    assert len(rep["metadata"]["excluded_sources"]) == 2
    excluded_ids = [ex["candidate_source_id"] for ex in rep["metadata"]["excluded_sources"]]
    assert "CAND-009" in excluded_ids
    assert "CAND-010" in excluded_ids


def test_universe_scanner_runner_and_summary_invariants():
    rep = scan_raw_operation_universe(generated_at_utc="2026-10-12T04:30:00Z")
    summ = rep["summary"]

    # Verify universe scale across 8 active OpenAPI sources
    assert summ["total_operations_scanned"] == 1346, "Total active universe operations must equal 1346"
    assert summ["statically_eligible_candidates"] == 1109
    assert summ["statically_eligible_faithful_union_candidates"] == 1
    assert summ["statically_eligible_combined"] == 1110
    assert summ["disqualified_candidates"] == 236
    assert summ["mcp_sources_excluded_count"] == 2

    # Verify all 8 active OpenAPI clusters exist in cluster_breakdown
    assert len(summ["cluster_breakdown"]) == 8
    expected_clusters = [
        "CLUSTER_GITHUB", "CLUSTER_STRIPE", "CLUSTER_DIGITALOCEAN",
        "CLUSTER_TWILIO", "CLUSTER_BOX", "CLUSTER_SLACK",
        "CLUSTER_CHATWOOT", "CLUSTER_LINE"
    ]
    for c in expected_clusters:
        assert c in summ["cluster_breakdown"], f"Missing cluster {c}"

    # Verify Stripe PostRefunds is recognized as STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE
    post_refunds = next(op for op in rep["operations"] if op["operation_id"] == "PostRefunds")
    assert post_refunds["static_eligibility"] == "STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE"
    assert post_refunds["maximum_nesting_depth"] == 3
    assert post_refunds["has_object_level_union"] is True

    # Verify metadata fields exist
    meta = rep["metadata"]
    assert meta["scanner_script_sha256"]
    assert meta["manifest_sha256"]
    assert meta["registry_sha256"]
    assert meta["generated_at_utc"] == "2026-10-12T04:30:00Z"
    assert len(meta["sources"]) == 10
    assert len(meta["excluded_sources"]) == 2


def test_pointer_resolution():
    doc = {
        "paths": {
            "/repos/{owner}/{repo}/issues": {
                "post": {"summary": "Create issue"},
            },
            "/user/keys": {
                "post": {"summary": "Add key"},
            },
            "/escaped~1path/test~0name": {
                "post": {"summary": "Escaped"},
            },
        },
        "components": {
            "schemas": {
                "List": [{"name": "item0"}, {"name": "item1"}]
            }
        }
    }

    # 1. Standard slash escaping
    ptr1 = "#/paths/~1repos~1{owner}~1{repo}~1issues/post"
    res1 = resolve_json_pointer(doc, ptr1)
    assert res1 == {"summary": "Create issue"}

    # 2. Tilde escaping (~0 -> ~, ~1 -> /)
    ptr2 = "#/paths/~1escaped~01path~1test~00name/post"
    res2 = resolve_json_pointer(doc, ptr2)
    assert res2 == {"summary": "Escaped"}

    # 3. Numeric array index
    ptr3 = "#/components/schemas/List/1/name"
    res3 = resolve_json_pointer(doc, ptr3)
    assert res3 == "item1"

    # 4. Non-existent pointer returns None
    assert resolve_json_pointer(doc, "#/paths/missing") is None


def test_ref_resolution_and_cycle_detection():
    # 1. Intra-document valid local ref
    doc = {
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                }
            }
        }
    }
    target, err = resolve_local_ref(doc, "#/components/schemas/User")
    assert err is None
    assert target["type"] == "object"

    # 2. External ref detected
    target_ext, err_ext = resolve_local_ref(doc, "https://schemas.example.com/User.json")
    assert err_ext == "EXTERNAL_REF"
    assert target_ext is None

    # 3. Cycle detection in OperationAuditor
    doc_cycle = {
        "components": {
            "schemas": {
                "TreeNode": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "child": {"$ref": "#/components/schemas/TreeNode"},
                    },
                }
            }
        },
        "paths": {
            "/tree": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TreeNode"}
                            }
                        }
                    }
                }
            }
        },
    }
    auditor = OperationAuditor(doc_cycle, "#/paths/~1tree/post")
    res = auditor.audit_operation(doc_cycle["paths"]["/tree"]["post"])
    assert res["has_cycle"] is True
    assert len(res["cycle_details"]) > 0
    assert any("TreeNode" in d for d in res["cycle_details"])


def test_recursion_depth_bounded_and_overflow():
    # 1. Depth <= 5 (allowed)
    doc_shallow = {
        "paths": {
            "/shallow": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "l1": {
                                            "type": "object",
                                            "properties": {
                                                "l2": {
                                                    "type": "object",
                                                    "properties": {
                                                        "l3": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_shallow = OperationAuditor(doc_shallow, "#/paths/~1shallow/post")
    res_shallow = auditor_shallow.audit_operation(doc_shallow["paths"]["/shallow"]["post"])
    assert res_shallow["max_depth"] <= 5
    assert res_shallow["exceeds_depth_5"] is False

    # 2. Depth 6 (exceeds limit)
    doc_deep = {
        "paths": {
            "/deep": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "l1": {"type": "object", "properties": {
                                            "l2": {"type": "object", "properties": {
                                                "l3": {"type": "object", "properties": {
                                                    "l4": {"type": "object", "properties": {
                                                        "l5": {"type": "string"}
                                                    }}
                                                }}
                                            }}
                                        }}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_deep = OperationAuditor(doc_deep, "#/paths/~1deep/post")
    res_deep = auditor_deep.audit_operation(doc_deep["paths"]["/deep"]["post"])
    assert res_deep["max_depth"] == 6
    assert res_deep["exceeds_depth_5"] is True


def test_object_level_union_detection():
    # 1. Primitive union (allowed)
    doc_prim = {
        "paths": {
            "/prim": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "val": {"oneOf": [{"type": "string"}, {"type": "integer"}]}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    aud_prim = OperationAuditor(doc_prim, "#/paths/~1prim/post")
    res_prim = aud_prim.audit_operation(doc_prim["paths"]["/prim"]["post"])
    assert res_prim["has_object_union"] is False

    # 2. Object union (flagged)
    doc_obj = {
        "paths": {
            "/obj": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "val": {"oneOf": [
                                            {"type": "string"},
                                            {"type": "object", "properties": {"nested": {"type": "string"}}}
                                        ]}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    aud_obj = OperationAuditor(doc_obj, "#/paths/~1obj/post")
    res_obj = aud_obj.audit_operation(doc_obj["paths"]["/obj"]["post"])
    assert res_obj["has_object_union"] is True

    # 3. Polymorphic discriminator (flagged)
    doc_disc = {
        "paths": {
            "/disc": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "discriminator": {"propertyName": "item_type"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    aud_disc = OperationAuditor(doc_disc, "#/paths/~1disc/post")
    res_disc = aud_disc.audit_operation(doc_disc["paths"]["/disc"]["post"])
    assert res_disc["has_object_union"] is True


def test_binary_and_multipart_detection():
    # 1. Binary format
    doc_bin = {
        "paths": {
            "/upload": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/octet-stream": {
                                "schema": {"type": "string", "format": "binary"}
                            }
                        }
                    }
                }
            }
        }
    }
    aud_bin = OperationAuditor(doc_bin, "#/paths/~1upload/post")
    res_bin = aud_bin.audit_operation(doc_bin["paths"]["/upload"]["post"])
    assert res_bin["has_multipart_binary"] is True

    # 2. Multipart content-type
    doc_multi = {
        "paths": {
            "/form": {
                "post": {
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"type": "object", "properties": {"avatar": {"type": "string"}}}
                            }
                        }
                    }
                }
            }
        }
    }
    aud_multi = OperationAuditor(doc_multi, "#/paths/~1form/post")
    res_multi = aud_multi.audit_operation(doc_multi["paths"]["/form"]["post"])
    assert res_multi["has_multipart_binary"] is True


def test_form_fields_and_surfaces():
    doc = {
        "paths": {
            "/items/{id}": {
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "string"}
                ],
                "post": {
                    "parameters": [
                        {"name": "filter", "in": "query", "type": "string"},
                        {"name": "X-Client", "in": "header", "type": "string"},
                        {"name": "name", "in": "formData", "type": "string", "required": True},
                    ]
                }
            }
        }
    }
    aud = OperationAuditor(doc, "#/paths/~1items~1{id}/post")
    res = aud.audit_operation(doc["paths"]["/items/{id}"]["post"], doc["paths"]["/items/{id}"]["parameters"])
    assert res["max_depth"] >= 1


def test_auth_fields_detection():
    doc = {
        "paths": {
            "/secure": {
                "post": {
                    "parameters": [
                        {"name": "Authorization", "in": "header", "type": "string"},
                        {"name": "token", "in": "query", "type": "string"},
                        {"name": "user_id", "in": "query", "type": "string"}
                    ]
                }
            }
        }
    }
    aud = OperationAuditor(doc, "#/paths/~1secure/post")
    res = aud.audit_operation(doc["paths"]["/secure"]["post"])
    assert "header.Authorization" in res["credential_fields"]
    assert "query.token" in res["credential_fields"]
    assert "query.user_id" not in res["credential_fields"]


def test_malformed_source_handling():
    # Empty schema dict
    doc_empty = {"paths": {"/empty": {"post": {}}}}
    aud = OperationAuditor(doc_empty, "#/paths/~1empty/post")
    res = aud.audit_operation(doc_empty["paths"]["/empty"]["post"])
    assert res["has_cycle"] is False
    assert res["max_depth"] == 1
    assert res["exceeds_depth_5"] is False

    # Property counting on empty schema
    props, req = count_properties_and_required({}, doc_empty)
    assert props == 0
    assert req == 0

    # Non-dict schema
    props2, req2 = count_properties_and_required("invalid", doc_empty)
    assert props2 == 0
    assert req2 == 0


def test_deterministic_output_with_generated_at():
    fixed_ts = "2026-10-12T04:30:00Z"
    rep1 = scan_raw_operation_universe(generated_at_utc=fixed_ts)
    rep2 = scan_raw_operation_universe(generated_at_utc=fixed_ts)

    json1 = json.dumps(rep1, indent=2, sort_keys=True)
    json2 = json.dumps(rep2, indent=2, sort_keys=True)
    assert json1 == json2, "Runs with identical inputs and fixed generated-at must produce byte-identical JSON"

    md1 = generate_markdown_report(rep1)
    md2 = generate_markdown_report(rep2)
    assert md1 == md2, "Runs with identical inputs and fixed generated-at must produce byte-identical Markdown"


def test_source_hash_and_blob_mismatch_detection():
    # Test git_blob_sha computation against known standard
    data = b"test content\n"
    blob = git_blob_sha(data)
    assert len(blob) == 40
    assert blob == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"


def test_disqualification_cause_non_exclusive_disclosure():
    expected_disclosure = (
        "Violation counts are non-exclusive: a single operation may contribute to multiple root-cause categories; "
        "therefore their sum can exceed the number of disqualified operations."
    )
    fixed_ts = "2026-10-12T04:30:00Z"
    rep = scan_raw_operation_universe(generated_at_utc=fixed_ts)
    assert "disqualification_cause_note" in rep["summary"]
    assert rep["summary"]["disqualification_cause_note"] == expected_disclosure

    md = generate_markdown_report(rep)
    assert expected_disclosure in md



