@echo off
:: Telegram Exporter - Quick Launcher
:: Launches tkinter GUI directly

title Telegram Exporter
cd /d "%~dp0"

echo.
echo ========================================
echo   Telegram Messages Exporter
echo ========================================
echo.
echo Starting application...
echo.

:: Проверка Python (пробуем разные варианты)
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :run_gui
)

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :run_gui
)

python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :run_gui
)

echo [ERROR] Python not found!
echo Please install Python from https://www.python.org/
echo.
pause
exit /b 1

:run_gui
:: Запуск GUI
%PYTHON_CMD% gui_visual.py

:: Если программа закрылась с ошибкой
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application crashed!
    pause
)
