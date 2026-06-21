"""Frontend overlay data — injection points + zone heatmap (Task 12).

Turns a ZoneReport plus the per-view detections into coordinate data a frontend
can paint on the analyzed photo:

- injection points: the zone's clinically relevant landmarks, as normalized
  [0,1] (x, y) in the view the zone is anchored on, so the UI can drop markers;
- a heatmap anchor (zone-landmark centroid) with an intensity (severity / 10) and
  a severity-graded colour, so the UI can render a treatment-need heatmap.

Coordinates are normalized to the ANALYZED (preprocessed / face-centred) frame the
landmarks were detected in — not necessarily the original upload. The per-view
`image_dimensions` give that frame's pixel size. Pure functions, no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import ZONE_LANDMARKS

# Severity → heatmap colour (treatment need). Matches the report's severity bands.
_COLOR_HIGH = "#dc2626"    # >= 6 : marked
_COLOR_MED = "#f59e0b"     # >= 3 : moderate
_COLOR_LOW = "#22c55e"     # <  3 : minimal


@dataclass
class InjectionPoint:
    """One candidate injection landmark, normalized to the anchor view's frame."""
    landmark_index: int
    x: float  # normalized [0,1]
    y: float


@dataclass
class ZoneOverlay:
    """Overlay + heatmap data for one zone."""
    zone_id: str
    zone_name: str
    region: str
    view: str               # which view's image these coordinates map to
    severity: float
    intensity: float        # severity / 10, clamped to [0,1] — heatmap weight/alpha
    color_code: str
    centroid_x: float       # heatmap anchor (normalized)
    centroid_y: float
    injection_points: list[InjectionPoint] = field(default_factory=list)


@dataclass
class OverlayData:
    """Complete overlay payload across zones."""
    zones: list[ZoneOverlay] = field(default_factory=list)
    # per anchor view: {"width": int, "height": int} of the analyzed frame
    image_dimensions: dict[str, dict[str, int]] = field(default_factory=dict)
    # Which PHYSICAL oblique upload the canonical "oblique" overlay was computed on
    # ("oblique_left" | "oblique_right" | "oblique"), or None when no oblique view
    # contributed. Set by the orchestrator; lets a frontend place the oblique
    # heatmap on the correct uploaded photo (both obliques look alike otherwise).
    canonical_oblique_view: str | None = None


def _severity_color(severity: float) -> str:
    if severity >= 6.0:
        return _COLOR_HIGH
    if severity >= 3.0:
        return _COLOR_MED
    return _COLOR_LOW


def build_overlay(
    zone_report,
    view_detections: dict[str, DetectionResult],
    view_transforms: dict[str, dict] | None = None,
) -> OverlayData:
    """Build injection-point + heatmap overlay data for the analyzed zones.

    Args:
        zone_report: ZoneReport with ranked zones (each carries primary_view).
        view_detections: canonical view name -> DetectionResult, e.g.
            {"frontal": det, "profile": det, "oblique": det}. The oblique entry
            should be the detection driving the volume engine (the canonical
            oblique). Detections are used only for landmark coordinates.
        view_transforms: optional canonical view name -> source-transform dict
            (source_width/height, crop_x/y/width/height) mapping the analyzed frame
            back to the EXIF-corrected upload. Merged into `image_dimensions` so a
            frontend can place markers on the original image:
                orig_norm_x = (crop_x + x * crop_width)  / source_width
                orig_norm_y = (crop_y + y * crop_height) / source_height

    Returns:
        OverlayData. Zones whose primary view is unavailable, or that have no
        discrete injection landmarks (e.g. Forehead, profile-line zones), are
        skipped — their absence is intentional, not an error.
    """
    overlay = OverlayData()
    view_transforms = view_transforms or {}

    # Record analyzed-frame dimensions (+ source back-transform) per available view.
    for view, det in view_detections.items():
        if det is not None:
            dims = {
                "width": int(det.image_width),
                "height": int(det.image_height),
            }
            tf = view_transforms.get(view)
            if tf is not None:
                dims.update({k: int(v) for k, v in tf.items()})
            overlay.image_dimensions[view] = dims

    for zone in zone_report.zones:
        anchors = ZONE_LANDMARKS.get(zone.zone_id)
        if anchors is None or not anchors.primary_landmarks:
            continue  # no discrete injection landmarks for this zone

        det = view_detections.get(zone.primary_view)
        if det is None:
            # Fall back to frontal if the primary view wasn't captured.
            det = view_detections.get("frontal")
            anchor_view = "frontal" if det is not None else None
        else:
            anchor_view = zone.primary_view
        if det is None:
            continue

        points: list[InjectionPoint] = []
        xs: list[float] = []
        ys: list[float] = []
        for idx in anchors.primary_landmarks:
            if idx >= det.num_landmarks:
                continue
            nx = float(det.landmarks[idx][0])
            ny = float(det.landmarks[idx][1])
            points.append(InjectionPoint(landmark_index=int(idx), x=round(nx, 5), y=round(ny, 5)))
            xs.append(nx)
            ys.append(ny)

        if not points:
            continue

        overlay.zones.append(ZoneOverlay(
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            region=zone.region,
            view=anchor_view,
            severity=round(zone.severity, 1),
            intensity=round(min(1.0, max(0.0, zone.severity / 10.0)), 3),
            color_code=_severity_color(zone.severity),
            centroid_x=round(sum(xs) / len(xs), 5),
            centroid_y=round(sum(ys) / len(ys), 5),
            injection_points=points,
        ))

    return overlay
