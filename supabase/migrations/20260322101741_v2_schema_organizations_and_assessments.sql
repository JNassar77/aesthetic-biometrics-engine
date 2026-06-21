-- =====================================================
-- V2 Schema Migration: Multi-Tenant + Zone-Based Analysis
-- =====================================================

-- 1. Organizations (Multi-Tenant Root)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Add organization_id to patients (nullable for backward compat with V1 data)
ALTER TABLE patients
    ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- 3. Assessments: a complete 3-view assessment
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'processing'
        CHECK (status IN ('processing', 'completed', 'failed', 'partial')),

    -- Image references (Supabase Storage Bucket paths)
    frontal_image_path TEXT,
    profile_image_path TEXT,
    oblique_image_path TEXT,

    -- Quality
    image_quality JSONB,

    -- Analysis results
    global_metrics JSONB,
    zones JSONB,
    treatment_plan JSONB,
    blendshapes JSONB,
    aesthetic_score REAL,
    calibration_method TEXT,

    -- Metadata
    engine_version TEXT NOT NULL DEFAULT '2.0.0',
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Treatment Comparisons (Before/After)
CREATE TABLE IF NOT EXISTS treatment_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    pre_assessment_id UUID REFERENCES assessments(id),
    post_assessment_id UUID REFERENCES assessments(id),
    treatment_date DATE NOT NULL,
    treatment_notes TEXT,
    zone_deltas JSONB,
    improvement_score REAL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Indexes
CREATE INDEX IF NOT EXISTS idx_patients_org ON patients(organization_id);
CREATE INDEX IF NOT EXISTS idx_assessments_org ON assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_assessments_patient_date ON assessments(patient_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comparisons_org ON treatment_comparisons(organization_id);
CREATE INDEX IF NOT EXISTS idx_comparisons_patient ON treatment_comparisons(patient_id);

-- 6. Enable RLS on new tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE treatment_comparisons ENABLE ROW LEVEL SECURITY;
