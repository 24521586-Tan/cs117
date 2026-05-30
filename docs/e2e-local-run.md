# Running MeetMind end-to-end on localhost

Two paths are available. Start with the **CLI path** to validate every secret
before touching the web UI.

```
Path A — CLI (fastest):   python scripts\run_pipeline_local.py --audio x.mp3 --pdf x.pdf
Path B — Web UI:          backend API (port 8000) + frontend dev server (port 5173)
```

---

## Part 1 — One-time service setup

Do this once. All four services are free tiers.

### 1.1 Supabase

1. Create a project at <https://supabase.com> (or use an existing one).
2. **Storage bucket** — Dashboard → Storage → New bucket → name: `audio-files` →
   uncheck *Public* → Create.
3. **Apply migrations** — Dashboard → SQL Editor, run in order:
   - `db/migrations/001_create_profiles_and_jobs.sql`
   - `db/migrations/002_add_pipeline_fields.sql`
4. **Google OAuth** *(only needed for the web path)* — Dashboard →
   Authentication → Providers → Google → enable → paste your Google OAuth Client
   ID + Secret. Callback URL: `http://localhost:8000/auth/callback`.
5. **Collect keys** — Dashboard → Project Settings → API:
   - `SUPABASE_URL` (Project URL)
   - `SUPABASE_ANON_KEY` (anon/public key)
   - `SUPABASE_SERVICE_ROLE_KEY` (service_role key, keep secret)

### 1.2 Google Gemini API key

1. Go to <https://aistudio.google.com/app/apikey> → **Create API key**.
2. Copy the key → `GEMINI_API_KEY`.

### 1.3 Notion integration + database

Follow [docs/notion-setup.md](notion-setup.md) (5 min). You'll end up with:
- `NOTION_TOKEN` — internal integration secret
- `NOTION_DATABASE_ID` — 32-char hex from the database URL

### 1.4 Colab WhisperX server *(optional — skip for mock transcript)*

> Without this the pipeline runs with a two-line mock transcript. Skip for
> initial wiring; add when you need real transcription.

1. Open `colab/meetmind-whisperx-server.ipynb` in Google Colab.
2. Runtime → Change runtime type → **T4 GPU** → Save.
3. Run all cells (takes ~3 min first time).
4. Copy the public `ngrok` URL printed in the last cell → `COLAB_WHISPER_URL`.
5. **Keep the Colab tab open** while processing jobs; the URL changes each session.

---

## Part 2 — Local installation

### 2.1 Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` and fill in all values:

```env
# Supabase (from Part 1.1)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# WhisperX Colab server (from Part 1.4 — leave empty for mock)
COLAB_WHISPER_URL=https://xxxx.ngrok-free.app/transcribe

# Google Gemini (from Part 1.2)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash

# Notion (from Part 1.3)
NOTION_TOKEN=ntn_xxxx...
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

ALLOWED_ORIGINS=http://localhost:5173
```

### 2.2 Frontend *(only for Path B)*

```powershell
cd frontend
npm install
copy .env.example .env
```

Edit `frontend/.env`:

```env
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_API_URL=http://localhost:8000
```

---

## Part 3 — Running

### Path A — CLI (no auth, no browser)

The fastest way to prove the full pipeline works.

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
{ "title": "…", "summary": "…", … }
→ Creating Notion page…

✅ Notion page: https://www.notion.so/…
```

The Notion URL opens a page with **📌 Meeting Summary** and **✅ To-do List**.

> **Note:** the CLI uploads the audio file to Supabase Storage so the Colab server
> can download it via a signed URL. The file is deleted from Storage at the end
> regardless of success or failure.

---

### Path B — Full web UI

**Terminal 1 — backend:**
```powershell
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
Verify: `curl http://localhost:8000/health` → `{"status":"ok"}`

**Terminal 2 — frontend:**
```powershell
cd frontend
npm run dev
```
Open <http://localhost:5173>.

**Flow:**
1. Click **Sign in with Google** → complete OAuth.
2. Drop your audio file (`.mp3 / .m4a / .wav`) into the first zone.
3. Click the second zone and pick the slide PDF.
4. Click **Bắt đầu phân tích**.
5. Watch the three stages advance:
   - *Tạo bản ghi lời nói* (WhisperX)
   - *Phân tích nội dung* (Gemini)
   - *Đồng bộ sang Notion*
6. Click **Mở trang Notion** when done.

---

## Part 4 — Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `GEMINI_API_KEY is not set` | Key not in `.env` or venv restarted before fill | Re-check `backend/.env`; restart uvicorn |
| `NOTION_TOKEN / NOTION_DATABASE_ID not set` | Missing Notion keys | Fill keys; see [notion-setup.md](notion-setup.md) |
| Notion `404 Object not found` | Integration not connected to the DB | Reopen DB → ⋯ → Connections → add MeetMind |
| Job stuck at `transcribing` | `COLAB_WHISPER_URL` is wrong or Colab timed out | Re-run Colab cells, copy new URL, update `.env` + restart uvicorn |
| Slides show empty text | Image-only PDF (scanned) | Only text-based PDFs are supported (constraint) |
| `slide_path` column not found | Migration 002 not applied | Run `db/migrations/002_add_pipeline_fields.sql` in Supabase SQL Editor |
| Job `failed` with error shown in UI | Any pipeline exception | Error text is stored in `jobs.error` column; check it in Supabase → Table Editor |

## Part 5 — Input constraints

| | Limit |
|---|---|
| Audio format | `.mp3`, `.m4a`, `.wav` |
| Audio duration | ≤ 60 minutes |
| Audio language | English |
| Slide format | text-based `.pdf` |
| Slide pages | ≤ 50 |
| Privacy | Audio + PDF auto-deleted from Storage after Notion page is created |
