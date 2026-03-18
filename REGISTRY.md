# Registry — Aesthetic Biometrics Engine

> Master index of all project artifacts. Single point of reference to find anything.

---

## Documentation Registry

| Document | Path | Purpose | Owner |
|---|---|---|---|
| Project Context | `CLAUDE.md` | AI assistant context, conventions, architecture overview | Maintained every session |
| Tasks & Roadmap | `TASKS.md` | Sprint planning, backlog, phase tracking | Updated per feature |
| Features | `FEATURES.md` | Complete feature catalog with workflows and clinical relevance | Updated per feature |
| API Contracts | `CONTRACTS.md` | Request/response schemas, error codes, webhook payloads | Updated per API change |
| Architecture | `ARCHITECTURE.md` | System design, math foundations, security considerations | Updated per structural change |
| System Graphs | `GRAPH.md` | Mermaid diagrams: system overview, sequence, ER, module deps | Updated per structural change |
| Contributing | `CONTRIBUTING.md` | Dev setup, branch strategy, code standards, test guide | Updated per process change |
| Registry | `REGISTRY.md` | This file — master index of all artifacts | Always current |
| Definition of Done | `DOD.md` | Quality gates for features, fixes, and releases | Baseline, rarely changes |

---

## Code Module Registry

| Module | Path | Responsibility | Dependencies |
|---|---|---|---|
| App Entrypoint | `app/main.py` | FastAPI app, CORS, router mounting | config, routes |
| Configuration | `app/config.py` | Environment variables via Pydantic Settings | — |
| API Routes | `app/api/routes.py` | HTTP endpoints, request handling, orchestration | all core, all services, schemas |
| Schemas | `app/models/schemas.py` | Pydantic models for all request/response types | — |
| Landmark Detector | `app/core/landmark_detector.py` | MediaPipe FaceMesh wrapper, landmark mapping | mediapipe |
| Image Validator | `app/core/image_validator.py` | Quality checks (blur, brightness, contrast) | opencv, schemas |
| Frontal Analyzer | `app/core/frontal_analyzer.py` | Symmetry, facial thirds, lip ratio | landmark_detector, geometry, schemas |
| Profile Analyzer | `app/core/profile_analyzer.py` | E-line, nasolabial angle, chin projection | landmark_detector, geometry, schemas |
| Oblique Analyzer | `app/core/oblique_analyzer.py` | Ogee curve, midface volume | landmark_detector, geometry, schemas |
| Geometry Utils | `app/utils/geometry.py` | Distance, angle, px→mm, point-to-line math | numpy |
| Supabase Service | `app/services/supabase_service.py` | DB persistence, image fetch from storage | supabase, config |
| n8n Service | `app/services/n8n_service.py` | Webhook notification to n8n | httpx, config |

---

## Infrastructure Registry

| Component | Technology | Location / ID |
|---|---|---|
| GitHub Repo | Git | `JNassar77/aesthetic-biometrics-engine` |
| Supabase Project | PostgreSQL | `mbwteypkehrmeqzdzdph` (AestheticBiometricsDB, eu-west-1) |
| Supabase URL | — | `https://mbwteypkehrmeqzdzdph.supabase.co` |
| Docker Image | Python 3.11-slim | `Dockerfile` in repo root |
| Docker Compose | Dev environment | `docker-compose.yml` in repo root |
| Deployment Target | Railway | Not yet configured |
| n8n Webhook | n8n | Configured via `N8N_WEBHOOK_URL` env var |

---

## Database Table Registry

| Table | Purpose | Key Columns | Indexes |
|---|---|---|---|
| `patients` | Patient demographics | id, external_id, name, DOB | PK on id, UNIQUE on external_id |
| `biometric_analyses` | Individual view analysis results | id, patient_id, view_angle, result_json | patient_id, view_angle, created_at DESC |
| `treatment_sessions` | Pre/post treatment grouping | id, patient_id, treatment_type, pre/post IDs | patient_id |

---

## API Endpoint Registry

| Method | Path | Purpose | Auth | Status |
|---|---|---|---|---|
| POST | `/api/v1/analyze` | Run facial analysis on image | None (planned) | Active |
| GET | `/api/v1/health` | Health check | None | Active |
| GET | `/` | Service info & discovery | None | Active |
| GET | `/docs` | Swagger UI (auto-generated) | None | Active |

---

## Environment Variable Registry

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SUPABASE_URL` | Yes (for persistence) | `""` | Supabase project URL |
| `SUPABASE_KEY` | Yes (for persistence) | `""` | Supabase anon/service key |
| `N8N_WEBHOOK_URL` | No | `""` | n8n webhook for analysis notifications |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000` | CORS allowed origins (comma-separated) |
| `MAX_IMAGE_SIZE_MB` | No | `10` | Maximum upload size |
| `MIN_FACE_CONFIDENCE` | No | `0.7` | Minimum detection confidence threshold |

---

## Dependency Registry

| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.115.6 | Web framework |
| uvicorn | 0.34.0 | ASGI server |
| mediapipe | 0.10.21 | Face landmark detection |
| opencv-python-headless | 4.11.0.86 | Image processing |
| numpy | 2.2.3 | Numerical computation |
| scipy | 1.15.2 | Scientific computation |
| Pillow | 11.1.0 | Image format support |
| supabase | 2.13.0 | Supabase Python client |
| python-dotenv | 1.0.1 | .env file loading |
| httpx | 0.28.1 | Async HTTP client |
| pydantic | 2.10.6 | Data validation |
| pydantic-settings | 2.7.1 | Settings management |
| python-multipart | 0.0.20 | File upload parsing |
