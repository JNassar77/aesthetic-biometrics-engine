"""Tests for structured JSON logging."""

import json
import logging
import pytest

from app.utils.logging import JSONFormatter, setup_logging, log_step


class TestJSONFormatter:
    def test_formats_as_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Hello %s", args=("world",), exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["message"] == "Hello world"
        assert data["level"] == "INFO"
        assert data["logger"] == "test"

    def test_includes_extra_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Step done", args=(), exc_info=None,
        )
        record.step = "detect"
        record.view = "frontal"
        record.duration_ms = 42

        output = formatter.format(record)
        data = json.loads(output)
        assert data["step"] == "detect"
        assert data["view"] == "frontal"
        assert data["duration_ms"] == 42

    def test_handles_exception(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Failed", args=(), exc_info=exc_info,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert "ValueError" in data["exception"]


class TestSetupLogging:
    def test_adds_json_handler(self):
        setup_logging(logging.DEBUG)
        root = logging.getLogger()
        json_handlers = [
            h for h in root.handlers
            if isinstance(h, logging.StreamHandler) and isinstance(h.formatter, JSONFormatter)
        ]
        assert len(json_handlers) >= 1

    def test_idempotent(self):
        setup_logging()
        setup_logging()
        root = logging.getLogger()
        json_handlers = [
            h for h in root.handlers
            if isinstance(h, logging.StreamHandler) and isinstance(h.formatter, JSONFormatter)
        ]
        # Should not add duplicate handlers
        assert len(json_handlers) == 1


class TestLogStep:
    def test_context_manager_logs_duration(self, caplog):
        test_logger = logging.getLogger("test.logstep")
        with caplog.at_level(logging.INFO, logger="test.logstep"):
            with log_step(test_logger, "test_step", view="frontal"):
                pass

        assert any("Starting test_step" in r.message for r in caplog.records)
        assert any("test_step completed" in r.message for r in caplog.records)

    def test_context_manager_logs_error(self, caplog):
        test_logger = logging.getLogger("test.logstep.err")
        with caplog.at_level(logging.ERROR, logger="test.logstep.err"):
            with pytest.raises(ValueError):
                with log_step(test_logger, "fail_step"):
                    raise ValueError("boom")

        assert any("fail_step failed" in r.message for r in caplog.records)

    def test_context_yields_dict_for_extra_data(self, caplog):
        test_logger = logging.getLogger("test.logstep.ctx")
        with caplog.at_level(logging.INFO, logger="test.logstep.ctx"):
            with log_step(test_logger, "ctx_step") as ctx:
                ctx["landmarks"] = 478

        # Should complete successfully
        assert any("ctx_step completed" in r.message for r in caplog.records)
