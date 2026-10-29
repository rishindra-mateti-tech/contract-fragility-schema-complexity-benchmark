"""Tests for Stage C Release 2 Task Validator (Track 2).

Verifies that the validator validates clean Release 2 tasks and detects
deliberate corruptions.
"""

from pathlib import Path
import copy
import json
import pytest

from src.stage_c_release2_task_validator import StageCRelease2TaskValidator, R2_TASKS_DIR


def test_validator_on_clean_release2_suite():
    validator = StageCRelease2TaskValidator()
    ok, errors = validator.validate_all()
    assert ok is True, f"Clean validation failed: {errors}"
    assert len(errors) == 0


def test_validator_catches_corrupted_marker():
    validator = StageCRelease2TaskValidator()
    task_file = R2_TASKS_DIR / "TASK_R2_AC_001.json"

    with open(task_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    try:
        # Deliberately corrupt release marker
        corrupted = copy.deepcopy(original_data)
        corrupted["release_marker"] = "RELEASE_1_CORRUPTED"
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(corrupted, f, indent=2)

        ok, errors = validator.validate_all()
        assert ok is False
        assert any("release marker" in e for e in errors)
    finally:
        # Restore original
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(original_data, f, indent=2, sort_keys=True)


def test_validator_catches_tool_leak():
    validator = StageCRelease2TaskValidator()
    task_file = R2_TASKS_DIR / "TASK_R2_AC_001.json"

    with open(task_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    try:
        # Deliberately inject tool name into prompt
        corrupted = copy.deepcopy(original_data)
        corrupted["user_prompt"] = f"Please run {corrupted['expected_tool_name']} right now."
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(corrupted, f, indent=2)

        ok, errors = validator.validate_all()
        assert ok is False
        assert any("leaks tool name" in e or "prompt_sha256 mismatch" in e for e in errors)
    finally:
        # Restore original
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(original_data, f, indent=2, sort_keys=True)
