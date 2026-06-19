@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..") do set "PROJECT_ROOT=%%~fI"
set "DOCKER_DIR=%PROJECT_ROOT%\infra\docker"

docker info >nul 2>nul
if errorlevel 1 (
  echo Docker Desktop is not running. Please start Docker Desktop first.
  pause
  exit /b 1
)

if not exist "%DOCKER_DIR%\docker_config.local.yaml" (
  if not exist "%DOCKER_DIR%\docker_config.example.yaml" (
    echo Missing docker_config.example.yaml
    pause
    exit /b 1
  )
  copy /Y "%DOCKER_DIR%\docker_config.example.yaml" "%DOCKER_DIR%\docker_config.local.yaml" >nul
)

cd /d "%DOCKER_DIR%"
echo Starting PostgreSQL for Phase 0 backend recovery...
docker compose up -d postgres
if errorlevel 1 (
  echo Failed to start PostgreSQL.
  pause
  exit /b 1
)

echo Waiting for PostgreSQL to become healthy...
for /L %%I in (1,1,45) do (
  for /f "usebackq delims=" %%S in (`docker inspect -f "{{.State.Health.Status}}" zuno-postgres 2^>nul`) do (
    set "POSTGRES_STATUS=%%S"
  )
  if /I "!POSTGRES_STATUS!"=="healthy" goto :postgres_ready
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2"
)

echo PostgreSQL did not become healthy in time.
pause
exit /b 1

:postgres_ready
cd /d "%PROJECT_ROOT%"
echo.
echo Phase 0 backend recovery runtime starting...
echo Health URL: http://127.0.0.1:7860/health
echo Press Ctrl+C to stop uvicorn. Use Zuno-Phase0-Backend-Stop.cmd if needed.
echo.
python -m uvicorn --app-dir src/backend zuno.main:app --host 127.0.0.1 --port 7860
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo.
  echo Phase 0 backend exited with code %EXITCODE%.
  pause
)
exit /b %EXITCODE%
