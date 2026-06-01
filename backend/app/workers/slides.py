"""Slide PDF -> text.

markitdown produces the stored markdown (the required extractor); pypdf provides
per-page text so the LLM can attribute each task to a source slide number.
"""

import io

from markitdown import MarkItDown
from pypdf import PdfReader

MAX_PAGES = 60

_md = MarkItDown()


def extract_slides(pdf_bytes: bytes) -> dict:
    """Return { "markdown": str, "pages": [{page, text}], "page_count": int }."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = [
        {"page": i, "text": (page.extract_text() or "").strip()}
        for i, page in enumerate(reader.pages, start=1)
    ]

    try:
        markdown = _md.convert_stream(io.BytesIO(pdf_bytes), file_extension=".pdf").text_content
    except Exception:
        # Fallback so the pipeline still proceeds if markitdown chokes on a PDF.
        markdown = "\n\n".join(p["text"] for p in pages if p["text"])

    return {"markdown": markdown, "pages": pages, "page_count": len(reader.pages)}


def pages_as_prompt(pages: list[dict]) -> str:
    """Page-numbered slide text block fed to the LLM for slide attribution."""
    return "\n\n".join(f"[Slide {p['page']}]\n{p['text']}" for p in pages if p["text"])
