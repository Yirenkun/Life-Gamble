@echo off
setlocal
cd /d "%~dp0"
set "APPDIR=%~dp0"
if exist "%APPDIR%dashboard\.env" goto RUN
if not exist "%APPDIR%dashboard\.env" copy /Y "%APPDIR%dashboard\.env.example" "%APPDIR%dashboard\.env" >nul
:RUN
where docker >nul 2>&1
if %errorlevel%==0 goto DOCKER
where python >nul 2>&1
if %errorlevel%==0 goto PYTHON
start "" "https://www.python.org/downloads/windows/"
echo Please install Python 3.11+ and run this file again.
pause
exit /b 1
:DOCKER
cd /d "%APPDIR%dashboard"
docker compose up --build -d
if %errorlevel% neq 0 (
  echo Docker startup failed. Try running "docker compose up --build" manually.
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8080"
echo Whale Hunter is running at http://127.0.0.1:8080
timeout /t 3 >nul
exit /b 0
:PYTHON
cd /d "%APPDIR%"
if not exist ".venv\Scripts\python.exe" python -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt -r dashboard\backend\requirements.txt
set "PYTHONPATH=%APPDIR%"
start "Whale Hunter Backend" cmd /k "cd /d %APPDIR% && set PYTHONPATH=%APPDIR% && .venv\Scripts\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8080"
timeout /t 3 >nul
start "" "http://127.0.0.1:8080"
echo Whale Hunter is running at http://127.0.0.1:8080
exit /b 0
