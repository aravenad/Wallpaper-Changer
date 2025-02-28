@echo off
cd /d "%~dp0"
title Wallpaper Changer

echo Wallpaper Changer - Starting...
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found. Setting up...
    python create_venv.py
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo.
)

REM Activate virtual environment and run the application
echo Starting Wallpaper Changer...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate the virtual environment.
    pause
    exit /b 1
)

REM Pass all command line arguments to the script
python -m src.integrated_main %*
if errorlevel 1 (
    echo Wallpaper Changer exited with an error.
    pause
)

REM Deactivate virtual environment when done
call deactivate