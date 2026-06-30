@echo off
title FaceTrack Pro
cd /d "%~dp0"
echo.
echo  Starting FaceTrack Pro...
echo.
python app.py
if %errorlevel% neq 0 (
    echo.
    echo  Error: Could not start. Run install.bat first.
    pause
)
