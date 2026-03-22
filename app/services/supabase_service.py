"""
Supabase integration service.

Handles:
- V1 legacy: save_analysis, fetch_image_from_url
- V2: save_assessment, get_assessment, get_patient_history, upload_image,
       save_comparison
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx
from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


# ──────────────────────── V1 Legacy ────────────────────────


async def save_analysis(patient_id: str, view_angle: str, result: dict) -> dict:
    """Insert analysis result into Supabase (V1 legacy)."""
    client = get_client()
    row = {
        "patient_id": patient_id,
        "view_angle": view_angle,
        "result_json": result,
        "confidence": result.get("confidence", 0),
        "landmarks_detected": result.get("landmarks_detected", 0),
    }
    resp = client.table("biometric_analyses").insert(row).execute()
    return resp.data[0] if resp.data else {}


async def fetch_image_from_url(url: str) -> bytes:
    """Download image bytes from a Supabase storage URL."""
    async with httpx.AsyncClient() as http:
        resp = await http.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content


# ──────────────────────── V2 Assessment Persistence ────────────────────────


async def save_assessment(
    assessment_id: UUID,
    organization_id: UUID,
    patient_id: UUID | None,
    status: str,
    image_quality: dict[str, Any] | None,
    global_metrics: dict[str, Any] | None,
    zones: list[dict[str, Any]] | None,
    treatment_plan: dict[str, Any] | None,
    aesthetic_score: float | None,
    calibration_method: str | None,
    engine_version: str,
    processing_time_ms: int | None,
    frontal_image_path: str | None = None,
    profile_image_path: str | None = None,
    oblique_image_path: str | None = None,
) -> dict:
    """Insert a V2 assessment into the assessments table.

    Returns:
        The inserted row as a dict, or empty dict on failure.
    """
    client = get_client()
    row: dict[str, Any] = {
        "id": str(assessment_id),
        "organization_id": str(organization_id),
        "status": status,
        "image_quality": image_quality,
        "global_metrics": global_metrics,
        "zones": zones,
        "treatment_plan": treatment_plan,
        "aesthetic_score": aesthetic_score,
        "calibration_method": calibration_method,
        "engine_version": engine_version,
        "processing_time_ms": processing_time_ms,
        "frontal_image_path": frontal_image_path,
        "profile_image_path": profile_image_path,
        "oblique_image_path": oblique_image_path,
    }
    if patient_id:
        row["patient_id"] = str(patient_id)

    resp = client.table("assessments").insert(row).execute()
    return resp.data[0] if resp.data else {}


async def get_assessment(assessment_id: UUID) -> dict | None:
    """Fetch a single assessment by ID.

    Returns:
        The assessment row as a dict, or None if not found.
    """
    client = get_client()
    resp = (
        client.table("assessments")
        .select("*")
        .eq("id", str(assessment_id))
        .execute()
    )
    if resp.data:
        return resp.data[0]
    return None


async def get_patient_history(
    patient_id: UUID,
    limit: int = 50,
) -> list[dict]:
    """Fetch all assessments for a patient, ordered by created_at DESC.

    Returns:
        List of assessment rows.
    """
    client = get_client()
    resp = (
        client.table("assessments")
        .select(
            "id, patient_id, status, aesthetic_score, zones, "
            "engine_version, processing_time_ms, created_at"
        )
        .eq("patient_id", str(patient_id))
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


# ──────────────────────── V2 Comparison Persistence ────────────────────────


async def save_comparison(
    organization_id: UUID,
    patient_id: UUID | None,
    pre_assessment_id: UUID,
    post_assessment_id: UUID,
    treatment_date: str,
    treatment_notes: str | None,
    zone_deltas: list[dict[str, Any]],
    improvement_score: float,
) -> dict:
    """Insert a treatment comparison record.

    Returns:
        The inserted row as a dict, or empty dict on failure.
    """
    client = get_client()
    row: dict[str, Any] = {
        "organization_id": str(organization_id),
        "pre_assessment_id": str(pre_assessment_id),
        "post_assessment_id": str(post_assessment_id),
        "treatment_date": treatment_date,
        "treatment_notes": treatment_notes,
        "zone_deltas": zone_deltas,
        "improvement_score": improvement_score,
    }
    if patient_id:
        row["patient_id"] = str(patient_id)

    resp = client.table("treatment_comparisons").insert(row).execute()
    return resp.data[0] if resp.data else {}


# ──────────────────────── V2 Image Storage ────────────────────────


async def upload_image(
    bucket: str,
    path: str,
    image_bytes: bytes,
    content_type: str = "image/jpeg",
) -> str | None:
    """Upload an image to Supabase Storage.

    Args:
        bucket: Storage bucket name (e.g. "patient-images").
        path: Object path within the bucket (e.g. "org-id/assessment-id/frontal.jpg").
        image_bytes: Raw image bytes.
        content_type: MIME type.

    Returns:
        The storage path on success, None on failure.
    """
    try:
        client = get_client()
        client.storage.from_(bucket).upload(
            path,
            image_bytes,
            file_options={"content-type": content_type},
        )
        return path
    except Exception as exc:
        logger.warning("Image upload failed (%s): %s", path, exc)
        return None
