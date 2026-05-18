import re
import unicodedata
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase
from app.workers.transcribe import transcribe_audio

router = APIRouter(prefix="/upload", tags=["upload"])
bearer = HTTPBearer()

ALLOWED_TYPES = {"audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a"}


def safe_filename(name: str) -> str:
    """Normalize unicode → ASCII, replace unsafe chars with hyphens."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^\w.\-]", "-", name)
    return name.strip("-") or "audio"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """Validate Bearer token and return user."""
    sb = get_supabase()
    try:
        result = sb.auth.get_user(credentials.credentials)
        return result.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("")
async def upload_audio(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Only .mp3 / .m4a files are accepted")

    sb = get_supabase()

    # Ensure profile row exists (foreign key required before inserting job)
    sb.table("profiles").upsert(
        {"id": user.id, "email": user.email},
        on_conflict="id",
    ).execute()

    file_bytes = await file.read()
    storage_path = f"{user.id}/{uuid.uuid4()}-{safe_filename(file.filename or 'audio')}"

    sb.storage.from_("audio-files").upload(
        storage_path,
        file_bytes,
        file_options={"content-type": file.content_type},
    )

    job = (
        sb.table("jobs")
        .insert({"user_id": user.id, "status": "pending", "file_path": storage_path})
        .execute()
        .data[0]
    )

    job_id = job["id"]
    background_tasks.add_task(transcribe_audio, job_id, storage_path)

    return {"job_id": job_id}
