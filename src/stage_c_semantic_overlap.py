"""Stage C Semantic Overlap and Distractor Calibration Engine.

Computes lexical similarity, schema property overlap, signature collision,
and candidate tool viability heuristics for Tool Selection and Abstention tasks.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import re


class StageCSemanticOverlap:
    """Heuristic algorithms for measuring semantic and lexical overlap between tools."""

    @staticmethod
    def tokenize(text: str) -> Set[str]:
        """Extracts lowercase tokens excluding punctuation."""
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    @classmethod
    def jaccard_similarity(cls, set_a: Set[str], set_b: Set[str]) -> float:
        """Computes Jaccard index between two token sets."""
        if not set_a and not set_b:
            return 1.0
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        return len(intersection) / len(union) if union else 0.0

    @classmethod
    def text_similarity(cls, text_a: str, text_b: str) -> float:
        """Computes token Jaccard similarity between two text strings."""
        tokens_a = cls.tokenize(text_a)
        tokens_b = cls.tokenize(text_b)
        return cls.jaccard_similarity(tokens_a, tokens_b)

    @classmethod
    def compute_schema_overlap(
        cls,
        schema_a: Dict[str, Any],
        schema_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compares properties, required arrays, and types of two JSON schemas."""
        props_a = set(schema_a.get("properties", {}).keys())
        props_b = set(schema_b.get("properties", {}).keys())

        req_a = set(schema_a.get("required", []))
        req_b = set(schema_b.get("required", []))

        shared_props = props_a.intersection(props_b)
        prop_jaccard = cls.jaccard_similarity(props_a, props_b)

        # Check for signature collision
        identical_required = (req_a == req_b and len(req_a) > 0)

        # Check type matches for shared properties
        type_matches = 0
        p_dict_a = schema_a.get("properties", {})
        p_dict_b = schema_b.get("properties", {})
        for p in shared_props:
            type_a = p_dict_a.get(p, {}).get("type")
            type_b = p_dict_b.get(p, {}).get("type")
            if type_a == type_b:
                type_matches += 1

        type_match_ratio = (type_matches / len(shared_props)) if shared_props else 0.0

        return {
            "shared_properties": sorted(list(shared_props)),
            "property_jaccard": round(prop_jaccard, 4),
            "identical_required_signature": identical_required,
            "type_match_ratio": round(type_match_ratio, 4),
            "total_props_a": len(props_a),
            "total_props_b": len(props_b)
        }

    @classmethod
    def evaluate_distractor_proximity(
        cls,
        target_tool: Dict[str, Any],
        distractor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluates lexical and structural proximity between target tool and a distractor."""
        name_sim = cls.text_similarity(target_tool.get("tool_name", ""), distractor.get("tool_name", ""))
        desc_sim = cls.text_similarity(target_tool.get("description", ""), distractor.get("description", ""))

        schema_comp = cls.compute_schema_overlap(
            target_tool.get("schema", {}),
            distractor.get("schema", {})
        )

        is_duplicate = (
            target_tool.get("tool_name") == distractor.get("tool_name") or
            (desc_sim > 0.95 and schema_comp["property_jaccard"] > 0.95)
        )

        # Composite proximity heuristic score [0.0, 1.0]
        composite_score = round(
            0.3 * name_sim + 0.3 * desc_sim + 0.4 * schema_comp["property_jaccard"],
            4
        )

        return {
            "distractor_name": distractor.get("tool_name"),
            "name_similarity": round(name_sim, 4),
            "description_similarity": round(desc_sim, 4),
            "schema_overlap": schema_comp,
            "composite_proximity": composite_score,
            "is_duplicate_identity": is_duplicate,
            "identical_required": schema_comp["identical_required_signature"]
        }
