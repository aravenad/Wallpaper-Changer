# tests/test_cli.py

import sys
import pytest
from src import cli

def test_parse_args_defaults(monkeypatch):
    test_argv = ["prog"]
    monkeypatch.setattr(sys, "argv", test_argv)
    args = cli.parse_args()
    assert args.interval == "1.5"
    assert args.category == "random"
