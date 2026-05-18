-- Rollback: 001_create_profiles_and_jobs
-- Created: 2026-05-18

drop policy if exists "Users see own jobs" on public.jobs;
drop policy if exists "Users see own profile" on public.profiles;

drop table if exists public.jobs;
drop table if exists public.profiles;
