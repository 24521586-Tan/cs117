"""Slide source -> text.

PDF: markitdown produces the stored markdown; pypdf gives per-page text so the
LLM can attribute each task to a source slide number.

Plain text (.txt/.md/.json): read directly as a single synthetic "page" — keeps
the pipeline contract identical to the PDF path so analyze/Notion stages don't
need to branch.
"""

import io
import json

from markitdown import MarkItDown
from pypdf import PdfReader

MAX_PAGES = 60
MAX_TEXT_CHARS = 200_000  # ~50 PDF pages worth of dense text

SUPPORTED_SLIDE_EXTS = (".pdf", ".txt", ".md", ".json")

_md = MarkItDown()


def extract_slides_any(raw: bytes, ext: str) -> dict:
    """Route by extension. Returns { markdown, pages, page_count } in all cases."""
    ext = (ext or "").lower()
    if ext == ".pdf":
        return _extract_pdf(raw)
    if ext in (".txt", ".md"):
        return _extract_text(raw, fmt=ext)
    if ext == ".json":
        return _extract_json(raw)
    raise ValueError(f"Unsupported slide extension: {ext}")


def extract_slides(pdf_bytes: bytes) -> dict:
    """Backwards-compatible PDF-only entry point."""
    return _extract_pdf(pdf_bytes)


def _extract_pdf(pdf_bytes: bytes) -> dict:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = [
        {"page": i, "text": (page.extract_text() or "").strip()}
        for i, page in enumerate(reader.pages, start=1)
    ]
    try:
        markdown = _md.convert_stream(io.BytesIO(pdf_bytes), file_extension=".pdf").text_content
    except Exception:
        markdown = "\n\n".join(p["text"] for p in pages if p["text"])
    return {"markdown": markdown, "pages": pages, "page_count": len(reader.pages)}


def _decode(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def _extract_text(raw: bytes, fmt: str) -> dict:
    text = _decode(raw).strip()
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(f"Slide text exceeds {MAX_TEXT_CHARS} characters.")
    pages = [{"page": 1, "text": text}] if text else []
    return {"markdown": text, "pages": pages, "page_count": 1 if text else 0}


def _extract_json(raw: bytes) -> dict:
    """Accept either a list of page strings or a dict with a `pages` key."""
    decoded = _decode(raw)
    try:
        data = json.loads(decoded)
    except json.JSONDecodeError:
        # Not valid JSON — treat as plain text so the pipeline still works.
        return _extract_text(raw, fmt=".txt")

    pages: list[dict] = []
    if isinstance(data, list):
        for i, item in enumerate(data, start=1):
            pages.append({"page": i, "text": str(item).strip()})
    elif isinstance(data, dict) and isinstance(data.get("pages"), list):
        for i, item in enumerate(data["pages"], start=1):
            if isinstance(item, dict) and "text" in item:
                pages.append({"page": int(item.get("page", i)), "text": str(item["text"]).strip()})
            else:
                pages.append({"page": i, "text": str(item).strip()})
    else:
        pages = [{"page": 1, "text": json.dumps(data, ensure_ascii=False)}]

    markdown = "\n\n".join(p["text"] for p in pages if p["text"])
    if len(markdown) > MAX_TEXT_CHARS:
        raise ValueError(f"Slide text exceeds {MAX_TEXT_CHARS} characters.")
    return {"markdown": markdown, "pages": pages, "page_count": len(pages)}


def pages_as_prompt(pages: list[dict]) -> str:
    """Page-numbered slide text block fed to the LLM for slide attribution."""
    return "\n\n".join(f"[Slide {p['page']}]\n{p['text']}" for p in pages if p["text"])
