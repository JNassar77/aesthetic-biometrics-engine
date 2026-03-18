import numpy as np


def euclidean_2d(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return float(np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2))


def midpoint_2d(p1: tuple[float, float], p2: tuple[float, float]) -> tuple[float, float]:
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def angle_between_points(
    vertex: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
) -> float:
    """Angle at vertex formed by rays vertex->p1 and vertex->p2, in degrees."""
    v1 = np.array(p1) - np.array(vertex)
    v2 = np.array(p2) - np.array(vertex)
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_angle)))


def point_to_line_distance(
    point: tuple[float, float],
    line_p1: tuple[float, float],
    line_p2: tuple[float, float],
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
    """Rough conversion factor from pixels to mm based on average face width."""
    return assumed_face_width_mm / max(face_width_px, 1.0)
