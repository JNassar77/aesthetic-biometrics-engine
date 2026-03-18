"""Tests for landmark index completeness and consistency."""

from app.detection.landmark_index import (
    MIDLINE, PAIRED, IRIS, ZONE_LANDMARKS,
    LIP_UPPER_OUTER, LIP_LOWER_OUTER, FACE_OVAL,
    all_zone_ids, get_zone,
)


class TestLandmarkIndex:
    def test_midline_landmarks_in_range(self):
        for name, idx in MIDLINE.items():
            assert 0 <= idx <= 477, f"Midline landmark {name}={idx} out of range"

    def test_paired_landmarks_in_range(self):
        for name, (left, right) in PAIRED.items():
            assert 0 <= left <= 477, f"Paired {name} left={left} out of range"
            assert 0 <= right <= 477, f"Paired {name} right={right} out of range"
            assert left != right, f"Paired {name} left==right"

    def test_iris_landmarks_in_refined_range(self):
        for name, idx in IRIS.items():
            assert 468 <= idx <= 477, f"Iris landmark {name}={idx} not in iris range 468-477"

    def test_all_16_zones_defined(self):
        zone_ids = all_zone_ids()
        expected = ["T1", "Bw1", "Bw2", "Ck1", "Ck2", "Ck3", "Tt1", "Ns1",
                    "Lp1", "Lp2", "Lp3", "Mn1", "Jw1", "Ch1", "Jl1", "Pf1"]
        for zid in expected:
            assert zid in zone_ids, f"Zone {zid} missing from ZONE_LANDMARKS"

    def test_zone_landmarks_in_range(self):
        for zone_id, zone in ZONE_LANDMARKS.items():
            for idx in zone.primary_landmarks:
                assert 0 <= idx <= 477, f"Zone {zone_id} primary landmark {idx} out of range"
            for idx in zone.secondary_landmarks:
                assert 0 <= idx <= 477, f"Zone {zone_id} secondary landmark {idx} out of range"

    def test_get_zone_returns_correct(self):
        zone = get_zone("Ck2")
        assert zone is not None
        assert zone.zone_name == "Zygomatic Eminence"

    def test_get_zone_nonexistent_returns_none(self):
        assert get_zone("INVALID") is None

    def test_lip_contours_are_closed_loops(self):
        assert LIP_UPPER_OUTER[0] == 61
        assert LIP_UPPER_OUTER[-1] == 291
        assert LIP_LOWER_OUTER[0] == 291
        assert LIP_LOWER_OUTER[-1] == 61

    def test_face_oval_is_closed(self):
        assert FACE_OVAL[0] == FACE_OVAL[-1]
