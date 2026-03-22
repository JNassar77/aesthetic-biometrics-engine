# Tasks — Aesthetic Biometrics Engine V2

> Living document. Update status as work progresses.
> Format: `- [x] Done` / `- [ ] Open` / `- [~] In Progress`
> Referenz-Architektur: `docs/ARCHITECTURE_V2.md`

---

## V1 Baseline (abgeschlossen)

- [x] Project scaffolding (FastAPI, directory structure)
- [x] MediaPipe Legacy FaceMesh (478 points)
- [x] Frontal/Profile/Oblique Einzelanalysen
- [x] Supabase Schema V1, GitHub Repo, Dockerfile, Docs

---

## Phase 1: Detection Layer Upgrade (Sprint 1-2)

> **Ziel:** Neue MediaPipe Tasks API, Iris-Kalibrierung, solide Bildvorverarbeitung.
> Das Fundament, auf dem alles aufbaut.

### Sprint 1 — MediaPipe Tasks API + Preprocessing ✅ (18.03.2026)

- [x] MediaPipe Face Landmarker `.task` Model herunterladen und einbinden
- [x] `detection/face_landmarker.py` — Neuer Wrapper mit Tasks API
  - [x] 478 Landmarks + 52 Blendshapes + Transformation Matrix
  - [x] Confidence-Scoring aus der neuen API
- [x] `detection/head_pose.py` — Yaw/Pitch/Roll aus Transformation Matrix
- [x] `detection/landmark_index.py` — Vollstaendige 478-Punkt-Referenz mit anatomischen Gruppierungen
- [x] `pipeline/image_preprocessor.py` — EXIF-Rotation, Resize, Face-Crop (Lens Distortion Fix)
- [x] `pipeline/quality_gate.py` — Erweiterte Qualitaetskontrolle + Neutral-Expression-Check
- [x] V1-Code in `app/core/` als Legacy markieren (Deprecation-Docstrings hinzugefuegt)

### Sprint 2 — Iris-Kalibrierung + Geometrie-Upgrade ✅ (21.03.2026)

- [x] `utils/pixel_calibration.py` — Iris-basierte px→mm Kalibrierung (11.7mm Referenz)
- [x] `utils/geometry.py` — Erweitert um 3D-Operationen (nutzt z-Koordinaten)
- [x] Unit Tests fuer Kalibrierung und Geometrie
- [x] Benchmark: Kalibrierungs-Genauigkeit vs. V1-Schaetzung mit Testbildern
- [x] Head-Pose-Validation: Bild ablehnen wenn Kopf zu stark gedreht

---

## Phase 2: Zone-System + Analyse-Engines (Sprint 3-5)

> **Ziel:** Das medizinische Herzstaeck — 16 Behandlungszonen mit Severity-Scoring.

### Sprint 3 — Zone-Definitionen + Symmetrie/Proportionen ✅ (21.03.2026)

- [x] `treatment/zone_definitions.py` — 19 Zonen mit:
  - [x] Landmark-Zuordnungen (welche Landmarks gehoeren zu welcher Zone)
  - [x] Referenzwerte (Ideal-Ranges pro Messung)
  - [x] View-Prioritaeten (welche View ist primaer fuer welche Zone)
- [x] `models/zone_models.py` — Zone Pydantic Models
- [x] `analysis/symmetry_engine.py` — Neu:
  - [x] 6 Symmetrie-Achsen (nicht nur Mittellinie)
  - [x] Pro-Zone Asymmetrie-Score
  - [x] Blendshape-basierte dynamische Asymmetrie
- [x] `analysis/proportion_engine.py` — Neu:
  - [x] Gesichtsdrittel (mit mm statt px)
  - [x] Fifths-Analyse (horizontale Fuenftel)
  - [x] Golden Ratio Deviation
  - [x] Lip Ratio mit Cupid's-Bow-Analyse

### Sprint 4 — Profil-, Volumen- und Aging-Engines ✅ (21.03.2026)

- [x] `analysis/profile_engine.py` — Erweitert:
  - [x] Ricketts E-Line (jetzt in echten mm via Iris-Kalibrierung)
  - [x] Nasolabial-Winkel
  - [x] Chin Projection
  - [x] **Neu:** Nasal dorsum analysis (Hump/Saddle)
  - [x] **Neu:** Lip projection relative to Steiner line
  - [x] **Neu:** Chin-neck angle (cervicomental)
- [x] `analysis/volume_engine.py` — Neu:
  - [x] Ogee Curve (verbessert mit 3D-Depth-Daten)
  - [x] Temporal Hollowing Detection
  - [x] Tear Trough Depth Estimation
  - [x] Pre-jowl Sulcus Detection
  - [x] Buccal Corridor Analysis (in volume_engine.py, mouth_corner + cheekbone Landmarks)
- [x] `analysis/aging_engine.py` — Neu:
  - [x] Blendshape-Muster → Muskeltonus-Profil
  - [x] Gravitationelle Veraenderungen (Landmark-Drift nach unten)
  - [x] Periorbitale Analyse (Crow's feet, unter-Lid Laxitaet)

### Sprint 5 — Multi-View Fusion + Zone Analyzer ✅ (21.03.2026)

- [x] `analysis/multi_view_fusion.py` — Das Kernmodul:
  - [x] Confidence-gewichtete Fusion wenn Zone in mehreren Views sichtbar
  - [x] Widerspruechs-Erkennung zwischen Views
  - [x] Finale Severity-Berechnung pro Zone
- [x] `analysis/zone_analyzer.py` — Orchestriert alle Engines:
  - [x] Mappt Engine-Ergebnisse auf Zonen
  - [x] Erzeugt Zone-Reports mit Findings-Texten
  - [x] Sortiert nach Severity
  - [x] Aesthetic Score (Composite KPI, 0-100)
- [x] `pipeline/quality_gate.py` — Neutral-Expression Deviation Score hinzugefuegt
- [x] Integration Tests: 54 neue Tests (224 total), alle gruen

---

## Phase 3: Treatment Intelligence (Sprint 6-7)

> **Ziel:** Aus Analyse wird Behandlungsplan. Das Alleinstellungsmerkmal.

### Sprint 6 — Behandlungsplan-Generator ✅ (21.03.2026)

- [x] `treatment/product_database.py` — Filler/Botox Wissensbasis:
  - [x] Produkt-Eigenschaften (G', Viskositaet, Haltbarkeit) — 14 Produkte
  - [x] Zone-zu-Produkt Mapping — 17 Zonen mit Empfehlungen
  - [x] Technik-Empfehlungen pro Zone
  - [x] Volumen-Schaetzungen
  - [x] Neurotoxin-Indikationen (3 Zonen)
  - [x] Vaskulaere Risiko-Zonen (8 Zonen)
  - [x] Strukturelle Priorisierung (alle 19 Zonen)
- [x] `treatment/plan_generator.py` — Kernlogik:
  - [x] Severity-basierte Priorisierung
  - [x] Klinische Reihenfolge-Logik (Struktur → Detail)
  - [x] Sitzungs-Planung (was in Session 1 vs. 2)
  - [x] Gesamtvolumen-Schaetzung
  - [x] Composite Priority Score (severity × 2 + structural weight)
- [x] `treatment/contraindication_check.py` — Sicherheit:
  - [x] Gefaessrisiko-Zonen markieren
  - [x] Warnungen bei extremen Asymmetrien (moegliche Pathologie)
  - [x] Tear-Trough-Spezialwarnung
  - [x] Ueberbehandlungs-Risiko
  - [x] Glabella/Forehead-Abhaengigkeit

### Sprint 7 — Vergleichs-Engine (Before/After) ✅ (21.03.2026)

- [x] `analysis/comparison_engine.py` — Kernmodul:
  - [x] Delta-Berechnung pro Zone (pre vs. post Assessment)
  - [x] Verbesserungs-Score pro Zone (0-100, gewichtet nach Region)
  - [x] Measurement-level Deltas mit Ideal-Range-Vergleich
  - [x] Visualisierungsdaten fuer Frontend (Zone-Heatmap-Daten mit Farb-Codes)
  - [x] Status-Klassifikation (improved/worsened/unchanged/resolved/new)
  - [x] Summary-Textgenerierung
- [ ] `POST /api/v2/compare` Endpoint → Sprint 8
- [ ] Supabase `treatment_comparisons` Migration → Sprint 8

---

## Phase 4: API + Integration (Sprint 8-9)

> **Ziel:** Alles zusammenfuegen, neue Endpoints, Supabase V2.

### Sprint 8 — V2 API + Supabase Schema ✅ (22.03.2026)

- [x] `models/schemas_v2.py` — Pydantic V2 Schemas komplett neu:
  - [x] AssessmentResponse, ComparisonResponse, TreatmentPlanResponse
  - [x] Zone/Finding/Measurement response models
  - [x] PatientHistoryResponse, HealthResponse
- [x] `api/v2_routes.py` — Neue Endpoints:
  - [x] `POST /api/v2/assessment` (3 Bilder, 1 Response)
  - [x] `POST /api/v2/compare` (Before/After, Supabase-Integration Sprint 9)
  - [x] `GET /api/v2/patients/{id}/history` (Supabase-Integration Sprint 9)
  - [x] `GET /api/v2/health`
- [x] `pipeline/orchestrator.py` — Verbindet alles:
  - [x] 3 Bilder empfangen → Preprocessing → Detection → Analysis → Plan → Response
  - [x] Partial-Failure Handling (nur akzeptierte Views werden analysiert)
  - [x] Treatment plan failure non-blocking (Zone Report bleibt verfuegbar)
- [x] Supabase Schema Migration V2:
  - [x] `organizations` Tabelle (Multi-Tenant Root)
  - [x] `assessments` Tabelle (JSONB fuer Zonen + Plan)
  - [x] `treatment_comparisons` Tabelle
  - [x] `patients.organization_id` Spalte hinzugefuegt
  - [x] Indexes fuer org, patient, date
- [x] Multi-Tenant RLS Policies:
  - [x] Org-Isolation auf allen V2-Tabellen
  - [x] Service-Role Bypass fuer API-Backend
  - [x] V1 Legacy-Policies gefixt (kein USING(true) mehr)
- [x] Supabase Storage Bucket `patient-images` eingerichtet:
  - [x] 10MB Limit, JPEG/PNG/WebP
  - [x] Org-scoped RLS auf Storage-Objects
- [x] `main.py` aktualisiert: V1 + V2 Router, Version 2.0.0
- [x] 47 neue Tests (381 total), alle gruen

### Sprint 9 — n8n + Async + Legacy Compat ✅ (22.03.2026)

- [x] `services/n8n_service.py` — V2-Payload mit Envelope (event, assessment_id, aesthetic_score)
- [x] `services/supabase_service.py` — V2: save_assessment, get_assessment, get_patient_history, upload_image, save_comparison
- [x] `api/v2_routes.py` — BackgroundTasks fuer async Supabase + Storage
- [x] `api/v2_routes.py` — /compare: Supabase-Read → ZoneReport-Rekonstruktion → compare()
- [x] `api/v2_routes.py` — /history: Supabase-Query → AssessmentSummary-Liste
- [x] `utils/logging.py` — Structured JSON Logging mit JSONFormatter + log_step context manager
- [x] `api/routes.py` → `api/v1_routes.py` umbenannt (backward compat bleibt)
- [x] 24 neue Tests (405 total): test_n8n_service, test_supabase_service, test_logging

---

## Phase 5: Validation + Hardening (Sprint 10-11)

> **Ziel:** Vertrauen in die Ergebnisse. Genauigkeit validieren.

### Sprint 10 — Test-Suite + Reorganisierung ✅ (22.03.2026)

- [x] Tests reorganisiert: `tests/` flach → Unterverzeichnisse:
  - [x] `tests/analysis/` ← Symmetrie, Proportionen, Engines, Fusion, ZoneAnalyzer, Comparison, **Blendshapes (NEU)**
  - [x] `tests/treatment/` ← Zone-Definitionen, Produkt-DB, Kontraindikationen, Plan-Generator
  - [x] `tests/integration/` ← Orchestrator, V2-Routes, Schemas
  - [x] `tests/services/` ← n8n, Supabase, Logging
  - [x] `tests/edge_cases/` ← **NEU:** Kein Gesicht, korrupte Bilder, Partial Views, Iris-Occlusion
  - [x] `tests/fixtures/` ← **NEU:** Synthetische Landmark-Daten (symmetric, asymmetric, aged, blendshapes)
- [x] `tests/fixtures/synthetic.py` — Factory-Funktionen:
  - [x] `make_symmetric_face()` — perfekt symmetrisch, 478 Punkte + Iris
  - [x] `make_asymmetric_face()` — bewusst asymmetrisch (Brow, Cheekbone, Mouth)
  - [x] `make_aged_face()` — gravitationelle Drift, vertiefte Traenentaeler
  - [x] `make_blendshapes(neutral/aging/expression)` — 52 Koeffizienten
  - [x] `make_calibration()` — Standard-CalibrationResult
- [x] Edge Case Tests (12 Tests): korrupte Bytes, kein Gesicht, partielle Views, Pipeline-Level
- [x] Partial Detection Tests (7 Tests): Iris-Occlusion, extreme Pose, Boundary-Werte
- [x] Blendshape Tests (15 Tests): Neutral vs. Expression, dynamische Asymmetrie, Aging-Muster
- [x] Coverage: 80% (439 Tests, alle gruen)

### Sprint 11 — Klinische Validierung + Feintuning

- [ ] Messungen gegen klinische Referenzdaten validieren
- [ ] Iris-Kalibrierung mit physischem Referenzmassstab verifizieren
- [ ] Test mit diversen Demographien (Alter, Geschlecht, Ethnie)
- [ ] Behandlungsplan-Review durch klinischen Berater
- [ ] Severity-Schwellenwerte kalibrieren
- [x] Performance-Benchmark: < 3s fuer 3-Bild-Assessment (tests/test_benchmark_performance.py, avg < 1ms)

---

## Phase 6: Deployment + Production (Sprint 12)

> **Ziel:** Live gehen.

### Sprint 12 — Production-Ready

- [x] Docker Image optimieren (Multi-stage Build)
- [ ] Railway Deployment konfigurieren
- [x] Health Monitoring (V2 /health mit DB-Check, Model-Check, Uptime)
- [x] Rate Limiting (`app/api/rate_limit.py`, sliding window, RATE_LIMIT_RPM)
- [x] API Key Authentication (`app/api/auth.py`, X-API-Key, API_KEYS env var)
- [x] CI/CD Pipeline (`.github/workflows/ci.yml`: pytest + Docker build)
- [ ] `.env.production` Konfiguration
- [x] Swagger/OpenAPI Docs finalisieren (Tags, Descriptions, Examples, Version 2.1.0)
- [ ] DSGVO-Checkliste (Patientendaten, Bildloeschung)

---

## Backlog / Future

- [ ] PDF/DOCX Report-Generation pro Assessment
- [ ] Injection-Point SVG Overlay fuer Frontend
- [ ] Real-time Video-Analyse (WebSocket)
- [ ] 3D Face Reconstruction aus Multi-View
- [ ] Aging Simulation (Behandlungshaltbarkeit)
- [ ] AR Overlay fuer Behandlungsvisualisierung
- [ ] Multi-Language Reports (DE/EN/AR)
- [ ] DICOM-Integration
- [ ] HIPAA/DSGVO Compliance Audit
- [ ] GPU-Beschleunigung (ONNX Runtime)
- [ ] Auto-View-Angle Detection
- [ ] Patient Self-Service Upload Portal
