-- Migration: 001_create_profiles_and_jobs
-- Created: 2026-05-18

-- Users (sync with Supabase Auth)
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  email text,
  google_access_token text,
  google_refresh_token text,
  created_at timestamptz default now()
);

-- Jobs (one per upload)
create table public.jobs (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade,
  status text default 'pending', -- pending | processing | done | failed
  file_path text,                -- Supabase Storage path
  transcript jsonb,              -- WhisperX output
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Row Level Security
alter table public.profiles enable row level security;
alter table public.jobs enable row level security;

create policy "Users see own profile" on public.profiles
  for all using (auth.uid() = id);

create policy "Users see own jobs" on public.jobs
  for all using (auth.uid() = user_id);
