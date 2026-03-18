"""
Oblique (45 deg) Analysis
=========================
Measurements:
  1. Ogee curve: S-shaped convexity from forehead through malar eminence
     to the buccal region. Evaluates midface volume.

Mathematical basis:
  - Sample key points along the expected ogee path: temporal, malar high,
    malar low, buccal hollow approximation.
  - Compute curvature as the deviation of intermediate points from
    a straight line connecting the endpoints.
  - A well-defined double convexity indicates adequate volume.
  - Flattening indicates volume loss amenable to filler.
  - Malar prominence ratio: distance from malar high point to the
    facial midline, normalized by face width.
"""

import numpy as np
from app.core.landmark_detector import FaceLandmarks, LANDMARKS
from app.models.schemas import ObliqueAnalysis, OgeeCurve
from app.utils.geometry import euclidean_2d, point_to_line_distance, px_to_mm_estimate


def analyze_oblique(lm: FaceLandmarks) -> ObliqueAnalysis:
    ogee = _compute_ogee_curve(lm)
    return ObliqueAnalysis(ogee_curve=ogee)


def _compute_ogee_curve(lm: FaceLandmarks) -> OgeeCurve:
    # Ogee path points (using the more visible side in oblique view)
    # We use both sides and pick the one with larger lateral spread
    left_mh = lm.px(LANDMARKS["left_malar_high"])
    right_mh = lm.px(LANDMARKS["right_malar_high"])
    left_ml = lm.px(LANDMARKS["left_malar_low"])
    right_ml = lm.px(LANDMARKS["right_malar_low"])
    left_cb = lm.px(LANDMARKS["left_cheekbone"])
    right_cb = lm.px(LANDMARKS["right_cheekbone"])

    glabella = lm.px(LANDMARKS["glabella"])
    mouth_left = lm.px(LANDMARKS["left_mouth_corner"])
    mouth_right = lm.px(LANDMARKS["right_mouth_corner"])

    # Determine which side is more visible (further from center in x)
    center_x = lm.image_width / 2
    left_spread = abs(left_mh[0] - center_x)
    right_spread = abs(right_mh[0] - center_x)

    if left_spread > right_spread:
        malar_high = left_mh
        malar_low = left_ml
        cheekbone = left_cb
        mouth_corner = mouth_left
    else:
        malar_high = right_mh
        malar_low = right_ml
        cheekbone = right_cb
        mouth_corner = mouth_right

    # Ogee curve path: glabella -> malar_high -> cheekbone -> malar_low -> mouth_corner
    path_start = glabella
    path_end = mouth_corner
    intermediate_points = [malar_high, cheekbone, malar_low]

    # Compute bulge: max perpendicular distance of intermediate points from the chord
    deviations = []
    for pt in intermediate_points:
        d = abs(point_to_line_distance(pt, path_start, path_end))
        deviations.append(d)

    max_deviation = max(deviations)
    chord_length = euclidean_2d(path_start, path_end)

    # Normalize deviation by chord length
    curvature_ratio = max_deviation / max(chord_length, 1.0)

    # Map to 0-100 score (empirically: good ogee ~0.15-0.25 ratio)
    if curvature_ratio > 0.25:
        score = 95.0
    elif curvature_ratio > 0.15:
        score = 60.0 + (curvature_ratio - 0.15) / 0.10 * 35.0
    elif curvature_ratio > 0.08:
        score = 30.0 + (curvature_ratio - 0.08) / 0.07 * 30.0
    else:
        score = curvature_ratio / 0.08 * 30.0

    score = round(max(0, min(100, score)), 1)

    if score >= 70:
        volume_assessment = "adequate"
    elif score >= 40:
        volume_assessment = "moderate_loss"
    else:
        volume_assessment = "significant_loss"

    # Malar prominence: lateral distance of malar_high normalized by face width
    face_width_px = euclidean_2d(
        lm.px(LANDMARKS["left_gonion"]),
        lm.px(LANDMARKS["right_gonion"]),
    )
    malar_lateral = abs(malar_high[0] - center_x)
    malar_ratio = round(malar_lateral / max(face_width_px / 2, 1.0), 3)

    return OgeeCurve(
        curve_score=score,
        midface_volume_assessment=volume_assessment,
        malar_prominence_ratio=malar_ratio,
    )
