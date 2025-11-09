@echo off
chcp 65001 >nul
:: Quick Desktop Shortcut Creator for Silent GUI

title Create Silent GUI Shortcut

echo.
echo ========================================
echo   Create Silent GUI Shortcut
echo ========================================
echo.
echo This will create a desktop shortcut that
echo launches the Telegram Exporter GUI
echo WITHOUT showing console windows!
echo.
pause

:: Get current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

:: Target - Silent VBS launcher
set "TARGET=%SCRIPT_DIR%\Launch_Silent.vbs"

if not exist "%TARGET%" (
    echo [ERROR] Launch_Silent.vbs not found!
    echo Expected: %TARGET%
    pause
    exit /b 1
)

:: Create VBS script to make shortcut
set "VBS_SCRIPT=%TEMP%\create_shortcut_silent.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%DESKTOP%\Telegram Exporter (Silent).lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TARGET%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Description = "Telegram Messages Exporter - Silent GUI" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

:: Run VBS script
cscript //nologo "%VBS_SCRIPT%"

:: Clean up
del "%VBS_SCRIPT%"

echo.
echo ========================================
echo SUCCESS! Shortcut created!
echo ========================================
echo.
echo Location: %DESKTOP%\Telegram Exporter (Silent).lnk
echo.
echo Double-click the shortcut to launch the GUI
echo without any console windows!
echo.
pause
