"""Stage C Response Parser.

Parses model output text or structured payloads into candidate tool invocations
or explicit abstention signals.
Handles varied LLM output formats: tool_calls list, JSON code blocks, raw JSON,
and explicit abstention phrases.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import re


@dataclass
class ParsedCandidateInvocation:
    """Standardized representation of a model's parsed action."""
    tool_name: Optional[str]
    arguments: Optional[Dict[str, Any]]
    is_abstention: bool
    raw_response: str
    parse_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "is_abstention": self.is_abstention,
            "raw_response": self.raw_response,
            "parse_errors": self.parse_errors
        }


class StageCResponseParser:
    """Deterministic offline parser for model responses."""

    ABSTENTION_PATTERNS = [
        r"\bABSTAIN\b",
        r"\bcannot\s+(?:safely\s+|completely\s+)?fulfill\b",
        r"\bmissing\s+(?:mandatory|required)\s+parameter\b",
        r"\bnot\s+supported\s+by\s+available\s+tools\b",
        r"\bunable\s+to\s+execute\b",
        r"\bdo\s+not\s+have\s+sufficient\s+information\b",
    ]

    @classmethod
    def parse_response(cls, response: Any) -> ParsedCandidateInvocation:
        """Parses model response into a standardized invocation or abstention."""
        # 1. Structured API tool_calls object (OpenAI / Anthropic format)
        if isinstance(response, dict) and "tool_calls" in response:
            tool_calls = response.get("tool_calls", [])
            if not tool_calls:
                # Empty tool_calls list treated as abstention
                return ParsedCandidateInvocation(
                    tool_name=None,
                    arguments=None,
                    is_abstention=True,
                    raw_response=json.dumps(response)
                )

            first_call = tool_calls[0]
            func = first_call.get("function", {})
            name = func.get("name")
            raw_args = func.get("arguments", {})
            parsed_args = {}
            errors = []

            if isinstance(raw_args, str):
                try:
                    parsed_args = json.loads(raw_args)
                except Exception as exc:
                    errors.append(f"JSON decode error: {str(exc)}")
            elif isinstance(raw_args, dict):
                parsed_args = raw_args

            return ParsedCandidateInvocation(
                tool_name=name,
                arguments=parsed_args if not errors else None,
                is_abstention=False,
                raw_response=json.dumps(response),
                parse_errors=errors
            )

        # 2. String responses
        raw_text = str(response).strip() if response is not None else ""

        if not raw_text:
            return ParsedCandidateInvocation(
                tool_name=None,
                arguments=None,
                is_abstention=True,
                raw_response=""
            )

        # Check for abstention cues
        for pat in cls.ABSTENTION_PATTERNS:
            if re.search(pat, raw_text, re.IGNORECASE):
                return ParsedCandidateInvocation(
                    tool_name=None,
                    arguments=None,
                    is_abstention=True,
                    raw_response=raw_text
                )

        # Extract markdown JSON blocks ```json ... ```
        json_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if json_block_match:
            candidate_json = json_block_match.group(1)
            try:
                parsed = json.loads(candidate_json)
                if isinstance(parsed, dict):
                    # Check if schema specifies name/arguments wrapper
                    name = parsed.get("name") or parsed.get("tool_name")
                    args = parsed.get("arguments") or parsed.get("parameters") or parsed
                    if name and isinstance(args, dict):
                        return ParsedCandidateInvocation(
                            tool_name=name,
                            arguments=args,
                            is_abstention=False,
                            raw_response=raw_text
                        )
                    elif isinstance(parsed, dict):
                        # Direct argument dictionary
                        return ParsedCandidateInvocation(
                            tool_name=None,
                            arguments=parsed,
                            is_abstention=False,
                            raw_response=raw_text
                        )
            except Exception as exc:
                return ParsedCandidateInvocation(
                    tool_name=None,
                    arguments=None,
                    is_abstention=False,
                    raw_response=raw_text,
                    parse_errors=[f"Markdown block JSON decode error: {str(exc)}"]
                )

        # Attempt raw JSON parse
        if raw_text.startswith("{") and raw_text.endswith("}"):
            try:
                parsed = json.loads(raw_text)
                name = parsed.get("name") or parsed.get("tool_name")
                args = parsed.get("arguments") or parsed.get("parameters")
                if name and isinstance(args, dict):
                    return ParsedCandidateInvocation(
                        tool_name=name,
                        arguments=args,
                        is_abstention=False,
                        raw_response=raw_text
                    )
                else:
                    return ParsedCandidateInvocation(
                        tool_name=name,
                        arguments=parsed,
                        is_abstention=False,
                        raw_response=raw_text
                    )
            except Exception as exc:
                return ParsedCandidateInvocation(
                    tool_name=None,
                    arguments=None,
                    is_abstention=False,
                    raw_response=raw_text,
                    parse_errors=[f"Raw text JSON decode error: {str(exc)}"]
                )

        # Unstructured text that did not match abstention pattern
        return ParsedCandidateInvocation(
            tool_name=None,
            arguments=None,
            is_abstention=False,
            raw_response=raw_text,
            parse_errors=["Response did not contain valid structured tool invocation or abstention."]
        )
