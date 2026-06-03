# Phase 04 — Extend slide pipeline to txt/md/json

**Status:** pending
**Depends on:** Phase 03

## Files to modify
- `backend/app/workers/slides.py`
- `backend/app/workers/pipeline.py` (small: pass extension hint)

## Design
- New top-level fn `extract_slides_any(raw: bytes, ext: str) -> dict` returning the same shape `{ "markdown": str, "pages": [{page, text}], "page_count": int }`.
- `.pdf` → existing path.
- `.txt`, `.md` → decode utf-8 (fallback latin-1); treat as 1 "page"; markdown=text.
- `.json` → `json.loads`; if list of strings, each entry = 1 page; if dict with `pages` key, use it; else stringify.
- `MAX_PAGES` cap still applies; for text formats compute synthetic pages.

## Pipeline change
- `process_job` reads `slide_path` extension from stored path (we encode it in filename via `safe_filename`) and routes accordingly.

## Eval parity check
- Confirm `evaluation/run_eval.py` calls into the same `extract_slides_any` (or matching) so prod and eval share the parser.

## Done when
- `LEC1.md` and `LEC1.json` both produce non-empty `slide_text` and reach `done`.
- `scripts/run_pipeline_local.py --pdf slides.md` works.
