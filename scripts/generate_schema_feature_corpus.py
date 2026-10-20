#!/usr/bin/env python3
"""Generates the Stage B synthetic schema feature corpus.

Creates synthetic OpenAPI 3.0 / JSON Schema specifications under:
tests/fixtures/schema_feature_corpus/

These fixtures systematically test all schema features, edge cases,
deep nesting, ref chains, naming anomalies, and unsupported fail-closed constructs.
"""

import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(ROOT_DIR, "tests", "fixtures", "schema_feature_corpus")


def make_openapi_wrapper(operation_id: str, parameters: list, request_body: dict = None, components: dict = None) -> dict:
    op: dict = {
        "operationId": operation_id,
        "summary": f"Synthetic operation {operation_id}",
        "description": f"Detailed description for synthetic operation {operation_id}",
        "parameters": parameters,
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {"application/json": {"schema": {"type": "object"}}},
            }
        },
    }
    if request_body:
        op["requestBody"] = request_body

    doc = {
        "openapi": "3.0.3",
        "info": {"title": f"Synthetic Fixture Spec - {operation_id}", "version": "1.0.0"},
        "paths": {
            f"/synthetic/{operation_id}": {
                "post": op
            }
        },
    }
    if components:
        doc["components"] = components
    return doc


def main() -> None:
    os.makedirs(FIXTURES_DIR, exist_ok=True)

    # 1. Primitives Fixture
    primitives_schema = {
        "type": "object",
        "properties": {
            "str_val": {"type": "string", "description": "String property"},
            "int_val": {"type": "integer", "format": "int64", "description": "Integer property"},
            "num_val": {"type": "number", "format": "double", "description": "Float property"},
            "bool_val": {"type": "boolean", "description": "Boolean flag"},
            "null_val": {"type": "null", "description": "Explicit null"},
            "date_time_val": {"type": "string", "format": "date-time"},
            "uuid_val": {"type": "string", "format": "uuid"},
            "uri_val": {"type": "string", "format": "uri"},
            "email_val": {"type": "string", "format": "email"},
        },
        "required": ["str_val", "int_val", "bool_val"],
    }
    prim_doc = make_openapi_wrapper(
        "synthetic_primitives",
        [],
        {"content": {"application/json": {"schema": primitives_schema}}},
    )
    with open(os.path.join(FIXTURES_DIR, "primitives_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(prim_doc, f, indent=2, sort_keys=True)

    # 2. Enums and Defaults Fixture
    enums_defaults_schema = {
        "type": "object",
        "properties": {
            "str_enum": {"type": "string", "enum": ["ACTIVE", "INACTIVE", "PENDING"]},
            "int_enum": {"type": "integer", "enum": [10, 20, 30, 40]},
            "const_val": {"type": "string", "const": "CANONICAL_TARGET"},
            "default_str": {"type": "string", "default": "fallback_token"},
            "default_int": {"type": "integer", "default": 42},
            "example_str": {"type": "string", "example": "sample_account_id"},
            "examples_map": {
                "type": "string",
                "examples": {"ex1": {"value": "first"}, "ex2": {"value": "second"}},
            },
        },
        "required": ["str_enum", "const_val"],
    }
    enums_doc = make_openapi_wrapper(
        "synthetic_enums_defaults",
        [],
        {"content": {"application/json": {"schema": enums_defaults_schema}}},
    )
    with open(os.path.join(FIXTURES_DIR, "enums_defaults_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(enums_doc, f, indent=2, sort_keys=True)

    # 3. Bounds and Constraints Fixture
    bounds_schema = {
        "type": "object",
        "properties": {
            "bounded_int": {"type": "integer", "minimum": 1, "maximum": 100, "multipleOf": 5},
            "exclusive_num": {"type": "number", "exclusiveMinimum": 0.0, "exclusiveMaximum": 1.0},
            "bounded_str": {
                "type": "string",
                "minLength": 3,
                "maxLength": 64,
                "pattern": "^[a-zA-Z0-9_-]+$",
            },
            "bounded_arr": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 10,
                "uniqueItems": True,
            },
            "bounded_obj": {
                "type": "object",
                "minProperties": 1,
                "maxProperties": 5,
                "additionalProperties": {"type": "string"},
            },
        },
    }
    bounds_doc = make_openapi_wrapper(
        "synthetic_bounds_constraints",
        [],
        {"content": {"application/json": {"schema": bounds_schema}}},
    )
    with open(os.path.join(FIXTURES_DIR, "bounds_constraints_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(bounds_doc, f, indent=2, sort_keys=True)

    # 4. Objects and Arrays Fixture (with deep nesting, naming anomalies, descriptions)
    objects_arrays_schema = {
        "type": "object",
        "properties": {
            "camelCaseProp": {"type": "string"},
            "snake_case_prop": {"type": "integer"},
            "kebab-case-prop": {"type": "boolean"},
            "123_numeric_leading": {"type": "string"},
            "markdown_desc": {
                "type": "string",
                "description": "Line 1\nLine 2 with `code` & unicode: \u2713 and symbols <>&'\"",
            },
            "empty_desc": {"type": "string", "description": ""},
            "arr_of_prims": {"type": "array", "items": {"type": "string"}},
            "arr_of_arrs": {"type": "array", "items": {"type": "array", "items": {"type": "integer"}}},
            "arr_of_objs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}, "weight": {"type": "number"}},
                    "required": ["id"],
                },
            },
            "open_object": {"type": "object", "additionalProperties": True},
            "closed_object": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"fixed_key": {"type": "string"}},
            },
            "schema_map_object": {
                "type": "object",
                "additionalProperties": {"type": "string", "description": "Dynamic tag value"},
            },
            # Depth 1 -> 2 -> 3 -> 4 -> 5 nesting
            "level1": {
                "type": "object",
                "properties": {
                    "level2": {
                        "type": "object",
                        "properties": {
                            "level3": {
                                "type": "object",
                                "properties": {
                                    "level4": {
                                        "type": "object",
                                        "properties": {
                                            "level5_leaf": {"type": "string", "description": "Max depth leaf"}
                                        },
                                    }
                                },
                            }
                        },
                    }
                },
            },
        },
    }
    objs_doc = make_openapi_wrapper(
        "synthetic_objects_arrays",
        [],
        {"content": {"application/json": {"schema": objects_arrays_schema}}},
    )
    with open(os.path.join(FIXTURES_DIR, "objects_arrays_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(objs_doc, f, indent=2, sort_keys=True)

    # 5. References Fixture (1-hop, 2-hop, 3-hop)
    ref_components = {
        "schemas": {
            "LeafSchema": {
                "type": "object",
                "properties": {"leaf_code": {"type": "string"}, "leaf_score": {"type": "integer"}},
                "required": ["leaf_code"],
            },
            "Hop2Schema": {
                "type": "object",
                "properties": {
                    "hop2_title": {"type": "string"},
                    "leaf_target": {"$ref": "#/components/schemas/LeafSchema"},
                },
            },
            "Hop3Schema": {
                "type": "object",
                "properties": {
                    "hop3_root": {"type": "string"},
                    "hop2_target": {"$ref": "#/components/schemas/Hop2Schema"},
                },
            },
        }
    }
    refs_doc = make_openapi_wrapper(
        "synthetic_references",
        [],
        {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Hop3Schema"}}}},
        components=ref_components,
    )
    with open(os.path.join(FIXTURES_DIR, "references_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(refs_doc, f, indent=2, sort_keys=True)

    # 6. Modifiers and Metadata Fixture
    modifiers_schema = {
        "type": "object",
        "title": "ModifiersMetadataContract",
        "description": "Contract testing nullable, readOnly, writeOnly, deprecated, format",
        "properties": {
            "nullable_str": {"type": "string", "nullable": True},
            "readonly_id": {"type": "string", "readOnly": True},
            "writeonly_secret": {"type": "string", "writeOnly": True},
            "deprecated_flag": {"type": "boolean", "deprecated": True},
            "formatted_timestamp": {"type": "string", "format": "date-time"},
        },
    }
    mod_doc = make_openapi_wrapper(
        "synthetic_modifiers_metadata",
        [],
        {"content": {"application/json": {"schema": modifiers_schema}}},
    )
    with open(os.path.join(FIXTURES_DIR, "modifiers_metadata_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(mod_doc, f, indent=2, sort_keys=True)

    # 7. Transport Surfaces Fixture (path params + query + header + body)
    surfaces_params = [
        {"name": "org_id", "in": "path", "required": True, "schema": {"type": "string", "pattern": "^org_[a-z0-9]+$"}},
        {"name": "include_details", "in": "query", "required": False, "schema": {"type": "boolean", "default": False}},
        {"name": "X-Idempotency-Key", "in": "header", "required": False, "schema": {"type": "string"}},
    ]
    surfaces_body = {
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {"action": {"type": "string"}, "target": {"type": "string"}},
                    "required": ["action"],
                }
            }
        }
    }
    surfaces_doc = make_openapi_wrapper("synthetic_transport_surfaces", surfaces_params, surfaces_body)
    with open(os.path.join(FIXTURES_DIR, "transport_surfaces_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(surfaces_doc, f, indent=2, sort_keys=True)

    # 8. Form Modifiers Fixture (application/x-www-form-urlencoded + deepObject)
    form_body = {
        "content": {
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "integer"},
                        "currency": {"type": "string"},
                        "metadata": {"type": "object", "additionalProperties": {"type": "string"}},
                    },
                    "required": ["amount", "currency"],
                },
                "encoding": {
                    "metadata": {"style": "deepObject", "explode": True}
                },
            }
        }
    }
    form_doc = make_openapi_wrapper("synthetic_form_modifiers", [], form_body)
    with open(os.path.join(FIXTURES_DIR, "form_modifiers_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(form_doc, f, indent=2, sort_keys=True)

    # 9. Composition Fixture (allOf)
    comp_components = {
        "schemas": {
            "BaseEntity": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "created_at": {"type": "integer"}},
                "required": ["id"],
            },
            "ExtendedEntity": {
                "allOf": [
                    {"$ref": "#/components/schemas/BaseEntity"},
                    {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "role": {"type": "string"}},
                        "required": ["name"],
                    },
                ]
            },
        }
    }
    comp_doc = make_openapi_wrapper(
        "synthetic_composition",
        [],
        {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/ExtendedEntity"}}}},
        components=comp_components,
    )
    with open(os.path.join(FIXTURES_DIR, "composition_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(comp_doc, f, indent=2, sort_keys=True)

    # 10. Unsupported Fixtures (FAIL CLOSED)
    unsupported_defs = [
        ("unsupported_oneof_fixture.json", {"oneOf": [{"type": "string"}, {"type": "integer"}]}),
        ("unsupported_anyof_fixture.json", {"anyOf": [{"type": "string"}, {"type": "number"}]}),
        ("unsupported_not_fixture.json", {"not": {"type": "string"}}),
        ("unsupported_discriminator_fixture.json", {"type": "object", "discriminator": {"propertyName": "kind"}}),
        ("unsupported_tuple_fixture.json", {"type": "array", "items": [{"type": "string"}, {"type": "integer"}]}),
        ("unsupported_binary_fixture.json", {"type": "string", "format": "binary"}),
        ("unsupported_byte_fixture.json", {"type": "string", "format": "byte"}),
        ("unsupported_allow_reserved_fixture.json", {"type": "string", "allowReserved": True}),
        ("unsupported_external_ref_fixture.json", {"$ref": "./external.json#/definitions/Target"}),
        ("unsupported_remote_ref_fixture.json", {"$ref": "https://api.example.com/schemas/spec.json"}),
        ("unsupported_pipe_delimited_fixture.json", {"type": "array", "style": "pipeDelimited"}),
        ("unsupported_space_delimited_fixture.json", {"type": "array", "style": "spaceDelimited"}),
        ("unsupported_stream_fixture.json", {"type": "string", "format": "stream"}),
    ]

    for fname, schema_body in unsupported_defs:
        doc = make_openapi_wrapper(fname.replace(".json", ""), [], {"content": {"application/json": {"schema": schema_body}}})
        with open(os.path.join(FIXTURES_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, sort_keys=True)

    # Parameter-level unsupported fixtures (cookie)
    cookie_doc = make_openapi_wrapper("unsupported_cookie", [{"name": "session_id", "in": "cookie", "schema": {"type": "string"}}])
    with open(os.path.join(FIXTURES_DIR, "unsupported_cookie_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(cookie_doc, f, indent=2, sort_keys=True)

    # Content-type unsupported fixtures (multipart, text/plain, octet-stream)
    for ct, fname in [
        ("multipart/form-data", "unsupported_multipart_fixture.json"),
        ("text/plain", "unsupported_text_plain_fixture.json"),
        ("application/octet-stream", "unsupported_octet_stream_fixture.json"),
    ]:
        doc = make_openapi_wrapper(fname.replace(".json", ""), [], {"content": {ct: {"schema": {"type": "string"}}}})
        with open(os.path.join(FIXTURES_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, sort_keys=True)

    # Cyclical ref fixture
    cyclic_components = {
        "schemas": {
            "CyclicNode": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "child": {"$ref": "#/components/schemas/CyclicNode"},
                },
            }
        }
    }
    cyclic_doc = make_openapi_wrapper(
        "unsupported_cyclic",
        [],
        {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/CyclicNode"}}}},
        components=cyclic_components,
    )
    with open(os.path.join(FIXTURES_DIR, "unsupported_cyclic_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(cyclic_doc, f, indent=2, sort_keys=True)

    # Excessive depth fixture (depth 6)
    excessive_schema = {"type": "object", "properties": {}}
    cur = excessive_schema
    for i in range(6):
        cur["properties"] = {"child": {"type": "object", "properties": {}}}
        cur = cur["properties"]["child"]
    cur["properties"] = {"leaf": {"type": "string"}}
    excessive_doc = make_openapi_wrapper(
        "unsupported_excessive_depth",
        [],
        {"content": {"application/json": {"schema": excessive_schema}}},
    )
    with open(os.path.join(FIXTURES_DIR, "unsupported_excessive_depth_fixture.json"), "w", encoding="utf-8") as f:
        json.dump(excessive_doc, f, indent=2, sort_keys=True)

    print(f"Generated synthetic fixture corpus at {FIXTURES_DIR}")


if __name__ == "__main__":
    main()
