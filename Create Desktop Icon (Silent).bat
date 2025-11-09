@echo off
:: Create Desktop Icon - Premium version (no console window)
:: Creates shortcut to VBS launcher for cleaner experience

title Create Desktop Shortcut

echo.
echo ========================================
echo   Create Desktop Shortcut (Silent)
echo ========================================
echo.

:: Get current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

:: Target - use VBS launcher (no console window)
set "TARGET=%SCRIPT_DIR%\Launch_Silent.vbs"

if not exist "%TARGET%" (
    echo [ERROR] Launch_Silent.vbs not found!
    echo Expected: %TARGET%
    pause
    exit /b 1
)

:: Create VBS script to make shortcut
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%DESKTOP%\Telegram Exporter.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TARGET%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Description = "Telegram Messages Exporter" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

:: Run VBS script
cscript //nologo "%VBS_SCRIPT%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Desktop shortcut created!
    echo ========================================
    echo.
    echo Look for "Telegram Exporter" on your desktop
    echo Double-click it to launch the application
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
