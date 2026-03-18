# API Contracts — Aesthetic Biometrics Engine

> Single source of truth for all API interfaces, request/response schemas, and integration contracts.

---

## Base URL

```
Production:  https://<railway-domain>/api/v1
Local:       http://localhost:8000/api/v1
```

---

## Endpoints

### POST `/api/v1/analyze`

Analyze a facial image from a specified view angle.

#### Request

**Content-Type:** `multipart/form-data` (with file) or `application/x-www-form-urlencoded` (with URL)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `view_angle` | query string | Yes | `frontal` \| `oblique` \| `profile` |
| `patient_id` | query string | No | UUID — enables Supabase persistence |
| `image_url` | query string | No | Supabase storage URL (alternative to file) |
| `file` | multipart file | No | JPEG or PNG image (max 10MB) |

> Provide either `file` or `image_url`, not both.

#### Response — `200 OK`

```jsonc
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",  // null if not provided
  "view_angle": "frontal",
  "analysis": { /* view-specific, see below */ },
  "quality_warnings": [
    {"code": "LOW_CONTRAST", "message": "Image has low contrast..."}
  ],
  "landmarks_detected": 478,
  "confidence": 0.89,
  "metadata": {
    "image_size": "1920x1080",
    "view_angle": "frontal"
  }
}
```

#### Analysis Schemas by View

**Frontal (`view_angle=frontal`)**
```jsonc
{
  "symmetry": {
    "horizontal_deviation_mm": 1.2,   // float, >= 0
    "vertical_deviation_mm": 0.8,     // float, >= 0
    "symmetry_score": 92.5            // float, 0–100
  },
  "facial_thirds": {
    "upper_third_ratio": 0.31,        // float, 0–1
    "middle_third_ratio": 0.34,       // float, 0–1
    "lower_third_ratio": 0.35,        // float, 0–1
    "deviation_from_ideal": 2.1       // float, % deviation from 1:1:1
  },
  "lip_analysis": {
    "upper_lip_height_px": 18.3,      // float, pixels
    "lower_lip_height_px": 29.1,      // float, pixels
    "ratio": 0.629,                   // float, upper/lower
    "deviation_from_ideal": 0.6       // float, % from 1:1.6
  }
}
```

**Profile (`view_angle=profile`)**
```jsonc
{
  "e_line": {
    "upper_lip_to_eline_mm": -3.2,    // float, negative=behind line
    "lower_lip_to_eline_mm": -1.8,    // float
    "assessment": "ideal"             // "retruded" | "ideal" | "protruded"
  },
  "nasolabial_angle": {
    "angle_degrees": 97.3,            // float
    "ideal_min": 90.0,                // float, constant
    "ideal_max": 105.0,               // float, constant
    "assessment": "within ideal range"
  },
  "chin_projection": {
    "pogonion_offset_mm": -2.1,       // float, negative=retruded
    "assessment": "well-projected"    // "retruded" | "well-projected" | "prominent"
  }
}
```

**Oblique (`view_angle=oblique`)**
```jsonc
{
  "ogee_curve": {
    "curve_score": 72.5,              // float, 0–100
    "midface_volume_assessment": "adequate",  // "adequate" | "moderate_loss" | "significant_loss"
    "malar_prominence_ratio": 0.82    // float
  }
}
```

#### Error Responses

| Status | Condition | Body |
|---|---|---|
| `400` | No file or URL provided | `{"detail": "Provide either 'file' or 'image_url'"}` |
| `400` | Corrupt image | `{"detail": "Could not decode image..."}` |
| `400` | Bad URL | `{"detail": "Failed to fetch image from URL: ..."}` |
| `413` | File too large | `{"detail": "Image exceeds 10MB limit"}` |
| `422` | No face detected | `{"detail": "No face detected. Ensure..."}` |

---

### GET `/api/v1/health`

Health check for monitoring and load balancers.

#### Response — `200 OK`
```json
{"status": "ok", "service": "aesthetic-biometrics-engine"}
```

---

### GET `/`

Service info and discovery.

#### Response — `200 OK`
```json
{
  "service": "Aesthetic Biometrics Engine",
  "version": "0.1.0",
  "docs": "/docs",
  "endpoints": {
    "analyze": "/api/v1/analyze",
    "health": "/api/v1/health"
  }
}
```

---

## Quality Warning Codes

| Code | Trigger | Severity |
|---|---|---|
| `LOW_RESOLUTION` | Image < 640x480 | Medium |
| `UNDEREXPOSED` | Mean brightness < 50 | High |
| `OVEREXPOSED` | Mean brightness > 220 | High |
| `LOW_CONTRAST` | Brightness std < 30 | Medium |
| `BLURRY` | Laplacian variance < 50 | High |
| `LOW_CONFIDENCE` | Face detection < 0.7 | High |
| `STORAGE_ERROR` | Supabase save failed | Low (non-blocking) |

---

## n8n Webhook Contract

**Method:** POST
**URL:** Configured via `N8N_WEBHOOK_URL` env var
**Content-Type:** `application/json`
**Payload:** Full `AnalysisResponse` JSON (same as API response)
**Timeout:** 15 seconds
**Failure behavior:** Silent — does not affect API response

### Expected Webhook Payload Shape

```jsonc
{
  "patient_id": "uuid|null",
  "view_angle": "frontal|oblique|profile",
  "analysis": { /* view-specific schema */ },
  "quality_warnings": [],
  "landmarks_detected": 478,
  "confidence": 0.89,
  "metadata": {}
}
```

---

## Supabase Data Contracts

### Table: `patients`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, auto-generated |
| `external_id` | TEXT | UNIQUE, nullable |
| `first_name` | TEXT | nullable |
| `last_name` | TEXT | nullable |
| `date_of_birth` | DATE | nullable |
| `notes` | TEXT | nullable |
| `created_at` | TIMESTAMPTZ | auto |
| `updated_at` | TIMESTAMPTZ | auto |

### Table: `biometric_analyses`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, auto-generated |
| `patient_id` | UUID | FK → patients(id) ON DELETE CASCADE |
| `view_angle` | TEXT | CHECK: frontal \| oblique \| profile |
| `result_json` | JSONB | NOT NULL, full AnalysisResponse |
| `confidence` | REAL | NOT NULL, default 0 |
| `landmarks_detected` | INTEGER | NOT NULL, default 0 |
| `image_url` | TEXT | nullable |
| `created_at` | TIMESTAMPTZ | auto |

### Table: `treatment_sessions`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, auto-generated |
| `patient_id` | UUID | FK → patients(id) ON DELETE CASCADE |
| `treatment_type` | TEXT | NOT NULL |
| `treatment_date` | DATE | NOT NULL, default today |
| `notes` | TEXT | nullable |
| `pre_analysis_ids` | UUID[] | default '{}' |
| `post_analysis_ids` | UUID[] | default '{}' |
| `created_at` | TIMESTAMPTZ | auto |

### Indexes

| Index | Table | Column(s) |
|---|---|---|
| `idx_analyses_patient` | biometric_analyses | patient_id |
| `idx_analyses_view` | biometric_analyses | view_angle |
| `idx_analyses_created` | biometric_analyses | created_at DESC |
| `idx_sessions_patient` | treatment_sessions | patient_id |
