# Features — Aesthetic Biometrics Engine

> Complete feature catalog for the V2 engine (`POST /api/v2/assessment`, zone-based,
> engine v2.3.0). Each feature lists purpose, module, workflow/output and — where
> relevant — clinical relevance. The V1 single-image API (`/api/v1/analyze`) was
> removed (mediapipe 0.10.35 dropped the `mp.solutions` FaceMesh it ran on); its
> per-view analyses now live inside the V2 zone flow below.

---

## Core

### F-100: Multi-View Zone Assessment (up to 4 views)
**Module:** `app/pipeline/orchestrator.py` · **Endpoint:** `POST /api/v2/assessment`

One call takes frontal (0°) + profile (90°) + bilateral obliques (45°L/R) and returns
a 19-zone analysis with severity ranking, treatment plan, aesthetic score, calibration,
3D-reconstruction quality and overlay data.

**Workflow:** preprocess (EXIF, face-crop) → detect (478 landmarks + 52 blendshapes +
pose) → iris px→mm calibration → 3D reconstruction → engines (symmetry / proportion /
profile / volume / aging) → multi-view fusion → zone report + aesthetic score →
treatment plan → overlay. **Output:** `AssessmentResponse` (see `CONTRACTS.md`).

### F-101: Metric 3D Depth (multi-view reconstruction)
**Module:** `app/analysis/multiview_reconstruction.py`

Real anterior-posterior depth for the volume zones (ogee/malar, temporal, tear-trough,
jowl) via orthographic triangulation from frontal + bilateral obliques (profile excluded
— iris too foreshortened at 90°). Replaces meaningless relative-z pseudo-mm.

**Honesty:** depths stay `estimated` until thresholds are recalibrated against real 3D mm
(Sprint 11); the `reconstruction` block reports views_used / angular spread / reprojection
RMS. Validated on real photos (interpupillary 61.9 mm, reproj RMS 2.7 mm). `profile_engine`
deliberately stays 2D (sagittal gold standard; 3D was empirically worse there).
**Clinical relevance:** trustworthy volume-loss assessment requires bilateral obliques and
a true 90° profile (≥55° yaw, else the quality gate rejects it).

### F-102: Clinical PDF Report
**Module:** `app/services/pdf_report.py` · **Endpoints:** `POST /api/v2/report`,
`GET /api/v2/assessment/{id}/report`

Clinician-facing PDF per assessment — summary, global metrics, zones by severity, per-zone
measurements (estimated values flagged `†`), treatment plan + totals, contraindications,
honesty footer. reportlab (pure-Python, runs on the slim image). POST is lossless from an
`AssessmentResponse`; GET renders a stored assessment from Supabase.

### F-103: Frontend Overlay Data (injection points + heatmap)
**Module:** `app/analysis/overlay.py`

Per-zone injection-point coordinates + heatmap anchor (intensity = severity/10, severity
colour) in `AssessmentResponse.overlay`, normalized to the analyzed frame **with a
back-transform to the original upload** (`image_dimensions`: source size + crop rect).
Enables a UI to drop markers / render a treatment-need heatmap on the uploaded photo.
`canonical_oblique_view` names which physical oblique upload the canonical `oblique`
overlay maps to (`oblique_left` / `oblique_right` / `oblique`), so the UI paints the oblique
heatmap on the correct photo instead of guessing.

---

## Delivery & Frontend

### F-130: Secure engine proxy (Supabase Edge Function)
**Module:** `supabase/functions/engine-proxy/` (Deno) · **URL:** `…/functions/v1/engine-proxy`

Thin auth proxy so the browser never holds the engine `X-API-Key`. `verify_jwt` (callers send the
Supabase anon key); the tenant (`organization_id`) is injected **server-side** — the browser does
not choose it. Routes `POST /assessment` (multipart → engine), `POST /report`
(AssessmentResponse → PDF), `GET /health`; streams the engine response straight back. Secret
`ENGINE_API_KEY`; `ENGINE_URL` / `ENGINE_ORG_ID` / `ALLOWED_ORIGIN` optional (defaults in code).

### F-131: Aesthetic Scan frontend (guided capture → heatmap → PDF)
**Module:** `frontend/` (Vite + React + TS) · talks only to the engine-proxy

In-practice, tablet-first web app: Consent → guided 4-angle capture (live camera + per-shot
upload fallback; ≤1600 px, JPEG, un-mirrored) → review → results. Results render a per-zone
heatmap mapped back onto the **original** photo, aesthetic score, top zones, contraindications,
quality/calibration banners, and a one-click PDF. Maps the engine's canonical overlay views to
the physical uploads via `canonical_oblique_view` (safe fallback omits the oblique heatmap when
ambiguous rather than risk the wrong cheek). Verified end-to-end against the live proxy
(`frontend/scripts/smoke-proxy.mjs`). **Posture:** DEV/TEST — consenting subjects only; the
consent screen is the MVP minimum, not the full DSGVO Art. 9 flow (Gate 0).

### F-132: Live EU deployment (Hetzner + Caddy)
**Module:** `deploy/hetzner/` · **URL:** `https://biometrics.novasyn.de`

Engine runs as an isolated Docker service (`127.0.0.1:8003`) behind Caddy auto-TLS on the
novasyn.de box, alongside (not touching) the other services. The image downloads + SHA-verifies
the MediaPipe model at build time (build **fails on model drift** — provenance for a
medical-device artifact). Own EU infra for biometric data sovereignty (chosen over Railway;
`railway.toml` retained as an alternative). Persistence ON. Runbook + rollback in the module.

---

## Analysis Engines

### F-104: Symmetry & Proportion (frontal)
**Modules:** `app/analysis/symmetry_engine.py`, `app/analysis/proportion_engine.py`

6-axis bilateral symmetry (+ blendshape-based dynamic asymmetry, view-bound), facial
thirds, horizontal fifths, golden-ratio deviation, lip ratio with Cupid's-bow analysis.
Feeds the frontal-primary zones and the global metrics.

| Measurement | Ideal | Clinical action if deviated |
|---|---|---|
| Symmetry score | >90 | Asymmetric Botox dosing, targeted filler |
| Facial thirds | 1:1:1 | Lower third short → chin filler; middle third flat → cheek filler |
| Lip ratio | 1:1.6 | Upper lip thin → lip filler augmentation |

### F-105: Profile Analysis (90°)
**Module:** `app/analysis/profile_engine.py`

Ricketts E-line, nasolabial + nasofrontal angle, chin projection, nasal dorsum
(hump/saddle), Steiner line, cervicomental angle. In-plane 2D from the dedicated profile
photo (the sagittal gold standard — intentionally NOT derived from 3D). Out-of-plane
values stay `estimated`.

| Measurement | Ideal | Clinical action if deviated |
|---|---|---|
| E-line upper lip | -4mm | Protruded → assess lip reduction; retruded → lip filler |
| E-line lower lip | -2mm | Same principle as upper |
| Nasolabial angle | 90–105° | Acute → rhinoplasty consideration; obtuse → over-rotated tip |
| Chin projection | ±5mm of subnasale | Retruded → chin filler/implant; prominent → assess jaw |

### F-106: Volume Analysis (oblique + 3D)
**Module:** `app/analysis/volume_engine.py`

Ogee curve, temporal hollowing, tear-trough depth, pre-jowl sulcus, buccal corridor.
Depth comes from the F-101 reconstruction when available (negated to the engine
convention), else falls back to single-view relative z; `depth_source` records which.
All depth values flagged `estimated`.

| Measurement | Ideal | Clinical action if deviated |
|---|---|---|
| Ogee curve score | >70 | <40: significant volume loss → deep-plane filler (Voluma/Radiesse) |
| Temporal / tear-trough / jowl depth | low | hollowing → targeted volumization (values estimated) |

### F-107: Aging Analysis
**Module:** `app/analysis/aging_engine.py`

Blendshape-derived muscle-tonus profile (frontalis, corrugator), gravitational drift
(brow/malar/jowl descent), periorbital analysis (crow's feet, lower-lid laxity). Drives
neurotoxin indications and descent-related zones.

### F-108: Multi-View Fusion
**Module:** `app/analysis/multi_view_fusion.py`

Confidence-weighted fusion of landmark-geometry measurements when a zone is seen in more
than one view, with contradiction detection. **Blendshapes are never fused** (expression
is view-bound). Produces the final per-zone severity inputs.

### F-109: Image Quality + Pose + Expression Gate
**Module:** `app/pipeline/quality_gate.py`

Pre-screens each view; warnings are **non-blocking** (returned in `image_quality`), hard
pose violations reject a view.

| Check | Threshold | Warning code |
|---|---|---|
| Resolution | <640×480 | `LOW_RESOLUTION` |
| Brightness | <50 / >220 mean | `UNDEREXPOSED` / `OVEREXPOSED` |
| Contrast | <30 std | `LOW_CONTRAST` |
| Sharpness | <50 Laplacian var | `BLURRY` |
| Head pose | outside view range / beyond hard limit | `HEAD_NOT_*` / `POSE_REJECTED` |
| Neutral expression (frontal) | active blendshapes | `NON_NEUTRAL_EXPRESSION` |

Calibration reliability gate: without a confident iris calibration, ALL mm values are
flagged `estimated` + a `CALIBRATION_UNRELIABLE` assessment warning is added.

---

## Treatment Intelligence

### F-110: Treatment Plan Generator
**Module:** `app/treatment/plan_generator.py` (+ `product_database.py`, `zone_definitions.py`)

Turns the ranked zones into a plan: severity-based prioritization, clinical ordering
(structure → detail), session planning, filler-volume + neurotoxin-unit estimates, product
recommendations (14 products), vascular-risk flags. In `AssessmentResponse.treatment_plan`.

### F-111: Contraindication / Safety Check
**Module:** `app/treatment/contraindication_check.py`

Flags extreme asymmetry (possible pathology), vascular-risk zones, tear-trough specials,
overtreatment risk, glabella/forehead dependency. Returned as `contraindications` with
severity (WARNING/CAUTION/REFERRAL/CONTRAINDICATED).

### F-112: Before/After Comparison
**Module:** `app/analysis/comparison_engine.py` · **Endpoint:** `POST /api/v2/compare`

Per-zone deltas, region-weighted improvement score, measurement-level deltas vs ideal
ranges, status classification (improved/worsened/unchanged/resolved/new) and a heatmap.

---

## Integration

### F-113: Supabase Persistence (V2)
**Module:** `app/services/supabase_service.py`

Async (non-blocking) persistence when an `organization_id` is provided: `assessments`
(JSONB analysis + plan), `treatment_comparisons`, image upload to the `patient-images`
storage bucket. Multi-tenant (org-scoped RLS). `GET /api/v2/patients/{id}/history` reads
the timeline. Project: AestheticBiometricsDB (mbwteypkehrmeqzdzdph, eu-west-1).

### F-114: n8n Webhook (V2)
**Module:** `app/services/n8n_service.py`

`notify_n8n_v2` posts an envelope (`event`, `engine_version`, `assessment_id`,
`aesthetic_score`, `zones_count`, `views_analyzed`, full `data`) to `N8N_WEBHOOK_URL`.
Fire-and-forget — never blocks the API response.

---

## Planned / Future

| ID | Feature | Status |
|---|---|---|
| F-008 | Before/after delta analysis | ✅ Done (F-112) |
| F-009 | Treatment recommendation engine | ✅ Done (F-110) |
| F-011 | Injection point mapping | ✅ Done — coordinate data (F-103) |
| F-014 | Periorbital analysis | ✅ Done (F-107) |
| F-015 | PDF report generation | ✅ Done (F-102) |
| F-019 | 3D face reconstruction | ✅ Done (F-101) |
| — | Patient/practice upload frontend | 🔜 Planned (in-practice web app MVP; design TBD) |
| — | Clinical 3D depth-threshold calibration | 🔜 Sprint 11 (needs caliper ground-truth) |
| F-007 | Auto view-angle detection | Backlog |
| F-010 | Batch multi-view analysis | Backlog |
| F-016 | Skin texture analysis | Backlog |
| F-017 | Golden ratio (Phi) overlay | Backlog |
| F-018 | Real-time video analysis (WebSocket) | Backlog |
| — | Multi-language reports (DE/EN/AR) | Backlog |
