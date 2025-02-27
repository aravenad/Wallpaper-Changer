# src/logger.py

import logging
import sys
import importlib
import os
import traceback
from datetime import datetime

# Define basic log format
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Better import handling
def import_optional(module_name):
    """Import a module if available, otherwise return None"""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Import colorama or use fallbacks
colorama = import_optional('colorama')
if colorama:
    from colorama import Fore, Style, init
    init(autoreset=True)
    
    # Color constants for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.WHITE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
        'SUCCESS': Fore.GREEN + Style.BRIGHT,
    }
    
    HAS_COLORAMA = True
else:
    # Define fallback color codes for environments without colorama
    class DummyFore:
        CYAN = ''
        WHITE = ''
        YELLOW = ''
        RED = ''
        GREEN = ''
        BLUE = ''
    
    class DummyStyle:
        RESET_ALL = ''
        BRIGHT = ''
    
    Fore = DummyFore()
    Style = DummyStyle()
    
    COLORS = {
        'DEBUG': '',
        'INFO': '',
        'WARNING': '',
        'ERROR': '',
        'CRITICAL': '',
        'SUCCESS': '',
    }
    
    HAS_COLORAMA = False
    print("Warning: colorama not installed, running without color output.")

from . import config

# Custom log level for success messages
SUCCESS_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL, 'SUCCESS')

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        
        if HAS_COLORAMA:
            # Apply color to the levelname based on the level
            if levelname in COLORS:
                record.levelname = f"{COLORS[levelname]}{levelname}{Style.RESET_ALL}"
                
            # Apply specific colors to the message based on content markers
            if hasattr(record, '__dict__') and 'color' in record.__dict__:
                record.msg = f"{record.__dict__['color']}{record.msg}{Style.RESET_ALL}"
            elif '[✓]' in str(record.msg):
                # Success marker in message gets green
                record.msg = str(record.msg).replace('[✓]', f"{Fore.GREEN + Style.BRIGHT}[✓]{Style.RESET_ALL}")
            elif '[!]' in str(record.msg):
                # Warning/important marker gets yellow
                record.msg = str(record.msg).replace('[!]', f"{Fore.YELLOW}[!]{Style.RESET_ALL}")
            elif '[Auto Update Imminent]' in str(record.msg):
                # Imminent update gets cyan
                record.msg = str(record.msg).replace('[Auto Update Imminent]', f"{Fore.CYAN}[Auto Update Imminent]{Style.RESET_ALL}")
            elif '[Auto Interval]' in str(record.msg):
                # Auto interval info gets blue
                record.msg = str(record.msg).replace('[Auto Interval]', f"{Fore.BLUE}[Auto Interval]{Style.RESET_ALL}")
        
        return super().format(record)

class ColorLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        
    def success(self, msg, *args, **kwargs):
        """Log a success message (green colored)"""
        if kwargs.get('extra') is None:
            kwargs['extra'] = {}
        kwargs['extra']['color'] = Fore.GREEN + Style.BRIGHT if HAS_COLORAMA else ''
        self.log(SUCCESS_LEVEL, msg, *args, **kwargs)

def get_colored_console_logger(name=__name__):
    logging.setLoggerClass(ColorLogger)
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)
    
    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
            fmt="%(asctime)s -> %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    return logger

def setup_logger(name, level=logging.INFO, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Remove all existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    
    handlers = []
    if log_file:
        dirname = os.path.dirname(log_file)
        # Only create directory if a non-empty dirname is provided.
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
        # Also create a stream handler when log_file is provided.
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handlers.append(handler)
    
    for h in handlers:
        # Ensure handler's level is an integer.
        if not isinstance(h.level, int):
            h.level = level
        logger.addHandler(h)
    
    return logger

def get_logger(name):
    """
    Get a logger by name. If it doesn't exist or has no handlers,
    create it with default configuration.
    
    Args:
        name (str): Name of the logger
    
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, return it
    if logger.handlers:
        return logger
    
    # Otherwise set up a new logger
    log_dir = os.path.expanduser("~/.wallpaper/logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    log_file = os.path.join(log_dir, f"{name}.log")
    return setup_logger(name, log_file=log_file)

def log_traceback(logger):
    """
    Log the current exception's traceback.
    
    Args:
        logger: Logger instance to use for logging
    """
    logger.error(traceback.format_exc())

# Initialize the main application logger
def init_logger():
    """Initialize the main application logger"""
    global logger
    logger = get_colored_console_logger('wallpaper_changer')
    return logger

# Initialize logger when module is imported
logger = init_logger()
