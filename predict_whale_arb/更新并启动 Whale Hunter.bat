@echo off
setlocal
cd /d "%~dp0"
set "ZIP=%TEMP%\Life-Gamble-latest.zip"
set "DEST=%TEMP%\Life-Gamble-latest"
echo [1/3] Downloading latest Whale Hunter...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing 'https://github.com/Yirenkun/Life-Gamble/archive/refs/heads/main.zip' -OutFile '%ZIP%'"
if errorlevel 1 goto FAIL
if exist "%DEST%" rmdir /s /q "%DEST%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Force '%ZIP%' '%TEMP%'"
if errorlevel 1 goto FAIL
if exist "%TEMP%\Life-Gamble-main" move /Y "%TEMP%\Life-Gamble-main" "%DEST%" >nul
echo [2/3] Starting Whale Hunter...
start "" "%DEST%\predict_whale_arb\启动 Whale Hunter.bat"
timeout /t 2 >nul
echo [3/3] Opening dashboard...
start "" "http://127.0.0.1:8080"
exit /b 0
:FAIL
echo Update failed. Open https://github.com/Yirenkun/Life-Gamble and download the latest ZIP manually.
pause
exit /b 1
