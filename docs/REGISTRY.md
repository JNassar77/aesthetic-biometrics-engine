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

---

## Code Module Registry

| Module | Path | Responsibility | Dependencies | Version |
|---|---|---|---|---|
| App Entrypoint | `app/main.py` | FastAPI app, CORS, router mounting | config, routes | V1 |
| Configuration | `app/config.py` | Environment variables via Pydantic Settings | — | V1 |
| API Routes | `app/api/routes.py` | HTTP endpoints, request handling, orchestration | all core, all services, schemas | V1 |
| Schemas | `app/models/schemas.py` | Pydantic models for all request/response types | — | V1 |
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
| Supabase Service | `app/services/supabase_service.py` | DB persistence, image fetch from storage | supabase, config | V1 |
| n8n Service | `app/services/n8n_service.py` | Webhook notification to n8n | httpx, config | V1 |

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
