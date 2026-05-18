import httpx

from app.core.config import settings
from app.core.supabase import get_supabase

MOCK_TRANSCRIPT = {
    "segments": [
        {"start": 0.0, "end": 3.5, "text": "[Mock] Hello, this is a local dev transcript."},
        {"start": 3.5, "end": 7.0, "text": "[Mock] Set COLAB_WHISPER_URL to use real WhisperX."},
    ],
    "language": "en",
}


def transcribe_audio(job_id: str, file_path: str) -> None:
    sb = get_supabase()

    def update_status(status: str, transcript=None):
        payload = {"status": status}
        if transcript is not None:
            payload["transcript"] = transcript
        sb.table("jobs").update(payload).eq("id", job_id).execute()

    update_status("processing")

    try:
        if not settings.COLAB_WHISPER_URL:
            update_status("done", MOCK_TRANSCRIPT)
            return

        signed = sb.storage.from_("audio-files").create_signed_url(file_path, expires_in=3600)
        audio_url = signed["signedURL"]

        response = httpx.post(
            settings.COLAB_WHISPER_URL,
            json={"audio_url": audio_url},
            timeout=600,
        )
        response.raise_for_status()
        update_status("done", response.json())

    except Exception:
        update_status("failed")
