"""Tests for Stage C Task Validator (Track 4).

Validates all 300 compiled task instances for Draft-07 schema compliance,
additionalProperties restrictions, expected tool/arguments validity,
and abstention invariants.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_task_validator import StageCTaskValidator


REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "data_stage_c" / "task_instances"


def test_all_300_tasks_pass_validation():
    validator = StageCTaskValidator()
    task_files = sorted(TASKS_DIR.glob("TASK_SYNTH_*.json"))
    assert len(task_files) == 300

    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            task = json.load(f)

        is_valid, errors = validator.validate_task(task)
        assert is_valid is True, f"Task {tf.name} validation failed: {errors}"
