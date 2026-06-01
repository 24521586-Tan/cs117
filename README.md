# MeetMind

Upload a meeting **recording + slide PDF** → get one **Notion page** with a
Meeting Summary and a grouped To-do list (checkbox · deadline · verbatim quote · source slide).

```
audio (.mp3/.m4a/.wav)  ┐
                         ├─► faster-whisper → Gemini → Notion page
slides (.pdf)           ┘
```

## Stack

| Layer    | Tech |
|----------|------|
| Frontend | React 19 + Vite + TypeScript |
| Backend  | FastAPI + BackgroundTasks (Python 3.13) |
| Auth/DB  | Supabase (Google OAuth, Postgres, Storage) |
| ASR      | faster-whisper (local, GPU via CUDA or CPU) |
| LLM      | Google Gemini `gemini-2.5-flash` |
| Output   | Notion database page |

---

## Part 1 — One-time service setup

### 1.1 Supabase

1. Create a project at <https://supabase.com>.
2. **Storage bucket** — Dashboard → Storage → New bucket → name: `audio-files` → uncheck *Public* → Create.
3. **Apply migrations** — Dashboard → SQL Editor, run in order:
   - `db/migrations/001_create_profiles_and_jobs.sql`
   - `db/migrations/002_add_pipeline_fields.sql`
4. **Google OAuth** *(web path only)* — Authentication → Providers → Google → enable → paste Google OAuth Client ID + Secret. Callback URL: `http://localhost:8000/auth/callback`.
5. **Collect keys** — Project Settings → API:
   - `SUPABASE_URL` (Project URL)
   - `SUPABASE_ANON_KEY` (anon/public)
   - `SUPABASE_SERVICE_ROLE_KEY` (service_role — keep secret)

### 1.2 Google Gemini API key

Go to <https://aistudio.google.com/app/apikey> → **Create API key** → copy → `GEMINI_API_KEY`.

### 1.3 Notion integration + database

1. <https://www.notion.so/my-integrations> → **New integration** → copy the **Internal Integration Secret** → `NOTION_TOKEN`.
2. In Notion, create a full-page database named e.g. `Meeting Notes` with exactly these columns:

   | Column | Type |
   |--------|------|
   | `Name` | Title |
   | `Date` | Date |
   | `Attendees` | Multi-select |

3. Open the database → **⋯** → **Connections** → add your integration. *(Skipping this causes `404 Object not found`.)*
4. Copy the 32-char hex ID from the URL → `NOTION_DATABASE_ID`.

### 1.4 Transcription — runs locally (no extra service)

Transcription uses **faster-whisper** in-process; nothing to set up here.

- **GPU (NVIDIA):** auto-detected. Default `WHISPER_MODEL=large-v2`,
  `WHISPER_COMPUTE_TYPE=int8_float16` (~3 GB VRAM; use `float16` for ~4.5 GB if you
  prefer). A 60-min clip transcribes in roughly 5–10 min.
- **CPU only:** set `WHISPER_DEVICE=cpu` and a smaller `WHISPER_MODEL` (e.g. `small`);
  `large-*` on CPU is impractically slow.
- **No transcription (test Gemini + Notion only):** set `WHISPER_MODEL=mock`.

---

## Part 2 — Install

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env    # then fill in the values below
```

**`backend/.env`:**

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

WHISPER_MODEL=large-v2      # tiny|base|small|medium|large-v2|large-v3|mock
WHISPER_DEVICE=auto         # auto|cuda|cpu
WHISPER_COMPUTE_TYPE=int8_float16   # cuda: float16/int8_float16; cpu forced to int8
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash
NOTION_TOKEN=ntn_xxxx...
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
```

**`frontend/.env`:**

```env
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_API_URL=http://localhost:8000
```

---

## Part 3 — Run

### Option A — CLI (no browser, no auth — fastest)

```powershell
cd backend
.venv\Scripts\python.exe scripts\run_pipeline_local.py --audio meeting.mp3 --pdf slides.pdf
```

Expected output:
```
→ Uploading audio for transcription…
→ Transcribing (WhisperX / mock)…
→ Extracting slides (markitdown)…
→ Analyzing with Gemini…
→ Creating Notion page…

✅ Notion page: https://www.notion.so/…
```

### Option B — Web UI

**Terminal 1:**
```powershell
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2:**
```powershell
cd frontend
npm run dev    # → http://localhost:5173
```

**Flow:** Sign in → drop audio file → pick slide PDF → **Bắt đầu phân tích** → watch stages → **Mở trang Notion**.

### Option C — Pipeline Evaluation (Đánh giá hiệu năng)

Run the automated evaluation system to measure transcription accuracy, analysis quality, and task extraction correctness.

**1. Prepare test files** — place files in the `evaluation/` subfolders. File names must match across folders (e.g., `LEC1.mp3` ↔ `LEC1.pdf` ↔ `LEC1.txt`):

```
evaluation/
├── audios/                        # Required — audio recordings
│   ├── LEC1.mp3
│   └── meeting_abc.wav
├── slides/                        # Optional — matching slide PDFs
│   ├── LEC1.pdf
│   └── meeting_abc.pdf
├── transcripts_ground_truth/      # Optional — human-written transcripts for WER
│   ├── LEC1.txt
│   └── meeting_abc.txt
└── run_eval.py                    # Evaluation script
```

> **Note:** Slides and ground truth transcripts are optional per test case. If missing, the script skips slide extraction or WER calculation respectively.

**2. Run the evaluation** (from the `backend/` directory so `.env` is loaded):

```bash
cd backend

# Run all test cases
python ../evaluation/run_eval.py

# Run a single test case
python ../evaluation/run_eval.py --file LEC1
```

**3. View the report** at `evaluation/evaluation_report.md`. Metrics measured:

| Category | Metric | Method |
|----------|--------|--------|
| Speech-to-Text | **WER** (Word Error Rate) | Levenshtein distance vs ground truth text |
| Speech-to-Text | **RTF** (Real-Time Factor) | Transcribe time ÷ audio duration |
| LLM Analysis | **Summary Completeness** | LLM-as-a-Judge (1–5) |
| LLM Analysis | **Summary Accuracy** | LLM-as-a-Judge (1–5) |
| Task Extraction | **Task Completeness** | LLM-as-a-Judge (1–5) — any missing tasks? |
| Task Extraction | **Task Assignment Accuracy** | LLM-as-a-Judge (1–5) — assigned to the right person? |
| Task Extraction | **Task Quote Accuracy** | LLM-as-a-Judge (1–5) — quotes match transcript? |
| System | **Success Rate** | % of test cases processed without errors |

---

## Part 4 — Troubleshooting

| Symptom | Fix |
|---------|-----|
| `GEMINI_API_KEY is not set` | Fill key in `backend/.env`; restart uvicorn |
| `NOTION_TOKEN / NOTION_DATABASE_ID not set` | Fill Notion keys in `backend/.env` |
| Notion `404 Object not found` | Database → ⋯ → Connections → add the integration |
| Job stuck/slow at `transcribing` | CPU + large model is very slow — set `WHISPER_DEVICE=cpu` + `WHISPER_MODEL=small`, or use a GPU |
| `Library cudnn_ops64_9.dll is not found` / CUDA errors | GPU libs missing — `pip install -r requirements.txt` (installs `nvidia-cudnn-cu12`), or fall back to `WHISPER_DEVICE=cpu` |
| Slides text empty | PDF is image-only (scanned) — only text-based PDFs are supported |
| `slide_path` column not found | Apply `db/migrations/002_add_pipeline_fields.sql` in Supabase SQL Editor |

---

## Pipeline stages

```
pending → transcribing → analyzing → syncing → done | failed
```

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
