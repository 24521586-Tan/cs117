# Phase 05 — English i18n sweep across frontend UI

**Status:** pending
**Scope:** UI strings + frontend-originated error/status text. Backend Vietnamese kept as-is (Phase 06 handles display).

## Files
- `src/pages/UploadPage.tsx` — headings, drop-zone labels, validation toasts, button states, hint text.
- `src/pages/HistoryPage.tsx` — `STATUS_LABEL`, "Đang tải…", empty-state, "Xem tiếp"/"Chi tiết", `toLocaleString('vi-VN')` → `'en-US'`.
- `src/pages/JobPage.tsx` — `STEPS[]`, "Đang xử lý cuộc họp", reconnect banner, error fallbacks.
- `src/pages/LoginPage.tsx` — read first, then translate.
- `src/pages/AuthCallbackPage.tsx` — "Xác thực thất bại", "Đang đăng nhập…", "Quay lại đăng nhập".
- `src/components/NavBar.tsx` — "Đăng xuất" → "Sign out", nav links if Vietnamese.

## Approach
- Direct inline replacement (project does not use i18n lib; KISS — don't introduce one).
- Keep copy short, sentence-case (Material-style), consistent terminology:
  - "cuộc họp" → "meeting"
  - "Bản ghi" / "transcript" → "transcript"
  - "Phân tích" → "Analysis"
  - "Đồng bộ Notion" → "Sync to Notion"
  - Stage labels exactly: `Pending`, `Transcribing`, `Analyzing`, `Syncing to Notion`, `Done`, `Failed`.

## Done when
- `grep -E "[ăâđêôơưĂÂĐÊÔƠƯáàảãạ...]" src/` returns no matches in non-comment lines.
- All pages render English without layout regression.
