"""Tests for n8n webhook service (V2 payload)."""

import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.n8n_service import notify_n8n, notify_n8n_v2


def run(coro):
    """Run an async function synchronously for testing."""
    return asyncio.run(coro)


class TestNotifyN8n:
    def test_returns_false_when_no_url(self):
        with patch("app.services.n8n_service.settings") as mock_settings:
            mock_settings.n8n_webhook_url = ""
            result = run(notify_n8n({"test": "data"}))
            assert result is False

    def test_returns_true_on_success(self):
        with patch("app.services.n8n_service.settings") as mock_settings, \
             patch("app.services.n8n_service.httpx.AsyncClient") as mock_client_cls:
            mock_settings.n8n_webhook_url = "http://n8n.local/webhook/test"

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client_cls.return_value = mock_client

            result = run(notify_n8n({"test": "data"}))
            assert result is True

    def test_returns_false_on_http_error(self):
        import httpx

        with patch("app.services.n8n_service.settings") as mock_settings, \
             patch("app.services.n8n_service.httpx.AsyncClient") as mock_client_cls:
            mock_settings.n8n_webhook_url = "http://n8n.local/webhook/test"

            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=httpx.HTTPError("Connection refused"))
            mock_client_cls.return_value = mock_client

            result = run(notify_n8n({"test": "data"}))
            assert result is False

    def test_returns_false_on_4xx(self):
        with patch("app.services.n8n_service.settings") as mock_settings, \
             patch("app.services.n8n_service.httpx.AsyncClient") as mock_client_cls:
            mock_settings.n8n_webhook_url = "http://n8n.local/webhook/test"

            mock_resp = MagicMock()
            mock_resp.status_code = 400
            mock_resp.text = "Bad Request"
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client_cls.return_value = mock_client

            result = run(notify_n8n({"test": "data"}))
            assert result is False


class TestNotifyN8nV2:
    def test_wraps_payload_with_envelope(self):
        with patch("app.services.n8n_service.settings") as mock_settings, \
             patch("app.services.n8n_service.httpx.AsyncClient") as mock_client_cls:
            mock_settings.n8n_webhook_url = "http://n8n.local/webhook/test"

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client_cls.return_value = mock_client

            result = run(notify_n8n_v2(
                assessment_id="abc-123",
                patient_id="patient-456",
                aesthetic_score=85.0,
                zones_count=12,
                views_analyzed=["frontal", "profile"],
                payload={"zones": []},
            ))
            assert result is True

            # Check the envelope structure
            call_args = mock_client.post.call_args
            sent_json = call_args.kwargs.get("json") or call_args[1].get("json")
            assert sent_json["event"] == "assessment_complete"
            assert sent_json["assessment_id"] == "abc-123"
            assert sent_json["aesthetic_score"] == 85.0
            assert "data" in sent_json

    def test_returns_false_when_no_url(self):
        with patch("app.services.n8n_service.settings") as mock_settings:
            mock_settings.n8n_webhook_url = ""
            result = run(notify_n8n_v2(
                assessment_id="abc", patient_id=None,
                aesthetic_score=0, zones_count=0,
                views_analyzed=[], payload={},
            ))
            assert result is False
