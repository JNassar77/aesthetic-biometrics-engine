-- Replace overly permissive V1 policies with service_role-only access
DROP POLICY IF EXISTS "Service access for analyses" ON biometric_analyses;
DROP POLICY IF EXISTS "Service access for patients" ON patients;
DROP POLICY IF EXISTS "Service access for sessions" ON treatment_sessions;

-- V1 tables: service_role only (API backend uses service_role key)
CREATE POLICY "service_role_analyses" ON biometric_analyses
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_sessions" ON treatment_sessions
    FOR ALL USING (auth.role() = 'service_role');
