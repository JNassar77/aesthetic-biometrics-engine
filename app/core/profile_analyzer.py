"""
Profile (90 deg) Analysis
=========================
Measurements:
  1. Ricketts E-line: line from pronasale (nose tip) to pogonion (chin).
     Upper lip should sit ~4mm behind, lower lip ~2mm behind this line.
  2. Nasolabial angle: angle between columella and upper lip at subnasale.
     Ideal range: 90-105 deg.
  3. Chin projection: pogonion position relative to a vertical dropped
     from subnasale, perpendicular to Frankfort horizontal.

Mathematical basis:
  - E-line: parametric line through nose tip and chin tip.
    Lip protrusion = signed distance from lip points to this line.
  - Nasolabial angle: angle at subnasale between vectors to columella
    and labrale superius.
  - Chin projection: horizontal distance from pogonion to the subnasale
    vertical reference.
"""

from app.core.landmark_detector import FaceLandmarks, LANDMARKS
from app.models.schemas import ProfileAnalysis, ProfileELine, NasolabialAngle, ChinProjection
from app.utils.geometry import point_to_line_distance, angle_between_points, euclidean_2d, px_to_mm_estimate


def analyze_profile(lm: FaceLandmarks) -> ProfileAnalysis:
    left_gon = lm.px(LANDMARKS["left_gonion"])
    right_gon = lm.px(LANDMARKS["right_gonion"])
    face_width_px = euclidean_2d(left_gon, right_gon)
    scale = px_to_mm_estimate(face_width_px)

    e_line = _compute_eline(lm, scale)
    nla = _compute_nasolabial_angle(lm)
    chin = _compute_chin_projection(lm, scale)

    return ProfileAnalysis(e_line=e_line, nasolabial_angle=nla, chin_projection=chin)


def _compute_eline(lm: FaceLandmarks, scale: float) -> ProfileELine:
    nose_tip = lm.px(LANDMARKS["pronasale"])
    pogonion = lm.px(LANDMARKS["pogonion"])
    upper_lip = lm.px(LANDMARKS["labrale_superius"])
    lower_lip = lm.px(LANDMARKS["labrale_inferius"])

    upper_dist_px = point_to_line_distance(upper_lip, nose_tip, pogonion)
    lower_dist_px = point_to_line_distance(lower_lip, nose_tip, pogonion)

    upper_mm = round(upper_dist_px * scale, 2)
    lower_mm = round(lower_dist_px * scale, 2)

    # Negative = behind the line (ideal)
    # Ideal: upper lip ~-4mm, lower lip ~-2mm
    if upper_mm > 2:
        assessment = "protruded"
    elif upper_mm < -8:
        assessment = "retruded"
    else:
        assessment = "ideal"

    return ProfileELine(
        upper_lip_to_eline_mm=upper_mm,
        lower_lip_to_eline_mm=lower_mm,
        assessment=assessment,
    )


def _compute_nasolabial_angle(lm: FaceLandmarks) -> NasolabialAngle:
    # Vectors from subnasale to columella (upward along nose) and to upper lip
    subnasale = lm.px(LANDMARKS["subnasale"])
    columella = lm.px(LANDMARKS["nasal_bridge_top"])  # approximation for columella direction
    upper_lip = lm.px(LANDMARKS["labrale_superius"])

    angle = angle_between_points(subnasale, columella, upper_lip)

    if angle < 90:
        assessment = "acute (may benefit from tip refinement)"
    elif angle > 105:
        assessment = "obtuse (over-rotated appearance)"
    else:
        assessment = "within ideal range"

    return NasolabialAngle(
        angle_degrees=round(angle, 1),
        assessment=assessment,
    )


def _compute_chin_projection(lm: FaceLandmarks, scale: float) -> ChinProjection:
    subnasale = lm.px(LANDMARKS["subnasale"])
    pogonion = lm.px(LANDMARKS["pogonion"])

    # Horizontal offset: pogonion.x relative to subnasale.x
    # In a profile view, positive = chin projects forward
    offset_px = pogonion[0] - subnasale[0]
    offset_mm = round(offset_px * scale, 2)

    if abs(offset_mm) < 5:
        assessment = "well-projected"
    elif offset_mm < -5:
        assessment = "retruded (filler or implant may improve profile)"
    else:
        assessment = "prominent"

    return ChinProjection(pogonion_offset_mm=offset_mm, assessment=assessment)
