@echo off
:: Create Desktop Icon - Web UI Silent Launch
:: Creates shortcut to VBS launcher for web interface

title Create Desktop Shortcut - Web UI

echo.
echo ========================================
echo   Create Desktop Shortcut (Web Silent)
echo ========================================
echo.

:: Get current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

:: Target - use VBS launcher for web (no console window)
set "TARGET=%SCRIPT_DIR%\Launch_Web_Silent.vbs"

if not exist "%TARGET%" (
    echo [ERROR] Launch_Web_Silent.vbs not found!
    echo Expected: %TARGET%
    pause
    exit /b 1
)

:: Create VBS script to make shortcut
set "VBS_SCRIPT=%TEMP%\create_shortcut_web.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%DESKTOP%\Telegram Exporter Web.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TARGET%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Description = "Telegram Messages Exporter - Web Interface" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

:: Run VBS script
cscript //nologo "%VBS_SCRIPT%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Desktop shortcut created!
    echo ========================================
    echo.
    echo Look for "Telegram Exporter Web" on your desktop
    echo Double-click it to launch the web interface
    echo (No console window will appear)
) else (
    echo.
    echo [ERROR] Failed to create shortcut
    echo Try running as Administrator
)

:: Cleanup
del "%VBS_SCRIPT%" 2>nul

echo.
pause
