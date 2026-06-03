"""End-to-end job orchestrator.

Chains transcribe -> extract slides -> analyze -> Notion, updating job status at
each step. On success deletes the uploaded audio + PDF (privacy). On any failure
records status='failed' with the reason.

Both audio and slides are optional (at least one is required by the upload
endpoint). The pipeline gracefully skips whichever step has no input.
"""

from typing import Optional

from app.core.supabase import new_supabase
from app.workers.analyze import analyze_meeting
from app.workers.notion_sync import create_meeting_page
import os

from app.workers.slides import MAX_PAGES, extract_slides_any, pages_as_prompt
from app.workers.transcribe import transcribe

_BUCKET = "audio-files"


def process_job(job_id: str, audio_path: Optional[str], slide_path: Optional[str]) -> None:
    sb = new_supabase()

    def upd(**fields):
        sb.table("jobs").update(fields).eq("id", job_id).execute()

    # Load any cached outputs from a prior (failed) run — lets retry resume at
    # the first stage that hasn't produced a result yet.
    cached = (
        sb.table("jobs")
        .select("transcript, analysis, notion_url")
        .eq("id", job_id)
        .execute()
        .data
    )
    cached_row = cached[0] if cached else {}
    cached_transcript = cached_row.get("transcript")
    cached_analysis = cached_row.get("analysis")
    cached_notion = cached_row.get("notion_url")

    def is_cancelled() -> bool:
        row = sb.table("jobs").select("status").eq("id", job_id).execute().data
        return bool(row) and row[0].get("status") == "cancelled"

    class _Cancelled(Exception):
        pass

    def check_cancelled() -> None:
        if is_cancelled():
            raise _Cancelled()

    # Write progress at most every 5% to keep DB chatter (and connection load) low.
    last_written = -5

    def on_progress(p: int) -> None:
        nonlocal last_written
        if p >= last_written + 5 or p >= 99:
            last_written = p
            upd(progress=p)

    try:
        check_cancelled()

        # ── Step 1: Transcribe audio (skip if cached or no audio uploaded) ──
        if cached_transcript:
            transcript = cached_transcript
            upd(progress=100)
        elif audio_path:
            upd(status="transcribing", progress=0)
            transcript = transcribe(audio_path, on_progress=on_progress)
            upd(transcript=transcript, progress=100)
        else:
            transcript = {"segments": [], "language": "en"}
            upd(transcript=transcript, progress=100)

        check_cancelled()

        # ── Step 2: Extract slide text (always re-run when a slide is present —
        # fast, and we need the page-numbered prompt format that isn't cached). ──
        slides_prompt = ""
        if slide_path and not cached_analysis:
            slide_bytes = sb.storage.from_(_BUCKET).download(slide_path)
            slide_ext = os.path.splitext(slide_path)[1].lower()
            slides = extract_slides_any(slide_bytes, slide_ext)
            if slides["page_count"] > MAX_PAGES:
                raise ValueError(f"Slide có {slides['page_count']} trang, vượt quá giới hạn {MAX_PAGES} trang.")
            upd(slide_text=slides["markdown"])
            slides_prompt = pages_as_prompt(slides["pages"])

        check_cancelled()

        # ── Step 3: Analyze with LLM (skip if cached) ──
        if cached_analysis:
            analysis = cached_analysis
            upd(status="syncing")
        else:
            upd(status="analyzing")
            analysis = analyze_meeting(transcript, slides_prompt)
            upd(analysis=analysis, status="syncing")

        check_cancelled()

        # ── Step 4: Sync to Notion (skip if cached) ──
        if cached_notion:
            notion_url = cached_notion
        else:
            notion_url = create_meeting_page(analysis)
        upd(notion_url=notion_url, status="done")

        # Privacy: remove uploaded source files once the Notion page exists.
        try:
            paths_to_remove = [p for p in (audio_path, slide_path) if p]
            if paths_to_remove:
                sb.storage.from_(_BUCKET).remove(paths_to_remove)
        except Exception:
            pass

    except _Cancelled:
        # User-initiated cancel — clean up uploaded files but leave status as 'cancelled'.
        try:
            paths_to_remove = [p for p in (audio_path, slide_path) if p]
            if paths_to_remove:
                sb.storage.from_(_BUCKET).remove(paths_to_remove)
        except Exception:
            pass

    except Exception as exc:
        upd(status="failed", error=str(exc)[:500])
