"""Stage C Leakage Features and Finding Representation.

Defines feature extractors, token normalizers, and the formal finding data structure
for auditing shortcut and prompt leakage in Stage C task instances.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple
import re


COMMON_DOMAIN_VOCABULARY = {
    "user", "name", "id", "email", "time", "date", "status", "type",
    "data", "message", "count", "limit", "value", "text", "file",
    "query", "record", "event", "session", "key", "code", "role"
}

MUTATION_FAMILY_LABELS = {
    "canonical", "nested", "hierarchy", "optionality", "bloat",
    "ambiguous", "identifiers", "distractor", "complexity"
}


@dataclass
class LeakageFinding:
    """Formal audit record for a detected leakage or shortcut pattern."""
    task_id: str
    dimension: str
    severity: str  # "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    classification: str  # "CLEAR", "REQUIRES_HUMAN_REVIEW", "AMBIGUOUS", "INVALID"
    evidence: str
    span: str
    remediation_category: str  # "NONE", "PARAPHRASE_VOCABULARY", "MASK_TOOL_NAME", "MARK_INVALID_REPLACE"
    requires_human_review: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StageCLeakageFeatures:
    """Feature extraction routines for prompt and schema leakage analysis."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Extracts lowercase alpha-numeric tokens."""
        return re.findall(r"[a-zA-Z0-9_]+", text.lower())

    @staticmethod
    def split_identifier(identifier: str) -> List[str]:
        """Splits snake_case or camelCase into component sub-words."""
        # Handle snake_case
        parts = identifier.split("_")
        subparts = []
        for p in parts:
            # Handle camelCase
            words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", p)
            if words:
                subparts.extend([w.lower() for w in words])
            elif p:
                subparts.append(p.lower())
        return [sp for sp in subparts if len(sp) > 1]

    @classmethod
    def check_tool_name_leakage(cls, prompt: str, tool_name: Optional[str]) -> Tuple[bool, bool, List[str]]:
        """Checks for exact tool name or sub-token stem occurrences in prompt.
        
        Returns: (has_exact_leak, has_stem_leak, matching_stems)
        """
        if not tool_name:
            return False, False, []

        p_lower = prompt.lower()
        tool_lower = tool_name.lower()

        # 1. Exact match (as whole word or contiguous phrase)
        exact_match = bool(re.search(r"\b" + re.escape(tool_lower) + r"\b", p_lower))

        # 2. Sub-token stems (excluding ultra-generic verbs like 'get', 'set', 'list')
        generic_verbs = {"get", "set", "list", "fetch", "create", "delete", "update", "run"}
        stems = cls.split_identifier(tool_name)
        meaningful_stems = [s for s in stems if s not in generic_verbs and len(s) > 3]

        p_spaced = p_lower.replace("_", " ")
        matched_stems = []
        for s in meaningful_stems:
            if re.search(r"\b" + re.escape(s) + r"\b", p_spaced):
                matched_stems.append(s)

        has_stem = len(matched_stems) >= 2 or (len(matched_stems) == 1 and not exact_match and len(matched_stems[0]) > 6)
        return exact_match, has_stem, matched_stems

    @classmethod
    def check_field_name_leakage(
        cls,
        prompt: str,
        schema_properties: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """Identifies schema field names appearing in prompt text.
        
        Distinguishes between common domain vocabulary and specialized parameter names.
        Returns list of (field_name, category) where category is 'UNAVOIDABLE_DOMAIN_WORD' or 'SHORTCUT_LEAK'.
        """
        p_lower = prompt.lower()
        findings = []

        for field_name in schema_properties.keys():
            # Check exact occurrence
            if re.search(r"\b" + re.escape(field_name.lower()) + r"\b", p_lower):
                if field_name.lower() in COMMON_DOMAIN_VOCABULARY:
                    findings.append((field_name, "UNAVOIDABLE_DOMAIN_WORD"))
                else:
                    findings.append((field_name, "SHORTCUT_LEAK"))
            else:
                # Check if multi-word snake_case leaked as contiguous phrase
                if "_" in field_name:
                    spaced = field_name.replace("_", " ").lower()
                    if spaced in p_lower:
                        findings.append((field_name, "SHORTCUT_LEAK"))

        return findings

    @classmethod
    def check_mutation_label_leakage(cls, prompt: str) -> List[str]:
        """Detects whether benchmark internal mutation labels leak into prompts."""
        p_lower = prompt.lower()
        leaks = []
        for label in MUTATION_FAMILY_LABELS:
            if re.search(r"\b" + re.escape(label) + r"\b", p_lower):
                leaks.append(label)
        return leaks
