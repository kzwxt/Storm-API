"""
Logging Configuration Module

This module provides structured JSON logging configuration for the application.
All logs are formatted as JSON for easy parsing by log aggregators and monitoring tools.

Components:
    - JSONFormatter: Custom formatter for JSON log output
    - setup_logging: Configure root logger with JSON formatter
    - get_logger: Get a named logger instance
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Formats log records as JSON strings with consistent field names
    for easy parsing by log aggregation systems.

    Attributes:
        None

    Example:
        >>> formatter = JSONFormatter()
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: The log record to format

        Returns:
            str: JSON-formatted log entry

        Example:
            >>> formatter = JSONFormatter()
            >>> log_record = logging.LogRecord(
            ...     name="test", level=logging.INFO, pathname="test.py",
            ...     lineno=1, msg="Test message", args=(), exc_info=None
            ... )
            >>> json_log = formatter.format(log_record)
            >>> print(json_log)
        """
        log_entry: Dict[str, Any] = {
            "level": record.levelname,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": record.getMessage(),
        }

        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'message', 'pathname', 'process', 'processName', 'relativeCreated',
            'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info'
        }

        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured JSON logging.

    Sets up the root logger with a JSON formatter and removes any existing
    handlers to ensure clean configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> setup_logging(level="DEBUG")
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()

    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Log message")
    """
    return logging.getLogger(name)