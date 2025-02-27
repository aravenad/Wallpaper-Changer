#!/usr/bin/env python
"""
Wallpaper Changer - Main entry point script

This script checks for required dependencies and launches the application.
"""

import sys
import os
import importlib.util

# Check if we're running as a script or frozen executable
if getattr(sys, 'frozen', False):
    # We're running as a compiled exe
    app_path = os.path.dirname(sys.executable)
else:
    # We're running as a script
    app_path = os.path.dirname(os.path.abspath(__file__))

# Add the application directory to sys.path
sys.path.insert(0, app_path)

# Try to import our dependency handler
try:
    from src.dependency_handler import ensure_dependencies
    
    # Check and install dependencies
    if not ensure_dependencies():
        print("Could not install all required dependencies. The program may not work correctly.")
except ImportError:
    # If even the dependency handler has issues, provide instructions
    print("Could not import dependency handler. Please install required packages manually:")
    print("pip install requests keyboard colorama pywin32 pytest pillow")

def main():
    """Main entry point for the wallpaper changer"""
    try:
        # Now we can safely import and run the main module
        from src import main
        return main.run()
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
