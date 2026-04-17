@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ACTION=%~1"
if /I "%ACTION%"=="start" goto :start
if /I "%ACTION%"=="stop" goto :stop
if /I "%ACTION%"=="rebuild" goto :rebuild
if /I "%ACTION%"=="full-rebuild" goto :full_rebuild

echo Unsupported action: %ACTION%
exit /b 1

:config
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "DOCKER_DIR=%PROJECT_ROOT%\docker"
exit /b 0

:ensure_docker
docker info >nul 2>nul
if not errorlevel 1 exit /b 0

echo Docker Desktop is not running. Trying to start it...
if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
) else if exist "C:\Program Files\Docker\Docker\resources\Docker Desktop.exe" (
  start "" "C:\Program Files\Docker\Docker\resources\Docker Desktop.exe"
) else (
  echo Docker Desktop is not installed in the default path.
  exit /b 1
)

for /L %%I in (1,1,90) do (
  docker info >nul 2>nul
  if not errorlevel 1 exit /b 0
  timeout /t 2 /nobreak >nul
)

echo Docker Desktop did not become ready in time.
exit /b 1

:ensure_local_config
cd /d "%DOCKER_DIR%"
if not exist "mysql\init" mkdir "mysql\init"
if exist "docker_config.local.yaml" exit /b 0
if not exist "docker_config.example.yaml" (
  echo Missing docker_config.example.yaml
  exit /b 1
)
copy /Y "docker_config.example.yaml" "docker_config.local.yaml" >nul
echo Created docker\docker_config.local.yaml from template.
echo Please review it before using the Docker stack.
exit /b 0

:start
call :config
call :ensure_docker
if errorlevel 1 goto :fail
call :ensure_local_config
if errorlevel 1 goto :fail
cd /d "%DOCKER_DIR%"
echo Starting Zuno Web stack...
docker compose up -d
if errorlevel 1 goto :fail
echo.
echo Zuno Web stack started.
echo Frontend: http://127.0.0.1:8090
echo Backend:  http://127.0.0.1:7860
echo Docs:     http://127.0.0.1:7860/docs
goto :done

:stop
call :config
call :ensure_docker
if errorlevel 1 goto :fail
cd /d "%DOCKER_DIR%"
echo Stopping Zuno Web stack...
docker compose down
if errorlevel 1 goto :fail
echo.
echo Zuno Web stack stopped.
goto :done

:rebuild
call :config
call :ensure_docker
if errorlevel 1 goto :fail
call :ensure_local_config
if errorlevel 1 goto :fail
cd /d "%DOCKER_DIR%"
echo Rebuilding and restarting Zuno Web stack...
docker compose up --build -d
if errorlevel 1 goto :fail
echo.
echo Zuno Web stack rebuilt.
goto :done

:full_rebuild
call :config
call :ensure_docker
if errorlevel 1 goto :fail
call :ensure_local_config
if errorlevel 1 goto :fail
cd /d "%DOCKER_DIR%"
echo Running full rebuild for Zuno Web stack...
docker compose down
docker compose build --no-cache
if errorlevel 1 goto :fail
docker compose up -d
if errorlevel 1 goto :fail
echo.
echo Zuno Web stack fully rebuilt.
goto :done

:fail
echo.
echo Zuno Web action failed.

:done
echo.
pause
exit /b 0
