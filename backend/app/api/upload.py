import io
import re
import unicodedata
import uuid

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File as FileParam
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mutagen import File as MutagenFile

from app.core.supabase import get_supabase
from app.workers.pipeline import process_job

router = APIRouter(prefix="/upload", tags=["upload"])
bearer = HTTPBearer()

ALLOWED_AUDIO = {"audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a",
                 "audio/wav", "audio/x-wav", "audio/wave"}
ALLOWED_PDF = {"application/pdf"}
_BUCKET = "audio-files"
MAX_AUDIO_MINUTES = 60


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
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
    file: Optional[UploadFile] = FileParam(None),
    slides: Optional[UploadFile] = FileParam(None),
):
    if not file and not slides:
        raise HTTPException(status_code=422, detail="Cần ít nhất 1 file (audio hoặc PDF).")
    if file and file.content_type not in ALLOWED_AUDIO:
        raise HTTPException(status_code=422, detail="Audio must be .mp3 / .m4a / .wav")
    if slides and slides.content_type not in ALLOWED_PDF:
        raise HTTPException(status_code=422, detail="Slides must be a .pdf file")

    sb = get_supabase()

    # Ensure profile row exists (foreign key required before inserting job)
    sb.table("profiles").upsert({"id": user.id, "email": user.email}, on_conflict="id").execute()

    # Read file bytes upfront so we can validate duration + store
    audio_bytes = await file.read() if file else None
    slide_bytes = await slides.read() if slides else None

    # Validate audio duration
    if audio_bytes:
        try:
            audio_info = MutagenFile(io.BytesIO(audio_bytes))
            if audio_info and audio_info.info and audio_info.info.length:
                duration_min = audio_info.info.length / 60
                if duration_min > MAX_AUDIO_MINUTES:
                    raise HTTPException(
                        status_code=422,
                        detail=f"File âm thanh dài {int(duration_min)} phút, vượt quá giới hạn {MAX_AUDIO_MINUTES} phút.",
                    )
        except HTTPException:
            raise
        except Exception:
            pass  # Cannot read duration — accept file, pipeline will process it

    audio_path = _store(sb, user.id, file, audio_bytes) if file and audio_bytes else None
    slide_path = _store(sb, user.id, slides, slide_bytes) if slides and slide_bytes else None

    job_data: dict = {
        "user_id": user.id,
        "status": "pending",
    }
    if audio_path:
        job_data["file_path"] = audio_path
    if slide_path:
        job_data["slide_path"] = slide_path

    job = (
        sb.table("jobs")
        .insert(job_data)
        .execute()
        .data[0]
    )

    job_id = job["id"]
    background_tasks.add_task(process_job, job_id, audio_path, slide_path)

    return {"job_id": job_id}
