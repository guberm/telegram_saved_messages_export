@echo off
REM Telegram Saved Messages Exporter - Visual GUI Launcher
echo ============================================================
echo Telegram Saved Messages Exporter - Visual GUI
echo ============================================================
echo.

py gui_visual.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting GUI. Make sure Python and dependencies are installed.
    echo Run: py -m pip install -r requirements.txt
    echo.
    pause
)
