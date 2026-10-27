"""Tests for Stage C Response Parser (Track 5).

Verifies handling of OpenAI tool_calls payloads, markdown JSON blocks,
raw text JSON, explicit abstention keywords, and malformed strings.
"""

from src.stage_c_response_parser import StageCResponseParser


def test_parse_openai_tool_calls_format():
    payload = {
        "tool_calls": [
            {
                "function": {
                    "name": "set_cache_entry",
                    "arguments": '{"key": "user_1024", "value": "active"}'
                }
            }
        ]
    }
    parsed = StageCResponseParser.parse_response(payload)
    assert parsed.is_abstention is False
    assert parsed.tool_name == "set_cache_entry"
    assert parsed.arguments == {"key": "user_1024", "value": "active"}
    assert len(parsed.parse_errors) == 0


def test_parse_openai_empty_tool_calls_as_abstention():
    payload = {"tool_calls": []}
    parsed = StageCResponseParser.parse_response(payload)
    assert parsed.is_abstention is True
    assert parsed.tool_name is None
    assert parsed.arguments is None


def test_parse_markdown_json_block():
    text = (
        "Here is the invocation:\n"
        "```json\n"
        '{"name": "fetch_metrics", "arguments": {"metric_id": "cpu_util"}}\n'
        "```"
    )
    parsed = StageCResponseParser.parse_response(text)
    assert parsed.is_abstention is False
    assert parsed.tool_name == "fetch_metrics"
    assert parsed.arguments == {"metric_id": "cpu_util"}


def test_parse_raw_json():
    text = '{"name": "send_alert", "arguments": {"level": "critical"}}'
    parsed = StageCResponseParser.parse_response(text)
    assert parsed.is_abstention is False
    assert parsed.tool_name == "send_alert"
    assert parsed.arguments == {"level": "critical"}


def test_parse_explicit_abstention_phrases():
    phrases = [
        "ABSTAIN",
        "I cannot safely fulfill this request due to missing arguments.",
        "Unable to execute because of contradictory bounds.",
        "The operation is not supported by available tools."
    ]
    for p in phrases:
        parsed = StageCResponseParser.parse_response(p)
        assert parsed.is_abstention is True, f"Failed to detect abstention in: {p}"
        assert parsed.tool_name is None


def test_parse_malformed_text():
    text = "Just some unformatted chat output without tools."
    parsed = StageCResponseParser.parse_response(text)
    assert parsed.is_abstention is False
    assert parsed.tool_name is None
    assert len(parsed.parse_errors) > 0
