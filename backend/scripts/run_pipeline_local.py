"""Run the full meeting pipeline on local files, no web/auth needed.

    python scripts/run_pipeline_local.py --audio meeting.mp3 --pdf slides.pdf

Reuses the same workers as the API. Audio is uploaded to Supabase Storage so the
transcribe step can fetch it the same way the API does, then transcribed locally
with faster-whisper (set WHISPER_MODEL=mock to skip ASR). Prints the Notion URL.
"""

import argparse
import json
import mimetypes
import sys
import uuid
from pathlib import Path

# Make `app` importable when run from backend/ (python scripts/run_pipeline_local.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.supabase import get_supabase  # noqa: E402
from app.workers.analyze import analyze_meeting  # noqa: E402
from app.workers.notion_sync import create_meeting_page  # noqa: E402
from app.workers.slides import MAX_PAGES, extract_slides_any, pages_as_prompt  # noqa: E402
from app.workers.transcribe import transcribe  # noqa: E402

_BUCKET = "audio-files"


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the meeting -> Notion pipeline locally.")
    ap.add_argument("--audio", required=True, help="Path to meeting audio (.mp3/.mp4/.m4a/.wav)")
    ap.add_argument("--pdf", required=True, help="Path to slide (.pdf/.txt/.md/.json)")
    args = ap.parse_args()

    audio = Path(args.audio)
    pdf = Path(args.pdf)
    for p in (audio, pdf):
        if not p.is_file():
            print(f"❌ File not found: {p}")
            return 1

    sb = get_supabase()
    audio_path = f"cli/{uuid.uuid4()}-{audio.name}"

    print("→ Uploading audio for transcription…")
    sb.storage.from_(_BUCKET).upload(
        audio_path,
        audio.read_bytes(),
        file_options={"content-type": mimetypes.guess_type(audio.name)[0] or "audio/mpeg"},
    )

    try:
        print("→ Transcribing (faster-whisper / mock)…")
        transcript = transcribe(audio_path)

        print("→ Extracting slides…")
        slides = extract_slides_any(pdf.read_bytes(), pdf.suffix.lower())
        if slides["page_count"] > MAX_PAGES:
            print(f"❌ Slide has {slides['page_count']} pages (max {MAX_PAGES}).")
            return 1

        print("→ Analyzing with Gemini…")
        analysis = analyze_meeting(transcript, pages_as_prompt(slides["pages"]))
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

        print("→ Creating Notion page…")
        url = create_meeting_page(analysis)
        print(f"\n✅ Notion page: {url}")
        return 0
    finally:
        try:
            sb.storage.from_(_BUCKET).remove([audio_path])
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
