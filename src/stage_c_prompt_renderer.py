"""Stage C Prompt Renderer.

Deterministically renders system prompts, tool declarations, and user instructions
for Stage C task instances without leaking solution parameters or oracle metadata.
"""

from typing import Any, Dict, List, Optional
import json


class StageCPromptRenderer:
    """Renders benchmark prompts for LLM tool invocation testing."""

    SYSTEM_TEMPLATE = (
        "You are an automated assistant with access to the following tools. "
        "When responding to the user's request, invoke the most appropriate tool "
        "with well-formed JSON arguments matching the tool's parameter schema. "
        "If the user's request cannot be safely or completely fulfilled with the available tools, "
        "or if mandatory information is missing, do not call any tool; instead, abstain."
    )

    @classmethod
    def render_prompt(
        cls,
        user_instruction: str,
        tool_declarations: List[Dict[str, Any]],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Renders standard messages payload containing system instruction, tools, and user message."""
        sys_msg = system_instruction or cls.SYSTEM_TEMPLATE

        # Clean tool representations (remove benchmark-internal metadata)
        clean_tools = []
        for t in tool_declarations:
            clean_tools.append({
                "type": "function",
                "function": {
                    "name": t["tool_name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("schema", {})
                }
            })

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_instruction}
        ]

        return {
            "messages": messages,
            "tools": clean_tools
        }

    @staticmethod
    def check_for_gold_leakage(user_instruction: str, expected_arguments: Optional[Dict[str, Any]]) -> List[str]:
        """Adversarial audit to verify prompt does not leak exact raw JSON argument strings."""
        leakages = []
        if not expected_arguments:
            return leakages

        # Check if raw JSON serialization is dumped verbatim in prompt
        raw_json = json.dumps(expected_arguments)
        if raw_json in user_instruction:
            leakages.append("Exact JSON serialization found in user prompt.")

        return leakages
