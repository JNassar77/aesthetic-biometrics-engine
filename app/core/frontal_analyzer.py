"""
Frontal (0 deg) Analysis
========================

.. deprecated:: 2.0.0
    V1 Legacy module. Retained for backward compatibility with /api/v1/analyze.
    New code should use the V2 engines:
    - analysis/symmetry_engine.py (6-axis bilateral symmetry)
    - analysis/proportion_engine.py (thirds, fifths, golden ratio, lip ratio)

Measurements:
  1. Symmetry: horizontal/vertical deviations from median sagittal line
  2. Facial thirds: Trichion-Glabella / Glabella-Subnasale / Subnasale-Mentum
  3. Lip ratio: upper-to-lower vertical height (ideal 1:1.6)

Mathematical basis:
  - Median sagittal line: best-fit vertical through midline landmarks
    (glabella, subnasale, mentum).
  - Symmetry score: average normalized deviation of paired landmarks
    from the sagittal line, mapped to 0-100 scale.
  - Facial thirds: vertical distances between horizontal planes.
  - Lip ratio: vermilion heights measured at the midline.
"""

import numpy as np
from app.core.landmark_detector import FaceLandmarks, LANDMARKS
from app.models.schemas import FrontalAnalysis, SymmetryResult, FacialThirds, LipAnalysis
from app.utils.geometry import euclidean_2d, midpoint_2d, px_to_mm_estimate


def analyze_frontal(lm: FaceLandmarks) -> FrontalAnalysis:
    # Pixel-to-mm scale
    left_gon = lm.px(LANDMARKS["left_gonion"])
    right_gon = lm.px(LANDMARKS["right_gonion"])
    face_width_px = euclidean_2d(left_gon, right_gon)
    scale = px_to_mm_estimate(face_width_px)

    symmetry = _compute_symmetry(lm, scale, face_width_px)
    thirds = _compute_facial_thirds(lm)
    lips = _compute_lip_ratio(lm)

    return FrontalAnalysis(symmetry=symmetry, facial_thirds=thirds, lip_analysis=lips)


def _compute_symmetry(lm: FaceLandmarks, scale: float, face_width_px: float) -> SymmetryResult:
    # Sagittal midline from glabella -> subnasale -> mentum
    midline_points = [
        lm.px(LANDMARKS["glabella"]),
        lm.px(LANDMARKS["subnasale"]),
        lm.px(LANDMARKS["mentum"]),
    ]
    mid_x = np.mean([p[0] for p in midline_points])

    paired = [
        ("left_eye_outer", "right_eye_outer"),
        ("left_eye_inner", "right_eye_inner"),
        ("left_mouth_corner", "right_mouth_corner"),
        ("left_brow_outer", "right_brow_outer"),
        ("left_cheekbone", "right_cheekbone"),
        ("left_gonion", "right_gonion"),
    ]

    h_devs = []
    v_devs = []

    for left_name, right_name in paired:
        lp = lm.px(LANDMARKS[left_name])
        rp = lm.px(LANDMARKS[right_name])

        # Horizontal: difference in distance from midline
        left_dist = abs(lp[0] - mid_x)
        right_dist = abs(rp[0] - mid_x)
        h_devs.append(abs(left_dist - right_dist))

        # Vertical: height difference between paired points
        v_devs.append(abs(lp[1] - rp[1]))

    avg_h_dev_px = float(np.mean(h_devs))
    avg_v_dev_px = float(np.mean(v_devs))

    # Normalize to face width and map to 0-100 score
    norm_dev = (avg_h_dev_px + avg_v_dev_px) / (2 * face_width_px)
    score = max(0.0, min(100.0, (1.0 - norm_dev * 10) * 100))

    return SymmetryResult(
        horizontal_deviation_mm=round(avg_h_dev_px * scale, 2),
        vertical_deviation_mm=round(avg_v_dev_px * scale, 2),
        symmetry_score=round(score, 1),
    )


def _compute_facial_thirds(lm: FaceLandmarks) -> FacialThirds:
    trichion_y = lm.px(LANDMARKS["trichion_approx"])[1]
    glabella_y = lm.px(LANDMARKS["glabella"])[1]
    subnasale_y = lm.px(LANDMARKS["subnasale"])[1]
    mentum_y = lm.px(LANDMARKS["mentum"])[1]

    upper = abs(glabella_y - trichion_y)
    middle = abs(subnasale_y - glabella_y)
    lower = abs(mentum_y - subnasale_y)
    total = upper + middle + lower + 1e-8

    upper_r = upper / total
    middle_r = middle / total
    lower_r = lower / total

    ideal = 1 / 3
    deviation = (abs(upper_r - ideal) + abs(middle_r - ideal) + abs(lower_r - ideal)) / 3
    deviation_pct = round(deviation * 100, 1)

    return FacialThirds(
        upper_third_ratio=round(upper_r, 3),
        middle_third_ratio=round(middle_r, 3),
        lower_third_ratio=round(lower_r, 3),
        deviation_from_ideal=deviation_pct,
    )


def _compute_lip_ratio(lm: FaceLandmarks) -> LipAnalysis:
    upper_lip_top = lm.px(LANDMARKS["labrale_superius"])
    stomion = lm.px(LANDMARKS["stomion"])
    lower_lip_bottom = lm.px(LANDMARKS["labrale_inferius"])

    upper_h = abs(stomion[1] - upper_lip_top[1])
    lower_h = abs(lower_lip_bottom[1] - stomion[1])

    ratio = upper_h / max(lower_h, 1e-8)
    ideal_ratio = 1 / 1.6  # 0.625
    deviation_pct = round(abs(ratio - ideal_ratio) / ideal_ratio * 100, 1)

    return LipAnalysis(
        upper_lip_height_px=round(upper_h, 1),
        lower_lip_height_px=round(lower_h, 1),
        ratio=round(ratio, 3),
        deviation_from_ideal=deviation_pct,
    )
