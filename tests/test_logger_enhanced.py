# tests/test_logger_enhanced.py

import logging
import pytest
from src.logger import setup_logger, get_logger, log_traceback

def test_setup_logger(caplog):
    # Provide a dummy log file path
    logger_obj = setup_logger("test_logger", level=logging.DEBUG, log_file="dummy.log")
    # Ensure all handlers have integer levels.
    for h in logger_obj.handlers:
        h.setLevel(logging.DEBUG)
    logger_obj.debug("Debug message")
    assert "Debug message" in caplog.text

def test_get_logger_new():
    logger = get_logger("new_logger")
    assert isinstance(logger, logging.Logger)

def test_get_logger_existing():
    logger1 = get_logger("existing_logger")
    logger2 = get_logger("existing_logger")
    # Should return the same logger instance.
    assert logger1 is logger2

def test_log_traceback(caplog):
    logger_obj = setup_logger("trace_logger", level=logging.ERROR, log_file="dummy.log")
    # Ensure all handlers have integer levels.
    for h in logger_obj.handlers:
        h.setLevel(logging.ERROR)
    try:
        raise ValueError("Test error")
    except Exception as e:
        # Pass the logger, not the exception.
        log_traceback(logger_obj)
    assert "Test error" in caplog.text
