# Phase 01 — Verify 405 root cause (env audit)

**Status:** pending — blocks all code changes for 405 fix
**Type:** Investigation, no code change

## Hypothesis
`VITE_API_URL` trên Vercel build hoặc rỗng hoặc relative (`/api`) → `fetch(\`${API}/upload\`)` → POST tới `cs117.vercel.app/upload` → SPA host trả 405.

## Evidence to collect from user
1. Vercel → Project → Settings → Environment Variables → giá trị `VITE_API_URL` (Production scope). Screenshot hoặc copy giá trị.
2. Railway backend public URL (`https://...up.railway.app`).
3. Railway env `ALLOWED_ORIGINS` hiện tại — có chứa `https://cs117.vercel.app` không?
4. Browser DevTools → Network tab → click failed `upload` request → confirm **Request URL** (host + path).

## Decision tree
- Request URL host = `cs117.vercel.app` → confirmed misconfig → Phase 02 (fix env).
- Request URL host = Railway, status 405 → backend route mismatch (`/upload` POST is defined) → check trailing slash / CORS preflight.
- Request URL host = Railway, status CORS-blocked → fix `ALLOWED_ORIGINS` on Railway, then retry.

## Done when
- Root cause confirmed in writing.
- Phase 02 has concrete fix to apply.
