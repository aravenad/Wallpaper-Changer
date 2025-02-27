#!/usr/bin/env python3
"""
Run all tests for the wallpaper changer application.
This script discovers and runs all tests in the tests directory.
"""

import unittest
import sys
import os

# Add the parent directory to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import any modules that need to be loaded before tests run
from src.categories import UNSPLASH_CATEGORIES

def run_all_tests():
    """Discover and run all tests"""
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover all tests in the tests directory
    # This will find all tests in files starting with 'test_'
    # and classes/methods starting with 'test' or 'Test'
    test_dir = os.path.abspath(os.path.dirname(__file__))
    pattern = 'test_*.py'  # Match any Python file starting with 'test_'
    
    # Discover and load all tests
    test_suite = loader.discover(test_dir, pattern=pattern)
    
    # Create a test runner and run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the test result code (0 for success, 1 for failure)
    return 0 if result.wasSuccessful() else 1

def run_pytest():
    """Run tests with pytest for better output and features"""
    import subprocess
    try:
        # Run pytest for all tests in the tests directory
        test_dir = os.path.abspath(os.path.dirname(__file__))
        result = subprocess.run([sys.executable, "-m", "pytest", test_dir, "-v"], 
                               check=False)
        return result.returncode
    except:
        # Fall back to unittest if pytest fails or isn't installed
        print("Falling back to unittest framework...")
        return run_all_tests()

if __name__ == "__main__":
    # Check if the user wants to use pytest or unittest
    if "--use-pytest" in sys.argv:
        sys.exit(run_pytest())
    else:
        sys.exit(run_all_tests())
