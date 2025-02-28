#!/bin/bash

# Wallpaper-Changer quick start script for Linux/macOS
# This script sets up the environment if needed and launches the application

# Define colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to handle errors
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    echo "Press any key to exit..."
    read -n 1
    exit 1
}

# Go to script directory (equivalent to cd /d "%~dp0" in batch)
cd "$(dirname "$0")" || error_exit "Failed to change to script directory"

# Display welcome message
echo -e "${BLUE}=== Wallpaper Changer Quick Start ===${NC}"
echo -e "${BLUE}Setting up your environment and starting the application...${NC}"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    error_exit "Python is not installed or not in PATH. Please install Python and try again."
fi

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Setting it up...${NC}"
    
    # Setup virtual environment
    python3 create_venv.py || error_exit "Failed to create virtual environment"
fi

# Activate the virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source .venv/bin/activate || error_exit "Failed to activate virtual environment"

# Install requirements
echo -e "${GREEN}Installing required packages...${NC}"
pip install -q keyboard colorama

# Start the application with auto mode and category list
echo -e "${GREEN}Starting Wallpaper Changer...${NC}"
echo

# Run application with appropriate default settings
python -m src.integrated_main --auto --list-categories "$@"
EXIT_CODE=$?

# Deactivate virtual environment when done
deactivate

# Show appropriate exit message
if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${RED}Wallpaper Changer exited with error code $EXIT_CODE${NC}"
    # Shell equivalent of "pause" is to wait for a keypress
    echo "Press any key to continue..."
    read -n 1
fi

# Exit with the same code as the application
exit $EXIT_CODE
