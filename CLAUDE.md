# Aesthetic Biometrics Engine

## Project Overview

Medical AI backend that extracts biometric facial measurements from standardized photographs (frontal 0°, oblique 45°, profile 90°) for aesthetic surgery and dermatology. Serves as an **Agent-as-a-Service** — receives images via API, returns structured JSON for downstream AI agents and n8n workflows.

**Domain:** Aesthetic medicine (Botulinum toxin, dermal fillers)
**Owner:** Jihad Nassar / Praxis Nassar

## Architecture

```
Client/n8n ──POST /api/v1/analyze──▶ FastAPI
                                        │
                              ┌─────────┼─────────┐
                              ▼         ▼         ▼
                          Frontal   Profile   Oblique
                          Analyzer  Analyzer  Analyzer
                              │         │         │
                              └────┬────┘─────────┘
                                   ▼
                            JSON Response
                              │         │
                              ▼         ▼
                          Supabase    n8n Webhook
```

### Directory Structure

```
app/
├── main.py              # FastAPI app entrypoint
├── config.py            # Pydantic settings (env vars)
├── api/
│   ├── v1_routes.py     # V1 API endpoints (/analyze, /health) — renamed Sprint 9
│   └── v2_routes.py     # V2 API: /assessment, /compare, /history, /health
├── detection/           # V2 landmark detection (Sprint 1) ✅
│   ├── face_landmarker.py     # Tasks API: 478 pts + blendshapes + matrix
│   ├── landmark_index.py      # Anatomical groups + 19 zone mappings
│   └── head_pose.py           # Yaw/pitch/roll from transform matrix
├── pipeline/            # V2 image processing (Sprint 1-2, 8) ✅
│   ├── image_preprocessor.py  # EXIF, face-crop, decode, resize, reprocess
│   ├── quality_gate.py        # Quality + pose + expression + hard rejection
│   └── orchestrator.py        # 3 images → preprocess → detect → analyze → plan (Sprint 8)
├── analysis/            # V2 analysis engines (Sprint 3-5) ✅
│   ├── symmetry_engine.py     # 6-axis bilateral symmetry + dynamic asymmetry
│   ├── proportion_engine.py   # Thirds, fifths, golden ratio, lip ratio
│   ├── profile_engine.py      # E-line, NLA, chin, nasal dorsum, Steiner
│   ├── volume_engine.py       # Ogee curve, temporal, tear trough, jowl (3D)
│   ├── aging_engine.py        # Muscle tonus, gravitational drift, periorbital
│   ├── multi_view_fusion.py   # Confidence-weighted landmark fusion (Sprint 5)
│   ├── zone_analyzer.py       # Orchestrates all engines → Zone Report (Sprint 5)
│   └── comparison_engine.py   # Before/After: deltas, improvement score, heatmap (Sprint 7)
├── treatment/           # V2 treatment intelligence (Sprint 3+6) ✅
│   ├── zone_definitions.py    # 19 zones with landmarks, reference ranges
│   ├── product_database.py    # 14 products, zone→product mapping, vascular risk
│   ├── plan_generator.py      # Severity prioritization, clinical ordering, sessions
│   └── contraindication_check.py  # Safety: asymmetry, vascular, overtreatment
├── core/                # V1 analysis engines (legacy, still functional)
│   ├── landmark_detector.py   # Legacy FaceMesh wrapper
│   ├── image_validator.py     # Legacy quality checks
│   ├── frontal_analyzer.py    # Symmetry, facial thirds, lip ratio
│   ├── profile_analyzer.py    # E-line, nasolabial angle, chin
│   └── oblique_analyzer.py    # Ogee curve, midface volume
├── models/
│   ├── schemas.py       # Pydantic request/response models (V1)
│   ├── schemas_v2.py   # V2 API schemas: Assessment, Comparison, Plan (Sprint 8)
│   └── zone_models.py  # Zone Pydantic models (V2)
├── services/            # External integrations (Supabase, n8n)
│   ├── supabase_service.py  # V1+V2: save_assessment, get, history, upload (Sprint 9)
│   └── n8n_service.py       # V1+V2: webhook with envelope (Sprint 9)
└── utils/
    ├── geometry.py          # 2D + 3D math (distance, angle, plane projection)
    ├── pixel_calibration.py # Iris-based px→mm calibration + face-width fallback
    └── logging.py           # Structured JSON logging + log_step (Sprint 9)
models/                  # ML model files (not in git, download manually)
  └── face_landmarker.task  # MediaPipe model (3.6MB, see Common Commands)
tests/                   # Test suite (439 tests passing, 80% coverage)
  ├── analysis/              # Symmetry, proportion, engines, fusion, comparison, blendshapes
  ├── treatment/             # Zone definitions, product DB, contraindications, plan generator
  ├── integration/           # Orchestrator, V2 routes, schemas
  ├── services/              # n8n, Supabase, logging
  ├── edge_cases/            # No face, corrupt images, partial views, boundary values
  ├── fixtures/              # Synthetic landmark data (symmetric, asymmetric, aged)
docs/                    # Project documentation
  TASKS.md               # Roadmap & backlog
  FEATURES.md            # Feature catalog
  CONTRACTS.md           # API & data contracts
  ARCHITECTURE.md        # Design & math
  GRAPH.md               # Mermaid diagrams
  REGISTRY.md            # Master artifact index
  DOD.md                 # Definition of Done
  CONTRIBUTING.md        # Dev guide
```

## Documentation

Start here depending on what you need:
- **Building a feature?** → `docs/FEATURES.md` → `docs/CONTRACTS.md` → `docs/DOD.md`
- **Understanding the system?** → `docs/ARCHITECTURE.md` → `docs/GRAPH.md`
- **Looking for something?** → `docs/REGISTRY.md`
- **What's next?** → `docs/TASKS.md`

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Face Detection | MediaPipe FaceMesh (478 landmarks) |
| Image Processing | OpenCV (headless) |
| Math | NumPy, SciPy |
| Database | Supabase (AestheticBiometricsDB) |
| Orchestration | n8n webhooks |
| Deployment | Docker → Railway |

## Freshness Rule — MANDATORY

**Never rely on training knowledge for library APIs.** Before writing or modifying code that uses any external library, ALWAYS verify the current API first:

### Context7 (primary — live docs)
Use `resolve-library-id` → `get-library-docs` for:
| Library | Context7 ID | Use for |
|---|---|---|
| FastAPI | `/fastapi/fastapi` | Routes, middleware, dependencies |
| FastAPI (full docs) | `/websites/fastapi_tiangolo` | Advanced patterns, deployment |
| MediaPipe | `/google-ai-edge/mediapipe` | FaceMesh API, landmark indices |
| Supabase Python | `/websites/supabase_reference_python` | Client methods, auth, storage |
| Supabase Platform | `/supabase/supabase` | RLS, migrations, edge functions |
| Pydantic | resolve first | Model config, validators |
| OpenCV | resolve first | Image processing functions |

### Supabase MCP (direct access)
- Use `search_docs` for Supabase platform features, RLS, Auth, Storage
- Use `list_tables` / `execute_sql` to verify actual schema before writing queries

### n8n MCP (direct access)
- Use `search_nodes` / `get_node` for current node configs and versions
- Use `tools_documentation` for webhook and workflow patterns

### Vercel MCP (direct access)
- Use `search_vercel_documentation` for deployment and platform features

### Web Search (fallback)
- For anything not in Context7 or MCP tools, use WebSearch with current year (2026)

**When in doubt: look it up. A 5-second Context7 call prevents hours of debugging stale APIs.**

## Key Conventions

### Code Style
- Python 3.11+, type hints everywhere
- Pydantic models for all API input/output
- Core analyzers are **pure functions** — they take `FaceLandmarks` and return Pydantic models, no side effects
- Services handle I/O (database, HTTP)
- All measurements in mm where possible (estimated via face-width heuristic)

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- API routes: `/api/v1/...` (versioned)
- Supabase tables: `snake_case`

### Error Handling
- `QualityWarning` list in every response — never silently degrade
- HTTP 422 if no face detected
- HTTP 400 for bad input (missing file, corrupt image)
- HTTP 413 for oversized images
- Supabase/n8n failures are non-blocking (warning appended, analysis still returned)

### Testing
- Tests go in `tests/` mirroring `app/` structure
- Test files: `test_<module>.py`
- Use pytest; mock external services, never mock core analyzers

## External Services

### Supabase (AestheticBiometricsDB)
- **Project ID:** `mbwteypkehrmeqzdzdph`
- **Region:** eu-west-1
- **Tables:** `patients`, `biometric_analyses`, `treatment_sessions`
- **DO NOT** use NovaCoreDB (`ywdwvjriklaevktswnwe`) — that is a separate project

### n8n
- Webhook URL configured via `N8N_WEBHOOK_URL` env var
- Payload: flat JSON (full `AnalysisResponse` model)

### GitHub
- Repo: `JNassar77/aesthetic-biometrics-engine`
- Branch strategy: `main` (stable) → feature branches → PR

## Common Commands

```bash
# Download ML model (required, not in git)
curl -L -o models/face_landmarker.task \
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

# Local dev
uvicorn app.main:app --reload --port 8000

# Docker
docker build -t aesthetic-biometrics .
docker run -p 8000:8000 --env-file .env aesthetic-biometrics

# Test
pytest tests/ -v

# API docs
# → http://localhost:8000/docs (Swagger UI)
```

## Medical Analysis Reference

### Frontal (0°)
- **Symmetry:** Paired landmark deviations from median sagittal line
- **Facial thirds:** Trichion→Glabella / Glabella→Subnasale / Subnasale→Mentum (ideal 1:1:1)
- **Lip ratio:** Upper:Lower vermilion height (ideal 1:1.6)

### Profile (90°)
- **Ricketts E-line:** Nose tip to chin line; lips should sit behind it
- **Nasolabial angle:** Columella↔Subnasale↔Upper lip (ideal 90–105°)
- **Chin projection:** Pogonion position vs. subnasale vertical

### Oblique (45°)
- **Ogee curve:** S-curve from forehead through malar to buccal region; flattening = volume loss
