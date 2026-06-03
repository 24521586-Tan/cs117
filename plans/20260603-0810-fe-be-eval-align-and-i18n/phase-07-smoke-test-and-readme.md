# Phase 07 — Smoke test on Railway+Vercel, update README

**Status:** pending

## Smoke matrix
| # | Scenario | Expect |
|---|---|---|
| 1 | `.mp3` + `.pdf` | 200, Notion page created |
| 2 | `.mp4` audio-only | 200, Notion page (no slides section) |
| 3 | `.md` slide-only | 200, summary from slide text |
| 4 | `.json` slide-only | 200, summary from json text |
| 5 | `.docx` slide | 422 with English message |
| 6 | Network kill mid-upload | English reconnect banner |
| 7 | Wrong VITE_API_URL (manually broken) | Explicit English error from `getApiBase()` |

## Doc updates
- `README.md` §2 frontend env: clarify `VITE_API_URL` MUST be absolute backend URL in prod.
- §3 Option B "Flow" section: replace Vietnamese "Bắt đầu phân tích" with the new English label.
- `evaluation/README.md` (if exists): note that prod and eval share the slide parser.

## Done when
- All 7 cases pass on Vercel prod against Railway prod.
- README env section unambiguous.
