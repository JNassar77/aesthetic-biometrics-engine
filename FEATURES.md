# Features — Aesthetic Biometrics Engine

> Complete feature catalog. Each feature includes its purpose, workflow, inputs/outputs, and current status.

---

## F-001: Frontal Face Analysis (0°)

**Status:** Implemented
**Module:** `app/core/frontal_analyzer.py`
**Endpoint:** `POST /api/v1/analyze?view_angle=frontal`

### Purpose
Analyze a frontal photograph for symmetry deviations, facial proportions, and lip balance. Primary use case: treatment planning for Botox (brow lift, masseter) and lip fillers.

### Workflow
1. Receive frontal image via upload or Supabase URL
2. Detect 478 facial landmarks via MediaPipe FaceMesh
3. Establish median sagittal line through midline landmarks (glabella, subnasale, mentum)
4. Compute three sub-analyses:
   - **Symmetry check:** Compare distances of 6 paired landmark groups from the midline
   - **Facial thirds:** Measure vertical proportions (upper / middle / lower face)
   - **Lip ratio:** Measure upper vs. lower vermilion height at midline

### Output
```json
{
  "symmetry": {
    "horizontal_deviation_mm": 1.2,
    "vertical_deviation_mm": 0.8,
    "symmetry_score": 92.5
  },
  "facial_thirds": {
    "upper_third_ratio": 0.31,
    "middle_third_ratio": 0.34,
    "lower_third_ratio": 0.35,
    "deviation_from_ideal": 2.1
  },
  "lip_analysis": {
    "upper_lip_height_px": 18.3,
    "lower_lip_height_px": 29.1,
    "ratio": 0.629,
    "deviation_from_ideal": 0.6
  }
}
```

### Clinical Relevance
| Measurement | Ideal | Clinical Action if Deviated |
|---|---|---|
| Symmetry score | >90 | Asymmetric Botox dosing, targeted filler |
| Facial thirds | 1:1:1 | Lower third short → chin filler; middle third flat → cheek filler |
| Lip ratio | 1:1.6 | Upper lip thin → lip filler augmentation |

---

## F-002: Profile Analysis (90°)

**Status:** Implemented
**Module:** `app/core/profile_analyzer.py`
**Endpoint:** `POST /api/v1/analyze?view_angle=profile`

### Purpose
Evaluate lateral facial harmony using established cephalometric reference lines. Primary use case: chin augmentation planning, rhinoplasty assessment, lip projection evaluation.

### Workflow
1. Receive profile image
2. Detect landmarks
3. Compute three sub-analyses:
   - **Ricketts E-line:** Line from nose tip to chin tip; measure lip distances
   - **Nasolabial angle:** Angle at subnasale between nose and upper lip vectors
   - **Chin projection:** Pogonion position relative to subnasale vertical

### Output
```json
{
  "e_line": {
    "upper_lip_to_eline_mm": -3.2,
    "lower_lip_to_eline_mm": -1.8,
    "assessment": "ideal"
  },
  "nasolabial_angle": {
    "angle_degrees": 97.3,
    "ideal_min": 90.0,
    "ideal_max": 105.0,
    "assessment": "within ideal range"
  },
  "chin_projection": {
    "pogonion_offset_mm": -2.1,
    "assessment": "well-projected"
  }
}
```

### Clinical Relevance
| Measurement | Ideal | Clinical Action if Deviated |
|---|---|---|
| E-line upper lip | -4mm | Protruded → assess lip reduction; retruded → lip filler |
| E-line lower lip | -2mm | Same principle as upper |
| Nasolabial angle | 90–105° | Acute → rhinoplasty consideration; obtuse → over-rotated tip |
| Chin projection | ±5mm of subnasale | Retruded → chin filler/implant; prominent → assess jaw |

---

## F-003: Oblique Analysis (45°)

**Status:** Implemented
**Module:** `app/core/oblique_analyzer.py`
**Endpoint:** `POST /api/v1/analyze?view_angle=oblique`

### Purpose
Assess the Ogee curve (S-shaped malar convexity) to identify midface volume loss. Primary use case: cheek filler and midface rejuvenation planning.

### Workflow
1. Receive oblique image
2. Detect landmarks
3. Determine which side of the face is more visible
4. Trace ogee path: glabella → malar high → cheekbone → malar low → mouth corner
5. Compute curvature deviation from the chord line

### Output
```json
{
  "ogee_curve": {
    "curve_score": 72.5,
    "midface_volume_assessment": "adequate",
    "malar_prominence_ratio": 0.82
  }
}
```

### Clinical Relevance
| Measurement | Ideal | Clinical Action if Deviated |
|---|---|---|
| Curve score | >70 | <40: significant volume loss → deep-plane filler (Voluma/Radiesse) |
| Malar prominence | >0.75 | Low ratio → malar augmentation with filler or implant |

---

## F-004: Image Quality Validation

**Status:** Implemented
**Module:** `app/core/image_validator.py`

### Purpose
Pre-screen images before analysis to warn about conditions that reduce measurement accuracy.

### Checks
| Check | Threshold | Warning Code |
|---|---|---|
| Resolution | <640x480 | `LOW_RESOLUTION` |
| Brightness | <50/255 mean | `UNDEREXPOSED` |
| Brightness | >220/255 mean | `OVEREXPOSED` |
| Contrast | <30 std dev | `LOW_CONTRAST` |
| Sharpness | <50 Laplacian var | `BLURRY` |
| Face confidence | <0.7 | `LOW_CONFIDENCE` |

### Behavior
Warnings are **non-blocking** — analysis proceeds but warnings are included in the response. The client/agent decides whether to accept or re-capture.

---

## F-005: Supabase Persistence

**Status:** Implemented
**Module:** `app/services/supabase_service.py`

### Purpose
Store analysis results linked to patient profiles for longitudinal tracking (before/after comparisons).

### Workflow
1. If `patient_id` is provided in the request, save the full result JSON to `biometric_analyses`
2. If save fails, append `STORAGE_ERROR` warning — analysis still returns
3. Treatment sessions link pre- and post-treatment analyses for delta tracking

### Tables
- `patients` — patient demographics
- `biometric_analyses` — individual view results (JSONB)
- `treatment_sessions` — groups pre/post analyses per treatment

---

## F-006: n8n Webhook Notification

**Status:** Implemented
**Module:** `app/services/n8n_service.py`

### Purpose
Push analysis results to n8n for downstream AI agent processing (report generation, scheduling, notifications).

### Workflow
1. After analysis completes, POST full response JSON to configured webhook URL
2. Fire-and-forget: failure does not block the API response
3. n8n can trigger follow-up workflows (e.g., generate PDF report, notify practitioner)

### Expected n8n Workflow
```
Webhook Trigger → Parse JSON → Conditional Logic →
  ├── Generate Treatment Report
  ├── Update Patient Dashboard
  ├── Send Notification to Practitioner
  └── Schedule Follow-up Analysis
```

---

## Planned Features

| ID | Feature | Priority | Phase |
|---|---|---|---|
| F-007 | Auto view-angle detection | High | 2 |
| F-008 | Before/after delta analysis | High | 3 |
| F-009 | Treatment recommendation engine | High | 3 |
| F-010 | Batch multi-view analysis | Medium | 3 |
| F-011 | Injection point mapping (SVG) | Medium | 3 |
| F-012 | Brow ptosis detection | Medium | 3 |
| F-013 | Jawline contour analysis | Medium | 3 |
| F-014 | Periorbital analysis | Medium | 3 |
| F-015 | PDF report generation | Medium | 3 |
| F-016 | Skin texture analysis | Low | 3 |
| F-017 | Golden ratio (Phi) overlay | Low | 3 |
| F-018 | Real-time video analysis | Low | 4 |
| F-019 | 3D face reconstruction | Low | Backlog |
