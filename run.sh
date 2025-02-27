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

# Display welcome message
echo -e "${BLUE}=== Wallpaper Changer Quick Start ===${NC}"
echo -e "${BLUE}Setting up your environment and starting the application...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 is not installed or not in PATH. Please install Python 3 and try again."
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

# Start the application
echo -e "${GREEN}Starting Wallpaper Changer...${NC}"
echo -e "${YELLOW}Tip: Press 'n' for new wallpaper, 's' to save current wallpaper, 'q' to quit${NC}"
echo ""

# Run the application with any passed arguments
python3 -m wallpaper_changer.main "$@"

# Deactivate virtual environment when done
deactivate

echo ""
echo -e "${GREEN}Thank you for using Wallpaper Changer!${NC}"
echo "Press any key to exit..."
read -n 1
