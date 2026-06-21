# Aesthetic Scan — Frontend (MVP)

Thin, guided **capture → heatmap → PDF** web app for the Aesthetic Biometrics Engine.
It talks **only** to the Supabase `engine-proxy` Edge Function — never to the engine
directly, and it never holds the engine API key. Built with Vite + React + TypeScript.

## Flow

`Consent → Capture (4 guided angles) → Review → Results (heatmap + plan + PDF)`

- **Capture** uses the live device camera (`getUserMedia`, front camera) with a per-step
  face-silhouette guide, **or** an "Upload instead" path per shot (desktop, or re-using
  standardized tripod photos — which give the best ~1–2 mm accuracy). Captures are
  downscaled to ≤1600 px / JPEG q0.85 and saved **un-mirrored**.
- **Results** overlays a heatmap on each analyzed photo: a soft blob per zone (coloured by
  severity, opacity = intensity) plus dots at injection points, mapped back onto the
  original upload via the per-view crop transform. Plus aesthetic score, symmetry, top
  zones, contraindications, quality/calibration banners, and a one-click PDF report.

## Config

Copy `.env.example` to `.env` and set both **public-safe** values:

```
VITE_ENGINE_PROXY_URL=https://mbwteypkehrmeqzdzdph.supabase.co/functions/v1/engine-proxy
VITE_SUPABASE_ANON_KEY=<supabase anon key>   # Supabase → Project Settings → API
```

The anon key only authenticates the caller to the proxy; the engine key stays server-side
in the Edge Function secret `ENGINE_API_KEY`.

## Develop

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # type-check + production build to dist/
npm run preview    # serve the production build
```

## Deploy

`npm run build` emits a static `dist/`. **Live at https://scan.novasyn.de** — served by
Caddy on the Hetzner box from `/srv/aesthetic-scan` (own vhost, auto-TLS).

Update (after a code or `.env` change — config is baked into the bundle at build time):

```bash
npm run build
tar czf - -C dist . | ssh hetzner 'tar xzf - -C /srv/aesthetic-scan && chmod -R a+rX /srv/aesthetic-scan'
```

First-time setup also needed: DNS A record (`scan.novasyn.de → 188.245.150.15`, IONOS); the
Caddy vhost (`root * /srv/aesthetic-scan; encode gzip; try_files {path} /index.html; file_server`
— `caddy validate` **with the systemd env loaded** for the existing `{$CADDY_API_KEY}` matchers,
then `systemctl reload caddy`); and the Edge Function secret `ALLOWED_ORIGIN=https://scan.novasyn.de`
(CORS hardening — `*` is dev-only; note this then blocks localhost browser dev against the live proxy).

## Notes

- **DEV/TEST posture:** consenting subjects only; consent here is the MVP minimum, not the
  full DSGVO Art. 9 flow (Gate 0).
- Real face photos are biometric data — never commit them. `test_images/` (repo root) is
  gitignored for exactly this reason.
- The contract this app consumes is documented in `docs/FRONTEND_MVP_LOVABLE_SPEC.md` and
  `docs/CONTRACTS.md`.
