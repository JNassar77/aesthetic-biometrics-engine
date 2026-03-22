"""
n8n webhook integration service.

Sends V2 AssessmentResponse payloads to n8n for downstream processing.
Non-blocking — failures are logged but never halt the API response.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def notify_n8n(payload: dict[str, Any]) -> bool:
    """Send analysis result to n8n webhook for downstream processing.

    Args:
        payload: Serialized AssessmentResponse (V2) or AnalysisResponse (V1).

    Returns:
        True if webhook accepted the payload (HTTP < 400), False otherwise.
    """
    if not settings.n8n_webhook_url:
        return False

    try:
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                settings.n8n_webhook_url,
                json=payload,
                timeout=15,
            )
            if resp.status_code >= 400:
                logger.warning(
                    "n8n webhook returned %d: %s",
                    resp.status_code,
                    resp.text[:200],
                )
                return False
            return True
    except httpx.HTTPError as exc:
        logger.warning("n8n webhook failed: %s", exc)
        return False


async def notify_n8n_v2(
    assessment_id: str,
    patient_id: str | None,
    aesthetic_score: float,
    zones_count: int,
    views_analyzed: list[str],
    payload: dict[str, Any],
) -> bool:
    """Send a V2 assessment notification to n8n with summary metadata.

    Wraps the full payload with top-level keys that n8n workflows
    can filter/route on without parsing the full JSON.

    Args:
        assessment_id: UUID of the assessment.
        patient_id: Optional patient UUID.
        aesthetic_score: Overall aesthetic score (0-100).
        zones_count: Number of zones analyzed.
        views_analyzed: List of view names processed.
        payload: Full serialized AssessmentResponse.

    Returns:
        True on success, False on failure.
    """
    if not settings.n8n_webhook_url:
        return False

    envelope = {
        "event": "assessment_complete",
        "engine_version": "2.0.0",
        "assessment_id": assessment_id,
        "patient_id": patient_id,
        "aesthetic_score": aesthetic_score,
        "zones_count": zones_count,
        "views_analyzed": views_analyzed,
        "data": payload,
    }

    return await notify_n8n(envelope)
