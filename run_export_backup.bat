@echo off
REM Telegram Export with Backup - Windows Batch Script
REM Double-click this file to run the export with backup

echo ============================================================
echo Telegram Saved Messages Exporter
echo ============================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the export with backup
py main.py --backup

echo.
echo ============================================================
pause
