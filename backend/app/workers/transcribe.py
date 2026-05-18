import httpx

from app.celery_app import celery
from app.core.config import settings
from app.core.supabase import get_supabase

MOCK_TRANSCRIPT = {
    "segments": [
        {"start": 0.0, "end": 3.5, "text": "[Mock] Hello, this is a local dev transcript."},
        {"start": 3.5, "end": 7.0, "text": "[Mock] Set COLAB_WHISPER_URL to use the real WhisperX endpoint."},
    ],
    "language": "en",
}


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def transcribe_audio(self, job_id: str, file_path: str):
    sb = get_supabase()

    def update_status(status: str, transcript=None):
        payload = {"status": status, "updated_at": "now()"}
        if transcript is not None:
            payload["transcript"] = transcript
        sb.table("jobs").update(payload).eq("id", job_id).execute()

    update_status("processing")

    try:
        if not settings.COLAB_WHISPER_URL:
            # Local dev mock
            update_status("done", MOCK_TRANSCRIPT)
            return

        # Get a signed URL so the Colab worker can download the file
        signed = (
            sb.storage.from_("audio-files")
            .create_signed_url(file_path, expires_in=3600)
        )
        audio_url = signed["signedURL"]

        response = httpx.post(
            settings.COLAB_WHISPER_URL,
            json={"audio_url": audio_url},
            timeout=600,
        )
        response.raise_for_status()
        transcript = response.json()
        update_status("done", transcript)

    except Exception as exc:
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            update_status("failed")
