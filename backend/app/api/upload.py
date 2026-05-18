import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase
from app.workers.transcribe import transcribe_audio

router = APIRouter(prefix="/upload", tags=["upload"])
bearer = HTTPBearer()

ALLOWED_TYPES = {"audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a"}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """Validate Bearer token and return user id."""
    sb = get_supabase()
    try:
        result = sb.auth.get_user(credentials.credentials)
        return result.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("")
async def upload_audio(
    file: UploadFile,
    user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Only .mp3 / .m4a files are accepted")

    sb = get_supabase()
    file_bytes = await file.read()
    storage_path = f"{user.id}/{uuid.uuid4()}-{file.filename}"

    # Upload to Supabase Storage bucket "audio-files"
    sb.storage.from_("audio-files").upload(
        storage_path,
        file_bytes,
        file_options={"content-type": file.content_type},
    )

    # Insert job row
    job = (
        sb.table("jobs")
        .insert(
            {
                "user_id": user.id,
                "status": "pending",
                "file_path": storage_path,
            }
        )
        .execute()
        .data[0]
    )

    job_id = job["id"]

    # Enqueue Celery task
    transcribe_audio.delay(job_id, storage_path)

    return {"job_id": job_id}
