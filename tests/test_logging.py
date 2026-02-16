"""Tests for structured logging configuration."""

import json
import logging

from tessera.logging import JSONFormatter, configure_logging


class TestJSONFormatter:
    """Tests for the JSON log formatter."""

    def test_basic_message(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="tessera.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "tessera.test"
        assert parsed["message"] == "hello world"
        assert "timestamp" in parsed
        assert "exc_info" not in parsed

    def test_exception_info(self) -> None:
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            record = logging.LogRecord(
                name="tessera.test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="something broke",
                args=(),
                exc_info=True,
            )
            # LogRecord with exc_info=True captures the current exception
            import sys

            record.exc_info = sys.exc_info()

        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "something broke"
        assert "ValueError: test error" in parsed["exc_info"]

    def test_output_is_single_line(self) -> None:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="tessera.test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="multi\nline\nmessage",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        # JSON output should be a single line (no pretty printing)
        assert "\n" not in output


class TestConfigureLogging:
    """Tests for the configure_logging function."""

    def test_text_format(self) -> None:
        configure_logging(level="DEBUG", fmt="text")
        root = logging.getLogger()
        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1
        assert not isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_json_format(self) -> None:
        configure_logging(level="WARNING", fmt="json")
        root = logging.getLogger()
        assert root.level == logging.WARNING
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_clears_existing_handlers(self) -> None:
        root = logging.getLogger()
        root.addHandler(logging.StreamHandler())
        root.addHandler(logging.StreamHandler())
        assert len(root.handlers) >= 2

        configure_logging(level="INFO", fmt="text")
        assert len(root.handlers) == 1
