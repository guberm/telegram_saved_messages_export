@echo off
chcp 65001 >nul
cls
echo ====================================
echo Telegram Exporter - System Launch
echo ====================================
echo.
echo Choose launch mode:
echo [1] Web UI Only (2 windows: API + React)
echo [2] GUI Only (1 window: Tkinter)
echo [3] All Components (3 windows: API + React + GUI)
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :web_only
if "%choice%"=="2" goto :gui_only
if "%choice%"=="3" goto :all_components
if "%choice%"=="4" exit /b 0

echo Invalid choice! Please run again.
pause
exit /b 1

:web_only
cls
echo ====================================
echo Launching Web UI Only
echo ====================================
echo.
goto :check_python

:gui_only
cls
echo ====================================
echo Launching GUI Only
echo ====================================
echo.
goto :check_python

:all_components
cls
echo ====================================
echo Launching All Components
echo ====================================
echo.
goto :check_python

:check_python
REM Check for Node.js (only if web components needed)
if "%choice%"=="1" goto :check_node
if "%choice%"=="3" goto :check_node
goto :find_python

:check_node
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not installed!
    echo Install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:find_python
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

if "%choice%"=="1" goto :launch_web
if "%choice%"=="2" goto :launch_gui
if "%choice%"=="3" goto :launch_all
goto :end

:launch_web
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
start "Telegram Exporter API" cmd /k "%PYTHON_CMD% web_server.py"
timeout /t 3 /nobreak >nul

cd web_ui
start "Telegram Exporter Web UI" cmd /k "npm start"
cd ..

echo.
echo ====================================
echo Web Services Launched! (2 windows)
echo ====================================
echo.
echo Web interface: http://localhost:3000
echo API server: http://localhost:8000
echo.
goto :end

:launch_gui
echo [1/1] Starting Tkinter GUI...
start "Telegram Exporter GUI" cmd /k "%PYTHON_CMD% gui_visual.py"

echo.
echo ====================================
echo GUI Launched! (1 window)
echo ====================================
echo.
goto :end

:launch_all
echo [1/5] Checking Python dependencies...
%PYTHON_CMD% -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Installing uvicorn...
    %PYTHON_CMD% -m pip install uvicorn fastapi python-multipart websockets
)

echo [2/5] Checking Node.js dependencies...
if not exist "web_ui\node_modules" (
    echo [!] Installing React dependencies...
    cd web_ui
    call npm install
    cd ..
)

echo [3/5] Starting FastAPI server...
start "Telegram Exporter API" cmd /k "%PYTHON_CMD% web_server.py"
timeout /t 3 /nobreak >nul

echo [4/5] Starting React interface...
cd web_ui
start "Telegram Exporter Web UI" cmd /k "npm start"
cd ..
timeout /t 5 /nobreak >nul

echo [5/5] Starting Tkinter GUI...
start "Telegram Exporter GUI" cmd /k "%PYTHON_CMD% gui_visual.py"

echo.
echo ====================================
echo All Components Launched! (3 windows)
echo ====================================
echo.
echo Web interface: http://localhost:3000
echo API server: http://localhost:8000
echo Tkinter GUI: separate window
echo.
goto :end

:end
echo To stop, close all terminal windows
echo ====================================
pause
