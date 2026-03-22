"""Tests for Supabase service V2 methods.

Uses unittest.mock to avoid needing the supabase package installed.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4


# Mock the supabase module before importing our service
@pytest.fixture(autouse=True)
def mock_supabase_module():
    """Patch the supabase module to avoid import errors."""
    mock_module = MagicMock()
    with patch.dict("sys.modules", {"supabase": mock_module}):
        yield mock_module


@pytest.fixture
def mock_client():
    """Mock the Supabase client singleton."""
    import importlib
    with patch.dict("sys.modules", {"supabase": MagicMock()}):
        import app.services.supabase_service as svc
        importlib.reload(svc)
        client = MagicMock()
        with patch.object(svc, "get_client", return_value=client):
            yield client, svc


class TestSaveAssessment:
    def test_inserts_assessment_row(self, mock_client):
        import asyncio
        client, svc = mock_client
        assessment_id = uuid4()
        org_id = uuid4()

        mock_resp = MagicMock()
        mock_resp.data = [{"id": str(assessment_id), "status": "completed"}]
        client.table.return_value.insert.return_value.execute.return_value = mock_resp

        result = asyncio.run(
            svc.save_assessment(
                assessment_id=assessment_id,
                organization_id=org_id,
                patient_id=None,
                status="completed",
                image_quality={"frontal": {"accepted": True}},
                global_metrics={"symmetry_index": 90.0},
                zones=[{"zone_id": "Ck2", "severity": 5.0}],
                treatment_plan={"primary_concerns": []},
                aesthetic_score=85.0,
                calibration_method="iris",
                engine_version="2.0.0",
                processing_time_ms=200,
            )
        )
        assert result["status"] == "completed"
        client.table.assert_called_with("assessments")

    def test_handles_empty_response(self, mock_client):
        import asyncio
        client, svc = mock_client

        mock_resp = MagicMock()
        mock_resp.data = []
        client.table.return_value.insert.return_value.execute.return_value = mock_resp

        result = asyncio.run(
            svc.save_assessment(
                assessment_id=uuid4(), organization_id=uuid4(),
                patient_id=None, status="completed",
                image_quality=None, global_metrics=None, zones=None,
                treatment_plan=None, aesthetic_score=0, calibration_method="iris",
                engine_version="2.0.0", processing_time_ms=0,
            )
        )
        assert result == {}

    def test_includes_patient_id_when_provided(self, mock_client):
        import asyncio
        client, svc = mock_client
        patient_id = uuid4()

        mock_resp = MagicMock()
        mock_resp.data = [{"id": "test"}]
        client.table.return_value.insert.return_value.execute.return_value = mock_resp

        asyncio.run(
            svc.save_assessment(
                assessment_id=uuid4(), organization_id=uuid4(),
                patient_id=patient_id, status="completed",
                image_quality=None, global_metrics=None, zones=None,
                treatment_plan=None, aesthetic_score=0, calibration_method="iris",
                engine_version="2.0.0", processing_time_ms=0,
            )
        )
        # Verify patient_id was included in the insert
        insert_call = client.table.return_value.insert.call_args
        row = insert_call[0][0]
        assert row["patient_id"] == str(patient_id)


class TestGetAssessment:
    def test_returns_assessment(self, mock_client):
        import asyncio
        client, svc = mock_client
        aid = uuid4()

        mock_resp = MagicMock()
        mock_resp.data = [{"id": str(aid), "zones": []}]
        client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_resp

        result = asyncio.run(svc.get_assessment(aid))
        assert result is not None
        assert result["id"] == str(aid)

    def test_returns_none_when_not_found(self, mock_client):
        import asyncio
        client, svc = mock_client

        mock_resp = MagicMock()
        mock_resp.data = []
        client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_resp

        result = asyncio.run(svc.get_assessment(uuid4()))
        assert result is None


class TestGetPatientHistory:
    def test_returns_ordered_history(self, mock_client):
        import asyncio
        client, svc = mock_client

        mock_resp = MagicMock()
        mock_resp.data = [
            {"id": str(uuid4()), "aesthetic_score": 85.0, "created_at": "2026-03-22T10:00:00Z"},
            {"id": str(uuid4()), "aesthetic_score": 80.0, "created_at": "2026-03-20T10:00:00Z"},
        ]
        client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_resp

        result = asyncio.run(svc.get_patient_history(uuid4()))
        assert len(result) == 2

    def test_empty_history(self, mock_client):
        import asyncio
        client, svc = mock_client

        mock_resp = MagicMock()
        mock_resp.data = []
        client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_resp

        result = asyncio.run(svc.get_patient_history(uuid4()))
        assert result == []


class TestSaveComparison:
    def test_inserts_comparison(self, mock_client):
        import asyncio
        client, svc = mock_client

        mock_resp = MagicMock()
        mock_resp.data = [{"id": str(uuid4()), "improvement_score": 72.5}]
        client.table.return_value.insert.return_value.execute.return_value = mock_resp

        result = asyncio.run(
            svc.save_comparison(
                organization_id=uuid4(), patient_id=None,
                pre_assessment_id=uuid4(), post_assessment_id=uuid4(),
                treatment_date="2026-03-22", treatment_notes="Session 1",
                zone_deltas=[{"zone_id": "Ck2"}], improvement_score=72.5,
            )
        )
        assert result["improvement_score"] == 72.5


class TestUploadImage:
    def test_returns_path_on_success(self, mock_client):
        import asyncio
        client, svc = mock_client

        result = asyncio.run(
            svc.upload_image("patient-images", "org/ass/frontal.jpg", b"\xff\xd8")
        )
        assert result == "org/ass/frontal.jpg"

    def test_returns_none_on_failure(self, mock_client):
        import asyncio
        client, svc = mock_client
        client.storage.from_.return_value.upload.side_effect = Exception("Upload failed")

        result = asyncio.run(
            svc.upload_image("patient-images", "org/ass/frontal.jpg", b"\xff\xd8")
        )
        assert result is None
