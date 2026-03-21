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
- [ ] V1-Code in `app/core/` als Legacy markieren (nicht loeschen) → verschoben auf Sprint 2

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
  - [ ] Buccal Corridor Analysis → verschoben auf Sprint 5 (abhaengig von Multi-View)
- [x] `analysis/aging_engine.py` — Neu:
  - [x] Blendshape-Muster → Muskeltonus-Profil
  - [x] Gravitationelle Veraenderungen (Landmark-Drift nach unten)
  - [x] Periorbitale Analyse (Crow's feet, unter-Lid Laxitaet)

### Sprint 5 — Multi-View Fusion + Zone Analyzer

- [ ] `analysis/multi_view_fusion.py` — Das Kernmodul:
  - [ ] Confidence-gewichtete Fusion wenn Zone in mehreren Views sichtbar
  - [ ] Widerspruechs-Erkennung zwischen Views
  - [ ] Finale Severity-Berechnung pro Zone
- [ ] `analysis/zone_analyzer.py` — Orchestriert alle Engines:
  - [ ] Mappt Engine-Ergebnisse auf Zonen
  - [ ] Erzeugt Zone-Reports mit Findings-Texten
  - [ ] Sortiert nach Severity
- [ ] Integration Tests: 3 Testbilder → vollstaendiger Zone-Report

---

## Phase 3: Treatment Intelligence (Sprint 6-7)

> **Ziel:** Aus Analyse wird Behandlungsplan. Das Alleinstellungsmerkmal.

### Sprint 6 — Behandlungsplan-Generator

- [ ] `treatment/product_database.py` — Filler/Botox Wissensbasis:
  - [ ] Produkt-Eigenschaften (G', Viskositaet, Haltbarkeit)
  - [ ] Zone-zu-Produkt Mapping
  - [ ] Technik-Empfehlungen pro Zone
  - [ ] Volumen-Schaetzungen
- [ ] `treatment/plan_generator.py` — Kernlogik:
  - [ ] Severity-basierte Priorisierung
  - [ ] Klinische Reihenfolge-Logik (Struktur → Detail)
  - [ ] Sitzungs-Planung (was in Session 1 vs. 2)
  - [ ] Gesamtvolumen-Schaetzung
- [ ] `treatment/contraindication_check.py` — Sicherheit:
  - [ ] Gefaessrisiko-Zonen markieren
  - [ ] Warnungen bei extremen Asymmetrien (moegliche Pathologie)

### Sprint 7 — Vergleichs-Engine (Before/After)

- [ ] `POST /api/v2/compare` Endpoint
- [ ] Delta-Berechnung pro Zone (pre vs. post Assessment)
- [ ] Verbesserungs-Score pro Zone
- [ ] Visualisierungsdaten fuer Frontend (Zone-Heatmap-Daten)

---

## Phase 4: API + Integration (Sprint 8-9)

> **Ziel:** Alles zusammenfuegen, neue Endpoints, Supabase V2.

### Sprint 8 — V2 API + Supabase Schema

- [ ] `api/v2_routes.py` — Neue Endpoints:
  - [ ] `POST /api/v2/assessment` (3 Bilder, 1 Response)
  - [ ] `POST /api/v2/compare` (Before/After)
  - [ ] `GET /api/v2/patients/{id}/history`
- [ ] Supabase Schema Migration V2:
  - [ ] `assessments` Tabelle (JSONB fuer Zonen + Plan)
  - [ ] `treatment_comparisons` Tabelle
  - [ ] Supabase Storage Bucket `patient-images` einrichten
- [ ] Pydantic V2 Schemas komplett neu (`models/schemas.py`, `models/zone_models.py`)
- [ ] `pipeline/orchestrator.py` — Verbindet alles:
  - [ ] 3 Bilder empfangen → Preprocessing → Detection → Analysis → Plan → Response

### Sprint 9 — n8n + Background Processing

- [ ] n8n Webhook Payload an V2-Schema anpassen
- [ ] FastAPI BackgroundTasks fuer Supabase-Speicherung
- [ ] Bilder in Supabase Storage hochladen (async, non-blocking)
- [ ] Error-Recovery: Teilanalyse zurueckgeben wenn 1 View fehlschlaegt
- [ ] Structured Logging (JSON) fuer alle Pipeline-Schritte
- [ ] `api/v1_routes.py` — Legacy-Endpoints beibehalten (backward compat)

---

## Phase 5: Validation + Hardening (Sprint 10-11)

> **Ziel:** Vertrauen in die Ergebnisse. Genauigkeit validieren.

### Sprint 10 — Test-Suite

- [ ] Unit Tests: Alle Analyse-Engines mit synthetischen Landmark-Daten
- [ ] Unit Tests: Zone-Definitionen (vollstaendige Abdeckung aller 16 Zonen)
- [ ] Unit Tests: Treatment Plan Generator (Priorisierung, Produkt-Matching)
- [ ] Integration Tests: Voller Pipeline-Durchlauf mit echten Testbildern
- [ ] Edge Cases: kein Gesicht, mehrere Gesichter, Teilverdeckung, Brille, Bart
- [ ] Blendshape-Tests: Ruhezustand vs. Ausdruck

### Sprint 11 — Klinische Validierung + Feintuning

- [ ] Messungen gegen klinische Referenzdaten validieren
- [ ] Iris-Kalibrierung mit physischem Referenzmassstab verifizieren
- [ ] Test mit diversen Demographien (Alter, Geschlecht, Ethnie)
- [ ] Behandlungsplan-Review durch klinischen Berater
- [ ] Severity-Schwellenwerte kalibrieren
- [ ] Performance-Benchmark: Ziel < 3s fuer 3-Bild-Assessment

---

## Phase 6: Deployment + Production (Sprint 12)

> **Ziel:** Live gehen.

### Sprint 12 — Production-Ready

- [ ] Docker Image optimieren (Multi-stage Build, < 1.5GB)
- [ ] Railway Deployment konfigurieren
- [ ] Health Monitoring (Healthcheck-Endpoint + Alerts)
- [ ] Rate Limiting + API Key Authentication
- [ ] CI/CD Pipeline (GitHub Actions: Test → Build → Deploy)
- [ ] `.env.production` Konfiguration
- [ ] Swagger/OpenAPI Docs finalisieren
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
