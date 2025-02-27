# tests/test_cli_enhanced.py

import pytest
import sys
from src.cli import parse_args

def test_parse_args_defaults():
    # When no args are provided, default values should be used.
    # Store original sys.argv
    original_argv = sys.argv
    sys.argv = [sys.argv[0]]  # Keep program name but remove any arguments
    try:
        args = parse_args()
        # Default values updated: category should be "random"
        assert args.category == "random"
        assert args.search is None
        assert args.save is False
        if hasattr(args, 'auto_interval'):
            assert args.auto_interval is None
    finally:
        sys.argv = original_argv

def test_parse_args_with_search_using_argv():
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--search", "mountains"]
    try:
        args = parse_args()
        assert args.search == "mountains"
    finally:
        sys.argv = original_argv

def test_parse_args_with_save_flag():
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--save"]
    try:
        args = parse_args()
        assert args.save is True
    finally:
        sys.argv = original_argv

def test_parse_args_with_auto_interval():
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--auto-interval", "15"]
    try:
        args = parse_args()
        # Assuming auto_interval is converted to an integer.
        assert args.auto_interval == 15
    finally:
        sys.argv = original_argv

def test_parse_args_with_search_direct():
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--search", "mountains"]
    try:
        args = parse_args()
        assert args.search == "mountains"
    finally:
        sys.argv = original_argv

def test_parse_args_with_save_flag_direct():
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--save"]
    try:
        args = parse_args()
        assert args.save is True
    finally:
        sys.argv = original_argv

def test_parse_args_with_auto_interval_direct():
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--auto-interval", "15"]
    try:
        args = parse_args()
        # Assuming auto_interval is converted to an integer.
        assert args.auto_interval == 15
    finally:
        sys.argv = original_argv
