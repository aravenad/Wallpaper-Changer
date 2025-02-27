"""
Tests for the wallpaper_changer.main module
"""
import argparse
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

from wallpaper_changer.main import main, parse_arguments


class TestWallpaperChangerMain(unittest.TestCase):
    """Test cases for wallpaper_changer.main module"""

    def test_parse_arguments_defaults(self):
        """Test argument parser with default values"""
        # Mock sys.argv to simulate command line arguments
        with patch('sys.argv', ['main.py']):
            args = parse_arguments()
            self.assertEqual(args.config, 'settings.json')
            self.assertIsNone(args.interval)
            self.assertIsNone(args.source)
            self.assertFalse(args.once)

    def test_parse_arguments_custom(self):
        """Test argument parser with custom values"""
        # Mock sys.argv to simulate command line arguments
        with patch('sys.argv', [
            'main.py',
            '--config', 'custom_config.json',
            '--interval', '60',
            '--source', 'custom_dir',
            '--once'
        ]):
            args = parse_arguments()
            self.assertEqual(args.config, 'custom_config.json')
            self.assertEqual(args.interval, 60)
            self.assertEqual(args.source, 'custom_dir')
            self.assertTrue(args.once)

    def test_parse_arguments_short_options(self):
        """Test argument parser with short option names"""
        # Mock sys.argv to simulate command line arguments
        with patch('sys.argv', [
            'main.py',
            '-c', 'custom_config.json',
            '-i', '60',
            '-s', 'custom_dir'
        ]):
            args = parse_arguments()
            self.assertEqual(args.config, 'custom_config.json')
            self.assertEqual(args.interval, 60)
            self.assertEqual(args.source, 'custom_dir')
            self.assertFalse(args.once)

    def test_main_once_mode(self):
        """Test main function in once mode - with completely fresh mocks"""
        # Create all fresh mocks for this test only
        with patch('sys.exit') as mock_exit, \
             patch('wallpaper_changer.main.Config') as mock_config_class, \
             patch('wallpaper_changer.main.WallpaperHandler') as mock_handler_class, \
             patch('wallpaper_changer.main.logging.basicConfig') as mock_logging_config:
            
            # Set up mocks
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            mock_handler = MagicMock()
            mock_handler_class.return_value = mock_handler
            mock_handler.change_wallpaper.return_value = True
            
            # Special handling for sys.exit - make it raise an exception to stop execution
            mock_exit.side_effect = SystemExit
            
            # Mock logger
            mock_logger = MagicMock()
            with patch('wallpaper_changer.main.logger', mock_logger):
                # Mock command line arguments
                mock_args = MagicMock()
                mock_args.config = 'settings.json'
                mock_args.interval = None
                mock_args.source = None
                mock_args.once = True
                
                with patch('wallpaper_changer.main.parse_arguments', return_value=mock_args):
                    # Call should exit with sys.exit
                    with self.assertRaises(SystemExit):
                        main()
                    
                # Verify the function flow
                mock_config_class.assert_called_once_with('settings.json')
                mock_handler_class.assert_called_once_with(mock_config)
                # Verify exactly one call
                self.assertEqual(mock_handler.change_wallpaper.call_count, 1)
                mock_logger.info.assert_any_call("Wallpaper Changer started")
                mock_logger.info.assert_any_call("Wallpaper changed successfully. Exiting.")
                mock_exit.assert_called_once_with(0)

    def test_main_continuous_mode(self):
        """Test main function in continuous mode with one iteration"""
        # Create all fresh mocks for this test only
        with patch('sys.exit') as mock_exit, \
             patch('wallpaper_changer.main.Config') as mock_config_class, \
             patch('wallpaper_changer.main.WallpaperHandler') as mock_handler_class, \
             patch('wallpaper_changer.main.time') as mock_time, \
             patch('wallpaper_changer.main.logging.basicConfig') as mock_logging_config:
            
            # Set up mocks
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Correct behavior: mock_config.get should return the OVERRIDDEN interval (60)
            # not the default 30 to match the expected sleep time
            mock_config.get.return_value = 60  # Return the overridden value when asked
            
            mock_handler = MagicMock()
            mock_handler_class.return_value = mock_handler
            mock_handler.change_wallpaper.return_value = True
            
            # Make time.sleep raise KeyboardInterrupt after first call to simulate user exit
            mock_time.sleep.side_effect = KeyboardInterrupt()
            
            # Special handling for sys.exit - make it raise an exception to stop execution
            mock_exit.side_effect = SystemExit
            
            # Mock logger
            mock_logger = MagicMock()
            with patch('wallpaper_changer.main.logger', mock_logger):
                # Mock command line arguments
                mock_args = MagicMock()
                mock_args.config = 'settings.json'
                mock_args.interval = 60  # Override interval
                mock_args.source = 'custom_source'  # Set custom source
                mock_args.once = False
                
                with patch('wallpaper_changer.main.parse_arguments', return_value=mock_args):
                    # Call should exit with sys.exit
                    with self.assertRaises(SystemExit):
                        main()
                    
                # Verify the function flow
                mock_config_class.assert_called_once_with('settings.json')
                mock_config.set.assert_has_calls([
                    call('interval', 60),
                    call('source', 'custom_source')
                ])
                mock_handler_class.assert_called_once_with(mock_config)
                mock_handler.change_wallpaper.assert_called_once()
                mock_time.sleep.assert_called_once_with(60 * 60)  # 60 minutes converted to seconds
                mock_logger.info.assert_any_call("Wallpaper Changer started")
                mock_logger.info.assert_any_call("Next wallpaper change in 60 minutes.")
                mock_logger.info.assert_any_call("Received exit signal. Shutting down...")
                mock_exit.assert_called_once_with(0)

    def test_main_exception_handling(self):
        """Test main function exception handling"""
        # Create all fresh mocks for this test only
        with patch('sys.exit') as mock_exit, \
             patch('wallpaper_changer.main.Config') as mock_config_class, \
             patch('wallpaper_changer.main.WallpaperHandler') as mock_handler_class, \
             patch('wallpaper_changer.main.logging.basicConfig') as mock_logging_config:
            
            # Set up mocks to raise an exception
            mock_config_class.side_effect = Exception("Test error")
            
            # Special handling for sys.exit - make it raise an exception to stop execution
            mock_exit.side_effect = SystemExit
            
            # Mock logger
            mock_logger = MagicMock()
            with patch('wallpaper_changer.main.logger', mock_logger):
                # Mock command line arguments
                mock_args = MagicMock()
                mock_args.config = 'settings.json'
                
                with patch('wallpaper_changer.main.parse_arguments', return_value=mock_args):
                    # Call should exit with sys.exit
                    with self.assertRaises(SystemExit):
                        main()
                    
                # Verify the exception was caught and logged
                mock_logger.error.assert_called_with("Unhandled exception: Test error")
                mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
