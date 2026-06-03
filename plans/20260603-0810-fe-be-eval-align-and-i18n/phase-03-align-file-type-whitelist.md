# Phase 03 — Align file-type whitelist FE/BE with evaluation

**Status:** pending

## Target whitelist (single source of truth)

| Kind | Extensions | Content-types accepted |
|---|---|---|
| Audio | `.mp3`, `.mp4`, `.m4a`, `.wav` | `audio/mpeg`, `audio/mp4`, `audio/x-m4a`, `audio/m4a`, `audio/wav`, `audio/x-wav`, `audio/wave`, `video/mp4` (mp4 audio-only) |
| Slide | `.pdf`, `.txt`, `.md`, `.json` | `application/pdf`, `text/plain`, `text/markdown`, `application/json` |

Decision: keep `.m4a` (FE/BE have it, eval ignores but won't conflict).

## Backend changes — `backend/app/api/upload.py`
- Expand `ALLOWED_AUDIO` and add `ALLOWED_SLIDES` set (PDF + text).
- For text-based slides, skip `PdfReader` page-count validation; use a `MAX_SLIDE_CHARS = 200_000` cap (≈ 50 pages).
- Persist content-type into Storage so pipeline can branch on it.

## Frontend changes — `frontend/src/pages/UploadPage.tsx`
- `ALLOWED_AUDIO` mirror backend.
- New `ALLOWED_SLIDE` accepts pdf/txt/md/json by extension fallback (browsers don't always set `text/markdown`).
- `<input accept>` attributes updated.
- Drop-zone copy updated (English in Phase 05).

## Done when
- Manual upload `.mp4` audio + `.md` slide succeeds end-to-end locally.
- Reject `.docx` slide with clear 422.
