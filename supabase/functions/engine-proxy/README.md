# engine-proxy — Supabase Edge Function

Secure proxy in front of the Aesthetic Biometrics Engine. The browser calls this
function; the engine's `X-API-Key` stays server-side. The tenant (`organization_id`)
is injected here, **not** chosen by the client.

- **Project:** `mbwteypkehrmeqzdzdph` (AestheticBiometricsDB, eu-west-1)
- **Base URL:** `https://mbwteypkehrmeqzdzdph.supabase.co/functions/v1/engine-proxy`
- **Auth:** `verify_jwt = true`. Callers send the Supabase **anon** key as
  `Authorization: Bearer <anon>` and `apikey: <anon>` (safe to ship in the browser).

## Routes
| Method | Path | Body | → Engine | Returns |
|---|---|---|---|---|
| GET | `/health` | — | `/api/v2/health` | JSON |
| POST | `/assessment` | multipart: `frontal`, `oblique_left`, `oblique_right`, `profile` (≥1) | `/api/v2/assessment` | `AssessmentResponse` JSON |
| POST | `/report` | `AssessmentResponse` JSON | `/api/v2/report` | PDF |

## Secrets — only `ENGINE_API_KEY` is required (the rest default in code)
| Name | Value |
|---|---|
| `ENGINE_URL` | `https://biometrics.novasyn.de` (the deployed engine) |
| `ENGINE_API_KEY` | one of the engine's `API_KEYS` |
| `ENGINE_ORG_ID` | `80c55491-46b6-4b82-98dc-2719758b4372` (Praxis Nassar) |
| `ALLOWED_ORIGIN` | dev: `*` · prod: the practice / Lovable origin |

Set via the dashboard (Edge Functions → Manage secrets) or the CLI:
```bash
supabase secrets set ENGINE_API_KEY=<engine key> --project-ref mbwteypkehrmeqzdzdph
```

## Deploy
```bash
supabase functions deploy engine-proxy --project-ref mbwteypkehrmeqzdzdph
```
(Also deployable via the Supabase MCP — the source here is the single source of truth.)

## Smoke test
```bash
ANON=<anon key>
curl -H "Authorization: Bearer $ANON" -H "apikey: $ANON" \
  https://mbwteypkehrmeqzdzdph.supabase.co/functions/v1/engine-proxy/health
# engine not yet live -> 502 {"error":"engine_unreachable",...}
# engine live         -> 200 {"status":"healthy","model_loaded":true,...}
```

## Notes
- **Server-side tenant injection.** Harden later to derive the org from the authenticated
  user (JWT claims) once patient accounts exist.
- Keep client images ~1600px — comfortably within the Edge Function 256MB / 2s-CPU limits.
- **DEV/TEST posture** — consenting subjects only; Gate 0 (DSGVO Art. 9) before real patients.
