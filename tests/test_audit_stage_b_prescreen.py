"""Tests for Stage B Candidate Pre-Screen Auditor (src/audit_stage_b_candidate_prescreen.py).

Verifies:
1. Object-level union detection (primitive allowed, object-level flagged)
2. Recursion depth overflow (depth <= 5 allowed, depth > 5 flagged)
3. Binary / multipart detection (file, binary format, multipart/form-data)
4. External $ref detection (intra-document allowed, external flagged)
5. Authentication field classification (properly categorized under Section 2.5)
6. Pre-screen runner artifact generation and byte-stability
"""

import json
import os
import pytest
from src.audit_stage_b_candidate_prescreen import (
    OperationAuditor,
    run_candidate_prescreen,
    generate_markdown_report,
    sha256_file,
    JSON_OUTPUT_PATH,
    MD_OUTPUT_PATH,
    ROOT_DIR,
    MANIFEST_PATH,
)


def test_object_union_detection():
    # 1. Primitive oneOf (allowed)
    doc_primitive = {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "field": {
                                            "oneOf": [{"type": "string"}, {"type": "integer"}]
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
    auditor_prim = OperationAuditor(doc_primitive, "#/paths/~1test/post")
    res_prim = auditor_prim.audit_openapi(doc_primitive["paths"]["/test"]["post"])
    assert res_prim["has_object_union"] is False, "Primitive union must pass without object union flag"

    # 2. Object-level oneOf (flagged)
    doc_object_union = {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "field": {
                                            "oneOf": [
                                                {"type": "string"},
                                                {"type": "object", "properties": {"nested": {"type": "string"}}}
                                            ]
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
    auditor_obj = OperationAuditor(doc_object_union, "#/paths/~1test/post")
    res_obj = auditor_obj.audit_openapi(doc_object_union["paths"]["/test"]["post"])
    assert res_obj["has_object_union"] is True, "Object-level union must be flagged"

    # 3. Polymorphic discriminator (flagged)
    doc_discriminator = {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "discriminator": {"propertyName": "type"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_disc = OperationAuditor(doc_discriminator, "#/paths/~1test/post")
    res_disc = auditor_disc.audit_openapi(doc_discriminator["paths"]["/test"]["post"])
    assert res_disc["has_object_union"] is True, "Discriminator must be flagged as object union"


def test_depth_overflow_detection():
    # 1. Depth <= 5 (allowed)
    doc_shallow = {
        "paths": {
            "/test": {
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
    auditor_shallow = OperationAuditor(doc_shallow, "#/paths/~1test/post")
    res_shallow = auditor_shallow.audit_openapi(doc_shallow["paths"]["/test"]["post"])
    assert res_shallow["exceeds_depth_5"] is False
    assert res_shallow["max_depth"] <= 5

    # 2. Depth > 5 (flagged)
    doc_deep = {
        "paths": {
            "/test": {
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
                                                        "l5": {"type": "object", "properties": {
                                                            "l6": {"type": "string"}
                                                        }}}
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
    }
    auditor_deep = OperationAuditor(doc_deep, "#/paths/~1test/post")
    res_deep = auditor_deep.audit_openapi(doc_deep["paths"]["/test"]["post"])
    assert res_deep["exceeds_depth_5"] is True
    assert res_deep["max_depth"] > 5


def test_binary_multipart_detection():
    # 1. format=binary
    doc_binary = {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "file_upload": {"type": "string", "format": "binary"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_bin = OperationAuditor(doc_binary, "#/paths/~1test/post")
    res_bin = auditor_bin.audit_openapi(doc_binary["paths"]["/test"]["post"])
    assert res_bin["has_multipart_binary"] is True

    # 2. multipart/form-data content-type
    doc_multipart = {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_mp = OperationAuditor(doc_multipart, "#/paths/~1test/post")
    res_mp = auditor_mp.audit_openapi(doc_multipart["paths"]["/test"]["post"])
    assert res_mp["has_multipart_binary"] is True


def test_external_ref_detection():
    # 1. Local ref (allowed)
    doc_local = {
        "components": {
            "schemas": {
                "MyType": {"type": "string"}
            }
        },
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MyType"}
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_local = OperationAuditor(doc_local, "#/paths/~1test/post")
    res_local = auditor_local.audit_openapi(doc_local["paths"]["/test"]["post"])
    assert res_local["has_external_ref"] is False

    # 2. External ref (flagged)
    doc_ext = {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "https://example.com/schema.json#/types/User"}
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_ext = OperationAuditor(doc_ext, "#/paths/~1test/post")
    res_ext = auditor_ext.audit_openapi(doc_ext["paths"]["/test"]["post"])
    assert res_ext["has_external_ref"] is True


def test_auth_field_classification():
    doc_auth = {
        "paths": {
            "/test": {
                "post": {
                    "parameters": [
                        {"name": "token", "in": "header", "type": "string", "required": True},
                        {"name": "apiKey", "in": "query", "type": "string"}
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "auth_token": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    auditor_auth = OperationAuditor(doc_auth, "#/paths/~1test/post")
    res_auth = auditor_auth.audit_openapi(doc_auth["paths"]["/test"]["post"])
    assert "header.token" in res_auth["credential_fields"]
    assert "query.apiKey" in res_auth["credential_fields"]
    assert "body.auth_token" in res_auth["credential_fields"]


def test_candidate_prescreen_runner_and_artifacts():
    report = run_candidate_prescreen(generated_at_utc="2026-10-12T03:30:00Z")
    assert report["summary"]["total_operations_audited"] == 32
    assert report["summary"]["clean_provisional_candidates_passed"] == 24
    assert report["summary"]["provisional_pending_union_amendment"] == 1
    assert report["summary"]["flagged_exclude_pending"] == 7
    assert report["summary"]["replacement_slots_required"] == 5
    assert "operations" in report
    assert len(report["operations"]) == 32
    # Verify metadata fields exist
    meta = report["metadata"]
    assert meta["audit_script_sha256"]
    assert meta["manifest_sha256"]
    assert meta["generated_at_utc"] == "2026-10-12T03:30:00Z"
    assert meta["python_version"]
    assert meta["command"] == "python src/audit_stage_b_candidate_prescreen.py --generated-at 2026-10-12T03:30:00Z"


def test_reproducibility_same_timestamp_byte_identical():
    fixed_ts = "2026-10-12T03:30:00Z"
    rep1 = run_candidate_prescreen(generated_at_utc=fixed_ts)
    rep2 = run_candidate_prescreen(generated_at_utc=fixed_ts)

    json1 = json.dumps(rep1, indent=2, sort_keys=True)
    json2 = json.dumps(rep2, indent=2, sort_keys=True)
    assert json1 == json2, "Runs with identical inputs and generated-at must produce byte-identical JSON"

    md1 = generate_markdown_report(rep1)
    md2 = generate_markdown_report(rep2)
    assert md1 == md2, "Runs with identical inputs and generated-at must produce byte-identical Markdown"


def test_reproducibility_different_timestamp_changes_only_timestamp_metadata():
    ts1 = "2026-10-12T01:00:00Z"
    ts2 = "2026-10-12T02:00:00Z"
    rep1 = run_candidate_prescreen(generated_at_utc=ts1)
    rep2 = run_candidate_prescreen(generated_at_utc=ts2)

    # Operations and summary must be identical
    assert rep1["summary"] == rep2["summary"], "Summary must not be affected by timestamp"
    assert rep1["operations"] == rep2["operations"], "Operation audits must not be affected by timestamp"

    # In metadata, generated_at_utc and command differ
    assert rep1["metadata"]["generated_at_utc"] == ts1
    assert rep2["metadata"]["generated_at_utc"] == ts2

    # When normalizing timestamp-dependent fields, metadata must be identical
    meta1_norm = {k: v for k, v in rep1["metadata"].items() if k not in ["generated_at_utc", "command"]}
    meta2_norm = {k: v for k, v in rep2["metadata"].items() if k not in ["generated_at_utc", "command"]}
    assert meta1_norm == meta2_norm, "Metadata excluding timestamp fields must be identical"

    # In Markdown, only header lines containing timestamp/command differ
    md1 = generate_markdown_report(rep1)
    md2 = generate_markdown_report(rep2)
    lines1 = md1.splitlines()
    lines2 = md2.splitlines()
    assert len(lines1) == len(lines2)
    differing_lines = [(l1, l2) for l1, l2 in zip(lines1, lines2) if l1 != l2]
    assert len(differing_lines) == 2, f"Expected exactly 2 differing lines (timestamp & command), got {differing_lines}"
    for l1, l2 in differing_lines:
        assert "Generated At" in l1 or "Execution Command" in l1


def test_audit_and_manifest_hashes_remain_correct():
    rep = run_candidate_prescreen(generated_at_utc="2026-10-12T03:30:00Z")
    audit_script_path = os.path.join(ROOT_DIR, "src", "audit_stage_b_candidate_prescreen.py")
    manifest_path = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")

    expected_script_sha = sha256_file(audit_script_path)
    expected_manifest_sha = sha256_file(manifest_path)

    assert rep["metadata"]["audit_script_sha256"] == expected_script_sha
    assert rep["metadata"]["manifest_sha256"] == expected_manifest_sha


def test_depth_overflow_with_object_unions_regression():
    report = run_candidate_prescreen(generated_at_utc="2026-10-12T03:30:00Z")
    ops_by_id = {op["operation_id"]: op for op in report["operations"]}

    # 1. Depth-6 object-union operations (PostCustomers, issues/create) remain EXCLUDE_PENDING
    # even when Amendment 003 exists, because Amendment 003 does not alter MAX_RECURSION_DEPTH=5.
    post_customers = ops_by_id["PostCustomers"]
    assert post_customers["max_depth_observed"] == 6
    assert post_customers["rule_checks"]["object_union_restricted"] == "FAIL"
    assert post_customers["rule_checks"]["recursion_depth_bounded"] == "FAIL"
    assert post_customers["audit_verdict"] == "EXCLUDE_PENDING"
    assert "DEPTH_6" in post_customers["blocking_failures"]

    issues_create = ops_by_id["issues/create"]
    assert issues_create["max_depth_observed"] == 6
    assert issues_create["rule_checks"]["object_union_restricted"] == "FAIL"
    assert issues_create["rule_checks"]["recursion_depth_bounded"] == "FAIL"
    assert issues_create["audit_verdict"] == "EXCLUDE_PENDING"
    assert "DEPTH_6" in issues_create["blocking_failures"]

    # 2. Depth-9 object-union operation (PostPaymentIntents) remains EXCLUDE_PENDING
    post_payment_intents = ops_by_id["PostPaymentIntents"]
    assert post_payment_intents["max_depth_observed"] == 9
    assert post_payment_intents["rule_checks"]["object_union_restricted"] == "FAIL"
    assert post_payment_intents["rule_checks"]["recursion_depth_bounded"] == "FAIL"
    assert post_payment_intents["audit_verdict"] == "EXCLUDE_PENDING"
    assert "DEPTH_9" in post_payment_intents["blocking_failures"]

    # 3. Depth-3 finite object-union operation (PostRefunds) is eligible only for PENDING_UNION_AMENDMENT status
    post_refunds = ops_by_id["PostRefunds"]
    assert post_refunds["max_depth_observed"] == 3
    assert post_refunds["rule_checks"]["recursion_depth_bounded"] == "PASS"
    assert post_refunds["rule_checks"]["object_union_restricted"] == "FAIL"
    assert post_refunds["audit_verdict"] == "FLAGGED_PENDING_UNION_AMENDMENT"
    assert post_refunds["blocking_failures"] == ["OBJECT_UNION"]
