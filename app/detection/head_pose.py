"""
Extract head pose (yaw, pitch, roll) from the Face Landmarker transformation matrix.

The transformation matrix is a 4x4 affine matrix that encodes:
- Rotation (3x3 upper-left)
- Translation (3x1 right column)

We decompose the rotation into Euler angles (yaw, pitch, roll) in degrees.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class HeadPose:
    yaw: float    # Left/right rotation (degrees). Positive = turned right.
    pitch: float  # Up/down tilt (degrees). Positive = looking up.
    roll: float   # Head tilt (degrees). Positive = tilted right.

    def is_within_tolerance(
        self,
        max_yaw: float = 15.0,
        max_pitch: float = 10.0,
        max_roll: float = 10.0,
    ) -> bool:
        """Check if head pose is within acceptable range for analysis."""
        return (
            abs(self.yaw) <= max_yaw
            and abs(self.pitch) <= max_pitch
            and abs(self.roll) <= max_roll
        )

    @property
    def estimated_view(self) -> str:
        """Estimate the view angle from head pose."""
        abs_yaw = abs(self.yaw)
        if abs_yaw < 15:
            return "frontal"
        elif abs_yaw < 60:
            return "oblique"
        else:
            return "profile"


def extract_head_pose(transformation_matrix: np.ndarray | None) -> HeadPose | None:
    """Extract Euler angles from the 4x4 transformation matrix.

    Uses the rotation-matrix-to-Euler decomposition (ZYX convention).

    Args:
        transformation_matrix: 4x4 affine matrix from Face Landmarker.

    Returns:
        HeadPose with yaw, pitch, roll in degrees, or None if matrix is unavailable.
    """
    if transformation_matrix is None:
        return None

    R = transformation_matrix[:3, :3]

    # Decompose rotation matrix to Euler angles (ZYX convention)
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)

    if sy > 1e-6:  # Not gimbal lock
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
        roll = np.arctan2(R[2, 1], R[2, 2])
    else:
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(-R[1, 2], R[1, 1])
        roll = 0.0

    return HeadPose(
        yaw=round(float(np.degrees(yaw)), 1),
        pitch=round(float(np.degrees(pitch)), 1),
        roll=round(float(np.degrees(roll)), 1),
    )
