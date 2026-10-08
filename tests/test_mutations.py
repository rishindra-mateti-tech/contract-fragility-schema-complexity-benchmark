"""
tests/test_mutations.py - Formal property-based unit tests verifying mutation isolation.
Asserts that each controlled structural mutation changes only its intended property
and leaves all other schema dimensions invariant.
"""

import json
import os
import unittest
from jsonschema import Draft7Validator

from src.schema_mutator import (
    OPTIONAL_BLOAT_PROPERTIES,
    AMBIGUOUS_NAME_MAPPINGS,
    create_canonical_variant,
    create_nested_variant,
    create_optionality_bloat_variant,
    create_ambiguous_identifiers_variant,
)

class TestMutationIsolation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_path = os.path.join(root_dir, "data", "base_schemas.json")
        distractor_path = os.path.join(root_dir, "data", "distractor_tools.json")

        with open(base_path, "r", encoding="utf-8") as f:
            cls.base_schemas = json.load(f)

        with open(distractor_path, "r", encoding="utf-8") as f:
            cls.distractors = json.load(f)

    def _convert_to_draft7(self, schema_dict):
        """Helper to convert uppercase types to lowercase for Draft7Validator checking."""
        s = json.loads(json.dumps(schema_dict))
        def _lower_types(obj):
            if isinstance(obj, dict):
                if "type" in obj and isinstance(obj["type"], str):
                    obj["type"] = obj["type"].lower()
                for v in obj.values():
                    _lower_types(v)
            elif isinstance(obj, list):
                for item in obj:
                    _lower_types(item)
        _lower_types(s)
        return s

    def test_canonical_invariance(self):
        """Canonical variant must be an exact structural copy of base schema with Draft-07 validity."""
        for base in self.base_schemas:
            var = create_canonical_variant(base)
            self.assertEqual(var["mutation_type"], "canonical")
            self.assertEqual(var["tool"]["name"], base["name"])
            self.assertEqual(var["tool"]["description"], base["description"])
            self.assertEqual(var["tool"]["parameters"], base["parameters"])
            self.assertEqual(var["expected_args"], base["ground_truth"])

            draft7 = self._convert_to_draft7(var["tool"]["parameters"])
            self.assertTrue(Draft7Validator.check_schema(draft7) is None,
                            f"Canonical schema {base['name']} failed Draft-07 validation")

    def test_nested_hierarchy_isolation(self):
        """Nested hierarchy must mutate depth: wrapping properties inside transaction_context -> data -> attributes."""
        for base in self.base_schemas:
            var = create_nested_variant(base)
            params = var["tool"]["parameters"]

            # 1. Exactly one root property
            self.assertEqual(list(params["properties"].keys()), ["transaction_context"])
            self.assertEqual(params["required"], ["transaction_context"])

            # 2. Sub-object properties match base properties exactly (at the deepest level)
            sub_obj = params["properties"]["transaction_context"]["properties"]["data"]["properties"]["attributes"]
            self.assertEqual(sub_obj["type"], "OBJECT")
            self.assertEqual(set(sub_obj["properties"].keys()), set(base["parameters"]["properties"].keys()))

            for prop_name, base_prop in base["parameters"]["properties"].items():
                nested_prop = sub_obj["properties"][prop_name]
                self.assertEqual(nested_prop["type"], base_prop["type"],
                                 f"Type mutated in nested property {prop_name}")
                if "enum" in base_prop:
                    self.assertEqual(nested_prop["enum"], base_prop["enum"])

            # 3. Required fields within sub-object match base required fields
            self.assertEqual(set(sub_obj.get("required", [])), set(base["parameters"].get("required", [])))

            # 4. Expected args wraps ground truth under transaction_context -> data -> attributes
            self.assertEqual(var["expected_args"], {"transaction_context": {"data": {"attributes": base["ground_truth"]}}})

            # 5. Draft-07 Validity
            draft7 = self._convert_to_draft7(params)
            self.assertTrue(Draft7Validator.check_schema(draft7) is None)

    def test_optionality_bloat_isolation(self):
        """Optionality bloat must mutate ONLY optional property density; all required fields remain invariant."""
        for base in self.base_schemas:
            var = create_optionality_bloat_variant(base)
            params = var["tool"]["parameters"]

            # 1. Base properties are preserved unchanged
            for prop_name, base_prop in base["parameters"]["properties"].items():
                self.assertIn(prop_name, params["properties"])
                self.assertEqual(params["properties"][prop_name]["type"], base_prop["type"])

            # 2. Required properties are 100% unchanged
            self.assertEqual(set(params.get("required", [])), set(base["parameters"].get("required", [])))

            # 3. Injected properties belong strictly to OPTIONAL_BLOAT_PROPERTIES
            new_keys = set(params["properties"].keys()) - set(base["parameters"]["properties"].keys())
            for k in new_keys:
                self.assertIn(k, OPTIONAL_BLOAT_PROPERTIES)
                self.assertNotIn(k, params.get("required", []), f"Bloat property {k} must not be required")

            # 4. Expected arguments remain identical to base ground truth
            self.assertEqual(var["expected_args"], base["ground_truth"])

            # 5. Draft-07 Validity
            draft7 = self._convert_to_draft7(params)
            self.assertTrue(Draft7Validator.check_schema(draft7) is None)

    def test_ambiguous_identifiers_isolation(self):
        """Ambiguous identifiers must mutate names and docstrings while preserving parameter types and enums."""
        for base in self.base_schemas:
            var = create_ambiguous_identifiers_variant(base)
            params = var["tool"]["parameters"]

            # 1. Property count matches base property count
            self.assertEqual(len(params["properties"]), len(base["parameters"]["properties"]))

            # 2. Required property count matches base required count
            self.assertEqual(len(params.get("required", [])), len(base["parameters"].get("required", [])))

            # 3. Tool name and description are mutated
            self.assertNotEqual(var["tool"]["name"], base["name"])
            self.assertNotEqual(var["tool"]["description"], base["description"])

            # 4. Parameter types and enums are preserved
            for old_name, old_prop in base["parameters"]["properties"].items():
                new_name = AMBIGUOUS_NAME_MAPPINGS.get(old_name, f"param_{old_name[:3]}_v2")
                self.assertIn(new_name, params["properties"])
                new_prop = params["properties"][new_name]
                self.assertEqual(new_prop["type"], old_prop["type"],
                                 f"Type mismatch under ambiguous rename: {old_name} -> {new_name}")
                if "enum" in old_prop:
                    self.assertEqual(new_prop["enum"], old_prop["enum"])

            # 5. Ground truth values are preserved under new keys
            for old_key, old_val in base["ground_truth"].items():
                new_key = AMBIGUOUS_NAME_MAPPINGS.get(old_key, f"param_{old_key[:3]}_v2")
                self.assertIn(new_key, var["expected_args"])
                self.assertEqual(var["expected_args"][new_key], old_val)

            # 6. Draft-07 Validity
            draft7 = self._convert_to_draft7(params)
            self.assertTrue(Draft7Validator.check_schema(draft7) is None)

    def test_distractor_tools_integrity(self):
        """Distractor catalog must contain valid Draft-07 schemas without target tool collisions."""
        for base in self.base_schemas:
            bid = base["id"]
            if bid in self.distractors:
                dist_suite = self.distractors[bid]
                self.assertGreaterEqual(len(dist_suite), 2, f"Distractor suite for {bid} has too few tools")
                for dtool in dist_suite:
                    # No name collision with target tool
                    self.assertNotEqual(dtool["name"], base["name"])
                    draft7 = self._convert_to_draft7(dtool["parameters"])
                    self.assertTrue(Draft7Validator.check_schema(draft7) is None,
                                    f"Distractor tool {dtool['name']} failed Draft-07 validation")

if __name__ == "__main__":
    unittest.main()
