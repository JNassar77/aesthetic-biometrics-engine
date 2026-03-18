# Tasks — Aesthetic Biometrics Engine

> Living document. Update status as work progresses.
> Format: `- [x] Done` / `- [ ] Open` / `- [~] In Progress`

---

## Phase 1: Foundation (MVP)

### Core Engine
- [x] Project scaffolding (FastAPI, directory structure)
- [x] MediaPipe FaceMesh landmark detection (478 points)
- [x] Frontal analyzer (symmetry, facial thirds, lip ratio)
- [x] Profile analyzer (E-line, nasolabial angle, chin projection)
- [x] Oblique analyzer (Ogee curve, midface volume)
- [x] Image quality validator (blur, brightness, contrast, resolution)
- [x] Geometry utilities (distance, angle, px→mm conversion)
- [x] Pydantic request/response models

### Infrastructure
- [x] Supabase schema (patients, analyses, treatment_sessions)
- [x] GitHub repo (JNassar77/aesthetic-biometrics-engine)
- [x] Dockerfile
- [x] .env configuration
- [ ] docker-compose.yml for local dev
- [ ] CI/CD pipeline (GitHub Actions)

### Integration
- [x] Supabase service (save analysis, fetch image)
- [x] n8n webhook service (notify on completion)
- [ ] Supabase Storage integration (image upload/retrieval)

---

## Phase 2: Validation & Hardening

### Testing
- [ ] Unit tests for geometry utils
- [ ] Unit tests for frontal analyzer
- [ ] Unit tests for profile analyzer
- [ ] Unit tests for oblique analyzer
- [ ] Integration test: full analyze endpoint with sample images
- [ ] Edge case tests: no face, multiple faces, partial occlusion

### Accuracy
- [ ] Validate measurements against clinical reference data
- [ ] Calibrate px→mm conversion with known-distance marker
- [ ] Test with diverse patient demographics
- [ ] Compare MediaPipe vs dlib vs InsightFace accuracy

### Error Handling
- [ ] Graceful handling of rotated/tilted images
- [ ] Auto-detect view angle from landmarks (instead of requiring user input)
- [ ] Multi-face rejection with clear error message

---

## Phase 3: Advanced Features

### Analysis Enhancements
- [ ] Brow position analysis (brow ptosis detection)
- [ ] Jawline contour analysis (masseter, pre-jowl sulcus)
- [ ] Periorbital analysis (tear trough, lateral canthal lines)
- [ ] Skin texture analysis (pore size, wrinkle depth via OpenCV)
- [ ] Golden ratio overlay (Phi mask)

### Treatment Intelligence
- [ ] Treatment recommendation engine (rule-based first)
- [ ] Before/after comparison endpoint (delta analysis)
- [ ] Injection point mapping (SVG overlay generation)
- [ ] Dosage suggestion based on muscle mass estimation

### Platform
- [ ] Patient dashboard API endpoints (history, trends)
- [ ] Batch analysis endpoint (all 3 views in one call)
- [ ] PDF report generation
- [ ] Real-time video analysis (WebSocket endpoint)

---

## Phase 4: Deployment & Scale

### DevOps
- [ ] Railway deployment
- [ ] Health monitoring & alerting
- [ ] Rate limiting & API key auth
- [ ] Logging & observability (structured JSON logs)

### Performance
- [ ] Response time benchmarking (<500ms target)
- [ ] Image preprocessing pipeline (resize, normalize)
- [ ] Caching layer for repeated analyses
- [ ] GPU acceleration evaluation (ONNX Runtime)

---

## Backlog / Ideas

- [ ] 3D face reconstruction from multi-view images
- [ ] Aging simulation (predict treatment longevity)
- [ ] AR overlay for treatment visualization
- [ ] DICOM integration for clinical workflows
- [ ] Multi-language report output (DE/EN/AR)
- [ ] HIPAA/DSGVO compliance audit
