-- Storage RLS: organization-scoped access to patient images
-- Folder structure: {organization_id}/{patient_id}/{assessment_id}/{view}.jpg

CREATE POLICY "org_images_select" ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'patient-images'
        AND (storage.foldername(name))[1] = (auth.jwt() ->> 'organization_id')
    );

CREATE POLICY "org_images_insert" ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'patient-images'
        AND (storage.foldername(name))[1] = (auth.jwt() ->> 'organization_id')
    );

CREATE POLICY "org_images_delete" ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'patient-images'
        AND (storage.foldername(name))[1] = (auth.jwt() ->> 'organization_id')
    );

-- Service role: full access
CREATE POLICY "service_role_storage" ON storage.objects
    FOR ALL
    USING (
        bucket_id = 'patient-images'
        AND auth.role() = 'service_role'
    );
