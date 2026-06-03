# FE/BE ↔ Evaluation Alignment + English i18n + 405 fix

**Created:** 2026-06-03
**Owner:** vanductan-NLT
**Branch:** main

## Goal
1. Đồng bộ file types FE/BE với evaluation (`.mp3/.mp4/.wav` audio; `.pdf/.txt/.md/.json` slide).
2. Translate all frontend UI + error-display copy → English (BE giữ nguyên).
3. Diagnose & fix Vercel 405 on `/upload` POST.

## Phases

| # | Phase | Status |
|---|---|---|
| 01 | Verify 405 root cause (env audit) | done (user fixed VITE_API_URL on Vercel) |
| 02 | Fix VITE_API_URL + defensive guard | done (user fixed env; runtime guard deferred — not needed if env stays set) |
| 03 | Align file-type whitelist FE/BE with evaluation | done |
| 04 | Extend slide pipeline to handle txt/md/json | done (shared parser used by prod + eval) |
| 05 | English i18n sweep across frontend UI | done |
| 06 | Map backend HTTPException status codes → English FE messages | done (`lib/error-messages.ts`) |
| 07 | Update README copy + extension list | done — smoke test on prod is up to you |

## Key dependencies
- Phase 02 needs Vercel env value + Railway URL from user (collected in Phase 01).
- Phase 04 must keep `scripts/run_pipeline_local.py` working — eval calls it.
- Phase 05 + 06 can run in parallel after 03.

## Out of scope
- Translate METHODOLOGY.md / README (user excluded).
- Translate backend HTTPException Vietnamese strings.
- New metrics on UI.

## Open questions
- Có cần hiển thị WER/RTF/coverage metrics ngay trên Job page (production)? — đã hỏi, bạn không chọn ⇒ skip.
- File `.json` slide spec: free-form text content hay schema cụ thể? — eval đọc text trực tiếp; sẽ áp dụng cùng cách ở BE.
