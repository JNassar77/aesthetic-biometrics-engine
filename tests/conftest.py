"""Shared pytest fixtures and test isolation."""

import pytest


@pytest.fixture(autouse=True)
def _reset_landmarker_singleton():
    """Reset the process-wide landmarker singleton around every test.

    `orchestrator.get_landmarker()` caches a single FaceLandmarkerV2 for the
    whole process (loaded once at runtime). Without resetting it between tests,
    a real instance loaded by one test would leak into another that expects to
    mock FaceLandmarkerV2 — making outcomes depend on test order.
    """
    import app.pipeline.orchestrator as orch

    orch._landmarker_singleton = None
    yield
    orch._landmarker_singleton = None
