@echo off
REM Backup Only - Windows Batch Script
REM Double-click this file to backup existing exports without exporting new messages

echo ============================================================
echo Telegram Export - Backup to Google Drive
echo ============================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run backup only
py main.py --backup-only --keep-archive

echo.
echo ============================================================
pause
