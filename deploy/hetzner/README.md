# Hetzner Deploy — Aesthetic Biometrics Engine

Deploys the engine as an **isolated** Docker service behind the existing Caddy on the
novasyn.de box (`188.245.150.15`, Nuremberg). It runs **alongside** browser-use (`:8000`),
sdk-agent (`:8001`), and klarbefund — touching none of them.

| Item | Value |
|---|---|
| Public URL | `https://biometrics.novasyn.de` |
| Bind | `127.0.0.1:8002` → container `:8000` |
| Health | `GET /api/v2/health` |
| Reverse proxy | Caddy (auto Let's Encrypt TLS) |
| Compose project | `aesthetic-biometrics` |

> **Verified locally:** the image builds (model downloaded + SHA-verified) and
> `/api/v2/health` returns `{"status":"healthy","model_loaded":true}`.

## Secrets you must provide
1. **`API_KEYS`** — generate with `openssl rand -hex 32`. The Supabase Edge Function sends this as `X-API-Key`.
2. **`SUPABASE_KEY`** — the **service-role** secret for `mbwteypkehrmeqzdzdph` (Supabase Dashboard → Project Settings → API → `service_role`). Backend-only; never in a browser.

## Pre-flight (on the server)
```bash
free -h                                   # confirm ≥ ~1.5 GB free (engine mem_limit is 1500m)
ss -tlnp | grep -E ':8002' || echo "8002 free"   # must be free
docker --version && caddy version
```

## 1. DNS
Point `biometrics.novasyn.de` → `188.245.150.15` (A record, IONOS zone `novasyn.de`).
_(Can be added via the IONOS MCP once the subdomain is confirmed.)_

## 2. Get the code on the box
```bash
git clone https://github.com/JNassar77/aesthetic-biometrics-engine.git
cd aesthetic-biometrics-engine
git checkout feat/frontend-mvp            # or main, once merged
```

## 3. Configure secrets
```bash
cp deploy/hetzner/.env.production.example deploy/hetzner/.env.production
nano deploy/hetzner/.env.production       # set API_KEYS and SUPABASE_KEY
```

## 4. Build + start
```bash
docker compose -f deploy/hetzner/docker-compose.yml up -d --build
docker compose -f deploy/hetzner/docker-compose.yml ps
docker compose -f deploy/hetzner/docker-compose.yml logs -f --tail=50   # Ctrl-C when healthy
curl -fsS http://127.0.0.1:8002/api/v2/health    # expect status healthy, model_loaded true
```

## 5. Caddy (TLS + public routing)
Append the block from `deploy/hetzner/Caddyfile.snippet` to `/etc/caddy/Caddyfile`, then:
```bash
caddy validate --config /etc/caddy/Caddyfile      # NEVER reload an invalid config
systemctl reload caddy                            # graceful; zero-downtime for the other sites
curl -fsS https://biometrics.novasyn.de/api/v2/health
```

## Update to a new version
```bash
git pull
docker compose -f deploy/hetzner/docker-compose.yml up -d --build
```

## Rollback / teardown
```bash
docker compose -f deploy/hetzner/docker-compose.yml down
# remove the biometrics.novasyn.de block from /etc/caddy/Caddyfile, then:
caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy
# optionally delete the DNS A record
```

## Notes
- **DEV/TEST posture.** Persistence is ON (images + results land in Supabase), but this is a
  development deployment for consenting test subjects only. Real-patient go-live stays behind
  **Gate 0** (MDR scope + DSGVO Art. 9 DPIA).
- The image downloads + SHA-verifies the MediaPipe model at build time — the build **fails on
  model drift** (provenance for a medical-device artifact).
- No `cpus` cap (single-user); `mem_limit` is a ceiling, not a reservation. Swap is disabled so
  an OOM fails loud instead of thrashing the host/Caddy.
