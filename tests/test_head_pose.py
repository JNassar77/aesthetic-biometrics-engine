"""Tests for head pose extraction from transformation matrix."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from app.detection.head_pose import extract_head_pose, HeadPose


def _rotation_matrix(yaw_deg: float, pitch_deg: float, roll_deg: float) -> np.ndarray:
    """Build a 4x4 affine matrix from yaw/pitch/roll, matching extract_head_pose.

    Uses the YXZ convention: yaw = rotation about the vertical Y axis (head turn),
    pitch = rotation about X (nod), roll = rotation about Z (tilt). This matches
    MediaPipe's transformation matrix — the earlier helper named the Z rotation
    "yaw", which (together with the old ZYX decode) self-confirmed a wrong result.
    """
    R = Rotation.from_euler("YXZ", [yaw_deg, pitch_deg, roll_deg], degrees=True).as_matrix()
    mat = np.eye(4)
    mat[:3, :3] = R
    return mat


class TestHeadPoseExtraction:
    def test_identity_matrix_gives_zero_pose(self):
        pose = extract_head_pose(np.eye(4))
        assert pose is not None
        assert abs(pose.yaw) < 0.5
        assert abs(pose.pitch) < 0.5
        assert abs(pose.roll) < 0.5

    def test_known_yaw(self):
        mat = _rotation_matrix(yaw_deg=30.0, pitch_deg=0.0, roll_deg=0.0)
        pose = extract_head_pose(mat)
        assert pose is not None
        assert abs(pose.yaw - 30.0) < 1.0

    def test_known_pitch(self):
        mat = _rotation_matrix(yaw_deg=0.0, pitch_deg=15.0, roll_deg=0.0)
        pose = extract_head_pose(mat)
        assert pose is not None
        assert abs(pose.pitch - 15.0) < 1.0

    def test_known_roll(self):
        mat = _rotation_matrix(yaw_deg=0.0, pitch_deg=0.0, roll_deg=10.0)
        pose = extract_head_pose(mat)
        assert pose is not None
        assert abs(pose.roll - 10.0) < 1.0

    def test_combined_angles(self):
        mat = _rotation_matrix(yaw_deg=20.0, pitch_deg=-5.0, roll_deg=3.0)
        pose = extract_head_pose(mat)
        assert pose is not None
        assert abs(pose.yaw - 20.0) < 2.0
        assert abs(pose.pitch - (-5.0)) < 2.0

    def test_none_matrix_returns_none(self):
        assert extract_head_pose(None) is None


class TestHeadPoseValidation:
    def test_frontal_within_tolerance(self):
        pose = HeadPose(yaw=5.0, pitch=3.0, roll=2.0)
        assert pose.is_within_tolerance(max_yaw=15.0, max_pitch=10.0, max_roll=10.0)

    def test_frontal_outside_tolerance(self):
        pose = HeadPose(yaw=25.0, pitch=3.0, roll=2.0)
        assert not pose.is_within_tolerance(max_yaw=15.0)

    def test_estimated_view_frontal(self):
        assert HeadPose(yaw=5.0, pitch=0, roll=0).estimated_view == "frontal"

    def test_estimated_view_oblique(self):
        assert HeadPose(yaw=40.0, pitch=0, roll=0).estimated_view == "oblique"

    def test_estimated_view_profile(self):
        assert HeadPose(yaw=80.0, pitch=0, roll=0).estimated_view == "profile"
