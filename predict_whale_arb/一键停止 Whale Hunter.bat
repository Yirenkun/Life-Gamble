@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>&1
if %errorlevel%==0 (
  cd /d "%~dp0dashboard"
  docker compose down
  echo Whale Hunter stopped.
  pause
  exit /b 0
)
echo Close the Whale Hunter Backend window to stop the local server.
pause
