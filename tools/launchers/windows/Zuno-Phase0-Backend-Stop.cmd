@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..") do set "PROJECT_ROOT=%%~fI"
set "DOCKER_DIR=%PROJECT_ROOT%\infra\docker"

for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -Command "$listener = Get-NetTCPConnection -LocalPort 7860 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($listener) { Write-Output $listener }"`) do (
  set "BACKEND_PID=%%P"
)

if not "%BACKEND_PID%"=="" (
  taskkill /PID %BACKEND_PID% /T /F >nul 2>nul
)

docker info >nul 2>nul
if errorlevel 1 (
  echo Docker Desktop is not running. Backend process cleanup is complete.
  exit /b 0
)

cd /d "%DOCKER_DIR%"
docker compose stop postgres >nul 2>nul
echo Phase 0 backend runtime stopped.
exit /b 0
