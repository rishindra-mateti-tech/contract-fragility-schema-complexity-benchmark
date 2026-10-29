"""Tests for Stage C Release 2 Task Compiler (Track 2).

Verifies that the task compiler generates 300 compliant task instances across
Argument Construction, Tool Selection, and Abstention with zero prompt leaks.
"""

from pathlib import Path
import json
import pytest

from src.stage_c_release2_task_compiler import (
    StageCRelease2TaskCompiler,
    R2_TASKS_DIR,
    R2_MANIFEST_PATH
)


def test_compiled_task_manifest_counts():
    assert R2_MANIFEST_PATH.is_file(), f"Missing manifest at {R2_MANIFEST_PATH}"

    with open(R2_MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("benchmark_release") == "RELEASE_2"
    assert manifest.get("release_marker") == "RELEASE_2_PENDING_HUMAN_VALIDATION"
    assert manifest.get("total_tasks") == 300

    dist = manifest.get("category_distribution", {})
    assert dist.get("ARGUMENT_CONSTRUCTION") == 100
    assert dist.get("TOOL_SELECTION") == 100
    assert dist.get("ABSTENTION") == 100


def test_argument_construction_task_structure():
    task_files = sorted(R2_TASKS_DIR.glob("TASK_R2_AC_*.json"))
    assert len(task_files) == 100

    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            t = json.load(f)

        assert t["category"] == "ARGUMENT_CONSTRUCTION"
        assert len(t["available_tools"]) == 1
        assert t["target_position"] == 0
        assert t["expected_tool_name"] is not None
        assert t["expected_arguments"] is not None

        # Verify no tool name leakage
        target_name = t["expected_tool_name"]
        assert target_name.lower() not in t["user_prompt"].lower()


def test_tool_selection_task_structure():
    task_files = sorted(R2_TASKS_DIR.glob("TASK_R2_TS_*.json"))
    assert len(task_files) == 100

    target_positions = {}
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            t = json.load(f)

        assert t["category"] == "TOOL_SELECTION"
        assert len(t["available_tools"]) >= 3
        assert t["expected_tool_name"] is not None

        target_name = t["expected_tool_name"]
        assert target_name.lower() not in t["user_prompt"].lower()

        pos = t["target_position"]
        target_positions[pos] = target_positions.get(pos, 0) + 1

    # Verify positional uniformity
    for p in range(5):
        assert target_positions.get(p) == 20


def test_abstention_task_structure():
    task_files = sorted(R2_TASKS_DIR.glob("TASK_R2_AB_*.json"))
    assert len(task_files) == 100

    forbidden = ["none of these", "cannot fulfill", "unavailable", "abstain", "no tool matches"]

    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            t = json.load(f)

        assert t["category"] == "ABSTENTION"
        assert t["expected_tool_name"] is None
        assert t["expected_arguments"] is None
        assert t["oracle_config"]["is_abstention"] is True

        for fb in forbidden:
            assert fb not in t["user_prompt"].lower()
