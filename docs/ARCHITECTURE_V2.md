# Architecture V2 — Aesthetic Biometrics Engine

> Kompletter Neuentwurf. Ersetzt die V1-Architektur.
> Designed aus der Perspektive eines Aesthetic-Medicine-Experten UND eines Systems-Engineers.

---

## Fundamentale Designaenderung gegenueber V1

**V1-Problem:** Drei isolierte Analysen (frontal, profile, oblique) die jeweils unabhaengig ein JSON zurueckgeben. Kein Zusammenhang zwischen den Views. Keine Behandlungsempfehlung. Keine Zonen-Zuordnung. Im Grunde ein Messgeraet ohne Interpretation.

**V2-Ansatz:** Ein **Multi-View Fusion System** das:
1. Alle 3 Fotos gemeinsam analysiert
2. Eine einheitliche **3D-Facial-Map** erstellt
3. Ergebnisse auf **anatomische Behandlungszonen** (inspiriert von MD Codes) mappt
4. Einen konkreten **Behandlungsplan** mit Priorisierung generiert

---

## System-Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
│                  POST /api/v2/assessment                        │
│              (3 Bilder + Patient-ID in einem Call)               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Pipeline  │
                    │ Orchestrator│
                    └──────┬──────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
     ┌────────────┐ ┌────────────┐  ┌────────────┐
     │  Frontal   │ │  Profile   │  │  Oblique   │
     │  Detector  │ │  Detector  │  │  Detector  │
     │ (478 pts)  │ │ (478 pts)  │  │ (478 pts)  │
     │+Blendshapes│ │            │  │            │
     └─────┬──────┘ └─────┬──────┘  └─────┬──────┘
           │              │               │
           └──────────┬───┘───────────────┘
                      ▼
            ┌──────────────────┐
            │  Multi-View      │
            │  Fusion Engine   │
            │                  │
            │ Combines 3 views │
            │ into unified     │
            │ facial profile   │
            └────────┬─────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │  Zone    │ │ Symmetry │ │ Aging    │
   │ Analyzer │ │ & Prop.  │ │ Pattern  │
   │ (MD Code │ │ Analyzer │ │ Detector │
   │  Mapping)│ │          │ │          │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        │            │            │
        └──────┬─────┘────────────┘
               ▼
     ┌──────────────────┐
     │  Treatment Plan  │
     │  Generator       │
     │                  │
     │  Zone priorities │
     │  Product recs    │
     │  Injection map   │
     └────────┬─────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 Supabase  n8n Hook   Response
 (persist)  (notify)   (JSON)
```

---

## Kern-Innovation: Anatomische Zonen statt abstrakter Messwerte

### Das Zone-System (inspiriert von MD Codes)

Statt roher Zahlen wie "symmetry_score: 87" mappt V2 auf **16 behandlungsrelevante Gesichtszonen**. Jede Zone bekommt:
- **Severity** (0-10): Wie dringend ist eine Behandlung?
- **Findings**: Was wurde erkannt?
- **Recommendations**: Konkrete Behandlungsvorschlaege

```
Zone-Map:
┌─────────────────────────────────────────┐
│              UPPER FACE                  │
│  T1/T2: Temporal (Schlaefe)             │
│  Bw1: Brow lateral                      │
│  Bw2: Brow medial (Glabella)           │
│  Fo1: Forehead lines                    │
├─────────────────────────────────────────┤
│              MID FACE                    │
│  Ck1: Zygomatic arch (Jochbogen)       │
│  Ck2: Zygomatic eminence (Wangenhoehe) │
│  Ck3: Anteromedial cheek (Mittelwange) │
│  Tt1: Infraorbital (Traenental)        │
│  Ns1: Nasolabial fold                   │
├─────────────────────────────────────────┤
│              LOWER FACE                  │
│  Lp1: Upper lip (Oberlippe)            │
│  Lp2: Lower lip (Unterlippe)           │
│  Lp3: Lip corners (Mundwinkel)         │
│  Mn1: Marionette lines                  │
│  Jw1: Pre-jowl sulcus                  │
│  Ch1: Chin projection (Kinn)           │
│  Jl1: Jawline definition               │
├─────────────────────────────────────────┤
│              PROFILE-SPECIFIC            │
│  Pf1: Nasal profile (Nasenprofil)      │
│  Pf2: Lip projection (Lippenprofil)    │
│  Pf3: Chin-neck angle                  │
└─────────────────────────────────────────┘
```

### Welche View analysiert welche Zone?

| Zone | Frontal | Profile | Oblique | Fusion |
|------|---------|---------|---------|--------|
| T1/T2 Temporal | - | - | Primary | - |
| Bw1/Bw2 Brow | Primary | Secondary | - | Yes |
| Ck1-Ck3 Cheek | Secondary | - | Primary | Yes |
| Tt1 Tear trough | Primary | Secondary | - | Yes |
| Ns1 Nasolabial | Primary | - | Secondary | Yes |
| Lp1-Lp3 Lips | Primary | Primary | - | Yes |
| Mn1 Marionette | Primary | - | Secondary | Yes |
| Ch1 Chin | Secondary | Primary | - | Yes |
| Jl1 Jawline | Secondary | Primary | Secondary | Yes |
| Pf1 Nasal profile | - | Primary | - | - |
| Pf2 Lip projection | - | Primary | - | - |
| Pf3 Chin-neck | - | Primary | - | - |

**Fusion** = Zone wird aus mehreren Views kombiniert fuer hoehere Genauigkeit.

---

## Technologie-Upgrade: MediaPipe Face Landmarker (nicht Legacy FaceMesh)

### V1 nutzte die Legacy API:
```python
# ALT — Legacy, wird nicht mehr weiterentwickelt
mp.solutions.face_mesh.FaceMesh(...)
```

### V2 nutzt die neue Tasks API:
```python
# NEU — Aktuelle API mit Blendshapes und Transformation Matrix
import mediapipe as mp
from mediapipe.tasks.python import vision

options = vision.FaceLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=vision.RunningMode.IMAGE,
    num_faces=1,
    min_face_detection_confidence=0.7,
    min_face_presence_confidence=0.7,
    output_face_blendshapes=True,                    # NEU: 52 Gesichtsausdruecke
    output_facial_transformation_matrixes=True,       # NEU: 3D-Transformationsmatrix
)
```

### Was uns das bringt:

| Feature | V1 (Legacy) | V2 (Tasks API) |
|---------|------------|----------------|
| Landmarks | 478 (x,y,z) | 478 (x,y,z) |
| Blendshapes | Nicht verfuegbar | **52 Expression-Koeffizienten** |
| Transformation Matrix | Nicht verfuegbar | **4x4 Affine Matrix** |
| Head Pose | Manuell berechnet | **Aus Matrix ableitbar** |
| Model Format | Built-in | `.task` Bundle (aktualisierbar) |

**Blendshapes sind ein Game-Changer** fuer Aesthetic Medicine:
- `browDownLeft/Right` → Brow-Ptosis-Erkennung
- `mouthSmileLeft/Right` → Asymmetrie-Erkennung bei Bewegung
- `jawOpen` → Masseter-Volumen-Indikator
- `cheekPuff` → Midface-Volumen-Approximation

---

## Neues Datenmodell

### API: Ein Call, drei Bilder, ein Behandlungsplan

```
POST /api/v2/assessment
Content-Type: multipart/form-data

Fields:
  patient_id:  UUID (optional)
  frontal:     JPEG/PNG
  profile:     JPEG/PNG
  oblique:     JPEG/PNG
```

### Response-Struktur

```jsonc
{
  "assessment_id": "uuid",
  "patient_id": "uuid | null",
  "timestamp": "2026-03-18T22:00:00Z",

  // Qualitaetskontrolle pro Bild
  "image_quality": {
    "frontal":  { "accepted": true, "warnings": [], "confidence": 0.94 },
    "profile":  { "accepted": true, "warnings": [], "confidence": 0.91 },
    "oblique":  { "accepted": true, "warnings": ["LOW_CONTRAST"], "confidence": 0.82 }
  },

  // Globale Gesichtsmesswerte
  "global_metrics": {
    "symmetry_index": 91.2,
    "facial_thirds": { "upper": 0.32, "middle": 0.34, "lower": 0.34 },
    "golden_ratio_deviation": 4.2,
    "estimated_biological_age_range": "38-42",
    "head_pose": { "yaw": 2.1, "pitch": -1.3, "roll": 0.8 }
  },

  // Das Herzstueck: Zone-basierte Analyse
  "zones": [
    {
      "zone_id": "Ck2",
      "zone_name": "Zygomatic Eminence",
      "region": "midface",
      "severity": 6,
      "findings": [
        "Malar flattening detected in oblique view",
        "Ogee curve score: 52/100 (moderate volume loss)",
        "Left-right asymmetry: 8% deviation"
      ],
      "primary_view": "oblique",
      "confirmed_by": ["frontal"],
      "measurements": {
        "ogee_curve_score": 52,
        "malar_prominence_ratio": 0.68,
        "volume_deficit_estimate_ml": 1.2
      }
    },
    {
      "zone_id": "Lp1",
      "zone_name": "Upper Lip",
      "region": "lower_face",
      "severity": 4,
      "findings": [
        "Upper-to-lower lip ratio: 1:2.1 (ideal: 1:1.6)",
        "Vermilion border definition: moderate loss",
        "Cupid's bow asymmetry: 3%"
      ],
      "primary_view": "frontal",
      "confirmed_by": ["profile"],
      "measurements": {
        "lip_ratio": 0.476,
        "vermilion_height_upper_mm": 5.8,
        "vermilion_height_lower_mm": 12.2,
        "cupid_bow_asymmetry_pct": 3.0
      }
    }
    // ... weitere Zonen
  ],

  // Behandlungsplan
  "treatment_plan": {
    "primary_concerns": [
      {
        "priority": 1,
        "zone_id": "Ck2",
        "concern": "Midface volume loss",
        "recommended_treatment": "Deep-plane HA filler (e.g., Juvederm Voluma / Radiesse)",
        "technique": "Bolus injection supraperiosteal at zygomatic eminence",
        "estimated_volume_ml": "1.0-1.5 per side",
        "expected_outcome": "Restored ogee curve, improved midface projection"
      },
      {
        "priority": 2,
        "zone_id": "Lp1",
        "concern": "Upper lip volume deficit",
        "recommended_treatment": "Soft HA filler (e.g., Juvederm Volbella / Restylane Kysse)",
        "technique": "Serial puncture along vermilion border + microdroplet in body",
        "estimated_volume_ml": "0.5-0.8",
        "expected_outcome": "Improved 1:1.6 ratio, defined cupid's bow"
      }
    ],
    "secondary_concerns": [ /* ... */ ],
    "contraindications": [],
    "session_estimate": "1-2 sessions, 4 weeks apart",
    "total_volume_estimate_ml": "3.0-4.5"
  },

  // Rohdaten fuer Experten
  "raw_data": {
    "frontal_landmarks": 478,
    "profile_landmarks": 478,
    "oblique_landmarks": 478,
    "blendshapes": { /* 52 values */ }
  }
}
```

---

## Pipeline-Architektur (Code-Struktur)

```
app/
├── main.py
├── config.py
│
├── api/
│   ├── v2_routes.py              # POST /assessment (3 images)
│   └── v1_routes.py              # Legacy single-image (backward compat)
│
├── pipeline/                     # NEU: Orchestrierung
│   ├── orchestrator.py           # Steuert den gesamten Analyse-Flow
│   ├── image_preprocessor.py     # Normalisierung, EXIF-Rotation, Resize
│   └── quality_gate.py           # Entscheidet ob Bild analysierbar ist
│
├── detection/                    # NEU: Landmark-Extraktion
│   ├── face_landmarker.py        # MediaPipe Tasks API Wrapper
│   ├── landmark_index.py         # 478 Landmark-Definitionen + Gruppierungen
│   └── head_pose.py              # Yaw/Pitch/Roll aus Transformation Matrix
│
├── analysis/                     # NEU: Medizinische Analyse-Module
│   ├── multi_view_fusion.py      # Kombiniert 3 Views zu einheitlichem Profil
│   ├── zone_analyzer.py          # Mappt Landmarks auf Behandlungszonen
│   ├── symmetry_engine.py        # Umfassende Symmetrie-Analyse
│   ├── proportion_engine.py      # Gesichtsdrittel, Golden Ratio, Lip Ratio
│   ├── profile_engine.py         # E-Line, Nasolabial, Chin, Nose
│   ├── volume_engine.py          # Ogee Curve, Temporal Hollowing, Tear Trough
│   └── aging_engine.py           # Blendshape-basierte Alterungsanalyse
│
├── treatment/                    # NEU: Behandlungsplan-Generator
│   ├── plan_generator.py         # Erstellt priorisierten Behandlungsplan
│   ├── zone_definitions.py       # Die 16+ Zonen mit Referenzwerten
│   ├── product_database.py       # Filler/Botox Produktempfehlungen
│   └── contraindication_check.py # Sicherheitspruefungen
│
├── models/
│   ├── schemas.py                # Pydantic V2 Models (komplett neu)
│   └── zone_models.py            # Zone-spezifische Datenmodelle
│
├── services/
│   ├── supabase_service.py       # DB + Storage (Bilder in Bucket)
│   └── n8n_service.py            # Webhook
│
└── utils/
    ├── geometry.py               # Mathematik
    └── pixel_calibration.py      # Px-zu-mm mit Iris-Referenz (NEU)
```

---

## Pixel-zu-Millimeter: Iris-Kalibrierung statt Schaetzung

### V1-Problem:
Annahme einer festen Gesichtsbreite von 140mm → ungenau bei verschiedenen Ethnien und Gesichtsgroessen.

### V2-Loesung: Iris-basierte Kalibrierung

Die menschliche Iris hat eine **nahezu konstante Breite von 11.7mm** (± 0.5mm), unabhaengig von Geschlecht, Alter oder Ethnie (Referenz: Hashemi et al., 2012).

MediaPipe liefert mit `refine_landmarks=True` praezise Iris-Konturen (Landmarks 468-477).

```python
# Iris-Diameter in Pixel messen
left_iris = [landmarks[468], landmarks[469], landmarks[470], landmarks[471]]
iris_width_px = distance(landmarks[469], landmarks[471])  # horizontal diameter

# Kalibrierung
IRIS_WIDTH_MM = 11.7
px_per_mm = iris_width_px / IRIS_WIDTH_MM

# Jetzt alle Messungen in echten Millimetern
lip_height_mm = lip_height_px / px_per_mm
```

**Genauigkeitsgewinn:** ca. 3-5x praeziser als die Gesichtsbreiten-Schaetzung.

---

## Blendshape-Integration fuer dynamische Analyse

Die 52 Blendshapes geben uns **Muskelspannung** — etwas das reine Landmark-Positionen nicht liefern:

| Blendshape | Klinische Relevanz |
|---|---|
| `browDownLeft/Right` | Corrugator-Aktivitaet → Glabella-Botox-Bedarf |
| `browInnerUp` | Frontalis-Kompensation bei Brow-Ptosis |
| `mouthSmileLeft/Right` | Asymmetrie → unilaterale Filler-Dosierung |
| `jawOpen` | Masseter-Volumen-Indikator → Masseter-Botox |
| `cheekPuff` | Buccal-Fat-Approximation |
| `noseSneerLeft/Right` | Nasalis-Aktivitaet → Bunny-Lines-Botox |
| `mouthPucker` | Orbicularis-Oris-Tonus → Lip-Flip-Botox |
| `eyeSquintLeft/Right` | Crow's Feet Potenzial |

---

## Supabase Schema V2

```sql
-- Assessments: ein vollstaendiger 3-View Durchlauf
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'processing'
        CHECK (status IN ('processing', 'completed', 'failed', 'partial')),

    -- Bild-Referenzen (Supabase Storage Bucket)
    frontal_image_path TEXT,
    profile_image_path TEXT,
    oblique_image_path TEXT,

    -- Qualitaet
    image_quality JSONB,

    -- Analyse-Ergebnisse
    global_metrics JSONB,
    zones JSONB,              -- Array der Zone-Analysen
    treatment_plan JSONB,     -- Generierter Behandlungsplan
    raw_landmarks JSONB,      -- Rohe Landmark-Daten (optional, gross)
    blendshapes JSONB,        -- 52 Blendshape-Werte

    -- Metadaten
    engine_version TEXT NOT NULL DEFAULT '2.0.0',
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Behandlungs-Verlauf (Vorher/Nachher)
CREATE TABLE treatment_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    pre_assessment_id UUID REFERENCES assessments(id),
    post_assessment_id UUID REFERENCES assessments(id),
    treatment_date DATE NOT NULL,
    treatment_notes TEXT,
    zone_deltas JSONB,        -- Veraenderung pro Zone
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index fuer schnelle Patienten-Historie
CREATE INDEX idx_assessments_patient_date
    ON assessments(patient_id, created_at DESC);
```

---

## API-Design V2

### Haupt-Endpoint: Vollstaendiges Assessment

```
POST /api/v2/assessment
Content-Type: multipart/form-data

Params:
  patient_id: UUID (optional, query)

Body:
  frontal: File (required)
  profile: File (required)
  oblique: File (required)

Response: 200 → CompleteAssessment JSON
          422 → Face not detected in one or more images
          400 → Missing images
```

### Einzel-View (Legacy-Kompatibilitaet)

```
POST /api/v1/analyze
(bleibt wie bisher fuer Rueckwaertskompatibilitaet)
```

### Vergleichs-Endpoint

```
POST /api/v2/compare
Body:
  pre_assessment_id: UUID
  post_assessment_id: UUID

Response: 200 → Delta-Analyse pro Zone
```

### Patienten-Historie

```
GET /api/v2/patients/{patient_id}/history

Response: 200 → Liste aller Assessments mit Trend-Daten
```

---

## Behandlungsplan-Logik

### Severity-Berechnung pro Zone

Jede Zone hat eine **gewichtete Severity** basierend auf:

```python
severity = (
    measurement_deviation * 0.4     # Wie weit vom Ideal?
    + volume_deficit * 0.3           # Geschaetzter Volumenverlust
    + asymmetry_score * 0.2          # Links-Rechts-Unterschied
    + aging_indicator * 0.1          # Blendshape-basiert
)
```

### Priorisierung (klinische Logik)

1. **Structural first:** Zonen die andere Zonen beeinflussen (Midface vor Nasolabial)
2. **High-impact:** Zonen mit groesstem visuellen Effekt zuerst
3. **Safety:** Zonen ohne Gefaessrisiko vor riskanten Zonen
4. **Patient concern:** (spaeter) Gewichtung nach Patientenwunsch

### Produkt-Datenbank

```python
PRODUCT_RECOMMENDATIONS = {
    "deep_volume": {
        "products": ["Juvederm Voluma", "Radiesse", "Sculptra"],
        "zones": ["Ck1", "Ck2", "Ch1", "T1"],
        "technique": "Bolus supraperiosteal or deep subcutaneous",
    },
    "soft_volume": {
        "products": ["Juvederm Volbella", "Restylane Kysse", "Teoxane Kiss"],
        "zones": ["Lp1", "Lp2", "Tt1"],
        "technique": "Serial puncture, microdroplet, linear threading",
    },
    "skin_quality": {
        "products": ["Profhilo", "Juvederm Volite"],
        "zones": ["Ck3", "T1", "T2"],
        "technique": "BAP technique, mesotherapy",
    },
    "neurotoxin": {
        "products": ["Botox", "Dysport", "Xeomin"],
        "zones": ["Bw2", "Fo1"],
        "indications": ["Glabella lines", "Forehead lines", "Crow's feet",
                        "Masseter reduction", "Lip flip"],
    },
}
```

---

## Performance-Ziele

| Metrik | Ziel |
|---|---|
| 3-Image Assessment | < 3 Sekunden |
| Einzelbild-Analyse | < 800ms |
| API Cold Start | < 5 Sekunden |
| Docker Image Size | < 1.5 GB |
| Landmark Precision | < 2px Abweichung bei 1080p |

---

## Quellen

- [MediaPipe Face Landmarker Python Guide](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python)
- [MediaPipe Face Mesh 478 Landmarks](https://github.com/google-ai-edge/mediapipe/issues/4435)
- [MD Codes — Mauricio de Maio (PubMed)](https://pubmed.ncbi.nlm.nih.gov/32445044/)
- [MD Codes — Springer Nature](https://link.springer.com/article/10.1007/s00266-020-01762-7)
- [Iris Diameter as Calibration Reference](https://pubmed.ncbi.nlm.nih.gov/)
- [FastAPI File Upload Documentation](https://github.com/fastapi/fastapi)
- [Supabase Storage Python Client](https://supabase.com/docs/reference/python/storage-from-upload)
