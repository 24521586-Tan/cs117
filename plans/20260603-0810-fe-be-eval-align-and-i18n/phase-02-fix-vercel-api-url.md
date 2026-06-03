# Phase 02 — Fix VITE_API_URL + defensive guard

**Status:** pending
**Depends on:** Phase 01 confirmed

## Action 1 — Vercel env
- Set `VITE_API_URL=https://<railway-public-url>` (no trailing slash) for Production + Preview.
- Trigger redeploy (env-only redeploy is enough).

## Action 2 — Frontend defensive guard
File: `frontend/src/lib/api-base.ts` (new)
- Export `getApiBase()`: throw clear error if `VITE_API_URL` is empty, relative, or same-origin as `window.location.origin`. Log to console.
- Replace direct `import.meta.env.VITE_API_URL` usage in `UploadPage.tsx`, `JobPage.tsx`, `HistoryPage.tsx` with `getApiBase()`.

## Action 3 — Railway CORS
- Ensure `ALLOWED_ORIGINS` includes `https://cs117.vercel.app` (comma-separated if multiple).

## Done when
- POST `/upload` from prod Vercel reaches Railway and returns 200/422 (not 405).
- If env missing locally, UI shows explicit error instead of opaque 405.
