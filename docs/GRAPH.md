# System Graphs — Aesthetic Biometrics Engine (V2)

> Diagrams for the current V2 engine (`/api/v2`, zone-based, engine v2.2.0). The V1
> single-image API (`/api/v1/analyze`) was removed.

## V2 Pipeline (`POST /api/v2/assessment`)

```mermaid
graph LR
    U[Client / n8n] -->|frontal + profile + 45°L + 45°R| API[FastAPI /api/v2/assessment]
    API --> PP[preprocess + EXIF + face-crop]
    PP --> DET[detect: 478 landmarks + blendshapes + pose]
    DET --> CAL[iris px→mm calibration]
    CAL --> REC[3D reconstruction<br/>frontal + bilateral obliques<br/>profile excluded]
    REC --> ENG[engines: symmetry / proportion / profile / volume*depth from 3D* / aging]
    ENG --> FUSE[multi-view fusion]
    FUSE --> ZR[zone report + aesthetic score]
    ZR --> PLAN[treatment plan]
    ZR --> OV[overlay: injection points + heatmap]
    PLAN --> RESP[AssessmentResponse]
    OV --> RESP
    REC --> RESP
    RESP --> PDF[/api/v2/report → clinical PDF/]
    RESP --> N8N[n8n webhook envelope]
    RESP --> SB[(Supabase: assessments + storage)]
```

Key stages unique to V2: the **3D reconstruction** (before the engines; volume depth reads
from it, negated), **bilateral obliques**, the **overlay** block, and the **PDF report**.

## Frontend Delivery (Sprint 14)

```mermaid
graph LR
    B[Browser / tablet<br/>Aesthetic Scan · Vite/React] -->|anon-key · multipart 4 views| PX[engine-proxy<br/>Supabase Edge Function]
    PX -->|X-API-Key · +tenant server-side| ENG[Engine on Hetzner<br/>Docker :8003 · Caddy TLS<br/>biometrics.novasyn.de]
    ENG -->|AssessmentResponse + overlay / PDF| PX
    PX --> B
    ENG -.async persist.-> SB[(Supabase<br/>assessments + patient-images)]
```

The browser never holds the engine key; the proxy injects the tenant. `canonical_oblique_view`
in the overlay tells the UI which physical oblique photo to paint the oblique heatmap on.

## System Overview

```mermaid
graph TB
    subgraph Clients
        APP[Aesthetic Scan web app<br/>Vite/React · via engine-proxy]
        N8N_TRIGGER[n8n workflow]
        API_CLIENT[Direct API consumer]
    end

    subgraph "Aesthetic Biometrics Engine (FastAPI /api/v2)"
        FASTAPI[v2_routes<br/>+ API-key auth + rate limit]
        ORCH[orchestrator]
        subgraph "Pipeline"
            PRE[preprocess]
            DET[face_landmarker<br/>MediaPipe Tasks API]
            QG[quality_gate]
            CAL[pixel_calibration]
            REC[multiview_reconstruction]
        end
        subgraph "Analysis"
            ENG[symmetry / proportion / profile / volume / aging]
            FUSE[multi_view_fusion]
            ZA[zone_analyzer]
        end
        subgraph "Treatment"
            PLAN[plan_generator]
            CONTRA[contraindication_check]
        end
        OV[overlay]
        PDF[pdf_report]
    end

    subgraph "External Services (EU)"
        SUPABASE[(Supabase<br/>AestheticBiometricsDB)]
        STORAGE[Supabase Storage<br/>patient-images]
        N8N_HOOK[n8n webhook]
    end

    APP & N8N_TRIGGER & API_CLIENT -->|POST /assessment| FASTAPI
    FASTAPI --> ORCH
    ORCH --> PRE --> DET --> QG --> CAL --> REC --> ENG --> FUSE --> ZA
    ZA --> PLAN --> CONTRA
    ZA --> OV
    FASTAPI -.->|/report| PDF
    FASTAPI -->|async persist| SUPABASE
    FASTAPI -->|async| N8N_HOOK
    FASTAPI -.->|upload| STORAGE

    style FASTAPI fill:#009688,color:#fff
    style DET fill:#FF5722,color:#fff
    style REC fill:#7E57C2,color:#fff
    style SUPABASE fill:#3ECF8E,color:#fff
    style N8N_HOOK fill:#FF6D5A,color:#fff
```

## Request Processing Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant F as FastAPI (v2_routes)
    participant O as Orchestrator
    participant P as Pipeline (preprocess/detect/pose/calibrate)
    participant R as Reconstruction
    participant Z as Zone Analyzer (+engines+fusion)
    participant T as Plan + Overlay
    participant S as Supabase / n8n

    C->>F: POST /api/v2/assessment<br/>(frontal, profile, 45°L, 45°R)
    F->>F: auth (X-API-Key), size checks
    F->>O: run_pipeline(...)
    loop each provided view
        O->>P: preprocess → detect → pose gate → calibrate
        alt no face / hard pose reject
            P-->>O: view rejected
        end
    end
    alt no usable view
        O-->>F: error
        F-->>C: 422 No face / analysis failed
    end
    O->>R: reconstruct_from_views(frontal + obliques)<br/>(profile excluded; iris-gated)
    R-->>O: 3D point cloud (or None → relative-z fallback)
    O->>Z: analyze(views, reconstruction)
    Z-->>O: zone report + aesthetic score
    O->>T: plan_generate + build_overlay
    T-->>O: plan + overlay
    O-->>F: PipelineResult
    F-->>C: 200 AssessmentResponse
    par Non-blocking (if organization_id + Supabase)
        F->>S: persist assessment + upload images + n8n envelope
    end
```

## Data Model (ER Diagram, V2)

```mermaid
erDiagram
    ORGANIZATIONS {
        uuid id PK
        text name
        text slug UK
        jsonb settings
    }
    PATIENTS {
        uuid id PK
        uuid organization_id FK
        text external_id
        text name
        date date_of_birth
    }
    ASSESSMENTS {
        uuid id PK
        uuid organization_id FK
        uuid patient_id FK
        text status
        jsonb image_quality
        jsonb global_metrics
        jsonb zones
        jsonb treatment_plan
        real aesthetic_score
        text calibration_method
        text engine_version
        text frontal_image_path
        text profile_image_path
        text oblique_image_path
        timestamptz created_at
    }
    TREATMENT_COMPARISONS {
        uuid id PK
        uuid organization_id FK
        uuid patient_id FK
        uuid pre_assessment_id FK
        uuid post_assessment_id FK
        jsonb zone_deltas
        real improvement_score
    }

    ORGANIZATIONS ||--o{ PATIENTS : "has many"
    ORGANIZATIONS ||--o{ ASSESSMENTS : "scopes (RLS)"
    PATIENTS ||--o{ ASSESSMENTS : "has many"
    ASSESSMENTS ||--o{ TREATMENT_COMPARISONS : "pre/post"
```

> Legacy V1 tables `biometric_analyses` and `treatment_sessions` remain in the DB but are
> unused by V2.

## Module Dependency Graph

```mermaid
graph LR
    subgraph "API"
        MAIN[main.py]
        ROUTES[api/v2_routes.py]
        AUTH[api/auth.py]
        RL[api/rate_limit.py]
        VER[version.py]
        CONFIG[config.py]
    end
    subgraph "Pipeline"
        ORCH[orchestrator.py]
        PRE[image_preprocessor.py]
        FL[face_landmarker.py]
        HP[head_pose.py]
        QG[quality_gate.py]
        CAL[pixel_calibration.py]
        REC[multiview_reconstruction.py]
    end
    subgraph "Analysis"
        ENG[symmetry / proportion / profile / volume / aging]
        FUSE[multi_view_fusion.py]
        ZA[zone_analyzer.py]
        OV[overlay.py]
        CMP[comparison_engine.py]
    end
    subgraph "Treatment"
        ZD[zone_definitions.py]
        PDB[product_database.py]
        PLAN[plan_generator.py]
        CONTRA[contraindication_check.py]
    end
    subgraph "Models / Services"
        SCH[schemas_v2.py / zone_models.py]
        SUPA[supabase_service.py]
        N8NS[n8n_service.py]
        PDFR[pdf_report.py]
    end

    MAIN --> ROUTES & AUTH & RL & VER
    ROUTES --> ORCH & SCH & SUPA & N8NS & PDFR & VER
    ORCH --> PRE & FL & HP & QG & CAL & REC & ZA & PLAN & OV
    ZA --> ENG & FUSE & ZD
    ENG --> REC & FL & CAL
    PLAN --> PDB & CONTRA & ZD
    CMP --> ZA
    SUPA --> CONFIG
    N8NS --> CONFIG & VER
    PDFR --> SCH

    style MAIN fill:#009688,color:#fff
    style FL fill:#FF5722,color:#fff
    style REC fill:#7E57C2,color:#fff
    style SCH fill:#2196F3,color:#fff
```

## n8n Integration Flow

```mermaid
graph LR
    API[Biometrics API] -->|notify_n8n_v2 envelope| WH[n8n Webhook Trigger]
    WH --> PARSE[Parse envelope<br/>event, assessment_id, aesthetic_score, zones_count]
    PARSE --> COND{Route on<br/>score / warnings}
    COND -->|low score / concerns| REPORT[Pull /api/v2/report PDF]
    COND -->|quality warnings| NOTIFY[Alert: re-capture]
    REPORT --> DASH[Update dashboard]
    REPORT --> SCHEDULE[Schedule follow-up]

    style API fill:#009688,color:#fff
    style WH fill:#FF6D5A,color:#fff
```
