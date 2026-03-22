"""
Performance benchmark for 3-image assessment pipeline.

Goal: < 3 seconds for a complete 3-view assessment with synthetic data.
Uses synthetic detection results to isolate analysis/planning performance
from actual MediaPipe inference time (which varies by hardware).
"""

import time

import pytest

from tests.fixtures.synthetic import (
    make_symmetric_face,
    make_asymmetric_face,
    make_calibration,
    make_blendshapes,
)


def _run_analysis_pipeline():
    """Run the full analysis pipeline with synthetic data (no actual images)."""
    from app.analysis.zone_analyzer import analyze as analyze_zones, ViewInput
    from app.treatment.plan_generator import generate

    calibration = make_calibration()

    # Create 3 synthetic detections (frontal, profile, oblique)
    frontal_det = make_asymmetric_face()
    profile_det = make_symmetric_face()
    oblique_det = make_asymmetric_face()

    blendshapes = make_blendshapes("neutral")

    # Run zone analyzer with all 3 views
    zone_report = analyze_zones(
        frontal=ViewInput(
            detection=frontal_det,
            calibration=calibration,
            blendshapes=blendshapes,
        ),
        profile=ViewInput(
            detection=profile_det,
            calibration=calibration,
            blendshapes=blendshapes,
        ),
        oblique=ViewInput(
            detection=oblique_det,
            calibration=calibration,
            blendshapes=blendshapes,
        ),
    )

    # Treatment planning
    plan = generate(zone_report.zones)

    return zone_report, plan


class TestPerformanceBenchmark:
    """Performance benchmarks for the analysis pipeline."""

    def test_full_analysis_under_3_seconds(self):
        """Full 3-view analysis should complete in < 3 seconds."""
        start = time.perf_counter()
        zone_report, plan = _run_analysis_pipeline()
        elapsed = time.perf_counter() - start

        assert elapsed < 3.0, (
            f"Full analysis took {elapsed:.2f}s, exceeding 3s target"
        )
        assert zone_report is not None
        assert len(zone_report.zones) > 0
        assert plan is not None

    def test_ten_iterations_average(self):
        """Average over 10 runs should be well under 3 seconds."""
        times = []
        for _ in range(10):
            start = time.perf_counter()
            _run_analysis_pipeline()
            times.append(time.perf_counter() - start)

        avg = sum(times) / len(times)
        p95 = sorted(times)[int(len(times) * 0.95)]

        print(f"\nPerformance: avg={avg:.3f}s, p95={p95:.3f}s, "
              f"min={min(times):.3f}s, max={max(times):.3f}s")

        assert avg < 3.0, f"Average {avg:.2f}s exceeds 3s target"

    def test_single_engine_latency(self):
        """Individual engines should each complete in < 500ms."""
        from app.analysis.symmetry_engine import analyze as analyze_symmetry
        from app.analysis.proportion_engine import analyze as analyze_proportions
        from app.analysis.volume_engine import analyze as analyze_volume

        calibration = make_calibration()
        det = make_symmetric_face()

        engines = {
            "symmetry": lambda: analyze_symmetry(det, calibration),
            "proportions": lambda: analyze_proportions(det, calibration),
            "volume": lambda: analyze_volume(det, calibration),
        }

        for name, fn in engines.items():
            start = time.perf_counter()
            fn()
            elapsed = time.perf_counter() - start
            assert elapsed < 0.5, (
                f"{name} engine took {elapsed:.3f}s, exceeding 500ms target"
            )
