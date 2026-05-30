import re
import unicodedata
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase
from app.workers.pipeline import process_job

router = APIRouter(prefix="/upload", tags=["upload"])
bearer = HTTPBearer()

ALLOWED_AUDIO = {"audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a",
                 "audio/wav", "audio/x-wav", "audio/wave"}
ALLOWED_PDF = {"application/pdf"}
_BUCKET = "audio-files"


def safe_filename(name: str) -> str:
    """Normalize unicode → ASCII, replace unsafe chars with hyphens."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^\w.\-]", "-", name)
    return name.strip("-") or "file"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """Validate Bearer token and return user."""
    sb = get_supabase()
    try:
        result = sb.auth.get_user(credentials.credentials)
        return result.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def _store(sb, user_id: str, upload: UploadFile, raw: bytes) -> str:
    path = f"{user_id}/{uuid.uuid4()}-{safe_filename(upload.filename or 'file')}"
    sb.storage.from_(_BUCKET).upload(
        path, raw, file_options={"content-type": upload.content_type or "application/octet-stream"}
    )
    return path


@router.post("")
async def upload_meeting(
    file: UploadFile,
    slides: UploadFile,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_AUDIO:
        raise HTTPException(status_code=422, detail="Audio must be .mp3 / .m4a / .wav")
    if slides.content_type not in ALLOWED_PDF:
        raise HTTPException(status_code=422, detail="Slides must be a .pdf file")

    sb = get_supabase()

    # Ensure profile row exists (foreign key required before inserting job)
    sb.table("profiles").upsert({"id": user.id, "email": user.email}, on_conflict="id").execute()

    audio_path = _store(sb, user.id, file, await file.read())
    slide_path = _store(sb, user.id, slides, await slides.read())

    job = (
        sb.table("jobs")
        .insert({
            "user_id": user.id,
            "status": "pending",
            "file_path": audio_path,
            "slide_path": slide_path,
        })
        .execute()
        .data[0]
    )

    job_id = job["id"]
    background_tasks.add_task(process_job, job_id, audio_path, slide_path)

    return {"job_id": job_id}
