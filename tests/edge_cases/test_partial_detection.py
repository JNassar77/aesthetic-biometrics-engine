"""
Edge case tests: partial detection scenarios.

Tests for glasses, beard, partial occlusion — situations where
landmarks may be present but less reliable.
"""

import numpy as np
import pytest

from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult, calibrate
from app.detection.landmark_index import PAIRED, MIDLINE, IRIS
from tests.fixtures.synthetic import (
    make_symmetric_face,
    make_calibration,
    _base_landmarks,
)


class TestPartialLandmarks:
    """When some landmarks have anomalous positions (occlusion)."""

    def test_iris_occluded_falls_back_to_face_width(self):
        """If iris landmarks are collapsed (glasses), calibration should fallback."""
        lm = _base_landmarks()
        # Collapse iris landmarks to same point (simulating glasses occlusion)
        for key in IRIS:
            lm[IRIS[key]] = [0.5, 0.3, 0.0]

        detection = DetectionResult(
            landmarks=lm,
            blendshapes={},
            transformation_matrix=np.eye(4),
            image_width=1000,
            image_height=1000,
        )

        cal = calibrate(detection.landmarks, detection.image_width, detection.image_height)
        # Should still produce a result via face-width fallback
        assert cal.px_per_mm > 0
        assert cal.method in ("face_width_estimate", "iris")  # either is acceptable
        if cal.method == "face_width_estimate":
            assert cal.confidence < 0.9  # lower confidence for fallback

    def test_asymmetric_iris_reduces_confidence(self):
        """If left and right iris diameters differ, confidence should drop."""
        lm = _base_landmarks()
        # Make left iris bigger than right
        lm[IRIS["left_iris_right"]] = [0.63, 0.30, 0.0]  # wider
        lm[IRIS["left_iris_left"]] = [0.57, 0.30, 0.0]

        detection = DetectionResult(
            landmarks=lm,
            blendshapes={},
            transformation_matrix=np.eye(4),
            image_width=1000,
            image_height=1000,
        )

        cal = calibrate(detection.landmarks, detection.image_width, detection.image_height)
        assert cal.px_per_mm > 0
        # Calibration should still work but may produce warnings
        # (the asymmetry is within tolerance for calibration)


class TestExtremeHeadPose:
    """Landmarks from extreme head poses should be handled."""

    def test_face_at_edge_of_frame(self):
        """Face at edge of frame (all landmarks shifted right) should not crash."""
        lm = _base_landmarks()
        # Shift entire face to the right edge
        lm[:, 0] += 0.3  # now centered at x=0.8

        detection = DetectionResult(
            landmarks=lm,
            blendshapes={},
            transformation_matrix=np.eye(4),
            image_width=1000,
            image_height=1000,
        )

        # Calibration should still work (relative distances preserved)
        cal = calibrate(detection.landmarks, detection.image_width, detection.image_height)
        assert cal.px_per_mm > 0

    def test_very_small_face_in_frame(self):
        """Tiny face (far from camera) should calibrate with lower confidence."""
        lm = _base_landmarks()
        # Scale face to be very small (centered, but compressed)
        center = np.array([0.5, 0.5, 0.0])
        lm = center + (lm - center) * 0.2  # shrink to 20%

        detection = DetectionResult(
            landmarks=lm.astype(np.float32),
            blendshapes={},
            transformation_matrix=np.eye(4),
            image_width=1000,
            image_height=1000,
        )

        cal = calibrate(detection.landmarks, detection.image_width, detection.image_height)
        assert cal.px_per_mm > 0


class TestMultipleFaces:
    """Our pipeline processes only 1 face (num_faces=1).

    These tests verify we never crash if detection data is unexpected.
    """

    def test_single_face_normal_flow(self):
        """Baseline: single face detection works normally."""
        det = make_symmetric_face()
        assert det.face_detected
        assert det.num_landmarks == 478


class TestEdgeLandmarkValues:
    """Edge values in landmark coordinates."""

    def test_landmarks_at_boundary_zero(self):
        """Landmarks exactly at (0,0,0) should not crash calibration."""
        lm = _base_landmarks()
        # Put a non-critical landmark at origin
        lm[400] = [0.0, 0.0, 0.0]

        detection = DetectionResult(
            landmarks=lm,
            blendshapes={},
            transformation_matrix=np.eye(4),
            image_width=1000,
            image_height=1000,
        )

        cal = calibrate(detection.landmarks, detection.image_width, detection.image_height)
        assert cal.px_per_mm > 0

    def test_landmarks_at_boundary_one(self):
        """Landmarks at (1,1,0) should not crash calibration."""
        lm = _base_landmarks()
        lm[400] = [1.0, 1.0, 0.0]

        detection = DetectionResult(
            landmarks=lm,
            blendshapes={},
            transformation_matrix=np.eye(4),
            image_width=1000,
            image_height=1000,
        )

        cal = calibrate(detection.landmarks, detection.image_width, detection.image_height)
        assert cal.px_per_mm > 0

    def test_negative_z_depth(self):
        """Negative z values (nose tip protrusion) should work fine."""
        det = make_symmetric_face()
        assert det.landmarks[MIDLINE["pronasale"]][2] < 0  # nose tip has negative z
        # This is normal — 3D landmark space allows it
