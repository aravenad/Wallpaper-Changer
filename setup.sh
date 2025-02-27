#!/bin/bash
echo "Setting up development environment..."
python3 create_venv.py
if [ $? -ne 0 ]; then
    echo "Setup failed with error $?"
    exit 1
fi
echo ""
echo "To activate the environment, run:"
echo "source .venv/bin/activate"
