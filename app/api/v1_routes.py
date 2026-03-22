import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from app.models.schemas import (
    AnalysisResponse, ViewAngle, QualityWarning,
)
from app.core.landmark_detector import LandmarkDetector
from app.core.image_validator import validate_image
from app.core.frontal_analyzer import analyze_frontal
from app.core.profile_analyzer import analyze_profile
from app.core.oblique_analyzer import analyze_oblique
from app.services.supabase_service import save_analysis, fetch_image_from_url
from app.services.n8n_service import notify_n8n
from app.config import settings

router = APIRouter()
detector = LandmarkDetector(min_confidence=settings.min_face_confidence)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    view_angle: ViewAngle = Query(..., description="Camera perspective: frontal, oblique, profile"),
    patient_id: str | None = Query(None, description="Optional patient UUID for Supabase storage"),
    image_url: str | None = Query(None, description="Supabase storage URL (alternative to file upload)"),
    file: UploadFile | None = File(None, description="Image file (JPEG/PNG)"),
):
    """
    Analyze a facial image from the specified view angle.
    Provide either `file` (multipart upload) or `image_url` (Supabase storage link).
    """
    # Load image bytes
    if file:
        contents = await file.read()
        if len(contents) > settings.max_image_size_mb * 1024 * 1024:
            raise HTTPException(413, f"Image exceeds {settings.max_image_size_mb}MB limit")
    elif image_url:
        try:
            contents = await fetch_image_from_url(image_url)
        except Exception as e:
            raise HTTPException(400, f"Failed to fetch image from URL: {e}")
    else:
        raise HTTPException(400, "Provide either 'file' or 'image_url'")

    # Decode image
    arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Could not decode image. Ensure it is a valid JPEG or PNG.")

    # Quality checks
    warnings = validate_image(image)

    # Detect landmarks
    landmarks = detector.detect(image)
    if landmarks is None:
        raise HTTPException(
            422,
            "No face detected. Ensure the face is clearly visible, well-lit, and facing the correct angle.",
        )

    if landmarks.confidence < settings.min_face_confidence:
        warnings.append(QualityWarning(
            code="LOW_CONFIDENCE",
            message=f"Detection confidence {landmarks.confidence:.2f} is below threshold {settings.min_face_confidence}.",
        ))

    # Run view-specific analysis
    if view_angle == ViewAngle.FRONTAL:
        analysis = analyze_frontal(landmarks)
    elif view_angle == ViewAngle.PROFILE:
        analysis = analyze_profile(landmarks)
    elif view_angle == ViewAngle.OBLIQUE:
        analysis = analyze_oblique(landmarks)
    else:
        raise HTTPException(400, f"Unsupported view angle: {view_angle}")

    response = AnalysisResponse(
        patient_id=patient_id,
        view_angle=view_angle,
        analysis=analysis,
        quality_warnings=warnings,
        landmarks_detected=len(landmarks.points),
        confidence=round(landmarks.confidence, 3),
        metadata={
            "image_size": f"{image.shape[1]}x{image.shape[0]}",
            "view_angle": view_angle.value,
        },
    )

    # Persist to Supabase if patient_id given
    if patient_id and settings.supabase_url:
        try:
            await save_analysis(patient_id, view_angle.value, response.model_dump())
        except Exception:
            warnings.append(QualityWarning(
                code="STORAGE_ERROR",
                message="Analysis completed but could not be saved to database.",
            ))

    # Notify n8n webhook
    if settings.n8n_webhook_url:
        await notify_n8n(response.model_dump())

    return response


@router.get("/health")
async def health():
    return {"status": "ok", "service": "aesthetic-biometrics-engine"}
