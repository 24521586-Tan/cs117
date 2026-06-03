# Phase 06 — Map backend errors → English FE messages

**Status:** pending
**Why:** User chose to keep backend HTTPException strings Vietnamese, but UI must be English.

## Strategy
- Stop displaying raw `body.detail` from backend.
- Translate by **status code + field hint** on the frontend.

## New helper — `src/lib/error-messages.ts`
- `mapApiError(status: number, body: unknown): string` returning English message:
  - `401` → "Your session expired. Please sign in again."
  - `405` → "The server rejected this request method. Check that VITE_API_URL points to the API, not the web app."
  - `413` / detail contains "too large" → "File is too large for the server."
  - `422` → parse `detail` for known keywords:
    - "âm thanh" / "audio" → "Audio file is invalid or too long (max 60 min)."
    - "PDF" / "trang" → "Slide file is invalid or too long (max 60 pages)."
    - else → "Invalid input. Please check your files and try again."
  - `5xx` → "Server error. Please try again."
  - Network/`TypeError` → "Cannot reach the server. Check your connection."

## Files updated
- `UploadPage.tsx`, `JobPage.tsx`, `HistoryPage.tsx` — replace inline error string logic with `mapApiError`.

## Done when
- Trigger each scenario (oversized file, 405, network down) and see only English in UI.
