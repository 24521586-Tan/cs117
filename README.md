# MeetMind

Upload a meeting **recording + slide PDF** → get one **Notion page** with a
Meeting Summary and a grouped To-do list (checkbox · deadline · verbatim quote ·
source slide number).

```
audio (.mp3/.m4a/.wav)  ┐
                         ├─► WhisperX → Gemini → Notion page
slides (.pdf)           ┘
```

## Quick start

**➜ [Full local run guide →  docs/e2e-local-run.md](docs/e2e-local-run.md)**

Short version — after filling `backend/.env`:

```powershell
# CLI (no browser, no auth — fastest way to verify)
cd backend
.venv\Scripts\python.exe scripts\run_pipeline_local.py --audio meeting.mp3 --pdf slides.pdf
# prints: ✅ Notion page: https://www.notion.so/…

# Web UI
cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev   # → http://localhost:5173
```

## Stack

| Layer    | Tech                                            |
|----------|-------------------------------------------------|
| Frontend | React 19 + Vite + TypeScript                    |
| Backend  | FastAPI + BackgroundTasks (Python 3.13)         |
| Auth/DB  | Supabase (Google OAuth, Postgres, Storage)      |
| ASR      | WhisperX on Google Colab (GPU) via ngrok        |
| LLM      | Google Gemini `gemini-2.5-flash`                |
| Output   | Notion database page                            |

## Prerequisites

| What | Where |
|------|-------|
| Supabase project + `audio-files` bucket | <https://supabase.com> |
| DB migrations applied (001 + 002) | Supabase → SQL Editor |
| Gemini API key | <https://aistudio.google.com/app/apikey> |
| Notion integration + database | [docs/notion-setup.md](docs/notion-setup.md) |
| Colab WhisperX server *(optional)* | `colab/meetmind-whisperx-server.ipynb` |

> Leave `COLAB_WHISPER_URL` empty to use a mock transcript — useful for testing
> the Gemini + Notion stages without a GPU.

## `backend/.env` keys

```env
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
COLAB_WHISPER_URL=          # leave empty for mock transcript
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
NOTION_TOKEN=
NOTION_DATABASE_ID=
ALLOWED_ORIGINS=http://localhost:5173
```

## `frontend/.env` keys

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=http://localhost:8000
```

## Pipeline stages

```
pending → transcribing → analyzing → syncing → done | failed
```

| Stage | What happens |
|-------|--------------|
| `transcribing` | Audio → WhisperX segments (Colab) or mock |
| `analyzing` | Transcript + slides → Gemini structured JSON (summary + tasks) |
| `syncing` | JSON → Notion page (Summary heading + per-person To-do blocks) |
| `done` | Notion URL written to DB; audio + PDF deleted from Storage |

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |
| GET | `/auth/callback` | — | Google OAuth callback |
| POST | `/upload` | Bearer | Upload `file` (audio) + `slides` (PDF) |
| GET | `/jobs/{id}/status` | Bearer | Poll status + `notion_url` when done |
| GET | `/jobs/{id}/result` | Bearer | `notion_url` + full analysis JSON |
| GET | `/jobs/{id}/transcript` | Bearer | Raw WhisperX transcript |

## Constraints

- Audio: English, `.mp3/.m4a/.wav`, ≤ 60 min, low background noise
- Slides: text-based `.pdf`, ≤ 50 pages
- Audio + PDF are **auto-deleted** from Storage after the Notion page is created
