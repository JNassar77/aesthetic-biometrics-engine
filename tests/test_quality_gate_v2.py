"""Tests for Sprint 2 quality gate additions (hard pose rejection)."""

import numpy as np
import pytest

from app.detection.head_pose import HeadPose
from app.pipeline.quality_gate import (
    check_hard_pose_rejection,
    QualityWarning,
)


class TestHardPoseRejection:
    """Test hard rejection thresholds for head pose."""

    def test_frontal_within_limits_no_rejection(self):
        pose = HeadPose(yaw=10.0, pitch=5.0, roll=3.0)
        assert check_hard_pose_rejection(pose, "frontal") is None

    def test_frontal_extreme_yaw_rejected(self):
        pose = HeadPose(yaw=30.0, pitch=0.0, roll=0.0)
        warning = check_hard_pose_rejection(pose, "frontal")
        assert warning is not None
        assert warning.code == "POSE_REJECTED"
        assert warning.severity == "critical"

    def test_frontal_extreme_pitch_rejected(self):
        pose = HeadPose(yaw=0.0, pitch=25.0, roll=0.0)
        warning = check_hard_pose_rejection(pose, "frontal")
        assert warning is not None
        assert warning.code == "POSE_REJECTED"

    def test_frontal_extreme_roll_rejected(self):
        pose = HeadPose(yaw=0.0, pitch=0.0, roll=18.0)
        warning = check_hard_pose_rejection(pose, "frontal")
        assert warning is not None
        assert warning.code == "POSE_REJECTED"

    def test_oblique_good_angle_no_rejection(self):
        pose = HeadPose(yaw=40.0, pitch=5.0, roll=3.0)
        assert check_hard_pose_rejection(pose, "oblique") is None

    def test_oblique_too_frontal_rejected(self):
        pose = HeadPose(yaw=10.0, pitch=0.0, roll=0.0)
        warning = check_hard_pose_rejection(pose, "oblique")
        assert warning is not None
        assert warning.code == "POSE_REJECTED"

    def test_oblique_too_profile_rejected(self):
        pose = HeadPose(yaw=80.0, pitch=0.0, roll=0.0)
        warning = check_hard_pose_rejection(pose, "oblique")
        assert warning is not None
        assert warning.code == "POSE_REJECTED"

    def test_profile_good_angle_no_rejection(self):
        pose = HeadPose(yaw=80.0, pitch=0.0, roll=0.0)
        assert check_hard_pose_rejection(pose, "profile") is None

    def test_profile_insufficient_yaw_rejected(self):
        pose = HeadPose(yaw=40.0, pitch=0.0, roll=0.0)
        warning = check_hard_pose_rejection(pose, "profile")
        assert warning is not None
        assert warning.code == "POSE_REJECTED"

    def test_none_pose_no_rejection(self):
        assert check_hard_pose_rejection(None, "frontal") is None

    def test_negative_yaw_works(self):
        """Negative yaw (turned left) should be handled correctly."""
        pose = HeadPose(yaw=-40.0, pitch=0.0, roll=0.0)
        assert check_hard_pose_rejection(pose, "frontal") is not None
        assert check_hard_pose_rejection(pose, "oblique") is None
