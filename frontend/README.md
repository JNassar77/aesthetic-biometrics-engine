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

`npm run build` emits a static `dist/`. Serve it from any static host (Caddy on the
Hetzner box, Vercel, etc.). After the production domain is known, set the Edge Function
secret `ALLOWED_ORIGIN` to that origin (CORS hardening — `*` is dev-only).

## Notes

- **DEV/TEST posture:** consenting subjects only; consent here is the MVP minimum, not the
  full DSGVO Art. 9 flow (Gate 0).
- Real face photos are biometric data — never commit them. `test_images/` (repo root) is
  gitignored for exactly this reason.
- The contract this app consumes is documented in `docs/FRONTEND_MVP_LOVABLE_SPEC.md` and
  `docs/CONTRACTS.md`.
