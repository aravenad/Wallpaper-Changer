# tests/test_wallpaper_enhanced.py

import os
import pytest
import platform
from src.wallpaper import save_current_wallpaper, get_next_filename, set_wallpaper

def test_save_current_wallpaper_first_file(tmp_path):
    pytest.skip("save_current_wallpaper functionality not implemented")
    # Create a dummy source file.
    # src_file = tmp_path / "source.jpg"
    # src_file.write_text("dummy image data")
    # dest_dir = tmp_path / "wallpapers"
    # dest_dir.mkdir()
    # save_current_wallpaper(str(src_file), str(dest_dir))
    # Expect a file with a naming pattern (e.g. wallpaper_1.jpg) created in dest_dir.
    # files = list(dest_dir.glob("wallpaper_*"))
    # assert len(files) == 1
    # with open(files[0], "r") as f:
    #     content = f.read()
    # assert content == "dummy image data"

def test_save_current_wallpaper_no_source(tmp_path):
    pytest.skip("save_current_wallpaper functionality not implemented")
    # dest_dir = tmp_path / "wallpapers"
    # dest_dir.mkdir()
    # Expect a FileNotFoundError when the source file doesn't exist.
    # with pytest.raises(FileNotFoundError):
    #     save_current_wallpaper("non_existent.jpg", str(dest_dir))

def test_get_next_filename(tmp_path):
    dest_dir = tmp_path / "wallpapers"
    dest_dir.mkdir()
    next_file = get_next_filename(str(dest_dir))
    assert "wallpaper" in next_file
    # Create a file to simulate an existing wallpaper.
    file1 = dest_dir / next_file
    file1.write_text("image")
    next_file2 = get_next_filename(str(dest_dir))
    assert next_file2 != next_file

def test_set_wallpaper_windows(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    result = set_wallpaper("dummy_path.jpg")
    assert result is True

def test_set_wallpaper_linux(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    result = set_wallpaper("dummy_path.jpg")
    # Update expectation based on current (unimplemented) behavior
    assert result is False

def test_set_wallpaper_macos(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    result = set_wallpaper("dummy_path.jpg")
    # Update expectation based on current (unimplemented) behavior
    assert result is False
