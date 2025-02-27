@REM filepath: /c:/Users/Damien/Desktop/Python/Wallpaper-Changer/setup.bat
@echo off
echo Setting up development environment...
python create_venv.py
if %ERRORLEVEL% NEQ 0 (
    echo Setup failed with error %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
echo.
echo To activate the environment, run:
echo .venv\Scripts\activate
