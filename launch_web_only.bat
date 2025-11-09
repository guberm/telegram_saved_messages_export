@echo off
chcp 65001 >nul
echo ====================================
echo Telegram Exporter - Web Only Launch
echo ====================================
echo.
echo This launches only the Web UI (React + API)
echo without the Tkinter GUI window.
echo.

REM Check for Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not installed!
    echo Install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check for Python (try different variants)
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :check_deps
)

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :check_deps
)

python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :check_deps
)

echo [ERROR] Python not installed!
echo Install Python from https://www.python.org/
pause
exit /b 1

:check_deps

echo [1/3] Checking Python dependencies...
%PYTHON_CMD% -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Installing uvicorn...
    %PYTHON_CMD% -m pip install uvicorn fastapi python-multipart websockets
)

echo [2/3] Checking Node.js dependencies...
if not exist "web_ui\node_modules" (
    echo [!] Installing React dependencies...
    cd web_ui
    call npm install
    cd ..
)

echo [3/3] Starting Web Services...
echo.
echo Starting FastAPI server...
start "Telegram Exporter API" cmd /k "%PYTHON_CMD% web_server.py"
timeout /t 3 /nobreak >nul

echo Starting React interface...
cd web_ui
start "Telegram Exporter Web UI" cmd /k "npm start"
cd ..

echo.
echo ====================================
echo Web Services Launched!
echo ====================================
echo.
echo Web interface: http://localhost:3000
echo API server: http://localhost:8000
echo.
echo To stop, close the terminal windows
echo ====================================
pause
