"""Audio -> transcript via local faster-whisper (GPU when available).

Pure step: returns the transcript dict or raises. Status/DB writes are owned by
the pipeline orchestrator (workers/pipeline.py).

faster-whisper is the CTranslate2 backend that WhisperX itself wraps, so with the
same model (e.g. large-v2) the transcript text is equivalent to the previous
Colab WhisperX server — minus the optional word-alignment/diarization steps the
pipeline never used. Output shape is unchanged:
    { "segments": [{start, end, text}], "language": str }.
"""

import os
import tempfile
from typing import Callable, Optional

from app.core.config import settings
from app.core.supabase import get_supabase

_BUCKET = "audio-files"

# Returned when WHISPER_MODEL == "mock", so the pipeline runs without loading a model.
MOCK_TRANSCRIPT = {
    "segments": [
        {"start": 0.0, "end": 3.5, "text": "[Mock] Hello, this is a local dev transcript."},
        {"start": 3.5, "end": 7.0, "text": "[Mock] Set WHISPER_MODEL to a real size to use faster-whisper."},
    ],
    "language": "en",
}

# Loaded once on first real transcription and reused across jobs (model load is slow
# and holds GPU VRAM). Module-level cache keyed by the running process.
_model = None


def _register_cuda_dll_dirs() -> None:
    """On Windows, make the pip-installed CUDA libs discoverable by CTranslate2.

    nvidia-cuda-runtime / cublas / cudnn drop their DLLs under site-packages, not on
    PATH. CTranslate2 loads its CUDA deps (cublas64_12.dll, cudart64_12.dll, ...) with
    a plain search that only consults PATH, so add_dll_directory alone is not enough —
    we prepend the bin dirs to PATH as well. No-op on non-Windows (Linux uses RPATH).
    """
    if os.name != "nt":
        return
    try:
        import nvidia

        base = os.path.dirname(nvidia.__file__)
    except Exception:
        return
    for sub in ("cuda_runtime", "cublas", "cudnn", "cuda_nvrtc"):
        d = os.path.join(base, sub, "bin")
        if not os.path.isdir(d):
            continue
        try:
            os.add_dll_directory(d)
        except Exception:
            pass
        if d not in os.environ.get("PATH", "").split(os.pathsep):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")


def _resolve_device() -> tuple[str, str]:
    """Pick (device, compute_type). CPU can't use GPU compute types, so clamp to int8."""
    device = settings.WHISPER_DEVICE
    compute_type = settings.WHISPER_COMPUTE_TYPE

    if device == "auto":
        try:
            import ctranslate2

            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            device = "cpu"

    if device == "cpu":
        compute_type = "int8"

    return device, compute_type


def _get_model():
    global _model
    if _model is None:
        device, compute_type = _resolve_device()
        if device == "cuda":
            _register_cuda_dll_dirs()

        from faster_whisper import WhisperModel

        _model = WhisperModel(settings.WHISPER_MODEL, device=device, compute_type=compute_type)
    return _model


def transcribe(file_path: str, on_progress: Optional[Callable[[int], None]] = None) -> dict:
    """Transcribe an audio file stored in Supabase Storage.

    on_progress(pct) is called with an increasing 0-99 percentage as segments are
    decoded (based on segment end time vs total audio duration), letting the caller
    surface a real progress bar. Returns { "segments": [...], "language": str }.
    """
    if settings.WHISPER_MODEL.strip().lower() in ("", "mock"):
        if on_progress:
            on_progress(99)
        return MOCK_TRANSCRIPT

    sb = get_supabase()
    audio_bytes = sb.storage.from_(_BUCKET).download(file_path)

    suffix = os.path.splitext(file_path)[1] or ".mp3"
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            tmp = f.name

        model = _get_model()
        # vad_filter trims silence -> fewer hallucinated segments on quiet stretches.
        segments_gen, info = model.transcribe(tmp, beam_size=5, vad_filter=True)

        total = info.duration or 0  # full audio length in seconds; 0 => unknown
        segments = []
        last_pct = 0
        for s in segments_gen:  # generator: iterating it runs the actual decoding
            segments.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
            if on_progress and total > 0:
                pct = min(99, int(s.end / total * 100))
                if pct > last_pct:
                    last_pct = pct
                    on_progress(pct)
        return {"segments": segments, "language": info.language}
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
