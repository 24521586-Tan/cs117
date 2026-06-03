from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase
from app.workers.pipeline import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])
bearer = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    sb = get_supabase()
    try:
        result = sb.auth.get_user(credentials.credentials)
        return result.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def _get_job(job_id: str, user_id: str):
    sb = get_supabase()
    rows = (
        sb.table("jobs")
        .select("*")
        .eq("id", job_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")
    return rows[0]


@router.get("")
async def list_jobs(user=Depends(get_current_user)):
    """All of the user's jobs, newest first — powers the history page."""
    sb = get_supabase()
    rows = (
        sb.table("jobs")
        .select("id,status,progress,notion_url,error,created_at,analysis")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(100)
        .execute()
        .data
    )
    jobs = []
    for r in rows:
        analysis = r.get("analysis")
        title = analysis.get("title") if isinstance(analysis, dict) else None
        jobs.append({
            "job_id": r["id"],
            "status": r["status"],
            "progress": r.get("progress") or 0,
            "notion_url": r.get("notion_url"),
            "error": r.get("error"),
            "created_at": r.get("created_at"),
            "title": title,
        })
    return {"jobs": jobs}


@router.get("/{job_id}/status")
async def get_job_status(job_id: str, user=Depends(get_current_user)):
    job = _get_job(job_id, user.id)
    return {
        "job_id": job["id"],
        "status": job["status"],
        "progress": job.get("progress") or 0,
        "notion_url": job.get("notion_url"),
        "error": job.get("error"),
    }


@router.get("/{job_id}/transcript")
async def get_job_transcript(job_id: str, user=Depends(get_current_user)):
    job = _get_job(job_id, user.id)
    if job["status"] != "done":
        raise HTTPException(status_code=409, detail=f"Job status is '{job['status']}', not done")
    return {"job_id": job["id"], "transcript": job["transcript"]}


@router.get("/{job_id}/result")
async def get_job_result(job_id: str, user=Depends(get_current_user)):
    job = _get_job(job_id, user.id)
    if job["status"] != "done":
        raise HTTPException(status_code=409, detail=f"Job status is '{job['status']}', not done")
    return {
        "job_id": job["id"],
        "notion_url": job.get("notion_url"),
        "analysis": job.get("analysis"),
    }


TERMINAL_STATUSES = {"done", "failed", "cancelled"}


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """Resume a failed/cancelled job from the first stage without a cached
    result. transcript/analysis/notion_url already stored in the row are reused
    automatically by the pipeline."""
    job = _get_job(job_id, user.id)
    if job["status"] not in {"failed", "cancelled"}:
        raise HTTPException(
            status_code=409,
            detail=f"Job status is '{job['status']}', not retryable.",
        )
    sb = get_supabase()
    sb.table("jobs").update({
        "status": "pending",
        "error": None,
    }).eq("id", job_id).execute()
    background_tasks.add_task(
        process_job,
        job_id,
        job.get("file_path"),
        job.get("slide_path"),
    )
    return {"job_id": job_id, "status": "pending"}


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str, user=Depends(get_current_user)):
    """Mark a running job as cancelled. The pipeline polls this flag between
    stages and bails out gracefully (mid-stage work in progress may still finish)."""
    job = _get_job(job_id, user.id)
    if job["status"] in TERMINAL_STATUSES:
        return {"job_id": job["id"], "status": job["status"]}
    sb = get_supabase()
    sb.table("jobs").update({
        "status": "cancelled",
        "error": "Cancelled by user",
    }).eq("id", job_id).execute()
    return {"job_id": job_id, "status": "cancelled"}
