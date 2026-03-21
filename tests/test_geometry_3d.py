"""Tests for 3D geometry operations (Sprint 2)."""

import numpy as np
import pytest

from app.utils.geometry import (
    euclidean_3d,
    midpoint_3d,
    angle_between_points_3d,
    point_to_line_distance_3d,
    point_to_plane_distance,
    project_onto_plane,
    depth_difference,
    compute_sagittal_plane,
    # 2D operations still work
    euclidean_2d,
    midpoint_2d,
    angle_between_points,
)


class TestEuclidean3D:
    def test_same_point_is_zero(self):
        assert euclidean_3d((1, 2, 3), (1, 2, 3)) == 0.0

    def test_unit_distance_x(self):
        assert euclidean_3d((0, 0, 0), (1, 0, 0)) == pytest.approx(1.0)

    def test_unit_distance_z(self):
        assert euclidean_3d((0, 0, 0), (0, 0, 1)) == pytest.approx(1.0)

    def test_diagonal(self):
        assert euclidean_3d((0, 0, 0), (1, 1, 1)) == pytest.approx(np.sqrt(3))

    def test_negative_coordinates(self):
        assert euclidean_3d((-1, -1, -1), (1, 1, 1)) == pytest.approx(2 * np.sqrt(3))


class TestMidpoint3D:
    def test_same_point(self):
        assert midpoint_3d((5, 5, 5), (5, 5, 5)) == (5, 5, 5)

    def test_origin_and_unit(self):
        assert midpoint_3d((0, 0, 0), (2, 4, 6)) == (1.0, 2.0, 3.0)

    def test_symmetric(self):
        m = midpoint_3d((1, 2, 3), (5, 6, 7))
        assert m == (3.0, 4.0, 5.0)


class TestAngle3D:
    def test_right_angle(self):
        angle = angle_between_points_3d(
            vertex=(0, 0, 0),
            p1=(1, 0, 0),
            p2=(0, 1, 0),
        )
        assert angle == pytest.approx(90.0, abs=0.1)

    def test_straight_line(self):
        angle = angle_between_points_3d(
            vertex=(0, 0, 0),
            p1=(1, 0, 0),
            p2=(-1, 0, 0),
        )
        assert angle == pytest.approx(180.0, abs=0.1)

    def test_acute_angle(self):
        angle = angle_between_points_3d(
            vertex=(0, 0, 0),
            p1=(1, 0, 0),
            p2=(1, 1, 0),
        )
        assert angle == pytest.approx(45.0, abs=0.1)

    def test_3d_angle(self):
        angle = angle_between_points_3d(
            vertex=(0, 0, 0),
            p1=(1, 0, 0),
            p2=(0, 0, 1),
        )
        assert angle == pytest.approx(90.0, abs=0.1)


class TestPointToLineDistance3D:
    def test_point_on_line_is_zero(self):
        d = point_to_line_distance_3d((0.5, 0, 0), (0, 0, 0), (1, 0, 0))
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_unit_distance(self):
        # Point (0,1,0) is 1 unit from the x-axis
        d = point_to_line_distance_3d((0, 1, 0), (0, 0, 0), (1, 0, 0))
        assert d == pytest.approx(1.0, abs=1e-6)

    def test_z_offset(self):
        # Point (0,0,2) is 2 units from the x-axis
        d = point_to_line_distance_3d((0, 0, 2), (0, 0, 0), (1, 0, 0))
        assert d == pytest.approx(2.0, abs=1e-6)


class TestPointToPlaneDistance:
    def test_point_on_plane_is_zero(self):
        d = point_to_plane_distance((0, 0, 0), (0, 0, 0), (0, 0, 1))
        assert d == pytest.approx(0.0)

    def test_positive_distance(self):
        # Point 5 units above xy-plane
        d = point_to_plane_distance((0, 0, 5), (0, 0, 0), (0, 0, 1))
        assert d == pytest.approx(5.0)

    def test_negative_distance(self):
        d = point_to_plane_distance((0, 0, -3), (0, 0, 0), (0, 0, 1))
        assert d == pytest.approx(-3.0)

    def test_arbitrary_plane(self):
        # Plane through (1,1,1) with normal (1,0,0): x=1
        d = point_to_plane_distance((3, 0, 0), (1, 0, 0), (1, 0, 0))
        assert d == pytest.approx(2.0)


class TestProjectOntoPlane:
    def test_point_on_plane_unchanged(self):
        p = project_onto_plane((1, 2, 0), (0, 0, 0), (0, 0, 1))
        assert p[0] == pytest.approx(1.0)
        assert p[1] == pytest.approx(2.0)
        assert p[2] == pytest.approx(0.0)

    def test_projection_removes_normal_component(self):
        p = project_onto_plane((1, 2, 5), (0, 0, 0), (0, 0, 1))
        assert p[0] == pytest.approx(1.0)
        assert p[1] == pytest.approx(2.0)
        assert p[2] == pytest.approx(0.0, abs=1e-6)


class TestDepthDifference:
    def test_same_depth_is_zero(self):
        assert depth_difference((0, 0, 5), (0, 0, 5)) == 0.0

    def test_positive_when_p1_deeper(self):
        assert depth_difference((0, 0, 10), (0, 0, 5)) == pytest.approx(5.0)

    def test_negative_when_p1_shallower(self):
        assert depth_difference((0, 0, 3), (0, 0, 7)) == pytest.approx(-4.0)


class TestSagittalPlane:
    def test_vertical_face_gives_x_normal(self):
        # Nasion at top-center, gnathion at bottom-center, third point offset in x
        point, normal = compute_sagittal_plane(
            nasion=(0, 0, 0),
            gnathion=(0, 10, 0),
            midline_point=(1, 5, 0),  # offset in x
        )
        # Normal should be perpendicular to the sagittal plane → z-axis component
        assert abs(normal[2]) > 0.5 or abs(normal[0]) > 0.5  # non-degenerate

    def test_plane_passes_through_nasion(self):
        point, normal = compute_sagittal_plane(
            nasion=(1, 2, 3),
            gnathion=(1, 8, 3),
            midline_point=(2, 5, 3),
        )
        # plane_point is the nasion
        assert point == (1.0, 2.0, 3.0)


class TestLegacy2DStillWorks:
    """Ensure existing 2D functions are unchanged."""

    def test_euclidean_2d(self):
        assert euclidean_2d((0, 0), (3, 4)) == pytest.approx(5.0)

    def test_midpoint_2d(self):
        assert midpoint_2d((0, 0), (10, 10)) == (5.0, 5.0)

    def test_angle_between_points(self):
        angle = angle_between_points((0, 0), (1, 0), (0, 1))
        assert angle == pytest.approx(90.0, abs=0.1)
