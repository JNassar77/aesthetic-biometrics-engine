-- Patients table
CREATE TABLE IF NOT EXISTS public.patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Biometric analyses: stores each individual view analysis
CREATE TABLE IF NOT EXISTS public.biometric_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    view_angle TEXT NOT NULL CHECK (view_angle IN ('frontal', 'oblique', 'profile')),
    result_json JSONB NOT NULL,
    confidence REAL NOT NULL DEFAULT 0,
    landmarks_detected INTEGER NOT NULL DEFAULT 0,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Treatment sessions: groups before/after analyses
CREATE TABLE IF NOT EXISTS public.treatment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    treatment_type TEXT NOT NULL,
    treatment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    notes TEXT,
    pre_analysis_ids UUID[] DEFAULT '{}',
    post_analysis_ids UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_analyses_patient ON public.biometric_analyses(patient_id);
CREATE INDEX IF NOT EXISTS idx_analyses_view ON public.biometric_analyses(view_angle);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON public.biometric_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_patient ON public.treatment_sessions(patient_id);

-- Enable RLS
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.biometric_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.treatment_sessions ENABLE ROW LEVEL SECURITY;

-- Policies for service role access
CREATE POLICY "Service access for patients" ON public.patients FOR ALL USING (true);
CREATE POLICY "Service access for analyses" ON public.biometric_analyses FOR ALL USING (true);
CREATE POLICY "Service access for sessions" ON public.treatment_sessions FOR ALL USING (true);
