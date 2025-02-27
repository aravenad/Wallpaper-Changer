import logging
from unittest.mock import patch, MagicMock, mock_open, call
from src.logger import setup_logger, get_logger, log_traceback

class TestLogger:
    @patch('src.logger.os.path.exists')
    @patch('src.logger.os.makedirs')
    @patch('src.logger.logging.FileHandler')
    @patch('src.logger.logging.StreamHandler')
    def test_setup_logger(self, mock_stream_handler, mock_file_handler, mock_makedirs, mock_exists):
        # Test logger setup with directory creation
        mock_exists.return_value = False
        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance
        mock_stream_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_stream_handler_instance
        
        # Pass log_file using keyword so that level remains default (an int)
        logger = setup_logger('test_logger', log_file='/path/to/log.txt')
        
        # Check directory was created for log file
        mock_makedirs.assert_called_once()
        
        # Check if handlers were created with correct parameters
        mock_file_handler.assert_called_once()
        mock_stream_handler.assert_called_once()
        
        # Check if logger has expected properties
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'
    
    @patch('src.logger.setup_logger')
    @patch('src.logger.logging.getLogger')
    def test_get_logger_new(self, mock_get_logger, mock_setup_logger):
        # Test getting a new logger
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        mock_setup_logger.return_value = mock_logger
        
        result = get_logger('test_component')
        
        mock_get_logger.assert_called_with('test_component')
        mock_setup_logger.assert_called_once()
        assert result == mock_logger
    
    @patch('src.logger.logging.getLogger')
    def test_get_logger_existing(self, mock_get_logger):
        # Test getting an existing logger
        mock_logger = MagicMock()
        mock_logger.handlers = [MagicMock()]  # Logger already has handlers
        mock_get_logger.return_value = mock_logger
        
        result = get_logger('existing_logger')
        
        mock_get_logger.assert_called_with('existing_logger')
        assert result == mock_logger
    
    @patch('src.logger.traceback.format_exc')
    def test_log_traceback(self, mock_format_exc):
        # Test logging a traceback
        mock_logger = MagicMock()
        mock_format_exc.return_value = "Formatted traceback"
        
        log_traceback(mock_logger)
        
        mock_format_exc.assert_called_once()
        mock_logger.error.assert_called_with("Formatted traceback")
