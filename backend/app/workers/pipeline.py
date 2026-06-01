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
from app.workers.slides import MAX_PAGES, extract_slides, pages_as_prompt
from app.workers.transcribe import transcribe

_BUCKET = "audio-files"


def process_job(job_id: str, audio_path: Optional[str], slide_path: Optional[str]) -> None:
    sb = new_supabase()

    def upd(**fields):
        sb.table("jobs").update(fields).eq("id", job_id).execute()

    # Write progress at most every 5% to keep DB chatter (and connection load) low.
    last_written = -5

    def on_progress(p: int) -> None:
        nonlocal last_written
        if p >= last_written + 5 or p >= 99:
            last_written = p
            upd(progress=p)

    try:
        # ── Step 1: Transcribe audio (skip if no audio uploaded) ──
        if audio_path:
            upd(status="transcribing", progress=0)
            transcript = transcribe(audio_path, on_progress=on_progress)
            upd(transcript=transcript, progress=100)
        else:
            transcript = {"segments": [], "language": "en"}
            upd(transcript=transcript, progress=100)

        # ── Step 2: Extract slide text (skip if no PDF uploaded) ──
        slides_prompt = ""
        if slide_path:
            pdf_bytes = sb.storage.from_(_BUCKET).download(slide_path)
            slides = extract_slides(pdf_bytes)
            if slides["page_count"] > MAX_PAGES:
                raise ValueError(f"Slide PDF has {slides['page_count']} pages (max {MAX_PAGES}).")
            upd(slide_text=slides["markdown"])
            slides_prompt = pages_as_prompt(slides["pages"])

        # ── Step 3: Analyze with LLM ──
        upd(status="analyzing")
        analysis = analyze_meeting(transcript, slides_prompt)
        upd(analysis=analysis, status="syncing")

        # ── Step 4: Sync to Notion ──
        notion_url = create_meeting_page(analysis)
        upd(notion_url=notion_url, status="done")

        # Privacy: remove uploaded source files once the Notion page exists.
        try:
            paths_to_remove = [p for p in (audio_path, slide_path) if p]
            if paths_to_remove:
                sb.storage.from_(_BUCKET).remove(paths_to_remove)
        except Exception:
            pass

    except Exception as exc:
        upd(status="failed", error=str(exc)[:500])
