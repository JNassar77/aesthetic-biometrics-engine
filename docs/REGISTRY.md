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
| Lehrbuch | `docs/lehrbuch/generate_book.js` | DOCX-Lehrbuch (12/16 Kapitel fertig: 3,4,5,6,7,8,9,10,11,12,13,14) | Updated per sprint |

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
| **Volume Engine** | `app/analysis/volume_engine.py` | **Ogee curve, temporal hollowing, tear trough, jowl assessment (3D depth)** | face_landmarker, pixel_calibration, geometry | **V2** |
| **Aging Engine** | `app/analysis/aging_engine.py` | **Muscle tonus from blendshapes, gravitational drift, periorbital aging** | face_landmarker, pixel_calibration | **V2** |
| **Multi-View Fusion** | `app/analysis/multi_view_fusion.py` | **Confidence-weighted landmark fusion across views + contradiction detection** | zone_definitions | **V2** |
| **Zone Analyzer** | `app/analysis/zone_analyzer.py` | **Orchestrates all engines → Zone Report + Aesthetic Score** | all engines, multi_view_fusion, zone_definitions | **V2** |
| **Product Database** | `app/treatment/product_database.py` | **14 products (HA/CaHA/PLLA/BoNT-A/boosters), zone→product mapping, vascular risk, structural priority** | — | **V2** |
| **Plan Generator** | `app/treatment/plan_generator.py` | **Zone→treatment plan: severity prioritization, clinical ordering, session planning, volume estimation** | product_database, contraindication_check, zone_definitions | **V2** |
| **Contraindication Check** | `app/treatment/contraindication_check.py` | **Safety: extreme asymmetry, vascular risk, tear trough, overtreatment, glabella/forehead dependency** | product_database | **V2** |
| **Comparison Engine** | `app/analysis/comparison_engine.py` | **Before/After: per-zone deltas, improvement score, measurement deltas, heatmap visualization** | zone_analyzer | **V2** |
| **Supabase Service** | `app/services/supabase_service.py` | **V1+V2: save_assessment, get_assessment, get_patient_history, upload_image, save_comparison** | supabase, config | **V2** |
| **n8n Service** | `app/services/n8n_service.py` | **V1+V2: webhook with V2 envelope (event, assessment_id, aesthetic_score)** | httpx, config | **V2** |
| **Structured Logging** | `app/utils/logging.py` | **JSON formatter, log_step context manager for pipeline instrumentation** | — | **V2** |

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
| `tests/` (root) | Head pose, quality gate, landmark index, preprocessor, geometry, calibration | ~100 |
| **TOTAL** | | **439** |

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

| Table | Purpose | Key Columns | Indexes | Version |
|---|---|---|---|---|
| `organizations` | Multi-tenant root | id, name, slug, settings | PK on id, UNIQUE on slug | **V2** |
| `patients` | Patient demographics | id, **organization_id**, external_id, name, DOB | PK, org_id, UNIQUE(org_id, external_id) | **V2** |
| `assessments` | 3-view zone analysis | id, org_id, patient_id, zones (JSONB), treatment_plan (JSONB), aesthetic_score | org_id, patient_date | **V2** |
| `treatment_comparisons` | Before/After deltas | id, org_id, patient_id, pre/post_assessment_id, zone_deltas, improvement_score | org_id, patient_id | **V2** |
| `biometric_analyses` | Individual view results (V1 legacy) | id, patient_id, view_angle, result_json | patient_id | V1 |
| `treatment_sessions` | Pre/post grouping (V1 legacy) | id, patient_id, treatment_type | patient_id | V1 |

### Storage Buckets

| Bucket | Purpose | Access | Limits |
|---|---|---|---|
| `patient-images` | Assessment images (frontal, profile, oblique) | Org-scoped RLS | 10MB, JPEG/PNG/WebP |

---

## API Endpoint Registry

| Method | Path | Purpose | Auth | Status |
|---|---|---|---|---|
| POST | `/api/v2/assessment` | **3-view zone analysis + treatment plan** | None (planned) | **Active** |
| POST | `/api/v2/compare` | **Before/After assessment comparison** | None (planned) | Stub (Sprint 9) |
| GET | `/api/v2/patients/{id}/history` | **Patient assessment history** | None (planned) | Stub (Sprint 9) |
| GET | `/api/v2/health` | **V2 health check** | None | **Active** |
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
