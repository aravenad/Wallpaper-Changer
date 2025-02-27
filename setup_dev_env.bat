@echo off
echo Setting up development environment for Wallpaper Changer...

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6 or higher.
    exit /b 1
)

:: Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)"
if %ERRORLEVEL% neq 0 (
    echo Python 3.6 or higher is required.
    exit /b 1
)

:: Create a virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies including development tools
echo Installing dependencies...
pip install -e .[dev]

echo.
echo Development environment setup complete!
echo.
echo To activate the environment:
echo     call venv\Scripts\activate.bat
echo.
echo To run tests:
echo     pytest
echo     - or -
echo     python tests\run_all_tests.py
echo.
echo To run the app:
echo     python -m src.main
echo.
