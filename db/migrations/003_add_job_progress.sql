-- Migration: 003_add_job_progress
-- Transcription progress (0-100) so the UI can show a real percentage while the
-- long ASR step runs. Other stages (analyzing/syncing) are quick and leave it as-is.

alter table public.jobs
  add column if not exists progress int not null default 0;
