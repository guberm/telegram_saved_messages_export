@echo off
REM Telegram Export - Windows Batch Script
REM Double-click this file to run the export

echo ============================================================
echo Telegram Saved Messages Exporter
echo ============================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the export
py main.py

echo.
echo ============================================================
pause
