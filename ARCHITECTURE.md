# Architecture — Aesthetic Biometrics Engine

## System Context

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Praxis App  │     │   n8n Agent  │     │  Direct API  │
│  (Frontend)  │     │  (Workflow)  │     │   Consumer   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────┬───────┘────────────────────┘
                    ▼
          ┌─────────────────┐
          │   FastAPI App   │
          │   (This Repo)   │
          └────────┬────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌─────────┐ ┌───────┐ ┌─────────┐
    │Supabase │ │  n8n  │ │Supabase │
    │   DB    │ │Webhook│ │ Storage │
    └─────────┘ └───────┘ └─────────┘
```

## Request Flow

```
1. Client sends POST /api/v1/analyze
   ├── file: image bytes (multipart)  OR
   ├── image_url: Supabase storage URL
   ├── view_angle: frontal | oblique | profile
   └── patient_id: optional UUID

2. Image Loading
   ├── Decode bytes → OpenCV BGR array
   └── Validate quality (blur, brightness, contrast)

3. Landmark Detection
   ├── MediaPipe FaceMesh → 478 3D landmarks
   ├── Confidence estimation
   └── Fail fast if no face detected (HTTP 422)

4. View-Specific Analysis
   ├── frontal → SymmetryResult + FacialThirds + LipAnalysis
   ├── profile → ProfileELine + NasolabialAngle + ChinProjection
   └── oblique → OgeeCurve

5. Response Assembly
   ├── Wrap analysis in AnalysisResponse
   ├── Attach quality warnings
   └── Include metadata (image size, confidence)

6. Side Effects (non-blocking)
   ├── Save to Supabase (if patient_id provided)
   └── POST to n8n webhook (if configured)

7. Return JSON
```

## Data Model (Supabase)

```
patients
├── id: UUID (PK)
├── external_id: TEXT (unique, from external systems)
├── first_name, last_name: TEXT
├── date_of_birth: DATE
├── notes: TEXT
└── created_at, updated_at: TIMESTAMPTZ

biometric_analyses
├── id: UUID (PK)
├── patient_id: UUID (FK → patients)
├── view_angle: TEXT (frontal|oblique|profile)
├── result_json: JSONB (full AnalysisResponse)
├── confidence: REAL
├── landmarks_detected: INTEGER
├── image_url: TEXT
└── created_at: TIMESTAMPTZ

treatment_sessions
├── id: UUID (PK)
├── patient_id: UUID (FK → patients)
├── treatment_type: TEXT
├── treatment_date: DATE
├── notes: TEXT
├── pre_analysis_ids: UUID[]
├── post_analysis_ids: UUID[]
└── created_at: TIMESTAMPTZ
```

## Measurement Mathematics

### Pixel-to-Millimeter Conversion

All pixel measurements are converted to approximate mm using:

```
scale = assumed_face_width_mm / face_width_px
```

Default assumed face width: **140mm** (adult average bizygomatic width).
Face width is measured as the Euclidean distance between left and right gonion landmarks.

> Note: This is an approximation. For clinical precision, a calibration marker
> (ruler or sticker of known size) in the image would be required.

### Frontal: Symmetry Score

```
For each paired landmark (eyes, brows, mouth corners, cheekbones, gonions):
  h_dev = |distance_left_to_midline - distance_right_to_midline|
  v_dev = |y_left - y_right|

normalized_deviation = mean(h_dev + v_dev) / (2 × face_width)
symmetry_score = clamp((1 - normalized_deviation × 10) × 100, 0, 100)
```

### Frontal: Facial Thirds

```
upper  = |glabella_y - trichion_y|
middle = |subnasale_y - glabella_y|
lower  = |mentum_y - subnasale_y|

ratio_i = segment_i / (upper + middle + lower)
deviation = mean(|ratio_i - 1/3|) × 100%
```

### Frontal: Lip Ratio

```
upper_lip_height = |stomion_y - labrale_superius_y|
lower_lip_height = |labrale_inferius_y - stomion_y|
ratio = upper / lower
ideal = 1/1.6 = 0.625
deviation = |ratio - ideal| / ideal × 100%
```

### Profile: Ricketts E-Line

```
E-line: straight line from pronasale (nose tip) to pogonion (chin tip)
For each lip point:
  distance = signed perpendicular distance to E-line
  negative = behind line (ideal)
  positive = in front of line (protruded)
```

### Profile: Nasolabial Angle

```
Vector A: subnasale → columella (nasal bridge direction)
Vector B: subnasale → labrale superius (upper lip direction)
angle = arccos(dot(A, B) / (|A| × |B|))
Ideal: 90°–105°
```

### Profile: Chin Projection

```
offset = pogonion_x - subnasale_x  (in profile view)
Converted to mm via scale factor.
< -5mm: retruded | > +5mm: prominent | else: well-projected
```

### Oblique: Ogee Curve

```
Path: glabella → malar_high → cheekbone → malar_low → mouth_corner
Chord: straight line glabella → mouth_corner
curvature_ratio = max_perpendicular_deviation / chord_length

Score mapping:
  ratio > 0.25 → 95 (excellent ogee)
  ratio 0.15–0.25 → 60–95 (good)
  ratio 0.08–0.15 → 30–60 (moderate loss)
  ratio < 0.08 → 0–30 (significant loss)
```

## Security Considerations

- **No PHI in logs:** Patient data is stored only in Supabase, never logged
- **RLS enabled:** All Supabase tables have Row Level Security
- **Image handling:** Images are processed in-memory, never written to disk
- **CORS:** Restricted to configured origins
- **Env vars:** Secrets via `.env`, never committed (`.gitignore`)
