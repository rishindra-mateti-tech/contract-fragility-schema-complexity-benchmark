"""Stage C Offline Local Human-Review Application.

Runs locally on localhost (127.0.0.1:8000) with zero external telemetry,
API keys, or cloud databases. Serves blinded task packages to human evaluators.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import copy
from datetime import datetime, timezone
import json
import os
import sys

from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.validate_stage_c_human_review_submission import StageCHumanReviewSubmissionValidator

R1_PACKAGES_DIR = ROOT_DIR / "data_stage_c" / "reviewer_packages"
R2_PACKAGES_DIR = ROOT_DIR / "data_stage_c_release2" / "reviewer_packages"
SESSIONS_DIR = APP_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Stage C Offline Reviewer Portal")

# Static and Templates
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


def get_packages_dir(release: str = "release2") -> Path:
    """Returns packages directory based on selected benchmark release."""
    if release and "1" in release.lower():
        return R1_PACKAGES_DIR
    return R2_PACKAGES_DIR


def load_blind_manifest(release: str = "release2") -> Dict[str, Any]:
    packages_dir = get_packages_dir(release)
    manifest_file = packages_dir / "blind_sample_manifest.json"
    if not manifest_file.is_file():
        raise RuntimeError(f"Blinded review package missing for {release}. Run package builder first.")
    with open(manifest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_session_file(pseudonym: str) -> Path:
    safe_name = "".join(c for c in pseudonym if c.isalnum() or c in "_-")
    return SESSIONS_DIR / f"{safe_name}.json"


def load_session(pseudonym: str, release: str = "release2") -> Dict[str, Any]:
    fpath = get_session_file(pseudonym)
    if fpath.is_file():
        with open(fpath, "r", encoding="utf-8") as f:
            sess = json.load(f)
            if "release" not in sess:
                sess["release"] = release
            return sess
    return {
        "pseudonym": pseudonym,
        "release": release,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "responses": {}
    }


def save_session(session_data: Dict[str, Any]) -> None:
    fpath = get_session_file(session_data["pseudonym"])
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, sort_keys=True)


@app.get("/", response_class=HTMLResponse)
async def index_view(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login")
async def login_view(pseudonym: str = Form(...), release: Optional[str] = Form(None)):
    clean_p = pseudonym.strip()
    if not clean_p:
        raise HTTPException(status_code=400, detail="Pseudonym cannot be empty.")
    sess = load_session(clean_p)
    if release:
        clean_rel = "release1" if "1" in release.lower() else "release2"
        sess["release"] = clean_rel
    else:
        clean_rel = sess.get("release", "release1" if "42" in clean_p else "release2")
        sess["release"] = clean_rel
    save_session(sess)
    response = RedirectResponse(url="/tasks", status_code=303)
    response.set_cookie(key="reviewer_pseudonym", value=clean_p)
    response.set_cookie(key="review_release", value=clean_rel)
    return response


@app.get("/tasks", response_class=HTMLResponse)
async def tasks_list_view(request: Request):
    pseudonym = request.cookies.get("reviewer_pseudonym")
    if not pseudonym:
        return RedirectResponse(url="/", status_code=303)

    session_data = load_session(pseudonym)
    cookie_rel = request.cookies.get("review_release")
    release = cookie_rel if cookie_rel else session_data.get("release", "release2")

    manifest_data = load_blind_manifest(release)
    all_tasks = manifest_data.get("tasks", [])
    completed_keys = set(session_data.get("responses", {}).keys())

    task_rows = []
    for t in all_tasks:
        btid = t["blind_task_id"]
        task_rows.append({
            "blind_task_id": btid,
            "packet_type": t.get("packet_type"),
            "is_completed": btid in completed_keys
        })

    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "pseudonym": pseudonym,
        "tasks": task_rows,
        "total_count": len(all_tasks),
        "completed_count": len(completed_keys),
        "selected_release": release
    })


@app.get("/task/{task_id}", response_class=HTMLResponse)
async def task_detail_view(task_id: str, request: Request):
    pseudonym = request.cookies.get("reviewer_pseudonym")
    if not pseudonym:
        return RedirectResponse(url="/", status_code=303)

    release = "release2" if "R2" in task_id else "release1"
    manifest_data = load_blind_manifest(release)
    task = next((t for t in manifest_data.get("tasks", []) if t["blind_task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in blind manifest.")

    # Format schemas for human readable display
    task_view = copy.deepcopy(task)
    for tool in task_view.get("candidate_tools", []):
        tool["schema_formatted"] = json.dumps(tool.get("schema", {}), indent=2)

    session_data = load_session(pseudonym)
    current_resp = session_data.get("responses", {}).get(task_id, {})
    current_args = current_resp.get("submitted_arguments", {})
    current_resp["arguments_json"] = json.dumps(current_args, indent=2) if current_args else ""

    return templates.TemplateResponse("task.html", {
        "request": request,
        "task": task_view,
        "current_response": current_resp
    })


@app.post("/task/{task_id}/submit")
async def task_submit_view(
    task_id: str,
    request: Request,
    selected_tool_name: Optional[str] = Form(None),
    submitted_arguments: Optional[str] = Form(None),
    abstain_from_invocation: bool = Form(False),
    confidence_score: int = Form(5),
    is_ambiguous: bool = Form(False),
    reviewer_notes: str = Form("")
):
    pseudonym = request.cookies.get("reviewer_pseudonym")
    if not pseudonym:
        return RedirectResponse(url="/", status_code=303)

    parsed_args = {}
    if not abstain_from_invocation and submitted_arguments and submitted_arguments.strip():
        try:
            parsed_args = json.loads(submitted_arguments.strip())
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Arguments must be valid JSON: {str(exc)}")

    response_record = {
        "blind_task_id": task_id,
        "selected_tool_name": None if abstain_from_invocation else (selected_tool_name or None),
        "submitted_arguments": parsed_args if not abstain_from_invocation else None,
        "abstain_from_invocation": abstain_from_invocation,
        "confidence_score": confidence_score,
        "is_ambiguous": is_ambiguous,
        "reviewer_notes": reviewer_notes.strip(),
        "item_timestamp": datetime.now(timezone.utc).isoformat()
    }

    session_data = load_session(pseudonym)
    session_data.setdefault("responses", {})[task_id] = response_record
    save_session(session_data)

    return RedirectResponse(url="/tasks", status_code=303)


@app.get("/summary", response_class=HTMLResponse)
async def summary_view(request: Request):
    pseudonym = request.cookies.get("reviewer_pseudonym")
    release = request.cookies.get("review_release", "release2")
    if not pseudonym:
        return RedirectResponse(url="/", status_code=303)

    manifest_data = load_blind_manifest(release)
    total_count = len(manifest_data.get("tasks", []))
    session_data = load_session(pseudonym, release=release)
    completed_count = len(session_data.get("responses", {}))

    return templates.TemplateResponse("summary.html", {
        "request": request,
        "pseudonym": pseudonym,
        "total_count": total_count,
        "completed_count": completed_count,
        "selected_release": release
    })


@app.get("/export")
async def export_submission_view(request: Request):
    pseudonym = request.cookies.get("reviewer_pseudonym")
    release = request.cookies.get("review_release", "release2")
    if not pseudonym:
        return RedirectResponse(url="/", status_code=303)

    session_data = load_session(pseudonym, release=release)
    responses_dict = session_data.get("responses", {})
    reviews = sorted(list(responses_dict.values()), key=lambda x: x["blind_task_id"])

    submission_bundle = {
        "submission_version": "1.0.0",
        "benchmark_release": release,
        "reviewer_pseudonym": pseudonym,
        "submission_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_items_reviewed": len(reviews),
        "reviews": reviews,
        "integrity_hash": StageCHumanReviewSubmissionValidator.compute_submission_hash(reviews)
    }

    # Validate bundle locally before download
    is_valid, errors = StageCHumanReviewSubmissionValidator.validate_submission_bundle(submission_bundle)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Submission validation error: {errors}")

    filename = f"stage_c_review_submission_{pseudonym}_{int(datetime.now().timestamp())}.json"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return JSONResponse(content=submission_bundle, headers=headers)


@app.post("/reconcile")
async def reconcile_author_view(submissions: List[Dict[str, Any]], release: str = "release2"):
    """Author-side local reconciliation mode."""
    if len(submissions) < 2:
        return {
            "status": "NO_HUMAN_REVIEW_RESULTS_PRESENT",
            "reason": "At least two independent reviewer submissions required to compute inter-rater metrics.",
            "submissions_provided": len(submissions)
        }

    key_path = get_packages_dir(release) / "author_reconciliation_map.json"
    if not key_path.is_file():
        raise HTTPException(status_code=500, detail="Author reconciliation key missing.")

    with open(key_path, "r", encoding="utf-8") as f:
        author_key = json.load(f)

    reconciled_all = []
    for sub in submissions:
        is_valid, errors = StageCHumanReviewSubmissionValidator.validate_submission_bundle(sub)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Submission bundle failed validation: {errors}")
        rec = StageCHumanReviewSubmissionValidator.reconcile_with_author_key(sub, author_key)
        reconciled_all.append(rec)

    return {
        "status": "RECONCILED",
        "total_submissions_reconciled": len(reconciled_all),
        "reconciled_data": reconciled_all
    }


def run_app():
    import uvicorn
    uvicorn.run("review_app.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run_app()
