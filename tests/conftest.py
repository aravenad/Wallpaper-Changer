import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the src directory to the path for all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Pre-mock modules that might be missing
required_mocks = [
    'colorama', 
    'keyboard', 
    'win32gui', 
    'win32con', 
    'pytest',
    'ctypes.windll.user32',
    'PIL'
]

# Create the necessary nested structure for ctypes.windll.user32
class MockUserDLL:
    def SystemParametersInfoW(self, *args, **kwargs):
        return True

class MockWindll:
    user32 = MockUserDLL()

# Apply mocks for all modules that might be missing
for mod_name in required_mocks:
    parts = mod_name.split('.')
    if len(parts) == 1:
        # Simple module
        if parts[0] not in sys.modules:
            sys.modules[parts[0]] = MagicMock()
    else:
        # Nested module (like ctypes.windll.user32)
        if parts[0] == 'ctypes':
            # Create proper module mock for ctypes with windll attribute
            mock_ctypes = MagicMock()
            mock_ctypes.windll = MockWindll()
            sys.modules['ctypes'] = mock_ctypes

@pytest.fixture(autouse=True)
def mock_logger(monkeypatch):
    """Mock logger for all tests to prevent console output during testing"""
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.success = MagicMock()
    mock_logger.debug = MagicMock()
    
    # Only patch the logger in modules that we know use it and are causing test output
    for module in ['unsplash_api', 'wallpaper', 'main', 'cli']:
        try:
            monkeypatch.setattr(f'src.{module}.logger', mock_logger)
        except (AttributeError, ImportError):
            pass
    
    return mock_logger

@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests and clean it up after"""
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

# Make sure categories module is properly loaded
try:
    from src.categories import UNSPLASH_CATEGORIES
    # Check for duplicates to fix tests
    from collections import Counter
    counts = Counter(UNSPLASH_CATEGORIES)
    duplicates = {item: count for item, count in counts.items() if count > 1}
    if duplicates:
        print(f"Warning: Duplicate categories found: {duplicates}")
except ImportError:
    print("Warning: Could not import categories module")
