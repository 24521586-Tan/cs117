import io
import os
import re
import unicodedata
import uuid

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File as FileParam
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mutagen import File as MutagenFile
from pypdf import PdfReader

from app.core.supabase import get_supabase
from app.workers.pipeline import process_job

router = APIRouter(prefix="/upload", tags=["upload"])
bearer = HTTPBearer()

# Matches evaluation/case_discovery.py so prod and eval accept the same inputs.
ALLOWED_AUDIO_EXTS = {".mp3", ".mp4", ".m4a", ".wav"}
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a",
    "audio/wav", "audio/x-wav", "audio/wave",
    "video/mp4",  # .mp4 audio-only — browsers often send this content-type
}
ALLOWED_SLIDE_EXTS = {".pdf", ".txt", ".md", ".json"}
ALLOWED_SLIDE_TYPES = {
    "application/pdf",
    "text/plain", "text/markdown", "text/x-markdown",
    "application/json", "application/octet-stream",  # some browsers send octet-stream for .md/.json
}
_BUCKET = "audio-files"
MAX_AUDIO_MINUTES = 60
MAX_SLIDE_PAGES = 60
MAX_SLIDE_CHARS = 200_000


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
        raise HTTPException(status_code=422, detail="Cần ít nhất 1 file (audio hoặc slide).")

    if file:
        audio_ext = os.path.splitext(file.filename or "")[1].lower()
        if audio_ext not in ALLOWED_AUDIO_EXTS and (file.content_type or "") not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=422,
                detail="File âm thanh không hợp lệ. Chỉ hỗ trợ .mp3, .mp4, .m4a hoặc .wav.",
            )

    if slides:
        slide_ext = os.path.splitext(slides.filename or "")[1].lower()
        if slide_ext not in ALLOWED_SLIDE_EXTS and (slides.content_type or "") not in ALLOWED_SLIDE_TYPES:
            raise HTTPException(
                status_code=422,
                detail="File slide không hợp lệ. Chỉ hỗ trợ .pdf, .txt, .md hoặc .json.",
            )

    sb = get_supabase()

    # Ensure profile row exists (foreign key required before inserting job)
    sb.table("profiles").upsert({"id": user.id, "email": user.email}, on_conflict="id").execute()

    # Read file bytes upfront so we can validate before storing
    audio_bytes = await file.read() if file else None
    slide_bytes = await slides.read() if slides else None

    # ── Collect ALL validation errors so the user sees every issue at once ──
    errors: list[str] = []

    # Validate audio duration
    if audio_bytes:
        try:
            audio_info = MutagenFile(io.BytesIO(audio_bytes))
            if audio_info and audio_info.info and audio_info.info.length:
                duration_min = audio_info.info.length / 60
                if duration_min > MAX_AUDIO_MINUTES:
                    errors.append(
                        f"File âm thanh dài {int(duration_min)} phút, vượt quá giới hạn {MAX_AUDIO_MINUTES} phút."
                    )
        except Exception:
            pass  # Cannot read duration — accept file, pipeline will process it

    # Validate slide size
    if slide_bytes and slides:
        slide_ext = os.path.splitext(slides.filename or "")[1].lower()
        if slide_ext == ".pdf":
            try:
                reader = PdfReader(io.BytesIO(slide_bytes))
                page_count = len(reader.pages)
                if page_count > MAX_SLIDE_PAGES:
                    errors.append(
                        f"File PDF có {page_count} trang, vượt quá giới hạn {MAX_SLIDE_PAGES} trang."
                    )
            except Exception:
                pass  # Cannot read pages — accept file, pipeline will re-check
        else:
            if len(slide_bytes) > MAX_SLIDE_CHARS * 4:  # generous byte->char headroom
                errors.append(
                    f"File slide vượt quá giới hạn {MAX_SLIDE_CHARS} ký tự."
                )

    # Return all errors at once
    if errors:
        raise HTTPException(status_code=422, detail="\n".join(errors))

    # ── Store files to Supabase Storage ──
    try:
        audio_path = _store(sb, user.id, file, audio_bytes) if file and audio_bytes else None
    except Exception as exc:
        if "413" in str(exc) or "too large" in str(exc).lower() or "maximum allowed size" in str(exc).lower():
            raise HTTPException(
                status_code=422,
                detail="File âm thanh quá lớn, vượt quá dung lượng tối đa cho phép của hệ thống.",
            )
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file âm thanh: {str(exc)[:200]}")

    try:
        slide_path = _store(sb, user.id, slides, slide_bytes) if slides and slide_bytes else None
    except Exception as exc:
        if "413" in str(exc) or "too large" in str(exc).lower() or "maximum allowed size" in str(exc).lower():
            raise HTTPException(
                status_code=422,
                detail="File PDF quá lớn, vượt quá dung lượng tối đa cho phép của hệ thống.",
            )
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file PDF: {str(exc)[:200]}")

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
