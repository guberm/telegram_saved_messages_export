@echo off
echo ====================================
echo Telegram Exporter - System Launch
echo ====================================
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

echo [ОШИБКА] Python не установлен!
echo Установите Python с https://www.python.org/
pause
exit /b 1

:check_deps

echo [1/5] Проверка зависимостей Python...
%PYTHON_CMD% -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Установка uvicorn...
    %PYTHON_CMD% -m pip install uvicorn fastapi python-multipart websockets
)

echo [2/5] Проверка зависимостей Node.js...
if not exist "web_ui\node_modules" (
    echo [!] Установка зависимостей React...
    cd web_ui
    call npm install
    cd ..
)

echo [3/5] Запуск FastAPI сервера...
start "Telegram Exporter API" cmd /k "%PYTHON_CMD% web_server.py"
timeout /t 3 /nobreak >nul

echo [4/5] Запуск React интерфейса...
cd web_ui
start "Telegram Exporter Web UI" cmd /k "npm start"
cd ..
timeout /t 5 /nobreak >nul

echo [5/5] Запуск Tkinter GUI...
start "Telegram Exporter GUI" cmd /k "%PYTHON_CMD% gui_visual.py"

echo.
echo ====================================
echo Все компоненты запущены!
echo ====================================
echo.
echo Web интерфейс: http://localhost:3000
echo API сервер: http://localhost:8000
echo Tkinter GUI: отдельное окно
echo.
echo Для остановки закройте все окна терминалов
echo ====================================
pause
