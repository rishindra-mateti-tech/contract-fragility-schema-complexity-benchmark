"""Tests for Stage C Offline Local Review Application (Track 5).

Verifies local endpoints, session management, blinding enforcement (no gold leaks in HTML),
response submission, export, and author reconciliation mode.
"""

from pathlib import Path
import json
import pytest
from starlette.testclient import TestClient

from review_app.app import app


@pytest.fixture(autouse=True)
def preserve_test_reviewer_session():
    session_file = Path(__file__).resolve().parent.parent / "review_app" / "sessions" / "test_reviewer_42.json"
    original_bytes = session_file.read_bytes() if session_file.exists() else None
    yield
    if original_bytes is not None:
        session_file.write_bytes(original_bytes)
    elif session_file.exists():
        session_file.unlink()


@pytest.fixture
def client():
    return TestClient(app)


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Stage C Benchmark Local Review Portal" in response.text
    assert "Reviewer Pseudonym" in response.text


def test_login_and_redirect(client):
    response = client.post("/login", data={"pseudonym": "test_reviewer_42"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"
    assert "reviewer_pseudonym=test_reviewer_42" in response.headers.get("set-cookie", "")


def test_tasks_view_requires_pseudonym(client):
    # Without cookie
    response = client.get("/tasks", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_tasks_view_with_session(client):
    client.cookies.set("reviewer_pseudonym", "test_reviewer_42")
    response = client.get("/tasks")
    assert response.status_code == 200
    assert "Blinded Task Assignment Queue" in response.text
    assert "BLIND_TASK_001" in response.text


def test_task_detail_strictly_blinded(client):
    client.cookies.set("reviewer_pseudonym", "test_reviewer_42")
    response = client.get("/task/BLIND_TASK_001")
    assert response.status_code == 200
    html = response.text

    # Verify blinding invariants: NO gold labels or internal mutation labels in HTML
    assert "expected_tool_name" not in html
    assert "expected_arguments" not in html
    assert "TASK_SYNTH_" not in html
    assert "BASE_SYNTH_" not in html


def test_task_submission_and_export(client):
    client.cookies.set("reviewer_pseudonym", "test_reviewer_42")

    # Submit task
    sub_data = {
        "selected_tool_name": "set_cache_entry",
        "submitted_arguments": '{"key": "test_key", "value": "test_val"}',
        "abstain_from_invocation": False,
        "confidence_score": 5,
        "is_ambiguous": False,
        "reviewer_notes": "Looks clear"
    }
    submit_resp = client.post("/task/BLIND_TASK_001/submit", data=sub_data, follow_redirects=False)
    assert submit_resp.status_code == 303

    # Export bundle
    export_resp = client.get("/export")
    assert export_resp.status_code == 200
    bundle = export_resp.json()

    assert bundle["reviewer_pseudonym"] == "test_reviewer_42"
    assert bundle["total_items_reviewed"] >= 1
    assert "integrity_hash" in bundle


def test_reconcile_endpoint_requires_two_submissions(client):
    # Only 1 submission provided
    single_sub = [{
        "submission_version": "1.0.0",
        "reviewer_pseudonym": "rev_single",
        "submission_timestamp": "2026-10-27T00:00:00Z",
        "total_items_reviewed": 1,
        "reviews": [{"blind_task_id": "BLIND_TASK_001", "selected_tool_name": "t1", "submitted_arguments": {}, "abstain_from_invocation": False, "confidence_score": 5, "is_ambiguous": False, "reviewer_notes": "", "item_timestamp": ""}],
        "integrity_hash": ""
    }]
    # compute valid hash
    from src.validate_stage_c_human_review_submission import StageCHumanReviewSubmissionValidator
    single_sub[0]["integrity_hash"] = StageCHumanReviewSubmissionValidator.compute_submission_hash(single_sub[0]["reviews"])

    rec_resp = client.post("/reconcile", json=single_sub)
    assert rec_resp.status_code == 200
    data = rec_resp.json()
    assert data["status"] == "NO_HUMAN_REVIEW_RESULTS_PRESENT"
