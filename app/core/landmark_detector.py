"""
V1 Legacy Landmark Detector.

.. deprecated:: 2.0.0
    V1 Legacy module. Retained for backward compatibility with /api/v1/analyze.
    New code should use detection/face_landmarker.py (Tasks API with 478 landmarks,
    52 blendshapes, transformation matrix for head pose).
"""

import mediapipe as mp
import numpy as np
import cv2
from dataclasses import dataclass


@dataclass
class FaceLandmarks:
    points: np.ndarray  # (478, 3) normalized coordinates
    image_width: int
    image_height: int
    confidence: float

    def px(self, idx: int) -> tuple[float, float]:
        """Get landmark as pixel coordinates."""
        p = self.points[idx]
        return (p[0] * self.image_width, p[1] * self.image_height)

    def px3d(self, idx: int) -> tuple[float, float, float]:
        """Get landmark as pixel coordinates with depth."""
        p = self.points[idx]
        return (p[0] * self.image_width, p[1] * self.image_height, p[2] * self.image_width)


# Key MediaPipe FaceMesh landmark indices for aesthetic analysis
LANDMARKS = {
    # Midline
    "glabella": 9,
    "nasion": 168,
    "pronasale": 4,       # nose tip
    "subnasale": 2,
    "labrale_superius": 0,  # upper lip center
    "stomion": 13,          # lip junction
    "labrale_inferius": 17, # lower lip center
    "mentum": 152,          # chin bottom
    "pogonion": 175,        # chin most anterior point

    # Paired landmarks
    "left_eye_outer": 263,
    "right_eye_outer": 33,
    "left_eye_inner": 362,
    "right_eye_inner": 133,
    "left_mouth_corner": 291,
    "right_mouth_corner": 61,
    "left_brow_outer": 276,
    "right_brow_outer": 46,
    "left_cheekbone": 330,
    "right_cheekbone": 101,
    "left_gonion": 365,     # jaw angle
    "right_gonion": 136,

    # Nose
    "left_alar": 309,
    "right_alar": 79,
    "columella": 2,

    # Forehead approximation (highest reliable point)
    "trichion_approx": 10,

    # Profile-specific
    "nasal_bridge_top": 6,
    "nasal_tip": 4,
    "upper_lip_vermilion": 0,
    "lower_lip_vermilion": 17,

    # Malar / midface
    "left_malar_high": 329,
    "right_malar_high": 100,
    "left_malar_low": 425,
    "right_malar_low": 205,
}


class LandmarkDetector:
    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_confidence,
            min_tracking_confidence=min_confidence,
        )

    def detect(self, image: np.ndarray) -> FaceLandmarks | None:
        """Detect face landmarks from BGR image. Returns None if no face found."""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        face = results.multi_face_landmarks[0]
        h, w = image.shape[:2]

        points = np.array([(lm.x, lm.y, lm.z) for lm in face.landmark])

        confidence = self._estimate_confidence(points, w, h)

        return FaceLandmarks(
            points=points,
            image_width=w,
            image_height=h,
            confidence=confidence,
        )

    def _estimate_confidence(self, points: np.ndarray, w: int, h: int) -> float:
        """Heuristic confidence based on landmark spread and face size."""
        xs = points[:, 0] * w
        ys = points[:, 1] * h
        face_width = xs.max() - xs.min()
        face_height = ys.max() - ys.min()

        # Face should occupy reasonable portion of image
        width_ratio = face_width / w
        height_ratio = face_height / h

        if width_ratio < 0.1 or height_ratio < 0.1:
            return 0.3
        if width_ratio > 0.95 or height_ratio > 0.95:
            return 0.5

        # Aspect ratio sanity check (face ~1:1.3)
        aspect = face_width / max(face_height, 1)
        aspect_score = 1.0 - min(abs(aspect - 0.77), 0.5) * 2

        return min(0.5 + aspect_score * 0.5, 1.0)

    def close(self):
        self._face_mesh.close()
