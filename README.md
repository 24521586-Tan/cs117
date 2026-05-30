# MeetMind

Upload a meeting **recording + slide PDF** → get one **Notion page** with a
Meeting Summary and a grouped To-do list (checkbox · deadline · verbatim quote ·
source slide).

Pipeline: `audio → WhisperX transcript → markitdown slides → Gemini analysis → Notion page`.

## Stack

| Layer    | Tech                                            |
|----------|-------------------------------------------------|
| Frontend | React + Vite + TypeScript                       |
| Backend  | FastAPI + BackgroundTasks                       |
| Auth/DB  | Supabase (Google OAuth, Postgres, Storage)      |
| ASR      | WhisperX on Google Colab (GPU) via ngrok        |
| LLM      | Google Gemini (`gemini-2.5-flash`)              |
| Output   | Notion database page                            |

## Run locally

### 0. Prereqs
- Supabase project (URL + anon + service-role keys) with an `audio-files` Storage bucket.
- Apply DB migrations in the Supabase SQL editor: `db/migrations/001_*.sql` then `db/migrations/002_*.sql`.
- A Google Gemini API key.
- A Notion integration + database — see [docs/notion-setup.md](docs/notion-setup.md).

### 1. Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # then fill in the values
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

`backend/.env` keys: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`,
`COLAB_WHISPER_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `NOTION_TOKEN`,
`NOTION_DATABASE_ID`, `ALLOWED_ORIGINS`.

### 2. Frontend
```powershell
cd frontend
npm install
copy .env.example .env   # set VITE_API_URL=http://localhost:8000
npm run dev              # → http://localhost:5173
```

### 3. Colab WhisperX
Run `colab/meetmind-whisperx-server.ipynb` (all cells) → copy the ngrok URL →
set `COLAB_WHISPER_URL` in `backend/.env`. If left empty, the worker returns a
**mock transcript** (handy for wiring up Gemini + Notion without a GPU).

## Fast end-to-end check (no web/auth)
Prove the whole pipeline on local files:
```powershell
cd backend
.venv\Scripts\python.exe scripts\run_pipeline_local.py --audio sample.mp3 --pdf slides.pdf
```
Prints the created Notion page URL.

## Constraints
- Audio: English, `.mp3/.m4a/.wav`, ≤ 60 min.
- Slides: text-based `.pdf`, ≤ 50 pages.
- Uploaded audio + PDF are **auto-deleted** from Storage after the Notion page is created.

## API

| Method | Path                      | Description                                  |
|--------|---------------------------|----------------------------------------------|
| GET    | `/health`                 | Health check                                 |
| GET    | `/auth/callback`          | Google OAuth callback                        |
| POST   | `/upload`                 | Upload `file` (audio) + `slides` (pdf), Bearer |
| GET    | `/jobs/{id}/status`       | Poll status (+ `notion_url` when done)       |
| GET    | `/jobs/{id}/transcript`   | Raw transcript when done                     |
| GET    | `/jobs/{id}/result`       | `notion_url` + analysis JSON when done       |

Job status lifecycle: `pending → transcribing → analyzing → syncing → done | failed`.
