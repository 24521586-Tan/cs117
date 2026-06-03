import os
import re
import unicodedata

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.supabase import get_supabase
from app.workers.pipeline import process_job

router = APIRouter(prefix="/upload", tags=["upload"])
bearer = HTTPBearer()

# Matches evaluation/case_discovery.py so prod and eval accept the same inputs.
ALLOWED_AUDIO_EXTS = {".mp3", ".mp4", ".m4a", ".wav"}
ALLOWED_SLIDE_EXTS = {".pdf", ".txt", ".md", ".json"}
_BUCKET = "audio-files"

# Hard caps enforced before issuing a signed upload URL. Storage bucket file-size
# limit on Supabase should be >= MAX_AUDIO_BYTES for these to actually let
# uploads through; we pre-check to fail fast with a friendly message.
MAX_AUDIO_BYTES = 100 * 1024 * 1024   # 100 MB — fits 60-min MP3 @ 192kbps
MAX_SLIDE_BYTES = 30 * 1024 * 1024    # 30 MB — generous for PDFs


def safe_filename(name: str) -> str:
    """Normalize unicode → ASCII, replace unsafe chars with hyphens."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^\w.\-]", "-", name)
    return name.strip("-") or "file"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    sb = get_supabase()
    try:
        return sb.auth.get_user(credentials.credentials).user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── New direct-upload flow ──────────────────────────────────────────────────
# 1. FE POST /upload/init with file metadata → BE creates job row + signed
#    upload URLs for audio and/or slide.
# 2. FE uploads bytes directly to Supabase Storage via the signed URLs
#    (bypasses Railway memory/body limits entirely).
# 3. FE POST /upload/complete with the job_id → BE updates job paths and
#    schedules process_job.

class UploadInitRequest(BaseModel):
    audio_filename: Optional[str] = None
    audio_size: Optional[int] = None
    slide_filename: Optional[str] = None
    slide_size: Optional[int] = None


class UploadCompleteRequest(BaseModel):
    job_id: str


def _validate_audio(filename: Optional[str], size: Optional[int]) -> None:
    if not filename:
        return
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTS:
        raise HTTPException(
            status_code=422,
            detail="File âm thanh không hợp lệ. Chỉ hỗ trợ .mp3, .mp4, .m4a hoặc .wav.",
        )
    if size is not None and size > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"File âm thanh quá lớn ({size // (1024*1024)} MB). Giới hạn {MAX_AUDIO_BYTES // (1024*1024)} MB.",
        )


def _validate_slide(filename: Optional[str], size: Optional[int]) -> None:
    if not filename:
        return
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_SLIDE_EXTS:
        raise HTTPException(
            status_code=422,
            detail="File slide không hợp lệ. Chỉ hỗ trợ .pdf, .txt, .md hoặc .json.",
        )
    if size is not None and size > MAX_SLIDE_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"File slide quá lớn ({size // (1024*1024)} MB). Giới hạn {MAX_SLIDE_BYTES // (1024*1024)} MB.",
        )


@router.post("/init")
async def upload_init(payload: UploadInitRequest, user=Depends(get_current_user)):
    if not payload.audio_filename and not payload.slide_filename:
        raise HTTPException(status_code=422, detail="Cần ít nhất 1 file (audio hoặc slide).")

    _validate_audio(payload.audio_filename, payload.audio_size)
    _validate_slide(payload.slide_filename, payload.slide_size)

    sb = get_supabase()
    sb.table("profiles").upsert({"id": user.id, "email": user.email}, on_conflict="id").execute()

    # Create job row up-front so we have a stable id to namespace storage paths.
    job = sb.table("jobs").insert({"user_id": user.id, "status": "pending"}).execute().data[0]
    job_id = job["id"]

    result: dict = {"job_id": job_id, "audio": None, "slide": None}

    if payload.audio_filename:
        ext = os.path.splitext(payload.audio_filename)[1].lower()
        path = f"{user.id}/{job_id}-audio{ext}"
        signed = sb.storage.from_(_BUCKET).create_signed_upload_url(path)
        result["audio"] = {"path": path, "token": signed["token"]}

    if payload.slide_filename:
        ext = os.path.splitext(payload.slide_filename)[1].lower()
        path = f"{user.id}/{job_id}-slide{ext}"
        signed = sb.storage.from_(_BUCKET).create_signed_upload_url(path)
        result["slide"] = {"path": path, "token": signed["token"]}

    return result


@router.post("/complete")
async def upload_complete(
    payload: UploadCompleteRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    sb = get_supabase()

    rows = (
        sb.table("jobs")
        .select("*")
        .eq("id", payload.job_id)
        .eq("user_id", user.id)
        .execute()
        .data
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")
    job = rows[0]
    if job["status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Job already in status '{job['status']}'.")

    # Look up storage paths created at init time (namespace = "{user_id}/{job_id}-*").
    audio_path: Optional[str] = None
    slide_path: Optional[str] = None
    try:
        listing = sb.storage.from_(_BUCKET).list(user.id, {"limit": 1000, "search": payload.job_id})
        for entry in listing or []:
            name = entry.get("name", "")
            if not name.startswith(f"{payload.job_id}-"):
                continue
            full = f"{user.id}/{name}"
            if "-audio" in name:
                audio_path = full
            elif "-slide" in name:
                slide_path = full
    except Exception:
        pass

    if not audio_path and not slide_path:
        raise HTTPException(
            status_code=422,
            detail="Không tìm thấy file đã upload. Vui lòng thử lại.",
        )

    update: dict = {}
    if audio_path:
        update["file_path"] = audio_path
    if slide_path:
        update["slide_path"] = slide_path
    sb.table("jobs").update(update).eq("id", payload.job_id).execute()

    background_tasks.add_task(process_job, payload.job_id, audio_path, slide_path)
    return {"job_id": payload.job_id}
