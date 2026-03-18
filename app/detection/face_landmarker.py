"""
MediaPipe Face Landmarker wrapper using the Tasks API (not legacy FaceMesh).

Returns 478 landmarks + 52 blendshapes + 4x4 transformation matrix.
This is the foundation for all V2 analysis engines.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import mediapipe as mp
import numpy as np

_BASE_OPTIONS = mp.tasks.BaseOptions
_FaceLandmarker = mp.tasks.vision.FaceLandmarker
_FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
_RunningMode = mp.tasks.vision.RunningMode

DEFAULT_MODEL_PATH = str(Path(__file__).resolve().parents[2] / "models" / "face_landmarker.task")


@dataclass
class DetectionResult:
    """Result from face landmark detection."""
    landmarks: np.ndarray                     # (478, 3) normalized x, y, z
    blendshapes: dict[str, float]             # 52 named blendshape coefficients
    transformation_matrix: np.ndarray | None  # (4, 4) affine matrix or None
    image_width: int
    image_height: int
    face_detected: bool = True

    def px(self, idx: int) -> tuple[float, float]:
        """Get landmark as pixel coordinates (x, y)."""
        pt = self.landmarks[idx]
        return (pt[0] * self.image_width, pt[1] * self.image_height)

    def px3d(self, idx: int) -> tuple[float, float, float]:
        """Get landmark as pixel coordinates with relative depth."""
        pt = self.landmarks[idx]
        return (pt[0] * self.image_width, pt[1] * self.image_height, pt[2] * self.image_width)

    @property
    def num_landmarks(self) -> int:
        return len(self.landmarks)


@dataclass
class NoFaceResult:
    """Returned when no face is detected."""
    face_detected: bool = False
    landmarks: None = None
    blendshapes: dict = field(default_factory=dict)
    transformation_matrix: None = None


class FaceLandmarkerV2:
    """Wrapper around MediaPipe Face Landmarker Tasks API."""

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        min_detection_confidence: float = 0.7,
        min_presence_confidence: float = 0.7,
    ):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Face Landmarker model not found at {model_path}. "
                "Download it: curl -L -o models/face_landmarker.task "
                "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
                "face_landmarker/float16/1/face_landmarker.task"
            )

        options = _FaceLandmarkerOptions(
            base_options=_BASE_OPTIONS(model_asset_path=model_path),
            running_mode=_RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=min_detection_confidence,
            min_face_presence_confidence=min_presence_confidence,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
        )
        self._landmarker = _FaceLandmarker.create_from_options(options)

    def detect(self, image: np.ndarray) -> DetectionResult | NoFaceResult:
        """Detect face landmarks from a BGR numpy array.

        Args:
            image: OpenCV BGR image (np.ndarray, shape HxWx3)

        Returns:
            DetectionResult with landmarks, blendshapes, and transformation matrix,
            or NoFaceResult if no face detected.
        """
        h, w = image.shape[:2]

        # MediaPipe expects RGB
        rgb = image[:, :, ::-1]  # BGR → RGB without copy overhead
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self._landmarker.detect(mp_image)

        if not result.face_landmarks:
            return NoFaceResult()

        face = result.face_landmarks[0]
        landmarks = np.array([(lm.x, lm.y, lm.z) for lm in face])

        # Extract blendshapes
        blendshapes = {}
        if result.face_blendshapes:
            for bs in result.face_blendshapes[0]:
                blendshapes[bs.category_name] = round(bs.score, 4)

        # Extract transformation matrix
        transform = None
        if result.facial_transformation_matrixes:
            mat = result.facial_transformation_matrixes[0]
            transform = np.array(mat).reshape(4, 4) if hasattr(mat, '__len__') else None

        return DetectionResult(
            landmarks=landmarks,
            blendshapes=blendshapes,
            transformation_matrix=transform,
            image_width=w,
            image_height=h,
        )

    def close(self):
        self._landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
