"""
Tests for the application's main run function.
"""
import pytest
from unittest.mock import patch, MagicMock

from src.main import run

@patch('src.main.init_dirs.ensure_directories')
@patch('src.main.cli.parse_args')
@patch('src.main.cli.select_category')
@patch('src.main.threading.Thread')
@patch('src.main.main_loop')
def test_run_normal(mock_main_loop, mock_thread, mock_select, mock_args, mock_dirs):
    """Test normal execution of run function."""
    # Setup mocks
    mock_args.return_value = MagicMock(interval='1.5')
    mock_select.return_value = 'nature'
    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance
    
    # Execute
    result = run()
    
    # Assert
    assert result == 0  # Should return success code
    mock_dirs.assert_called_once()
    mock_args.assert_called_once()
    mock_select.assert_called_once()
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    mock_main_loop.assert_called_once()

@patch('src.main.init_dirs.ensure_directories')
@patch('src.main.cli.parse_args')
@patch('src.main.cli.select_category')
@patch('src.main.threading.Thread')
@patch('src.main.main_loop')
def test_run_auto_mode(mock_main_loop, mock_thread, mock_select, mock_args, mock_dirs):
    """Test run function with auto mode."""
    # Setup mocks with auto interval
    mock_args.return_value = MagicMock(interval='auto')
    mock_select.return_value = 'nature'
    
    # Execute
    result = run()
    
    # Assert
    assert result == 0
    mock_main_loop.assert_called_once_with(True, None, 'nature')

@patch('src.main.init_dirs.ensure_directories')
@patch('src.main.cli.parse_args')
@patch('src.main.cli.select_category')
@patch('src.main.exit_flag')
def test_run_keyboard_interrupt(mock_exit_flag, mock_select, mock_args, mock_dirs):
    """Test run function with keyboard interrupt."""
    # Setup mock to raise KeyboardInterrupt
    mock_args.side_effect = KeyboardInterrupt()
    
    # Execute
    result = run()
    
    # Assert
    assert result == 0
    mock_exit_flag.set.assert_called_once()

@patch('src.main.init_dirs.ensure_directories')
@patch('src.main.cli.parse_args')
@patch('src.main.cli.select_category')
@patch('src.main.logger')
def test_run_exception(mock_logger, mock_select, mock_args, mock_dirs):
    """Test run function with exception."""
    # Setup mock to raise Exception
    mock_args.side_effect = Exception("Test error")
    
    # Execute
    result = run()
    
    # Assert
    assert result == 1  # Should return error code
    mock_logger.error.assert_called()  # Should log the error

@patch('src.main.init_dirs.ensure_directories')
@patch('src.main.cli.parse_args')
@patch('src.main.cli.select_category')
@patch('src.main.main_loop')
def test_run_with_category_list(mock_main_loop, mock_select, mock_args, mock_dirs):
    """Test run with a list of categories."""
    # Setup mocks with category list
    mock_args.return_value = MagicMock(interval='1.5')
    mock_select.return_value = ['nature', 'architecture']
    
    # Execute
    result = run()
    
    # Assert
    assert result == 0
    # Check that category list is correctly passed to main_loop
    mock_main_loop.assert_called_once_with(False, 1.5, ['nature', 'architecture'])
