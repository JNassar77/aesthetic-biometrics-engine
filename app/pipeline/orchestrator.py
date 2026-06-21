"""
Pipeline Orchestrator — connects all V2 analysis components.

Receives 3 images (frontal, profile, oblique), runs the full pipeline:
1. Preprocess each image
2. Detect landmarks + blendshapes + transformation matrix
3. Calibrate px→mm
4. Run zone analysis (all engines + fusion)
5. Generate treatment plan
6. Return structured AssessmentResponse

This is a pure orchestration layer — no I/O (database, HTTP).
I/O happens at the API route level (Supabase storage, persistence).
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from uuid import UUID, uuid4

import numpy as np

from app.detection.face_landmarker import (
    DetectionResult,
    FaceLandmarkerV2,
    NoFaceResult,
)
from app.detection.head_pose import extract_head_pose, HeadPose
from app.pipeline.image_preprocessor import (
    preprocess,
    reprocess_with_face_center,
    compute_face_crop_rect,
)
from app.pipeline.quality_gate import (
    QualityWarning,
    check_image_quality,
    check_head_pose,
    check_hard_pose_rejection,
    check_neutral_expression,
    compute_expression_deviation,
)
from app.utils.pixel_calibration import calibrate, CalibrationResult
from app.analysis.zone_analyzer import ViewInput, ZoneReport, analyze as zone_analyze
from app.analysis.multiview_reconstruction import (
    Reconstruction3D,
    reconstruct_from_views,
)
from app.analysis.overlay import OverlayData, build_overlay
from app.treatment.plan_generator import TreatmentPlan, generate as plan_generate
from app.models.zone_models import CalibrationInfo


# ──────────────────────── Data Containers ────────────────────────

@dataclass
class ViewResult:
    """Result of processing one view through the pipeline."""
    view: str  # "frontal", "profile", "oblique"
    image: np.ndarray | None = None
    detection: DetectionResult | None = None
    head_pose: HeadPose | None = None
    calibration: CalibrationResult | None = None
    quality_warnings: list[QualityWarning] = field(default_factory=list)
    accepted: bool = True
    confidence: float = 0.0
    rejection_reason: str | None = None
    # Maps the analyzed (face-cropped) frame back to the EXIF-corrected upload, so
    # overlay coordinates can be placed on the original image. Keys: source_width,
    # source_height, crop_x, crop_y, crop_width, crop_height (identity = full frame).
    source_transform: dict[str, int] | None = None


@dataclass
class PipelineResult:
    """Complete result of the orchestration pipeline."""
    assessment_id: UUID = field(default_factory=uuid4)
    zone_report: ZoneReport | None = None
    treatment_plan: TreatmentPlan | None = None
    view_results: dict[str, ViewResult] = field(default_factory=dict)
    reconstruction: Reconstruction3D | None = None
    overlay: OverlayData | None = None
    processing_time_ms: int = 0
    views_analyzed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ──────────────────────── Single View Processing ────────────────────────

def _process_single_view(
    image_bytes: bytes,
    view: str,
    landmarker: FaceLandmarkerV2,
) -> ViewResult:
    """Process a single view through preprocessing → detection → calibration.

    Args:
        image_bytes: Raw image bytes (JPEG/PNG)
        view: View angle — "frontal", "profile", or "oblique"
        landmarker: Shared FaceLandmarkerV2 instance

    Returns:
        ViewResult with detection, calibration, and quality info.
    """
    result = ViewResult(view=view)

    # Step 1: Preprocess (EXIF, resize, normalize)
    image = preprocess(image_bytes, apply_face_crop=False)
    if image is None:
        result.accepted = False
        result.rejection_reason = "IMAGE_DECODE_FAILED"
        result.quality_warnings.append(QualityWarning(
            code="IMAGE_DECODE_FAILED",
            message="Could not decode image. Ensure it is a valid JPEG or PNG.",
            severity="critical",
        ))
        return result

    # Step 2: Quality checks on raw image
    image_quality_warnings = check_image_quality(image)
    result.quality_warnings.extend(image_quality_warnings)

    # Step 3: Detect landmarks
    detection = landmarker.detect(image)

    if isinstance(detection, NoFaceResult) or not detection.face_detected:
        result.accepted = False
        result.rejection_reason = "NO_FACE_DETECTED"
        result.quality_warnings.append(QualityWarning(
            code="NO_FACE_DETECTED",
            message=f"No face detected in {view} image.",
            severity="critical",
        ))
        return result

    # Source (EXIF-corrected upload) dimensions, before the face-centred re-crop.
    src_h, src_w = image.shape[:2]

    # Step 4: Reprocess with face center for better accuracy
    reprocessed = reprocess_with_face_center(
        image,
        detection.landmarks,
        detection.image_width,
        detection.image_height,
    )

    # Re-detect on reprocessed image
    detection2 = landmarker.detect(reprocessed)
    if isinstance(detection2, NoFaceResult) or not detection2.face_detected:
        # Fallback to original detection — analyzed frame == source frame (identity).
        detection2 = detection
        result.source_transform = {
            "source_width": src_w, "source_height": src_h,
            "crop_x": 0, "crop_y": 0, "crop_width": src_w, "crop_height": src_h,
        }
    else:
        # Analyzed frame is the face crop of the source frame; record the rect so
        # overlay coords can be mapped back to the original upload.
        x1, y1, x2, y2 = compute_face_crop_rect(detection.landmarks, src_w, src_h)
        result.source_transform = {
            "source_width": src_w, "source_height": src_h,
            "crop_x": x1, "crop_y": y1,
            "crop_width": max(1, x2 - x1), "crop_height": max(1, y2 - y1),
        }
        image = reprocessed
        detection = detection2

    result.image = image
    result.detection = detection

    # Step 5: Head pose
    if detection.transformation_matrix is not None:
        result.head_pose = extract_head_pose(detection.transformation_matrix)

        # Pose validation. The bilateral obliques share the generic "oblique"
        # pose tolerances (the quality gate validates |yaw| range, not the turn
        # direction), so map oblique_left/oblique_right onto "oblique".
        pose_view = "oblique" if view.startswith("oblique") else view

        if result.head_pose:
            pose_warnings = check_head_pose(result.head_pose, pose_view)
            result.quality_warnings.extend(pose_warnings)

            hard_rejection = check_hard_pose_rejection(result.head_pose, pose_view)
            if hard_rejection:
                result.quality_warnings.append(hard_rejection)
                result.accepted = False
                result.rejection_reason = "HEAD_POSE_REJECTED"
                return result

    # Step 6: Expression check (frontal only)
    if view == "frontal" and detection.blendshapes:
        expression_warnings = check_neutral_expression(detection.blendshapes)
        result.quality_warnings.extend(expression_warnings)

    # Step 7: Calibrate px→mm
    result.calibration = calibrate(
        detection.landmarks,
        detection.image_width,
        detection.image_height,
    )
    if result.calibration.warnings:
        for w in result.calibration.warnings:
            result.quality_warnings.append(QualityWarning(
                code="CALIBRATION_WARNING",
                message=w,
                severity="low",
            ))

    # Confidence = detection + calibration average
    cal_conf = result.calibration.confidence if result.calibration else 0.5
    result.confidence = cal_conf

    return result


# ──────────────────────── Main Orchestrator ────────────────────────

_landmarker_singleton: FaceLandmarkerV2 | None = None
_landmarker_lock = threading.Lock()


def get_landmarker() -> FaceLandmarkerV2:
    """Return a process-wide shared FaceLandmarkerV2, created on first use.

    The model (~3.6 MB) is loaded once and reused; the landmarker serializes
    its own detect() calls internally, so it is safe to share across threads.
    """
    global _landmarker_singleton
    if _landmarker_singleton is None:
        with _landmarker_lock:
            if _landmarker_singleton is None:
                _landmarker_singleton = FaceLandmarkerV2()
    return _landmarker_singleton


def run_pipeline(
    frontal_bytes: bytes | None = None,
    profile_bytes: bytes | None = None,
    oblique_bytes: bytes | None = None,
    oblique_left_bytes: bytes | None = None,
    oblique_right_bytes: bytes | None = None,
    patient_id: UUID | None = None,
    landmarker: FaceLandmarkerV2 | None = None,
) -> PipelineResult:
    """Run the complete V2 analysis pipeline.

    Preferred capture protocol is four views — frontal (0°), 45° left, 45° right,
    90° profile. The bilateral obliques drive the metric 3D reconstruction (wider
    angular spread, both cheeks); the profile carries the 2D sagittal profile
    lines. A single generic `oblique` is still accepted for back-compatibility.

    Args:
        frontal_bytes: Raw frontal image bytes
        profile_bytes: Raw profile image bytes
        oblique_bytes: Raw generic oblique image bytes (back-compat)
        oblique_left_bytes: Raw left 45° oblique image bytes
        oblique_right_bytes: Raw right 45° oblique image bytes
        patient_id: Optional patient UUID for Supabase linkage
        landmarker: Optional shared FaceLandmarkerV2 (created if None)

    Returns:
        PipelineResult with zone_report, treatment_plan, reconstruction, and
        per-view quality.
    """
    start_time = time.monotonic()
    pipeline_result = PipelineResult()

    # Initialize landmarker if not provided (shared process-wide singleton)
    if landmarker is None:
        try:
            landmarker = get_landmarker()
        except FileNotFoundError as e:
            pipeline_result.errors.append(str(e))
            return pipeline_result

    # ── Step 1: Process each view ──
    view_map = {
        "frontal": frontal_bytes,
        "profile": profile_bytes,
        "oblique": oblique_bytes,
        "oblique_left": oblique_left_bytes,
        "oblique_right": oblique_right_bytes,
    }

    for view_name, image_bytes in view_map.items():
        if image_bytes is None:
            continue

        view_result = _process_single_view(image_bytes, view_name, landmarker)
        pipeline_result.view_results[view_name] = view_result

        if view_result.accepted and view_result.detection is not None:
            pipeline_result.views_analyzed.append(view_name)

    # Check that at least one view was successfully processed
    if not pipeline_result.views_analyzed:
        pipeline_result.errors.append(
            "No views could be processed. At least one image must contain a detectable face."
        )
        pipeline_result.processing_time_ms = int(
            (time.monotonic() - start_time) * 1000
        )
        return pipeline_result

    # ── Step 2: Build ViewInput objects for zone analyzer ──
    view_inputs: dict[str, ViewInput] = {}
    for view_name in pipeline_result.views_analyzed:
        vr = pipeline_result.view_results[view_name]
        if vr.detection is None or vr.calibration is None:
            continue
        view_inputs[view_name] = ViewInput(
            detection=vr.detection,
            calibration=vr.calibration,
            blendshapes=vr.detection.blendshapes or {},
        )

    frontal_input = view_inputs.get("frontal")
    profile_input = view_inputs.get("profile")
    oblique_input = view_inputs.get("oblique")
    oblique_left_input = view_inputs.get("oblique_left")
    oblique_right_input = view_inputs.get("oblique_right")

    # ── Step 2b: Metric 3D reconstruction (frontal + bilateral obliques) ──
    # The reconstruction policy (in multiview_reconstruction) excludes the profile
    # and requires a reliable iris calibration per contributing view.
    reconstruction = reconstruct_from_views(
        (view_name, vr.detection, vr.calibration)
        for view_name, vr in pipeline_result.view_results.items()
        if vr.accepted and vr.detection is not None and vr.calibration is not None
    )
    pipeline_result.reconstruction = reconstruction

    # ── Step 3: Run zone analysis ──
    try:
        zone_report = zone_analyze(
            frontal=frontal_input,
            profile=profile_input,
            oblique=oblique_input,
            oblique_left=oblique_left_input,
            oblique_right=oblique_right_input,
            reconstruction=reconstruction,
        )
        pipeline_result.zone_report = zone_report
    except Exception as e:
        pipeline_result.errors.append(f"Zone analysis failed: {e}")
        pipeline_result.processing_time_ms = int(
            (time.monotonic() - start_time) * 1000
        )
        return pipeline_result

    # ── Step 3b: Frontend overlay data (injection points + heatmap) ──
    # Canonical oblique = highest-confidence oblique (matches zone_analyzer).
    oblique_candidates = [
        v for v in (oblique_left_input, oblique_right_input, oblique_input) if v is not None
    ]
    canonical_oblique_input = (
        max(oblique_candidates, key=lambda v: v.calibration.confidence)
        if oblique_candidates else None
    )
    # Map canonical view name → (detection, source_transform) for the overlay.
    canonical_oblique_name = None
    if canonical_oblique_input is not None:
        canonical_oblique_name = next(
            (n for n in ("oblique_left", "oblique_right", "oblique")
             if view_inputs.get(n) is canonical_oblique_input),
            None,
        )
    view_detections = {}
    view_transforms: dict[str, dict] = {}
    for canon, vname in (("frontal", "frontal"), ("profile", "profile"),
                         ("oblique", canonical_oblique_name)):
        vi = view_inputs.get(vname) if vname else None
        if vi is not None:
            view_detections[canon] = vi.detection
            vr = pipeline_result.view_results.get(vname)
            if vr is not None and vr.source_transform is not None:
                view_transforms[canon] = vr.source_transform
    try:
        pipeline_result.overlay = build_overlay(zone_report, view_detections, view_transforms)
        # Tell the frontend which physical oblique the canonical "oblique" overlay
        # maps to, so it can paint the heatmap on the correct uploaded photo.
        pipeline_result.overlay.canonical_oblique_view = canonical_oblique_name
    except Exception as e:
        pipeline_result.errors.append(f"Overlay generation failed: {e}")
        # Non-blocking: overlay is optional frontend data.

    # ── Step 4: Generate treatment plan ──
    try:
        treatment_plan = plan_generate(zone_report.zones)
        pipeline_result.treatment_plan = treatment_plan
    except Exception as e:
        pipeline_result.errors.append(f"Treatment plan generation failed: {e}")
        # Non-blocking: return zone report without plan

    # ── Step 5: Finalize ──
    pipeline_result.processing_time_ms = int(
        (time.monotonic() - start_time) * 1000
    )

    return pipeline_result
