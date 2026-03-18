"""
Complete 478-landmark index for MediaPipe Face Landmarker.

Landmarks 0-467: core face mesh
Landmarks 468-472: left iris (refined)
Landmarks 473-477: right iris (refined)

Anatomical groupings map landmarks to clinically relevant regions.
"""

from dataclasses import dataclass


# --- Midline landmarks (sagittal plane) ---
MIDLINE = {
    "glabella": 9,
    "nasion": 168,
    "rhinion": 5,
    "pronasale": 4,           # nose tip
    "subnasale": 2,
    "labrale_superius": 0,    # upper lip midline
    "stomion": 13,            # lip junction midline
    "labrale_inferius": 17,   # lower lip midline
    "mentolabial_sulcus": 18,
    "pogonion": 175,          # chin most anterior
    "gnathion": 152,          # chin bottom (menton)
    "trichion_approx": 10,    # highest reliable forehead point
}

# --- Paired bilateral landmarks ---
PAIRED = {
    "eye_outer":        (263, 33),     # L, R
    "eye_inner":        (362, 133),
    "brow_outer":       (276, 46),
    "brow_inner":       (285, 55),
    "brow_peak":        (282, 52),
    "mouth_corner":     (291, 61),
    "cheekbone":        (330, 101),
    "alar":             (309, 79),     # nostril widest
    "gonion":           (365, 136),    # jaw angle
    "malar_high":       (329, 100),
    "malar_low":        (425, 205),
    "infraorbital":     (253, 23),     # tear trough region
    "preauricular":     (356, 127),
    "temporal":         (251, 21),
}

# --- Iris landmarks (require refine_landmarks=True) ---
IRIS = {
    "left_iris_center": 468,
    "left_iris_right": 469,
    "left_iris_top": 470,
    "left_iris_left": 471,
    "left_iris_bottom": 472,
    "right_iris_center": 473,
    "right_iris_right": 474,
    "right_iris_top": 475,
    "right_iris_left": 476,
    "right_iris_bottom": 477,
}

# --- Contour groups (for region analysis) ---
# MediaPipe connection constants (subset for aesthetic analysis)
LIP_UPPER_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
LIP_LOWER_OUTER = [291, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61]
LIP_UPPER_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
LIP_LOWER_INNER = [308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78]

FACE_OVAL = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10,
]

LEFT_EYE_CONTOUR = [263, 249, 390, 373, 374, 380, 381, 382, 362,
                     398, 384, 385, 386, 387, 388, 466, 263]
RIGHT_EYE_CONTOUR = [33, 7, 163, 144, 145, 153, 154, 155, 133,
                      173, 157, 158, 159, 160, 161, 246, 33]

LEFT_BROW = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
RIGHT_BROW = [46, 53, 52, 65, 55, 70, 63, 105, 66, 107]

JAWLINE_LEFT = [356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152]
JAWLINE_RIGHT = [127, 234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152]


@dataclass
class AnatomicalZoneLandmarks:
    """Maps treatment zones to their relevant landmark indices."""
    zone_id: str
    zone_name: str
    primary_landmarks: list[int]
    secondary_landmarks: list[int]
    paired: bool  # True if zone exists on both sides


# --- Treatment zone → landmark mappings ---
ZONE_LANDMARKS = {
    "T1": AnatomicalZoneLandmarks(
        zone_id="T1", zone_name="Temporal",
        primary_landmarks=[PAIRED["temporal"][0], PAIRED["temporal"][1]],
        secondary_landmarks=[PAIRED["preauricular"][0], PAIRED["preauricular"][1]],
        paired=True,
    ),
    "Bw1": AnatomicalZoneLandmarks(
        zone_id="Bw1", zone_name="Brow Lateral",
        primary_landmarks=[PAIRED["brow_outer"][0], PAIRED["brow_outer"][1],
                          PAIRED["brow_peak"][0], PAIRED["brow_peak"][1]],
        secondary_landmarks=list(LEFT_BROW[:3]) + list(RIGHT_BROW[:3]),
        paired=True,
    ),
    "Bw2": AnatomicalZoneLandmarks(
        zone_id="Bw2", zone_name="Glabella",
        primary_landmarks=[MIDLINE["glabella"],
                          PAIRED["brow_inner"][0], PAIRED["brow_inner"][1]],
        secondary_landmarks=[MIDLINE["nasion"]],
        paired=False,
    ),
    "Ck1": AnatomicalZoneLandmarks(
        zone_id="Ck1", zone_name="Zygomatic Arch",
        primary_landmarks=[PAIRED["cheekbone"][0], PAIRED["cheekbone"][1]],
        secondary_landmarks=[PAIRED["malar_high"][0], PAIRED["malar_high"][1]],
        paired=True,
    ),
    "Ck2": AnatomicalZoneLandmarks(
        zone_id="Ck2", zone_name="Zygomatic Eminence",
        primary_landmarks=[PAIRED["malar_high"][0], PAIRED["malar_high"][1]],
        secondary_landmarks=[PAIRED["cheekbone"][0], PAIRED["cheekbone"][1]],
        paired=True,
    ),
    "Ck3": AnatomicalZoneLandmarks(
        zone_id="Ck3", zone_name="Anteromedial Cheek",
        primary_landmarks=[PAIRED["malar_low"][0], PAIRED["malar_low"][1]],
        secondary_landmarks=[PAIRED["infraorbital"][0], PAIRED["infraorbital"][1]],
        paired=True,
    ),
    "Tt1": AnatomicalZoneLandmarks(
        zone_id="Tt1", zone_name="Infraorbital / Tear Trough",
        primary_landmarks=[PAIRED["infraorbital"][0], PAIRED["infraorbital"][1]],
        secondary_landmarks=[PAIRED["eye_inner"][0], PAIRED["eye_inner"][1]],
        paired=True,
    ),
    "Ns1": AnatomicalZoneLandmarks(
        zone_id="Ns1", zone_name="Nasolabial Fold",
        primary_landmarks=[PAIRED["alar"][0], PAIRED["alar"][1],
                          PAIRED["mouth_corner"][0], PAIRED["mouth_corner"][1]],
        secondary_landmarks=[PAIRED["malar_low"][0], PAIRED["malar_low"][1]],
        paired=True,
    ),
    "Lp1": AnatomicalZoneLandmarks(
        zone_id="Lp1", zone_name="Upper Lip",
        primary_landmarks=[MIDLINE["labrale_superius"], MIDLINE["stomion"]],
        secondary_landmarks=LIP_UPPER_OUTER[:6],
        paired=False,
    ),
    "Lp2": AnatomicalZoneLandmarks(
        zone_id="Lp2", zone_name="Lower Lip",
        primary_landmarks=[MIDLINE["stomion"], MIDLINE["labrale_inferius"]],
        secondary_landmarks=LIP_LOWER_OUTER[:6],
        paired=False,
    ),
    "Lp3": AnatomicalZoneLandmarks(
        zone_id="Lp3", zone_name="Lip Corners",
        primary_landmarks=[PAIRED["mouth_corner"][0], PAIRED["mouth_corner"][1]],
        secondary_landmarks=[61, 291],  # oral commissures
        paired=True,
    ),
    "Mn1": AnatomicalZoneLandmarks(
        zone_id="Mn1", zone_name="Marionette Lines",
        primary_landmarks=[PAIRED["mouth_corner"][0], PAIRED["mouth_corner"][1]],
        secondary_landmarks=[PAIRED["gonion"][0], PAIRED["gonion"][1]],
        paired=True,
    ),
    "Jw1": AnatomicalZoneLandmarks(
        zone_id="Jw1", zone_name="Pre-Jowl Sulcus",
        primary_landmarks=[PAIRED["gonion"][0], PAIRED["gonion"][1]],
        secondary_landmarks=[MIDLINE["pogonion"]],
        paired=True,
    ),
    "Ch1": AnatomicalZoneLandmarks(
        zone_id="Ch1", zone_name="Chin",
        primary_landmarks=[MIDLINE["pogonion"], MIDLINE["gnathion"],
                          MIDLINE["mentolabial_sulcus"]],
        secondary_landmarks=[],
        paired=False,
    ),
    "Jl1": AnatomicalZoneLandmarks(
        zone_id="Jl1", zone_name="Jawline",
        primary_landmarks=[PAIRED["gonion"][0], PAIRED["gonion"][1]],
        secondary_landmarks=JAWLINE_LEFT[:4] + JAWLINE_RIGHT[:4],
        paired=True,
    ),
    "Pf1": AnatomicalZoneLandmarks(
        zone_id="Pf1", zone_name="Nasal Profile",
        primary_landmarks=[MIDLINE["nasion"], MIDLINE["rhinion"],
                          MIDLINE["pronasale"], MIDLINE["subnasale"]],
        secondary_landmarks=[],
        paired=False,
    ),
}


def get_zone(zone_id: str) -> AnatomicalZoneLandmarks | None:
    return ZONE_LANDMARKS.get(zone_id)


def all_zone_ids() -> list[str]:
    return list(ZONE_LANDMARKS.keys())
