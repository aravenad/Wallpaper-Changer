import unittest
from itertools import chain, repeat
from unittest.mock import patch
from src.main import main_loop

# A helper function to provide a constant time value.
def constant_time():
    return 1000  # or any constant number

# A stub for any helper values needed in your tests.
def create_test_values():
    return {}

class TestMainOperations(unittest.TestCase):

    @patch('src.main.process_commands')
    @patch('src.main.update_wallpaper_cmd')
    @patch('src.main.compute_auto_interval')
    @patch('src.main.exit_flag')
    def test_main_loop_auto_mode(self, mock_exit_flag, mock_compute, mock_update, mock_process):
        # Use an infinite sequence: first 20 False then always True.
        mock_exit_flag.is_set.side_effect = chain([False] * 20, repeat(True))
        mock_compute.return_value = 30
        mock_process.return_value = False

        with patch('src.main.time.time', side_effect=constant_time), \
             patch('src.main.time.sleep') as mock_sleep:
            main_loop(True, None, 'nature')

    @patch('src.main.process_commands')
    @patch('src.main.update_wallpaper_cmd')
    @patch('src.main.exit_flag')
    def test_main_loop_fixed_mode(self, mock_exit_flag, mock_update, mock_process):
        # Again, provide an infinite sequence for is_set().
        mock_exit_flag.is_set.side_effect = chain([False] * 20, repeat(True))
        mock_process.return_value = False

        with patch('src.main.time.time', side_effect=constant_time), \
             patch('src.main.time.sleep') as mock_sleep:
            main_loop(False, 5, 'nature')

if __name__ == '__main__':
    unittest.main()
