"""Audio -> transcript via the WhisperX Colab server.

Pure step: returns the transcript dict or raises. Status/DB writes are owned by
the pipeline orchestrator (workers/pipeline.py).
"""

import httpx

from app.core.config import settings
from app.core.supabase import get_supabase

# Returned when COLAB_WHISPER_URL is unset, so the pipeline runs locally without a GPU.
MOCK_TRANSCRIPT = {
    "segments": [
        {"start": 0.0, "end": 3.5, "text": "[Mock] Hello, this is a local dev transcript."},
        {"start": 3.5, "end": 7.0, "text": "[Mock] Set COLAB_WHISPER_URL to use real WhisperX."},
    ],
    "language": "en",
}


def transcribe(file_path: str) -> dict:
    """Transcribe an audio file stored in Supabase Storage.

    Returns WhisperX output: { "segments": [{start, end, text}], "language": str }.
    """
    if not settings.COLAB_WHISPER_URL:
        return MOCK_TRANSCRIPT

    sb = get_supabase()
    signed = sb.storage.from_("audio-files").create_signed_url(file_path, expires_in=3600)
    audio_url = signed["signedURL"]

    response = httpx.post(
        settings.COLAB_WHISPER_URL,
        json={"audio_url": audio_url},
        timeout=600,
    )
    response.raise_for_status()
    return response.json()
