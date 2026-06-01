-- Migration: 002_add_pipeline_fields
-- Extends jobs with slide extraction, LLM analysis, and Notion output fields.
-- Status lifecycle becomes: pending -> transcribing -> analyzing -> syncing -> done | failed

alter table public.jobs
  add column if not exists slide_path text,   -- Supabase Storage path of uploaded slide PDF
  add column if not exists slide_text text,   -- markitdown-extracted slide markdown
  add column if not exists analysis jsonb,    -- { title, summary, attendees, tasks_by_person }
  add column if not exists notion_url text,   -- created Notion page URL
  add column if not exists error text;        -- failure reason when status = 'failed'
