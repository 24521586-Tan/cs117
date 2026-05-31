"""End-to-end job orchestrator.

Chains transcribe -> extract slides -> analyze -> Notion, updating job status at
each step. On success deletes the uploaded audio + PDF (privacy). On any failure
records status='failed' with the reason.
"""

from app.core.supabase import new_supabase
from app.workers.analyze import analyze_meeting
from app.workers.notion_sync import create_meeting_page
from app.workers.slides import MAX_PAGES, extract_slides, pages_as_prompt
from app.workers.transcribe import transcribe

_BUCKET = "audio-files"


def process_job(job_id: str, audio_path: str, slide_path: str) -> None:
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
        upd(status="transcribing", progress=0)
        transcript = transcribe(audio_path, on_progress=on_progress)
        upd(transcript=transcript, progress=100)

        pdf_bytes = sb.storage.from_(_BUCKET).download(slide_path)
        slides = extract_slides(pdf_bytes)
        if slides["page_count"] > MAX_PAGES:
            raise ValueError(f"Slide PDF has {slides['page_count']} pages (max {MAX_PAGES}).")
        upd(slide_text=slides["markdown"], status="analyzing")

        analysis = analyze_meeting(transcript, pages_as_prompt(slides["pages"]))
        upd(analysis=analysis, status="syncing")

        notion_url = create_meeting_page(analysis)
        upd(notion_url=notion_url, status="done")

        # Privacy: remove uploaded source files once the Notion page exists.
        try:
            sb.storage.from_(_BUCKET).remove([audio_path, slide_path])
        except Exception:
            pass

    except Exception as exc:
        upd(status="failed", error=str(exc)[:500])
