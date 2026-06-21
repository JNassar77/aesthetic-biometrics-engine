-- =====================================================
-- V2 RLS Policies: Organization-Level Isolation
-- =====================================================
-- organization_id is extracted from JWT claims.
-- Praxis A never sees data from Praxis B.

-- Organizations: users can only see their own org
CREATE POLICY "org_select_own" ON organizations
    FOR SELECT
    USING (id::text = (auth.jwt() ->> 'organization_id'));

-- Patients: org isolation
CREATE POLICY "patients_org_isolation" ON patients
    FOR ALL
    USING (organization_id::text = (auth.jwt() ->> 'organization_id'));

-- Assessments: org isolation
CREATE POLICY "assessments_org_isolation" ON assessments
    FOR ALL
    USING (organization_id::text = (auth.jwt() ->> 'organization_id'));

-- Treatment Comparisons: org isolation
CREATE POLICY "comparisons_org_isolation" ON treatment_comparisons
    FOR ALL
    USING (organization_id::text = (auth.jwt() ->> 'organization_id'));

-- Service role bypass: allow the API backend (service_role key) full access
CREATE POLICY "service_role_full_access_orgs" ON organizations
    FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "service_role_full_access_patients" ON patients
    FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "service_role_full_access_assessments" ON assessments
    FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "service_role_full_access_comparisons" ON treatment_comparisons
    FOR ALL
    USING (auth.role() = 'service_role');
