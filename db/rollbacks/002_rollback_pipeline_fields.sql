-- Rollback: 002_add_pipeline_fields

alter table public.jobs
  drop column if exists slide_path,
  drop column if exists slide_text,
  drop column if exists analysis,
  drop column if exists notion_url,
  drop column if exists error;
