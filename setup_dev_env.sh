#!/bin/bash

echo "Setting up development environment for Wallpaper Changer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.6 or higher."
    exit 1
fi

# Check Python version
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)"; then
    echo "Python 3.6 or higher is required."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies including development tools
echo "Installing dependencies..."
pip install -e ".[dev]"

echo
echo "Development environment setup complete!"
echo
echo "To activate the environment:"
echo "    source venv/bin/activate  # Linux/macOS"
echo "    venv\\Scripts\\activate.bat  # Windows"
echo
echo "To run tests:"
echo "    pytest"
echo "    - or -"
echo "    python tests/run_all_tests.py"
echo
echo "To run the app:"
echo "    python -m src.main"
echo
