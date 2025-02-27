# tests/test_init_dirs_enhanced.py

import os
import tempfile
import pytest
from src.init_dirs import create_app_dirs, check_config_file_exists, create_default_config_file

def test_create_app_dirs():
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Passing base_dir so folders are created directly under tmpdirname.
        create_app_dirs(base_dir=tmpdirname)
        config_dir = os.path.join(tmpdirname, "config")
        images_dir = os.path.join(tmpdirname, "images")
        saved_dir = os.path.join(tmpdirname, "saved")
        assert os.path.isdir(config_dir)
        assert os.path.isdir(images_dir)
        assert os.path.isdir(saved_dir)

def test_check_config_file_exists(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text("default config")
    assert check_config_file_exists(str(config_file)) is True

def test_check_config_file_not_exists(tmp_path):
    config_file = tmp_path / "config.ini"
    if config_file.exists():
        config_file.unlink()
    assert check_config_file_exists(str(config_file)) is False

def test_create_default_config_file(tmp_path):
    config_file = tmp_path / "default_config.ini"
    result = create_default_config_file(str(config_file))
    # Assuming the function returns True on success and writes non‐empty content.
    assert result is True
    assert config_file.read_text() != ""
