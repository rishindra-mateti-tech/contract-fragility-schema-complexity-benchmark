#!/usr/bin/env python3
"""Stage B Schema Feature Support Registry and Validation Engine.

Provides programmatic access to the Stage B Schema Feature Support Registry,
allowing tools to inspect feature policies, verify compliance, and enforce
fail-closed rejection of unsupported schema constructs.
"""

import os
from typing import Any, Dict, List, Optional, Set
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml")


class UnsupportedSchemaFeatureError(ValueError):
    """Raised when a schema contains a construct marked REJECT_AND_REPORT or UNSUPPORTED_FAIL_CLOSED."""

    def __init__(self, feature_id: str, message: str, pointer: str = ""):
        self.feature_id = feature_id
        self.pointer = pointer
        super().__init__(f"[{feature_id}] at '{pointer}': {message}")


class SchemaFeatureRegistry:
    """Interface to the Schema Feature Support Registry."""

    def __init__(self, registry_path: str = REGISTRY_PATH):
        self.registry_path = registry_path
        self._data: Optional[Dict[str, Any]] = None
        self._feature_index: Optional[Dict[str, Dict[str, Any]]] = None

    def _load(self) -> None:
        if self._data is not None:
            return
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Schema feature registry not found: {self.registry_path}")
        with open(self.registry_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)
        self._feature_index = {feat["feature_id"]: feat for feat in self._data.get("features", [])}

    @property
    def version(self) -> str:
        self._load()
        assert self._data is not None
        return self._data.get("registry_version", "unknown")

    @property
    def features(self) -> List[Dict[str, Any]]:
        self._load()
        assert self._data is not None
        return self._data.get("features", [])

    def get_feature(self, feature_id: str) -> Dict[str, Any]:
        self._load()
        assert self._feature_index is not None
        if feature_id not in self._feature_index:
            raise KeyError(f"Feature ID '{feature_id}' not found in registry")
        return self._feature_index[feature_id]

    def get_features_by_category(self, category: str) -> List[Dict[str, Any]]:
        self._load()
        assert self._data is not None
        return [f for f in self._data.get("features", []) if f.get("category") == category]

    def get_features_by_behavior(self, behavior: str) -> List[Dict[str, Any]]:
        self._load()
        assert self._data is not None
        return [f for f in self._data.get("features", []) if f.get("extraction_behavior") == behavior]

    def get_features_by_status(self, status: str) -> List[Dict[str, Any]]:
        self._load()
        assert self._data is not None
        return [f for f in self._data.get("features", []) if f.get("current_benchmark_status") == status]

    def validate_schema_compliance(
        self,
        schema: Any,
        pointer: str = "#",
        visited_ptrs: Optional[Set[str]] = None,
        current_depth: int = 0,
        fail_closed: bool = True,
        raw_doc: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Inspect a schema node for constructs that are unsupported or fail-closed.

        If fail_closed is True, raises UnsupportedSchemaFeatureError on the first violation.
        Otherwise returns a list of violation messages.
        """
        self._load()
        violations: List[str] = []

        if visited_ptrs is None:
            visited_ptrs = set()

        # Check recursion depth limit (5)
        if current_depth > 5:
            msg = f"Nesting depth {current_depth} exceeds benchmark maximum limit of 5 (FEAT_REC_EXCESSIVE_DEPTH)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_REC_EXCESSIVE_DEPTH", msg, pointer)
            violations.append(msg)
            return violations

        if not isinstance(schema, dict):
            return violations

        # Check cyclical reference
        if "$ref" in schema:
            ref_val = schema["$ref"]
            if ref_val in visited_ptrs:
                msg = f"Cyclical reference detected: {ref_val} (FEAT_REC_CYCLIC_SCHEMA)"
                if fail_closed:
                    raise UnsupportedSchemaFeatureError("FEAT_REC_CYCLIC_SCHEMA", msg, pointer)
                violations.append(msg)
                return violations

            # Check external reference
            if not ref_val.startswith("#/"):
                if ref_val.startswith("http://") or ref_val.startswith("https://"):
                    msg = f"Remote URL reference unsupported: {ref_val} (FEAT_REF_REMOTE_URL)"
                    if fail_closed:
                        raise UnsupportedSchemaFeatureError("FEAT_REF_REMOTE_URL", msg, pointer)
                    violations.append(msg)
                else:
                    msg = f"External file reference unsupported: {ref_val} (FEAT_REF_EXTERNAL_FILE)"
                    if fail_closed:
                        raise UnsupportedSchemaFeatureError("FEAT_REF_EXTERNAL_FILE", msg, pointer)
                    violations.append(msg)
                return violations

            if raw_doc is not None:
                new_visited = set(visited_ptrs)
                new_visited.add(ref_val)
                from src.extract_stage_b_canonical_contract import resolve_json_pointer
                try:
                    deref = resolve_json_pointer(raw_doc, ref_val)
                    violations.extend(
                        self.validate_schema_compliance(
                            deref,
                            ref_val,
                            new_visited,
                            current_depth,
                            fail_closed,
                            raw_doc,
                        )
                    )
                except KeyError:
                    pass
            return violations

        # Check composition / polymorphism keywords
        if "oneOf" in schema:
            msg = f"Polymorphic oneOf is unsupported fail-closed in general extractor (FEAT_COMP_ONEOF)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_COMP_ONEOF", msg, pointer)
            violations.append(msg)

        if "anyOf" in schema:
            msg = f"Polymorphic anyOf is unsupported fail-closed (FEAT_COMP_ANYOF)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_COMP_ANYOF", msg, pointer)
            violations.append(msg)

        if "not" in schema:
            msg = f"Negation keyword not is unsupported fail-closed (FEAT_COMP_NOT)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_COMP_NOT", msg, pointer)
            violations.append(msg)

        if "discriminator" in schema:
            msg = f"Discriminator object is unsupported fail-closed (FEAT_COMP_DISCRIMINATOR)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_COMP_DISCRIMINATOR", msg, pointer)
            violations.append(msg)

        # Check tuple array items
        if "items" in schema and isinstance(schema["items"], list):
            msg = f"Heterogeneous tuple array items is unsupported fail-closed (FEAT_ARR_ITEMS_TUPLE)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_ARR_ITEMS_TUPLE", msg, pointer)
            violations.append(msg)

        # Check binary formats
        fmt = schema.get("format")
        if fmt == "binary":
            msg = f"format: binary is unsupported fail-closed (FEAT_BIN_FORMAT_BINARY)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_BIN_FORMAT_BINARY", msg, pointer)
            violations.append(msg)
        elif fmt == "byte":
            msg = f"format: byte is unsupported fail-closed (FEAT_BIN_FORMAT_BYTE)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_BIN_FORMAT_BYTE", msg, pointer)
            violations.append(msg)

        # Check allowReserved
        if schema.get("allowReserved") is True:
            msg = f"allowReserved: true is unsupported fail-closed (FEAT_FORM_ALLOW_RESERVED)"
            if fail_closed:
                raise UnsupportedSchemaFeatureError("FEAT_FORM_ALLOW_RESERVED", msg, pointer)
            violations.append(msg)

        # Recurse properties
        if "properties" in schema and isinstance(schema["properties"], dict):
            for prop_name, prop_def in schema["properties"].items():
                violations.extend(
                    self.validate_schema_compliance(
                        prop_def,
                        f"{pointer}/properties/{prop_name}",
                        visited_ptrs,
                        current_depth + 1,
                        fail_closed,
                        raw_doc,
                    )
                )

        # Recurse items
        if "items" in schema and isinstance(schema["items"], dict):
            violations.extend(
                self.validate_schema_compliance(
                    schema["items"],
                    f"{pointer}/items",
                    visited_ptrs,
                    current_depth + 1,
                    fail_closed,
                    raw_doc,
                )
            )

        # Recurse additionalProperties if schema
        if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
            violations.extend(
                self.validate_schema_compliance(
                    schema["additionalProperties"],
                    f"{pointer}/additionalProperties",
                    visited_ptrs,
                    current_depth + 1,
                    fail_closed,
                    raw_doc,
                )
            )

        return violations


_GLOBAL_REGISTRY: Optional[SchemaFeatureRegistry] = None


def get_default_registry() -> SchemaFeatureRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = SchemaFeatureRegistry()
    return _GLOBAL_REGISTRY
