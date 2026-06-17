# API Contracts — Aesthetic Biometrics Engine (V2)

> Single source of truth for the V2 API interfaces, request/response schemas, and
> integration contracts. The V1 single-image `/api/v1/analyze` API was removed
> (mediapipe 0.10.35 dropped the `mp.solutions` FaceMesh API it ran on). Source of
> truth in code: `app/models/schemas_v2.py` + `app/api/v2_routes.py`.

---

## Base URL

```
Production:  https://<railway-domain>/api/v2
Local:       http://localhost:8000/api/v2
```

## Authentication

All endpoints except `/health` require an API key.

| Header | Value |
|---|---|
| `X-API-Key` | one of the comma-separated keys in `API_KEYS` |

- If `API_KEYS` is empty **and** `ENVIRONMENT != production` → auth is bypassed (dev mode).
- If `API_KEYS` is empty **and** `ENVIRONMENT == production` → `503` (fail closed; the
  biometric endpoints are never served unauthenticated in production).
- Missing key → `401`. Invalid key → `403`.

---

## Endpoints

### POST `/assessment`

Run a complete facial assessment. Preferred protocol is four images (frontal 0°,
45° left, 45° right, 90° profile): the bilateral obliques drive the metric 3D
reconstruction, the profile carries the 2D sagittal profile lines. At least one
image is required.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `frontal` | file | one of these | Frontal (0°) image (JPEG/PNG/WebP/HEIC) |
| `profile` | file | — | Profile (90°) image |
| `oblique` | file | — | Generic oblique (45°) image (back-compat) |
| `oblique_left` | file | — | Left 45° oblique |
| `oblique_right` | file | — | Right 45° oblique |
| `patient_id` | form string | No | UUID — set on the response |
| `organization_id` | form string | No | UUID — enables async Supabase persistence |

**Response — `200 OK`** → `AssessmentResponse` (see schema below).

#### Error Responses

| Status | Condition |
|---|---|
| `400` | No image provided, or malformed `patient_id` / `organization_id` |
| `413` | An image exceeds `MAX_IMAGE_SIZE_MB` |
| `422` | No face detected in any view, or analysis failed |
| `401` / `403` | Missing / invalid API key |

---

### POST `/report`

Render a clinical PDF from an assessment. Lossless and independent of Supabase —
post the `AssessmentResponse` you got from `/assessment`.

**Request:** body = `AssessmentResponse` JSON.
**Response — `200 OK`:** `application/pdf` (inline; zones, severity, plan, per-zone
measurements with `estimated` flagging, contraindications, honesty footer).

### GET `/assessment/{assessment_id}/report`

Render the clinical PDF for a stored assessment (fetched from Supabase, best-effort:
per-measurement `estimated` flags are preserved; full calibration/reconstruction are
not stored as columns — use `POST /report` for a lossless report).

| Status | Condition |
|---|---|
| `200` | `application/pdf` |
| `404` | Assessment not found |
| `503` | Supabase not configured |

---

### POST `/compare`

Before/After comparison of two stored assessments.

**Request** → `CompareRequest`:
```jsonc
{
  "pre_assessment_id": "uuid",
  "post_assessment_id": "uuid",
  "treatment_date": "2026-06-17",     // optional
  "treatment_notes": "..."            // optional
}
```
**Response — `200 OK`** → `ComparisonResponse` (per-zone deltas, improvement score,
zone status counts, heatmap). `404` if either assessment is missing; `503` without Supabase.

### GET `/patients/{patient_id}/history`

**Response — `200 OK`** → `PatientHistoryResponse` (assessment summaries, newest first).
`503` without Supabase.

### GET `/health`

**Response — `200 OK`** → `HealthResponse`:
```json
{"status": "healthy", "version": "2.2.0", "model_loaded": true,
 "supabase_connected": false, "uptime_seconds": 12.3}
```
`status` is `degraded` if the model file is missing. No auth.

---

## AssessmentResponse Schema

```jsonc
{
  "assessment_id": "uuid",
  "patient_id": "uuid|null",
  "timestamp": "2026-06-17T16:29:00Z",

  "image_quality": {                       // per provided view
    "frontal":  {"accepted": true, "confidence": 0.95, "warnings": [ /* QualityWarning */ ]},
    "profile":  { ... }, "oblique": { ... },
    "oblique_left": { ... }, "oblique_right": { ... }   // present only if provided
  },

  "global_metrics": {
    "symmetry_index": 88.5,                // 0–100
    "facial_thirds": {"upper": 0.33, "middle": 0.34, "lower": 0.33},
    "golden_ratio_deviation": 4.2,         // %
    "lip_ratio": 1.5,                      // upper:lower, nullable
    "head_pose": {"yaw": -1.2, "pitch": 4.8, "roll": 0.5}   // nullable
  },

  "zones": [                               // ranked by severity (desc)
    {
      "zone_id": "Tt1", "zone_name": "Tear Trough", "region": "midface",
      "severity": 6.5,                     // 0–10
      "primary_view": "frontal", "confirmed_by": ["oblique"],
      "calibration_method": "iris",
      "findings": [
        {"description": "...", "severity_contribution": 6.5, "source_view": "frontal"}
      ],
      "measurements": [
        {
          "name": "tear_trough_depth_left", "value": 3.2, "unit": "mm",
          "estimated": true,               // TRUE = NOT a validated metric value
          "ideal_min": 0.0, "ideal_max": 1.0, "deviation_pct": 220.0
        }
      ]
    }
  ],
  "aesthetic_score": 82.0,                 // 0–100 (100 = no treatment need)

  "treatment_plan": {
    "primary_concerns": [ /* TreatmentConcern */ ],
    "secondary_concerns": [ ... ],
    "contraindications": [
      {"severity": "CAUTION", "code": "VASCULAR_RISK", "zone_id": "Bw1",
       "message": "...", "recommendation": "..."}
    ],
    "sessions": [ /* SessionPlan */ ],
    "total_volume_estimate_ml": [0.8, 2.4],
    "total_neurotoxin_units": [2, 6],
    "session_count": 1
  },

  "calibration": {
    "method": "iris",                      // "iris" | "face_width_estimate" | "unknown"
    "px_per_mm": 4.6, "confidence": 0.95,
    "reliable": true                       // false → ALL mm values are estimates
  },

  "reconstruction": {                      // metric multi-view 3D, null if not attempted
    "available": true,
    "depth_source": "multi_view_3d",       // "multi_view_3d" | "relative_z"
    "views_used": ["frontal", "oblique_left", "oblique_right"],   // profile excluded by policy
    "n_views": 3,
    "angular_spread_deg": 62.8,            // higher = better depth
    "reprojection_rms_mm": 2.68            // lower = better fit
  },

  "overlay": {                             // frontend data, null if not computed
    "image_dimensions": {                  // per view: analyzed-frame size + back-transform to the upload
      "frontal": {"width": 1024, "height": 1024,
                  "source_width": 1158, "source_height": 1544,
                  "crop_x": 8, "crop_y": 499, "crop_width": 1072, "crop_height": 1045}
    },
    "zones": [
      {
        "zone_id": "Tt1", "zone_name": "Tear Trough", "region": "midface",
        "view": "frontal",                 // which view's image these coords map to
        "severity": 6.5, "intensity": 0.65,            // intensity = severity/10
        "color_code": "#dc2626",           // severity band (green/amber/red)
        "centroid_x": 0.504, "centroid_y": 0.381,      // heatmap anchor, normalized [0,1]
        "injection_points": [{"landmark_index": 253, "x": 0.49, "y": 0.38}]
      }
    ]
  },

  "engine_version": "2.2.0",
  "processing_time_ms": 842,
  "views_analyzed": ["frontal", "oblique_left", "oblique_right"],
  "warnings": ["CALIBRATION_UNRELIABLE: ..."]            // assessment-level
}
```

### The `estimated` flag — honesty contract

A measurement with `"estimated": true` is **not a validated clinical mm value** and
must not drive injection volumes. A value is flagged when:
- it is depth/projection-derived (volume-zone depths, ogee score, profile out-of-plane
  projections) — thresholds are not yet calibrated against real 3D mm (Sprint 11); **or**
- the iris calibration was not reliable (`calibration.reliable == false`) — then **every**
  mm value is flagged and an assessment-level `CALIBRATION_UNRELIABLE` warning is added.

Coordinates in `overlay` are normalized [0,1] to the analyzed (preprocessed /
face-centred) frame. To place markers on the **original upload**, map with the
per-view back-transform in `image_dimensions`:
```
orig_norm_x = (crop_x + x * crop_width)  / source_width
orig_norm_y = (crop_y + y * crop_height) / source_height
```
(When the face re-crop was skipped, the transform is identity: crop = full source.)

---

## Quality Warning Codes

| Code | Trigger | Severity |
|---|---|---|
| `LOW_RESOLUTION` | Image < 640x480 | medium |
| `UNDEREXPOSED` | Mean brightness < 50 | high |
| `OVEREXPOSED` | Mean brightness > 220 | high |
| `LOW_CONTRAST` | Brightness std < 30 | medium |
| `BLURRY` | Laplacian variance < 50 | high |
| `NON_NEUTRAL_EXPRESSION` | Active blendshapes (frontal) | medium |
| `HEAD_NOT_FRONTAL` / `HEAD_NOT_OBLIQUE` / `HEAD_NOT_PROFILE` | Pose outside the view's range | high |
| `POSE_REJECTED` | Pose beyond hard limits → image rejected | critical |
| `NO_FACE_DETECTED` | No face in the image | critical |
| `IMAGE_DECODE_FAILED` | Could not decode bytes | critical |
| `CALIBRATION_WARNING` | Single/asymmetric iris, fallback used | low |

> Pose note: a true profile needs |yaw| ≥ 55° (hard limit). A shot at ~45–50° is
> treated as an oblique, not a profile, and a `profile` slot below 55° is rejected.

---

## n8n Webhook Contract

**Method:** POST · **URL:** `N8N_WEBHOOK_URL` · **Content-Type:** `application/json`
**Timeout:** 15 s · **Failure behavior:** logged, never blocks the API response.
Fired after a successful assessment when an `organization_id` is provided.

```jsonc
{
  "event": "assessment_complete",
  "engine_version": "2.2.0",
  "assessment_id": "uuid",
  "patient_id": "uuid|null",
  "aesthetic_score": 82.0,
  "zones_count": 14,
  "views_analyzed": ["frontal", "oblique_left", "oblique_right"],
  "data": { /* full AssessmentResponse */ }
}
```

---

## Supabase Data Contracts (V2)

Project `mbwteypkehrmeqzdzdph` (AestheticBiometricsDB, eu-west-1). Multi-tenant —
`organization_id` on all V2 tables with RLS org-isolation; the API backend uses the
service role (RLS bypass).

### Table: `assessments`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK (= assessment_id) |
| `organization_id` | UUID | FK, RLS scope |
| `patient_id` | UUID | FK, nullable |
| `status` | TEXT | `completed` \| `partial` |
| `image_quality` / `global_metrics` / `zones` / `treatment_plan` | JSONB | analysis payload |
| `aesthetic_score` | REAL | |
| `calibration_method` | TEXT | |
| `engine_version` | TEXT | |
| `processing_time_ms` | INT | |
| `frontal_image_path` / `profile_image_path` / `oblique_image_path` | TEXT | storage paths |
| `created_at` | TIMESTAMPTZ | |

> The `reconstruction` and full `calibration`/`overlay` blocks are returned in the API
> response and the n8n payload but are not (yet) persisted as columns.

### Table: `treatment_comparisons`
`id`, `organization_id`, `patient_id`, `pre_assessment_id`, `post_assessment_id`,
`treatment_date`, `treatment_notes`, `zone_deltas` (JSONB), `improvement_score`, `created_at`.

### Tables: `organizations`, `patients`
`organizations`: `id`, `name`, `slug` (unique), `settings`. `patients`: `id`,
`organization_id`, `external_id` (unique per org), name, DOB.

### Storage Bucket
| Bucket | Purpose | Access | Limits |
|---|---|---|---|
| `patient-images` | Assessment images (`{org}/{assessment}/{view}.jpg`) | org-scoped RLS | 10MB, JPEG/PNG/WebP |

### Legacy V1 tables (retained, unused by V2)
`biometric_analyses`, `treatment_sessions` — from the removed single-image V1 API.
