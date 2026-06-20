-- Seed the MVP default tenant (single practice). Idempotent on slug.
-- Applied to mbwteypkehrmeqzdzdph (AestheticBiometricsDB). The engine's async
-- persistence requires a valid organizations.id; the Edge Function injects this
-- tenant server-side (ENGINE_ORG_ID).
--
-- NOTE: the five prior schema/RLS migrations (20260318* / 20260322*) live in the
-- remote migration history and predate this repo's supabase/ dir; export them here
-- for full from-scratch reproducibility when convenient.
insert into public.organizations (name, slug, settings)
values (
  'Praxis Nassar',
  'praxis-nassar',
  '{"environment":"dev","purpose":"MVP test org — consenting subjects only; Gate 0 (DSGVO Art. 9) before real patients"}'::jsonb
)
on conflict (slug) do update
  set name = excluded.name,
      settings = excluded.settings;
