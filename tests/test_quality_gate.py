"""Tests for the quality gate module."""

import numpy as np
import pytest
from app.pipeline.quality_gate import (
    check_image_quality,
    check_head_pose,
    check_neutral_expression,
    QualityWarning,
)
from app.detection.head_pose import HeadPose


class TestImageQuality:
    def test_good_image_no_warnings(self):
        # Bright, high-contrast, sharp image
        image = np.random.randint(80, 180, (1080, 1920, 3), dtype=np.uint8)
        warnings = check_image_quality(image)
        codes = [w.code for w in warnings]
        assert "UNDEREXPOSED" not in codes
        assert "OVEREXPOSED" not in codes

    def test_low_resolution(self):
        image = np.random.randint(80, 180, (200, 300, 3), dtype=np.uint8)
        warnings = check_image_quality(image)
        assert any(w.code == "LOW_RESOLUTION" for w in warnings)

    def test_underexposed(self):
        image = np.full((720, 1280, 3), 20, dtype=np.uint8)
        warnings = check_image_quality(image)
        assert any(w.code == "UNDEREXPOSED" for w in warnings)

    def test_overexposed(self):
        image = np.full((720, 1280, 3), 240, dtype=np.uint8)
        warnings = check_image_quality(image)
        assert any(w.code == "OVEREXPOSED" for w in warnings)

    def test_low_contrast(self):
        # Uniform image = zero contrast
        image = np.full((720, 1280, 3), 128, dtype=np.uint8)
        warnings = check_image_quality(image)
        assert any(w.code == "LOW_CONTRAST" for w in warnings)


class TestHeadPose:
    def test_good_frontal(self):
        pose = HeadPose(yaw=3.0, pitch=2.0, roll=1.0)
        warnings = check_head_pose(pose, "frontal")
        assert len(warnings) == 0

    def test_rotated_for_frontal(self):
        pose = HeadPose(yaw=25.0, pitch=2.0, roll=1.0)
        warnings = check_head_pose(pose, "frontal")
        assert any(w.code == "HEAD_NOT_FRONTAL" for w in warnings)

    def test_good_oblique(self):
        pose = HeadPose(yaw=40.0, pitch=2.0, roll=1.0)
        warnings = check_head_pose(pose, "oblique")
        assert not any(w.code == "HEAD_NOT_OBLIQUE" for w in warnings)

    def test_too_frontal_for_oblique(self):
        pose = HeadPose(yaw=10.0, pitch=0.0, roll=0.0)
        warnings = check_head_pose(pose, "oblique")
        assert any(w.code == "HEAD_NOT_OBLIQUE" for w in warnings)

    def test_good_profile(self):
        pose = HeadPose(yaw=85.0, pitch=0.0, roll=0.0)
        warnings = check_head_pose(pose, "profile")
        assert not any(w.code == "HEAD_NOT_PROFILE" for w in warnings)

    def test_not_enough_for_profile(self):
        pose = HeadPose(yaw=50.0, pitch=0.0, roll=0.0)
        warnings = check_head_pose(pose, "profile")
        assert any(w.code == "HEAD_NOT_PROFILE" for w in warnings)

    def test_tilted_head(self):
        pose = HeadPose(yaw=0.0, pitch=0.0, roll=15.0)
        warnings = check_head_pose(pose, "frontal")
        assert any(w.code == "HEAD_TILTED" for w in warnings)

    def test_none_pose(self):
        warnings = check_head_pose(None, "frontal")
        assert any(w.code == "NO_HEAD_POSE" for w in warnings)


class TestNeutralExpression:
    def test_neutral_face_no_warnings(self):
        blendshapes = {
            "mouthSmileLeft": 0.02,
            "mouthSmileRight": 0.03,
            "browDownLeft": 0.01,
            "jawOpen": 0.01,
        }
        warnings = check_neutral_expression(blendshapes)
        assert len(warnings) == 0

    def test_smiling_detected(self):
        blendshapes = {
            "mouthSmileLeft": 0.45,
            "mouthSmileRight": 0.42,
        }
        warnings = check_neutral_expression(blendshapes)
        assert any(w.code == "NON_NEUTRAL_EXPRESSION" for w in warnings)

    def test_frowning_detected(self):
        blendshapes = {
            "browDownLeft": 0.35,
            "browDownRight": 0.30,
        }
        warnings = check_neutral_expression(blendshapes)
        assert any(w.code == "NON_NEUTRAL_EXPRESSION" for w in warnings)

    def test_empty_blendshapes_no_warning(self):
        warnings = check_neutral_expression({})
        assert len(warnings) == 0
