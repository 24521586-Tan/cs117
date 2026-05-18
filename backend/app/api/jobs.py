from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase

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


@router.get("/{job_id}/status")
async def get_job_status(job_id: str, user=Depends(get_current_user)):
    job = _get_job(job_id, user.id)
    return {"job_id": job["id"], "status": job["status"]}


@router.get("/{job_id}/transcript")
async def get_job_transcript(job_id: str, user=Depends(get_current_user)):
    job = _get_job(job_id, user.id)
    if job["status"] != "done":
        raise HTTPException(status_code=409, detail=f"Job status is '{job['status']}', not done")
    return {"job_id": job["id"], "transcript": job["transcript"]}
