"""Tests for Stage C Task Compiler and Prompt Renderer (Track 4).

Verifies task compilation, category distribution, prompt rendering,
and leakage prevention.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_prompt_renderer import StageCPromptRenderer


REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "data_stage_c" / "task_instances"
MANIFEST_PATH = REPO_ROOT / "results_stage_c" / "TASK_SET_MANIFEST.json"


def test_task_manifest_and_category_counts():
    assert MANIFEST_PATH.is_file(), f"Manifest missing at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["total_tasks"] == 300
    assert len(manifest["tasks"]) == 300

    cats = manifest["category_distribution"]
    assert cats.get("ARGUMENT_CONSTRUCTION") == 100
    assert cats.get("TOOL_SELECTION") == 100
    assert cats.get("ABSTENTION") == 100

    task_files = list(TASKS_DIR.glob("TASK_SYNTH_*.json"))
    assert len(task_files) == 300


def test_prompt_renderer_clean_tools():
    tool_decl = [{
        "tool_name": "execute_query",
        "description": "Executes query",
        "schema": {"type": "object", "properties": {"q": {"type": "string"}}},
        "internal_benchmark_metadata": "do_not_leak"
    }]

    rendered = StageCPromptRenderer.render_prompt(
        user_instruction="Run query 'SELECT 1'",
        tool_declarations=tool_decl
    )

    assert "messages" in rendered
    assert "tools" in rendered
    assert len(rendered["tools"]) == 1

    clean_fn = rendered["tools"][0]["function"]
    assert clean_fn["name"] == "execute_query"
    assert clean_fn["description"] == "Executes query"
    assert "internal_benchmark_metadata" not in clean_fn


def test_prompt_leakage_detector():
    args = {"user_id": "usr_99", "action": "delete"}
    leaky_prompt = f"Please run tool with {json.dumps(args)}"
    clean_prompt = "Please delete user usr_99"

    assert len(StageCPromptRenderer.check_for_gold_leakage(leaky_prompt, args)) > 0
    assert len(StageCPromptRenderer.check_for_gold_leakage(clean_prompt, args)) == 0
