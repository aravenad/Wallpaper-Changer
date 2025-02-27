"""
Comprehensive tests for the main module to improve coverage.
"""

import os
import time
import json
import pytest
import threading
from unittest.mock import patch, MagicMock, call
from src.main import (
    compute_auto_interval,
    update_rate_limits,
    process_key_press,
    is_desktop_foreground,
    process_commands,
    read_requests_log,
    write_requests_log,
    update_wallpaper,
    fetch_wallpaper,
    display_categories,
    handle_auto_mode,
    manual_override_listener,
    main_loop,
    run
)

class TestRateLimiting:
    """Tests for rate limiting and interval computation functions."""
    
    def test_compute_auto_interval_fresh_start(self):
        """Test interval computation with no prior history."""
        interval = compute_auto_interval(start_time=None)
        assert interval == 90.0
        
    def test_compute_auto_interval_hour_reset(self):
        """Test interval computation when hour has elapsed."""
        # Set start time to 2 hours ago
        old_start = time.time() - 7200
        interval = compute_auto_interval(start_time=old_start, remaining_requests=10)
        assert interval == 90.0
        
    def test_compute_auto_interval_no_requests(self):
        """Test interval when no requests are available."""
        current_time = time.time()
        interval = compute_auto_interval(remaining_requests=5, start_time=current_time, reserved_requests=10)
        assert interval == 600.0  # Should return 10 minutes (600s)
        
    def test_compute_auto_interval_normal(self):
        """Test normal interval computation."""
        current_time = time.time()
        # 50 requests remaining, 30 minutes into the hour, 5 reserved
        interval = compute_auto_interval(
            remaining_requests=50,
            start_time=current_time-1800,  # 30 minutes ago
            reserved_requests=5
        )
        # Should be approximately 45 requests over 30 minutes = 40 seconds per request
        assert 35 <= interval <= 45
        
    def test_compute_auto_interval_minimum_enforced(self):
        """Test minimum interval is enforced."""
        current_time = time.time()
        # 1000 requests remaining, 50 minutes into the hour
        interval = compute_auto_interval(
            remaining_requests=1000,
            start_time=current_time-3000,  # 50 minutes ago
            reserved_requests=5
        )
        # Would calculate a very small interval, but should enforce 30s minimum
        assert interval == 30.0
        
    def test_update_rate_limits(self):
        """Test updating rate limits from headers."""
        headers = {'X-Ratelimit-Remaining': '42'}
        remaining = update_rate_limits(headers)
        assert remaining == 42
        
    def test_update_rate_limits_invalid(self):
        """Test handling invalid rate limit headers."""
        headers = {'X-Ratelimit-Remaining': 'invalid'}
        with patch('src.main.requests_remaining', 50):
            remaining = update_rate_limits(headers)
            # Should not change the value since header is invalid
            assert remaining == 50
            
    def test_update_rate_limits_missing(self):
        """Test handling missing rate limit headers."""
        headers = {}
        with patch('src.main.requests_remaining', 30):
            remaining = update_rate_limits(headers)
            # Should not change the value since header is missing
            assert remaining == 30

class TestUserInterface:
    """Tests for user interface and input handling."""
    
    @patch('src.main.win32gui')
    def test_is_desktop_foreground_true(self, mock_win32gui):
        """Test desktop foreground detection when true."""
        mock_win32gui.GetForegroundWindow.return_value = 123
        mock_win32gui.GetClassName.return_value = "Progman"
        
        result = is_desktop_foreground()
        assert result is True
        
    @patch('src.main.win32gui')
    def test_is_desktop_foreground_false(self, mock_win32gui):
        """Test desktop foreground detection when false."""
        mock_win32gui.GetForegroundWindow.return_value = 456
        mock_win32gui.GetClassName.return_value = "Notepad"
        
        result = is_desktop_foreground()
        assert result is False
        
    @patch('src.main.win32gui', None)
    def test_is_desktop_foreground_no_win32gui(self):
        """Test desktop foreground detection without win32gui."""
        result = is_desktop_foreground()
        assert result is True  # Default to True when win32gui not available
        
    @patch('src.main.is_desktop_foreground')
    def test_process_key_press_not_desktop(self, mock_is_desktop):
        """Test key processing when not on desktop."""
        mock_is_desktop.return_value = False
        
        result = process_key_press('n')
        assert result == (None, None, 0, 0)  # No command when not on desktop
        
    @patch('src.main.is_desktop_foreground')
    @patch('src.main.exit_flag')
    def test_process_key_press_quit(self, mock_exit_flag, mock_is_desktop):
        """Test processing quit key."""
        mock_is_desktop.return_value = True
        
        result = process_key_press('q')
        assert result[0] == "exit"
        mock_exit_flag.set.assert_called_once()
        
    @patch('src.main.is_desktop_foreground')
    @patch('src.main.requests_remaining', 20)
    def test_process_key_press_manual_update(self, mock_is_desktop):
        """Test processing manual update key."""
        mock_is_desktop.return_value = True
        
        result = process_key_press('n')
        command, trigger, last_manual, last_print = result
        
        assert command == "update"
        assert trigger == "manual"
        assert last_manual > 0  # Should have updated the timestamp
        
    @patch('src.main.is_desktop_foreground')
    @patch('src.main.requests_remaining', 0)
    def test_process_key_press_no_requests(self, mock_is_desktop):
        """Test processing manual update with no requests left."""
        mock_is_desktop.return_value = True
        
        result = process_key_press('n')
        assert result[0] is None  # No command when no requests left
        
    @patch('src.main.is_desktop_foreground')
    def test_process_key_press_cooldown(self, mock_is_desktop):
        """Test processing key during cooldown period."""
        mock_is_desktop.return_value = True
        current_time = time.time()
        
        # Set last manual time to very recent
        result = process_key_press('n', last_manual_time=current_time - 2)
        assert result[0] is None  # No command during cooldown
        
    @patch('src.main.command_queue')
    def test_process_commands(self, mock_queue):
        """Test processing commands from queue."""
        mock_queue.empty.side_effect = [False, False, True]  # Not empty twice, then empty
        mock_queue.get_nowait.side_effect = [
            ("update", "auto"),
            ("save", None)
        ]
        
        with patch('src.main.update_wallpaper_cmd') as mock_update, \
             patch('src.main.wallpaper') as mock_wallpaper:
            
            result = process_commands()
            
            assert result is True  # Commands were processed
            mock_update.assert_called_once()
            mock_wallpaper.save_current_wallpaper.assert_called_once()
            
    @patch('src.main.command_queue')
    def test_process_commands_empty(self, mock_queue):
        """Test processing an empty command queue."""
        mock_queue.empty.return_value = True
        
        result = process_commands()
        
        assert result is False  # No commands were processed

class TestConfigFunctions:
    """Tests for configuration and file operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_file = os.path.join(os.path.dirname(__file__), "temp_requests_log.json")
        
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_read_requests_log_not_exists(self):
        """Test reading non-existent log file."""
        data = read_requests_log("/path/does/not/exist.json")
        assert data == {"requests": []}
        
    def test_read_requests_log_exists(self):
        """Test reading existing log file."""
        # Create a test file
        test_data = {"requests": [{"timestamp": "2023-01-01T12:00:00"}]}
        with open(self.temp_file, 'w') as f:
            import json
            json.dump(test_data, f)
            
        data = read_requests_log(self.temp_file)
        assert data == test_data
        
    def test_read_requests_log_invalid(self):
        """Test reading invalid log file."""
        # Create invalid JSON file
        with open(self.temp_file, 'w') as f:
            f.write("Not valid JSON")
            
        data = read_requests_log(self.temp_file)
        assert data == {"requests": []}
        
    def test_write_requests_log(self):
        """Test writing to requests log."""
        test_data = {"requests": [{"timestamp": "2023-01-01T12:00:00"}]}
        write_requests_log(self.temp_file, test_data)
        
        # Verify file was written correctly
        with open(self.temp_file, 'r') as f:
            data = json.load(f)
        assert data == test_data


class TestWallpaperFunctions:
    """Tests for wallpaper functions."""
    
    @patch('src.main.unsplash_api.fetch_wallpaper')
    def test_fetch_wallpaper_success(self, mock_fetch):
        """Test successful wallpaper fetching."""
        mock_fetch.return_value = ('/path/to/image.jpg', '50')
        
        result = fetch_wallpaper('nature')
        
        mock_fetch.assert_called_once_with('nature')
        assert result is not None, "Expected a dictionary but got None"
        assert result['file_path'] == '/path/to/image.jpg'
        assert 'source_url' in result
        
    @patch('src.main.unsplash_api.fetch_wallpaper')
    def test_fetch_wallpaper_failure(self, mock_fetch):
        """Test failed wallpaper fetching."""
        mock_fetch.return_value = (None, '50')
        
        result = fetch_wallpaper('nature')
        
        assert result is None
        
    @patch('src.main.unsplash_api.fetch_wallpaper')
    def test_fetch_wallpaper_exception(self, mock_fetch):
        """Test exception handling in wallpaper fetching."""
        mock_fetch.side_effect = Exception("API Error")
        
        result = fetch_wallpaper('nature')
        
        assert result is None
        
    @patch('src.main.get_categories')
    @patch('builtins.print')
    def test_display_categories(self, mock_print, mock_get_categories):
        """Test category display function."""
        mock_get_categories.return_value = ['nature', 'architecture', 'travel']
        
        display_categories()
        
        mock_get_categories.assert_called_once()
        # Header + 3 categories = 4 calls
        assert mock_print.call_count >= 4

class TestMainOperations:
    """Tests for main application operations."""
    
    @patch('src.main.update_wallpaper')
    @patch('src.main.compute_auto_interval')
    @patch('src.main.time.sleep')
    def test_handle_auto_mode_normal(self, mock_sleep, mock_compute, mock_update):
        """Test normal operation of auto mode."""
        # Make it run for 2 iterations
        mock_compute.side_effect = [60, 90]  
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        handle_auto_mode()
        
        assert mock_update.call_count == 2
        assert mock_compute.call_count == 2
        assert mock_sleep.call_count == 2
        
    @patch('src.main.update_wallpaper')
    @patch('src.main.compute_auto_interval')
    @patch('src.main.time.sleep')
    def test_handle_auto_mode_with_max_interval(self, mock_sleep, mock_compute, mock_update):
        """Test auto mode with maximum interval limit."""
        mock_compute.return_value = 300
        mock_sleep.side_effect = KeyboardInterrupt()
        
        handle_auto_mode(auto_interval=60)
        
        mock_update.assert_called_once()
        mock_compute.assert_called_once()
        mock_sleep.assert_called_once_with(60)
        
    @patch('src.main.keyboard')
    @patch('src.main.exit_flag')
    def test_manual_override_listener_no_keyboard(self, mock_exit_flag, mock_keyboard):
        """Test manual override listener without keyboard module."""
        # Remove read_key attribute to simulate missing keyboard
        del mock_keyboard.read_key
        mock_exit_flag.is_set.side_effect = [False, True]
        
        manual_override_listener('nature')
        
        # Should wait for exit flag
        assert mock_exit_flag.is_set.call_count == 2
        
    @patch('src.main.keyboard')
    @patch('src.main.exit_flag')
    @patch('src.main.process_key_press')
    def test_manual_override_listener_with_keys(self, mock_process, mock_exit_flag, mock_keyboard):
        """Test manual override listener with key presses."""
        # Make it process one key then exit
        mock_keyboard.read_key.return_value = 'n'
        mock_exit_flag.is_set.side_effect = [False, True]
        mock_process.return_value = ('update', 'manual', 100, 0)
        
        # Mock queue and time
        with patch('src.main.command_queue') as mock_queue, \
             patch('src.main.time.time', return_value=100):
            
            manual_override_listener('nature')
            
            # Should process the key and put command in queue
            mock_process.assert_called_once()
            mock_queue.put.assert_called_once_with(('update', 'manual'))

    @patch('src.main.process_commands')
    @patch('src.main.update_wallpaper_cmd')
    @patch('src.main.compute_auto_interval')
    @patch('src.main.exit_flag')
    def test_main_loop_auto_mode(self, mock_exit_flag, mock_compute, mock_update, mock_process):
        """Test main loop in auto mode."""
        # We'll control the number of iterations through the exit_flag mock
        call_count = 0
        
        def exit_flag_side_effect():
            nonlocal call_count
            call_count += 1
            # Return True after 10 iterations to break the loop
            return call_count > 10
            
        mock_exit_flag.is_set.side_effect = exit_flag_side_effect
        mock_compute.return_value = 30
        mock_process.return_value = False

        with patch('src.main.time.time', return_value=100), \
             patch('src.main.time.sleep') as mock_sleep:
            main_loop(True, None, 'nature')

    @patch('src.main.process_commands')
    @patch('src.main.update_wallpaper_cmd')
    @patch('src.main.exit_flag')
    def test_main_loop_fixed_mode(self, mock_exit_flag, mock_update, mock_process):
        """Test main loop in fixed interval mode."""
        # We'll control the number of iterations through the exit_flag mock
        call_count = 0
        
        def exit_flag_side_effect():
            nonlocal call_count
            call_count += 1
            # Return True after 10 iterations to break the loop
            return call_count > 10
            
        mock_exit_flag.is_set.side_effect = exit_flag_side_effect
        mock_process.return_value = False

        with patch('src.main.time.time', return_value=100), \
             patch('src.main.time.sleep') as mock_sleep:
            main_loop(False, 5, 'nature')  # 5 minutes
