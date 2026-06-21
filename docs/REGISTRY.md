# Registry — Aesthetic Biometrics Engine

> Master index of all project artifacts. Single point of reference to find anything.

---

## Documentation Registry

| Document | Path | Purpose | Owner |
|---|---|---|---|
| Project Context | `CLAUDE.md` (root) | AI assistant context, conventions, architecture overview | Maintained every session |
| README | `README.md` (root) | GitHub landing page, quick start | Updated per release |
| Tasks & Roadmap | `docs/TASKS.md` | Sprint planning, backlog, phase tracking | Updated per feature |
| Features | `docs/FEATURES.md` | Complete feature catalog with workflows and clinical relevance | Updated per feature |
| API Contracts | `docs/CONTRACTS.md` | Request/response schemas, error codes, webhook payloads | Updated per API change |
| Architecture | `docs/ARCHITECTURE.md` | System design, math foundations, security considerations | Updated per structural change |
| System Graphs | `docs/GRAPH.md` | Mermaid diagrams: system overview, sequence, ER, module deps | Updated per structural change |
| Contributing | `docs/CONTRIBUTING.md` | Dev setup, branch strategy, code standards, test guide | Updated per process change |
| Registry | `docs/REGISTRY.md` | This file — master index of all artifacts | Always current |
| Definition of Done | `docs/DOD.md` | Quality gates for features, fixes, and releases | Baseline, rarely changes |
| Architecture V2 | `docs/ARCHITECTURE_V2.md` | Complete V2 system redesign with zones and treatment plans | Reference for all V2 work |
| Sprint Plan | `docs/SPRINTS.md` | 12 Sprints, 6 Phasen, Abhaengigkeiten, Meilensteine | Updated per sprint |
| Lehrbuch | `docs/lehrbuch/generate_book.js` | DOCX-Lehrbuch (16/16 Kapitel komplett) | Updated per sprint |
| Frontend Build Spec | `docs/FRONTEND_MVP_LOVABLE_SPEC.md` | Capture→heatmap→PDF frontend contract (endpoints, overlay back-transform, errors) | Sprint 14 |
| Frontend README | `frontend/README.md` | Aesthetic Scan app — flow, config, develop/deploy | Sprint 14 |
| Hetzner Deploy Runbook | `deploy/hetzner/README.md` | Isolated engine deploy (compose, Caddy, pre-flight, rollback) | Sprint 14 |
| Engine Proxy README | `supabase/functions/engine-proxy/README.md` | Edge Function routes, secrets, smoke test | Sprint 14 |
| Clinical Validation SOP | `docs/clinical/Klinische_Validierung_…_Caliper_Foto_SOP.docx` | Caliper + photo data-collection SOP (Sprint 11 prep) | Owner-provided |
| Session Logs | `docs/SESSION_2026-*.md` | Per-session status + next-session handover | Per session |

---

## Code Module Registry

| Module | Path | Responsibility | Dependencies | Version |
|---|---|---|---|---|
| App Entrypoint | `app/main.py` | FastAPI app, CORS, V1+V2 routers | config, routes, v2_routes | **V2** |
| Configuration | `app/config.py` | Environment variables via Pydantic Settings | — | V1 |
| API Routes V1 | `app/api/v1_routes.py` | Legacy V1 endpoints (/analyze, /health) | core, services, schemas | V1 |
| **API Routes V2** | `app/api/v2_routes.py` | **V2 endpoints: /assessment, /compare, /history, /health** | orchestrator, schemas_v2 | **V2** |
| Schemas V1 | `app/models/schemas.py` | Pydantic models for V1 request/response | — | V1 |
| **Schemas V2** | `app/models/schemas_v2.py` | **V2 API schemas: Assessment, Comparison, Treatment, History** | pydantic | **V2** |
| **Pipeline Orchestrator** | `app/pipeline/orchestrator.py` | **3 images → preprocess → detect → analyze → plan → response** | all pipeline, all analysis, plan_generator | **V2** |
| **Face Landmarker V2** | `app/detection/face_landmarker.py` | **Tasks API: 478 landmarks + 52 blendshapes + transform matrix** | mediapipe | **V2** |
| **Landmark Index** | `app/detection/landmark_index.py` | **478-point reference + 16 anatomical zone mappings** | — | **V2** |
| **Head Pose** | `app/detection/head_pose.py` | **Yaw/pitch/roll from transformation matrix + view estimation** | numpy | **V2** |
| **Image Preprocessor** | `app/pipeline/image_preprocessor.py` | **EXIF fix, face-crop (lens distortion), decode, resize** | opencv | **V2** |
| **Quality Gate** | `app/pipeline/quality_gate.py` | **Image quality + head pose + neutral expression validation** | opencv, head_pose | **V2** |
| Landmark Detector (legacy) | `app/core/landmark_detector.py` | Legacy FaceMesh wrapper | mediapipe | V1 |
| Image Validator (legacy) | `app/core/image_validator.py` | Legacy quality checks | opencv | V1 |
| Frontal Analyzer (legacy) | `app/core/frontal_analyzer.py` | Symmetry, facial thirds, lip ratio | landmark_detector, geometry | V1 |
| Profile Analyzer (legacy) | `app/core/profile_analyzer.py` | E-line, nasolabial angle, chin projection | landmark_detector, geometry | V1 |
| Oblique Analyzer (legacy) | `app/core/oblique_analyzer.py` | Ogee curve, midface volume | landmark_detector, geometry | V1 |
| **Pixel Calibration** | `app/utils/pixel_calibration.py` | **Iris-based px→mm calibration + face-width fallback** | numpy | **V2** |
| **Geometry Utils** | `app/utils/geometry.py` | **2D + 3D distance, angle, plane projection, sagittal plane** | numpy | **V2** |
| **Zone Definitions** | `app/treatment/zone_definitions.py` | **19 treatment zones with landmarks, reference ranges, view priorities** | landmark_index | **V2** |
| **Zone Models** | `app/models/zone_models.py` | **Pydantic models for zone results, symmetry, proportions** | pydantic | **V2** |
| **Symmetry Engine** | `app/analysis/symmetry_engine.py` | **6-axis bilateral symmetry + blendshape dynamic asymmetry** | face_landmarker, pixel_calibration | **V2** |
| **Proportion Engine** | `app/analysis/proportion_engine.py` | **Facial thirds, fifths, golden ratio, lip ratio + Cupid's bow** | face_landmarker, pixel_calibration | **V2** |
| **Profile Engine** | `app/analysis/profile_engine.py` | **E-line, nasolabial angle, chin projection, nasal dorsum, Steiner, cervicomental** | face_landmarker, pixel_calibration, geometry | **V2** |
| **Volume Engine** | `app/analysis/volume_engine.py` | **Ogee curve, temporal hollowing, tear trough, jowl, buccal corridor — depth from metric 3D reconstruction (negated; fallback relative-z), `estimated`** | face_landmarker, pixel_calibration, multiview_reconstruction | **V2.2** |
| **3D Reconstruction** | `app/analysis/multiview_reconstruction.py` | **Metric multi-view landmark triangulation (orthographic, iris scale); reconstruct_from_views policy excludes profile, requires iris calibration** | numpy | **V2.2** |
| **Overlay** | `app/analysis/overlay.py` | **Frontend data: per-zone injection points + heatmap (centroid, intensity, severity colour), normalized to analyzed frame; `canonical_oblique_view` names the physical oblique the canonical overlay maps to** | landmark_index | **V2.3** |
| **Aging Engine** | `app/analysis/aging_engine.py` | **Muscle tonus from blendshapes, gravitational drift, periorbital aging** | face_landmarker, pixel_calibration | **V2** |
| **Multi-View Fusion** | `app/analysis/multi_view_fusion.py` | **Confidence-weighted landmark fusion across views + contradiction detection** | zone_definitions | **V2** |
| **Zone Analyzer** | `app/analysis/zone_analyzer.py` | **Orchestrates all engines → Zone Report + Aesthetic Score** | all engines, multi_view_fusion, zone_definitions | **V2** |
| **Product Database** | `app/treatment/product_database.py` | **14 products (HA/CaHA/PLLA/BoNT-A/boosters), zone→product mapping, vascular risk, structural priority** | — | **V2** |
| **Plan Generator** | `app/treatment/plan_generator.py` | **Zone→treatment plan: severity prioritization, clinical ordering, session planning, volume estimation** | product_database, contraindication_check, zone_definitions | **V2** |
| **Contraindication Check** | `app/treatment/contraindication_check.py` | **Safety: extreme asymmetry, vascular risk, tear trough, overtreatment, glabella/forehead dependency** | product_database | **V2** |
| **Comparison Engine** | `app/analysis/comparison_engine.py` | **Before/After: per-zone deltas, improvement score, measurement deltas, heatmap visualization** | zone_analyzer | **V2** |
| **Supabase Service** | `app/services/supabase_service.py` | **V1+V2: save_assessment, get_assessment, get_patient_history, upload_image, save_comparison** | supabase, config | **V2** |
| **n8n Service** | `app/services/n8n_service.py` | **V1+V2: webhook with V2 envelope (event, assessment_id, aesthetic_score)** | httpx, config | **V2** |
| **PDF Report** | `app/services/pdf_report.py` | **Clinical PDF from AssessmentResponse — zones, severity, plan, measurements with `estimated` flagging** | reportlab | **V2.2** |
| **Structured Logging** | `app/utils/logging.py` | **JSON formatter, log_step context manager for pipeline instrumentation** | — | **V2** |
| **API Key Auth** | `app/api/auth.py` | **X-API-Key header validation, dev mode bypass** | config | **V2.1** |
| **Rate Limiter** | `app/api/rate_limit.py` | **In-memory sliding window rate limiting per IP** | config | **V2.1** |

---

## Test Registry

| Directory | Contents | Test Count |
|---|---|---|
| `tests/analysis/` | Symmetry, proportions, engines, fusion, zone analyzer, comparison, **blendshapes** | ~150 |
| `tests/treatment/` | Zone definitions, product database, contraindications, plan generator | ~90 |
| `tests/integration/` | Orchestrator, V2 routes, schemas | ~50 |
| `tests/services/` | n8n webhook, Supabase service, structured logging | ~25 |
| `tests/edge_cases/` | No face, corrupt images, partial views, boundary values | ~20 |
| `tests/fixtures/` | `synthetic.py` — factory functions for landmarks and blendshapes | — |
| `tests/` (root) | Head pose, quality gate, landmark index, preprocessor, geometry, calibration, **performance benchmark** | ~105 |
| `tests/analysis/` (3D wiring, overlay) | `test_engine_3d_wiring.py`, `test_overlay.py`, reconstruction policy | +34 |
| `tests/integration/` (PDF report) | `test_pdf_report.py` — renderer, row reconstruction, endpoints | +11 |
| **TOTAL** | | **503** |

---

## Infrastructure Registry

| Component | Technology | Location / ID |
|---|---|---|
| GitHub Repo | Git | `JNassar77/aesthetic-biometrics-engine` |
| Supabase Project | PostgreSQL | `mbwteypkehrmeqzdzdph` (AestheticBiometricsDB, eu-west-1) |
| Supabase URL | — | `https://mbwteypkehrmeqzdzdph.supabase.co` |
| Docker Image | Python 3.11-slim-bookworm (multi-stage; model downloaded + SHA-verified in build) | `Dockerfile` in repo root |
| CI/CD | GitHub Actions | `.github/workflows/ci.yml` (test + Docker build) |
| **Deployment (LIVE)** | **Hetzner + Docker + Caddy** | **`deploy/hetzner/` — bind `127.0.0.1:8003` → Caddy auto-TLS → `https://biometrics.novasyn.de` (188.245.150.15, Nuremberg); isolated beside the other novasyn.de services** |
| Deployment (alt) | Railway | `railway.toml` (Dockerfile build, EU europe-west4) — config retained, **not** the live target |
| **Engine Proxy** | **Supabase Edge Function** | **`engine-proxy` (Deno, `verify_jwt`) — `…/functions/v1/engine-proxy`; holds `ENGINE_API_KEY`, injects tenant server-side** |
| **Frontend App (LIVE)** | **Vite + React + TS** | **`frontend/` — Aesthetic Scan; LIVE at `https://scan.novasyn.de` (Caddy static from `/srv/aesthetic-scan`, auto-TLS); talks only to engine-proxy** |
| DNS | IONOS (`novasyn.de`) | `biometrics.novasyn.de` A → `188.245.150.15` |
| n8n Webhook | n8n | Configured via `N8N_WEBHOOK_URL` env var |

---

## Database Table Registry

| Table | Purpose | Key Columns | Indexes | Version |
|---|---|---|---|---|
| `organizations` | Multi-tenant root | id, name, slug, settings | PK on id, UNIQUE on slug | **V2** |
| `patients` | Patient demographics | id, **organization_id**, external_id, name, DOB | PK, org_id, UNIQUE(org_id, external_id) | **V2** |
| `assessments` | Zone analysis (up to 4 views) | id, org_id, patient_id, zones (JSONB), treatment_plan (JSONB), aesthetic_score | org_id, patient_date | **V2** |
| `treatment_comparisons` | Before/After deltas | id, org_id, patient_id, pre/post_assessment_id, zone_deltas, improvement_score | org_id, patient_id | **V2** |
| `biometric_analyses` | Individual view results (V1 legacy) | id, patient_id, view_angle, result_json | patient_id | V1 |
| `treatment_sessions` | Pre/post grouping (V1 legacy) | id, patient_id, treatment_type | patient_id | V1 |

### Storage Buckets

| Bucket | Purpose | Access | Limits |
|---|---|---|---|
| `patient-images` | Assessment images (frontal, profile, oblique, oblique_left/right) | Org-scoped RLS | 10MB, JPEG/PNG/WebP |

---

## API Endpoint Registry

| Method | Path | Purpose | Auth | Status |
|---|---|---|---|---|
| POST | `/api/v2/assessment` | **Up to 4-view zone analysis + plan + 3D reconstruction + overlay** | X-API-Key | **Active** |
| POST | `/api/v2/report` | **Render clinical PDF from an AssessmentResponse (lossless)** | X-API-Key | **Active** |
| GET | `/api/v2/assessment/{id}/report` | **Clinical PDF for a stored assessment (Supabase)** | X-API-Key | **Active** |
| POST | `/api/v2/compare` | **Before/After assessment comparison** | X-API-Key | **Active** |
| GET | `/api/v2/patients/{id}/history` | **Patient assessment history** | X-API-Key | **Active** |
| GET | `/api/v2/health` | **V2 health check (DB, model, uptime)** | None | **Active** |
| POST | `/api/v1/analyze` | Legacy single-image analysis | None (planned) | Active (legacy) |
| GET | `/api/v1/health` | Legacy health check | None | Active (legacy) |
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
| `API_KEYS` | No | `""` | Comma-separated API keys; empty = dev mode (no auth) |
| `RATE_LIMIT_RPM` | No | `60` | Requests per minute per IP; 0 = disabled |
| `ENVIRONMENT` | No | `development` | `production` enforces fail-closed auth (503 if no API_KEYS) |

---

### Proxy & Frontend Config (Sprint 14)

**Edge Function `engine-proxy` secrets** (Supabase): `ENGINE_API_KEY` (required — one of the
engine's `API_KEYS`), `ENGINE_URL` (default `https://biometrics.novasyn.de`), `ENGINE_ORG_ID`
(default Praxis Nassar tenant), `ALLOWED_ORIGIN` (default `*`; set to the frontend domain in prod).

**Frontend `frontend/.env`** (both public-safe browser values): `VITE_ENGINE_PROXY_URL`
(the proxy base URL), `VITE_SUPABASE_ANON_KEY` (Supabase anon key — authenticates the caller to
the proxy; the engine key stays server-side).

---

## Dependency Registry

> Minimum versions, mirroring `requirements.txt` (the source of truth).

| Package | Version | Purpose |
|---|---|---|
| fastapi | ≥0.137.1 | Web framework |
| uvicorn[standard] | ≥0.49.0 | ASGI server |
| python-multipart | ≥0.0.32 | File upload parsing |
| mediapipe | ≥0.10.35 | Face landmark detection (Tasks API) |
| opencv-python-headless | ≥4.13.0 | Image processing |
| numpy | ≥2.4.6 | Numerical computation |
| scipy | ≥1.17.1 | Scientific computation (rotation decomposition) |
| Pillow | ≥12.2.0 | Image format support |
| pillow-heif | ≥1.4.0 | HEIC/iPhone image decode |
| supabase | ≥2.31.0 | Supabase Python client |
| python-dotenv | ≥1.2.2 | .env file loading |
| httpx | ≥0.28.1 | Async HTTP client |
| pydantic | ≥2.13.4 | Data validation |
| pydantic-settings | ≥2.14.1 | Settings management |
| reportlab | ≥4.4.0 | Clinical PDF report generation |
