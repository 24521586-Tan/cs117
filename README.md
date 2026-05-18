# MeetMind

AI-powered meeting transcription. Upload  /  audio → WhisperX transcript → displayed in browser.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + TypeScript + TailwindCSS |
| Backend | FastAPI + BackgroundTasks |
| Auth | Supabase Google OAuth |
| Storage | Supabase Storage (bucket: ) |
| DB | Supabase PostgreSQL |

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\pip install -r requirements.txt
# macOS/Linux
.venv/bin/pip install -r requirements.txt

cp .env.example .env   # fill in your values
```

Run API server:
```bash
# Windows
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# macOS/Linux
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # fill in your values
npm run dev            # → http://localhost:5173
```

### 3. Colab WhisperX endpoint

1. Open the WhisperX Colab notebook (provided separately).
2. Run all cells — it exposes a public URL via  or .
3. Copy the URL into  as .
4. If  is empty, the worker returns a **mock transcript** for local development.

## Auth flow

1. Frontend → Supabase Google OAuth → redirects to 
2. Backend exchanges code for session → upserts  row → returns 
3. Frontend stores session via Supabase JS SDK

## API

| Method | Path | Description |
|--------|------|-------------|
| GET |  | Health check |
| GET |  | OAuth callback |
| POST |  | Upload audio file (Bearer) |
| GET |  | Poll job status (Bearer) |
| GET |  | Get transcript when done (Bearer) |
