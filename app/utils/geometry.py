"""
Geometry utilities for facial measurement.

2D operations (V1 — still used where z-depth is irrelevant):
- euclidean_2d, midpoint_2d, angle_between_points, point_to_line_distance

3D operations (V2 — use when z-coordinate adds clinical value):
- euclidean_3d, midpoint_3d, angle_between_points_3d
- point_to_plane_distance, project_onto_plane
- depth_difference (for volume/ogee-curve analysis)
"""

from __future__ import annotations

import numpy as np

# Type aliases for clarity
Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


# ───────────────────────────── 2D Operations ─────────────────────────────

def euclidean_2d(p1: Point2D, p2: Point2D) -> float:
    return float(np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))


def midpoint_2d(p1: Point2D, p2: Point2D) -> Point2D:
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def angle_between_points(
    vertex: Point2D,
    p1: Point2D,
    p2: Point2D,
) -> float:
    """Angle at vertex formed by rays vertex->p1 and vertex->p2, in degrees."""
    v1 = np.array(p1) - np.array(vertex)
    v2 = np.array(p2) - np.array(vertex)
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_angle)))


def point_to_line_distance(
    point: Point2D,
    line_p1: Point2D,
    line_p2: Point2D,
) -> float:
    """Signed perpendicular distance from point to line defined by two points.
    Positive = right of line (from p1 to p2), Negative = left."""
    x0, y0 = point
    x1, y1 = line_p1
    x2, y2 = line_p2
    num = (y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1
    den = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2) + 1e-8
    return float(num / den)


def px_to_mm_estimate(face_width_px: float, assumed_face_width_mm: float = 140.0) -> float:
    """Rough conversion factor from pixels to mm based on average face width.
    DEPRECATED: Use utils.pixel_calibration.calibrate() for iris-based calibration.
    """
    return assumed_face_width_mm / max(face_width_px, 1.0)


# ───────────────────────────── 3D Operations ─────────────────────────────

def euclidean_3d(p1: Point3D, p2: Point3D) -> float:
    """Euclidean distance in 3D space."""
    return float(np.sqrt(
        (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
    ))


def midpoint_3d(p1: Point3D, p2: Point3D) -> Point3D:
    """Midpoint of two 3D points."""
    return (
        (p1[0] + p2[0]) / 2,
        (p1[1] + p2[1]) / 2,
        (p1[2] + p2[2]) / 2,
    )


def angle_between_points_3d(
    vertex: Point3D,
    p1: Point3D,
    p2: Point3D,
) -> float:
    """Angle at vertex formed by rays vertex->p1 and vertex->p2, in degrees (3D)."""
    v1 = np.array(p1) - np.array(vertex)
    v2 = np.array(p2) - np.array(vertex)
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_angle)))


def point_to_line_distance_3d(
    point: Point3D,
    line_p1: Point3D,
    line_p2: Point3D,
) -> float:
    """Perpendicular distance from a 3D point to a line defined by two points."""
    p = np.array(point)
    a = np.array(line_p1)
    b = np.array(line_p2)
    ab = b - a
    ap = p - a
    cross = np.cross(ab, ap)
    return float(np.linalg.norm(cross) / (np.linalg.norm(ab) + 1e-8))


def point_to_plane_distance(
    point: Point3D,
    plane_point: Point3D,
    plane_normal: Point3D,
) -> float:
    """Signed distance from point to plane defined by a point and normal vector.

    Positive = point is on the side the normal points to.
    Useful for: E-line analysis, chin projection relative to facial planes.
    """
    p = np.array(point)
    pp = np.array(plane_point)
    n = np.array(plane_normal)
    n_norm = n / (np.linalg.norm(n) + 1e-8)
    return float(np.dot(p - pp, n_norm))


def project_onto_plane(
    point: Point3D,
    plane_point: Point3D,
    plane_normal: Point3D,
) -> Point3D:
    """Project a 3D point onto a plane.

    Useful for projecting landmarks onto the sagittal or coronal plane
    before measuring distances in a specific anatomical plane.
    """
    p = np.array(point)
    pp = np.array(plane_point)
    n = np.array(plane_normal)
    n_norm = n / (np.linalg.norm(n) + 1e-8)
    dist = np.dot(p - pp, n_norm)
    projected = p - dist * n_norm
    return (float(projected[0]), float(projected[1]), float(projected[2]))


def depth_difference(p1: Point3D, p2: Point3D) -> float:
    """Z-depth difference between two landmarks.

    Positive = p1 is further from camera (deeper) than p2.
    Useful for: ogee curve analysis, volume deficit estimation,
    malar prominence assessment.
    """
    return p1[2] - p2[2]


def compute_sagittal_plane(
    nasion: Point3D,
    gnathion: Point3D,
    midline_point: Point3D,
) -> tuple[Point3D, Point3D]:
    """Estimate the sagittal (mid-face) plane from midline landmarks.

    Returns:
        (plane_point, plane_normal) — defines the sagittal plane.
        The normal points left (toward the right side of the face in the image).
    """
    # Sagittal plane passes through nasion and gnathion,
    # with normal perpendicular to the nasion-gnathion line and
    # the line from midline_point to the nasion-gnathion midpoint
    a = np.array(nasion)
    b = np.array(gnathion)
    c = np.array(midline_point)

    v1 = b - a  # vertical direction
    v2 = c - (a + b) / 2  # lateral direction from midline

    normal = np.cross(v1, v2)
    norm_len = np.linalg.norm(normal)
    if norm_len < 1e-8:
        # Fallback: assume normal is along x-axis
        normal = np.array([1.0, 0.0, 0.0])
    else:
        normal = normal / norm_len

    plane_point = (float(a[0]), float(a[1]), float(a[2]))
    plane_normal = (float(normal[0]), float(normal[1]), float(normal[2]))
    return plane_point, plane_normal
