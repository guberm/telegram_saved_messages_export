@echo off
REM Telegram Saved Messages Exporter - Visual GUI Launcher
echo ============================================================
echo Telegram Saved Messages Exporter - Visual GUI
echo ============================================================
echo.

cd /d "%~dp0"
start "" /min py gui_visual.py
