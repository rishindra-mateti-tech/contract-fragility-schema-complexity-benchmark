#!/usr/bin/env python3
"""Tests for OpenAPI Local Reference Resolver under Policy 001."""

import json
import os
import shutil
import tempfile
import pytest
import yaml

from src.openapi_local_ref_resolver import (
    LocalReferenceResolver,
    ReferenceResolutionError,
    POLICY_ID,
    ERR_REMOTE_REF_PROHIBITED,
    ERR_ABSOLUTE_PATH_PROHIBITED,
    ERR_PATH_TRAVERSAL_DETECTED,
    ERR_LOCAL_REF_FILE_NOT_FOUND,
    ERR_REFERENCE_CYCLE_DETECTED,
    ERR_REF_DEPTH_EXCEEDED,
    ERR_FRAGMENT_NOT_FOUND,
    ERR_UNSUPPORTED_DOC_FORMAT,
)
from src.audit_openapi_reference_closure import audit_reference_closures


@pytest.fixture
def temp_bundle():
    """Create a temporary multi-file OpenAPI bundle structure."""
    tmp_dir = tempfile.mkdtemp(prefix="test_ref_bundle_")
    
    # Root specification
    root_spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test Multi-File API", "version": "1.0.0"},
        "paths": {
            "/items": {
                "post": {
                    "$ref": "resources/items/create_item.yaml"
                }
            },
            "/users": {
                "post": {
                    "$ref": "resources/users/create_user.json#/components/operations/createUser"
                }
            }
        },
        "components": {
            "schemas": {
                "InternalError": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer"},
                        "message": {"type": "string"}
                    },
                    "required": ["code", "message"]
                }
            }
        }
    }
    
    # Create subdirectories
    os.makedirs(os.path.join(tmp_dir, "resources", "items"), exist_ok=True)
    os.makedirs(os.path.join(tmp_dir, "resources", "users"), exist_ok=True)
    os.makedirs(os.path.join(tmp_dir, "common"), exist_ok=True)
    
    root_path = os.path.join(tmp_dir, "openapi.yaml")
    with open(root_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(root_spec, f)
        
    # resources/items/create_item.yaml
    item_op = {
        "operationId": "createItem",
        "description": "Create a new item",
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "../../common/item_schema.yaml#/Item"
                    }
                }
            }
        }
    }
    with open(os.path.join(tmp_dir, "resources", "items", "create_item.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(item_op, f)
        
    # common/item_schema.yaml
    common_item = {
        "Item": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
    }
    with open(os.path.join(tmp_dir, "common", "item_schema.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(common_item, f)
        
    # resources/users/create_user.json
    user_op = {
        "components": {
            "operations": {
                "createUser": {
                    "operationId": "createUser",
                    "summary": "Create user endpoint"
                }
            }
        }
    }
    with open(os.path.join(tmp_dir, "resources", "users", "create_user.json"), "w", encoding="utf-8") as f:
        json.dump(user_op, f, indent=2)

    yield tmp_dir, root_path

    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_valid_local_relative_resolution(temp_bundle):
    """Test standard local multi-file resolution across relative subdirectories."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)
    resolver.register_root_document(root_path)

    # 1. Resolve relative file without fragment
    node, target_file, frag = resolver.resolve_reference(
        "resources/items/create_item.yaml",
        current_file_path=root_path,
    )
    assert node["operationId"] == "createItem"
    assert frag == "#"
    assert os.path.exists(target_file)

    # 2. Resolve relative file with fragment in JSON file
    node_user, target_user, frag_user = resolver.resolve_reference(
        "resources/users/create_user.json#/components/operations/createUser",
        current_file_path=root_path,
    )
    assert node_user["operationId"] == "createUser"
    assert frag_user == "#/components/operations/createUser"

    # 3. Transitive relative navigation (../../common/item_schema.yaml#/Item)
    item_yaml_path = os.path.join(bundle_root, "resources", "items", "create_item.yaml")
    node_schema, target_schema, frag_schema = resolver.resolve_reference(
        "../../common/item_schema.yaml#/Item",
        current_file_path=item_yaml_path,
    )
    assert node_schema["type"] == "object"
    assert "name" in node_schema["properties"]


def test_internal_reference_resolution(temp_bundle):
    """Test resolution of purely internal document pointers (#/...)."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)
    resolver.register_root_document(root_path)

    node, target_file, frag = resolver.resolve_reference(
        "#/components/schemas/InternalError",
        current_file_path=root_path,
    )
    assert node["type"] == "object"
    assert node["required"] == ["code", "message"]
    assert target_file == os.path.realpath(root_path)


def test_rejection_of_remote_schemes(temp_bundle):
    """Test that HTTP, HTTPS, and file URLs are rejected fail-closed."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)

    remote_urls = [
        "https://example.com/schemas/item.yaml",
        "http://schema.org/thing.json",
        "ftp://files.example.com/spec.yaml",
        "file:///etc/passwd",
    ]

    for url in remote_urls:
        with pytest.raises(ReferenceResolutionError) as exc_info:
            resolver.resolve_reference(url, current_file_path=root_path)
        assert exc_info.value.code == ERR_REMOTE_REF_PROHIBITED


def test_rejection_of_absolute_filesystem_paths(temp_bundle):
    """Test that absolute filesystem paths are rejected fail-closed."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)

    abs_paths = [
        "/etc/schema.yaml",
        "C:\\Windows\\system32\\schema.yaml",
        "D:/specs/root.json",
    ]

    for p in abs_paths:
        with pytest.raises(ReferenceResolutionError) as exc_info:
            resolver.resolve_reference(p, current_file_path=root_path)
        assert exc_info.value.code == ERR_ABSOLUTE_PATH_PROHIBITED


def test_rejection_of_path_traversal_escaping_root(temp_bundle):
    """Test that references attempting to escape bundle root are rejected fail-closed."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)

    traversal_refs = [
        "../outside.yaml",
        "../../etc/passwd",
        "resources/../../../../secret.json",
    ]

    for t in traversal_refs:
        with pytest.raises(ReferenceResolutionError) as exc_info:
            resolver.resolve_reference(t, current_file_path=root_path)
        assert exc_info.value.code == ERR_PATH_TRAVERSAL_DETECTED


def test_missing_local_file_fails_closed(temp_bundle):
    """Test that non-existent local files raise ERR_LOCAL_REF_FILE_NOT_FOUND."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)

    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolver.resolve_reference("resources/items/non_existent.yaml", current_file_path=root_path)
    assert exc_info.value.code == ERR_LOCAL_REF_FILE_NOT_FOUND


def test_missing_fragment_fails_closed(temp_bundle):
    """Test that non-existent JSON Pointer fragments raise ERR_FRAGMENT_NOT_FOUND."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)

    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolver.resolve_reference("#/components/schemas/DoesNotExist", current_file_path=root_path)
    assert exc_info.value.code == ERR_FRAGMENT_NOT_FOUND


def test_reference_cycle_detection(temp_bundle):
    """Test detection of circular references across files."""
    bundle_root, root_path = temp_bundle
    
    # Create cycle: fileA.yaml -> fileB.yaml -> fileA.yaml
    path_a = os.path.join(bundle_root, "fileA.yaml")
    path_b = os.path.join(bundle_root, "fileB.yaml")
    
    with open(path_a, "w", encoding="utf-8") as f:
        yaml.safe_dump({"$ref": "fileB.yaml#/nodeB"}, f)
    with open(path_b, "w", encoding="utf-8") as f:
        yaml.safe_dump({"nodeB": {"$ref": "fileA.yaml#"}}, f)

    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)

    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolver.resolve_reference("fileA.yaml#", current_file_path=root_path)
    assert exc_info.value.code == ERR_REFERENCE_CYCLE_DETECTED


def test_maximum_depth_enforcement(temp_bundle):
    """Test that exceeding max_depth raises ERR_REF_DEPTH_EXCEEDED."""
    bundle_root, root_path = temp_bundle
    
    # Create a chain of 10 references
    for i in range(10):
        p = os.path.join(bundle_root, f"chain_{i}.yaml")
        next_p = f"chain_{i+1}.yaml" if i < 9 else "common/item_schema.yaml#/Item"
        with open(p, "w", encoding="utf-8") as f:
            yaml.safe_dump({"$ref": next_p}, f)

    # With max_depth=5, resolving chain_0 should fail
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root, max_depth=5)
    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolver.resolve_reference("chain_0.yaml", current_file_path=root_path)
    assert exc_info.value.code == ERR_REF_DEPTH_EXCEEDED


def test_closure_manifest_generation(temp_bundle):
    """Test generation and cryptographic hashing of reference closure manifest."""
    bundle_root, root_path = temp_bundle
    resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)
    resolver.register_root_document(root_path)

    resolver.resolve_reference("resources/items/create_item.yaml", current_file_path=root_path)
    resolver.resolve_reference("resources/users/create_user.json#/components/operations/createUser", current_file_path=root_path)

    manifest = resolver.get_reference_closure_manifest()
    assert manifest["policy_id"] == POLICY_ID
    assert manifest["accessed_files_count"] == 3  # root + create_item + create_user
    assert len(manifest["closure_sha256"]) == 64
    assert manifest["resolution_steps_count"] == 2


def test_audit_reference_closures_runs_cleanly():
    """Test that audit_reference_closures produces valid output reports."""
    res = audit_reference_closures()
    assert res["policy_id"] == POLICY_ID
    assert res["total_operations_audited"] == 30
    assert os.path.exists("results_stage_b/OPENAPI_REFERENCE_CLOSURE_AUDIT.json")
    assert os.path.exists("results_stage_b/OPENAPI_REFERENCE_CLOSURE_AUDIT.md")
