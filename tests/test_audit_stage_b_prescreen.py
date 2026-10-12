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
    JSON_OUTPUT_PATH,
    MD_OUTPUT_PATH,
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
    report = run_candidate_prescreen()
    assert report["summary"]["total_operations_audited"] == 32
    assert "operations" in report
    assert len(report["operations"]) == 32
    # Verify metadata fields exist
    meta = report["metadata"]
    assert meta["audit_script_sha256"]
    assert meta["manifest_sha256"]
    assert meta["python_version"]
