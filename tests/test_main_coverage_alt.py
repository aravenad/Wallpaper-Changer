import unittest
from unittest.mock import patch, MagicMock

from src.main import main_loop

class TestMainOperations(unittest.TestCase):
    @patch('src.main.process_commands')
    @patch('src.main.update_wallpaper_cmd')
    @patch('src.main.compute_auto_interval')
    @patch('src.main.exit_flag')
    def test_main_loop_auto_mode(self, mock_exit_flag, mock_compute, mock_update, mock_process):
        """Test main loop in auto mode using a callable side effect."""
        # Use a counter and a callable for the side effect
        call_count = 0
        
        def exit_flag_side_effect():
            nonlocal call_count
            call_count += 1
            # Return True after a certain number of calls
            return call_count > 15
            
        mock_exit_flag.is_set.side_effect = exit_flag_side_effect
        mock_compute.return_value = 30
        mock_process.return_value = False

        with patch('src.main.time.time', return_value=100), \
             patch('src.main.time.sleep'):
            main_loop(True, None, 'nature')

    @patch('src.main.process_commands')
    @patch('src.main.update_wallpaper_cmd')
    @patch('src.main.exit_flag')
    def test_main_loop_fixed_mode(self, mock_exit_flag, mock_update, mock_process):
        """Test main loop in fixed interval mode using a callable side effect."""
        # Use a counter and a callable for the side effect
        call_count = 0
        
        def exit_flag_side_effect():
            nonlocal call_count
            call_count += 1
            # Return True after a certain number of calls
            return call_count > 15
            
        mock_exit_flag.is_set.side_effect = exit_flag_side_effect
        mock_process.return_value = False

        with patch('src.main.time.time', return_value=100), \
             patch('src.main.time.sleep'):
            main_loop(False, 5, 'nature')  # 5 minutes
