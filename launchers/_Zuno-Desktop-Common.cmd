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
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "DOCKER_DIR=%PROJECT_ROOT%\docker"
set "FRONTEND_DIR=%PROJECT_ROOT%\src\frontend"
set "DESKTOP_DIR=%PROJECT_ROOT%\desktop"
set "RUNTIME_DIR=%TEMP%\zuno-desktop-runtime"
set "FRONTEND_LOG=%RUNTIME_DIR%\frontend.log"
set "FRONTEND_ERR_LOG=%RUNTIME_DIR%\frontend.err.log"
set "DESKTOP_LOG=%RUNTIME_DIR%\desktop.log"
set "DESKTOP_ERR_LOG=%RUNTIME_DIR%\desktop.err.log"
set "FRONTEND_PID_FILE=%RUNTIME_DIR%\frontend.pid"
set "DESKTOP_PID_FILE=%RUNTIME_DIR%\desktop.pid"
set "DESKTOP_FRONTEND_PORT=8091"
exit /b 0

:cleanup_logs
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
del /q "%FRONTEND_LOG%" "%FRONTEND_ERR_LOG%" "%DESKTOP_LOG%" "%DESKTOP_ERR_LOG%" >nul 2>nul
exit /b 0

:cleanup_processes
if exist "%DESKTOP_PID_FILE%" (
  set /p DESKTOP_PID=<"%DESKTOP_PID_FILE%"
  if not "!DESKTOP_PID!"=="" taskkill /PID !DESKTOP_PID! /T /F >nul 2>nul
  del /q "%DESKTOP_PID_FILE%" >nul 2>nul
)
if exist "%FRONTEND_PID_FILE%" (
  set /p FRONTEND_PID=<"%FRONTEND_PID_FILE%"
  if not "!FRONTEND_PID!"=="" taskkill /PID !FRONTEND_PID! /T /F >nul 2>nul
  del /q "%FRONTEND_PID_FILE%" >nul 2>nul
)
for %%P in (8091 8090) do (
  for /f "tokens=5" %%I in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
    taskkill /PID %%I /T /F >nul 2>nul
  )
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$targets = Get-CimInstance Win32_Process | Where-Object {" ^
  "  ($_.Name -match 'node|electron|cmd') -and (" ^
  "    ($_.CommandLine -like '*%PROJECT_ROOT%src\\frontend*') -or" ^
  "    ($_.CommandLine -like '*%PROJECT_ROOT%desktop*')" ^
  "  )" ^
  "};" ^
  "foreach ($proc in $targets) { try { Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop } catch {} }"
exit /b 0

:stop_backend
cd /d "%DOCKER_DIR%"
docker compose stop frontend backend mysql redis minio >nul 2>nul
exit /b 0

:wait_http
set "WAIT_URL=%~1"
set "WAIT_NAME=%~2"
set "WAIT_SECONDS=%~3"
if "%WAIT_SECONDS%"=="" set "WAIT_SECONDS=30"
for /L %%I in (1,1,%WAIT_SECONDS%) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { $r = Invoke-WebRequest -UseBasicParsing '%WAIT_URL%'; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 exit /b 0
  timeout /t 1 /nobreak >nul
)
echo %WAIT_NAME% did not become ready in time.
exit /b 1

:wait_container_healthy
set "WAIT_CONTAINER=%~1"
set "WAIT_NAME=%~2"
set "WAIT_SECONDS=%~3"
if "%WAIT_SECONDS%"=="" set "WAIT_SECONDS=90"
for /L %%I in (1,1,%WAIT_SECONDS%) do (
  set "CONTAINER_STATUS="
  for /f "usebackq delims=" %%S in (`powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { $status = docker inspect -f '{{.State.Health.Status}}' '%WAIT_CONTAINER%'; if ($LASTEXITCODE -ne 0 -or -not $status) { exit 2 }; Write-Output $status.Trim() } catch { exit 2 }"`) do (
    set "CONTAINER_STATUS=%%S"
  )
  if /I "!CONTAINER_STATUS!"=="healthy" exit /b 0
  if /I "!CONTAINER_STATUS!"=="unhealthy" (
    echo %WAIT_NAME% became unhealthy while waiting to start.
    exit /b 1
  )
  timeout /t 1 /nobreak >nul
)
echo %WAIT_NAME% did not become healthy in time.
exit /b 1

:ensure_deps
cd /d "%FRONTEND_DIR%"
if not exist node_modules (
  echo Installing frontend dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)
if not exist "%FRONTEND_DIR%\node_modules\.bin\vite.cmd" (
  echo Frontend dependencies look incomplete. Reinstalling frontend dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)

cd /d "%DESKTOP_DIR%"
if not exist node_modules (
  echo Installing desktop dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)
if not exist "%DESKTOP_DIR%\node_modules\.bin\electron.cmd" (
  echo Desktop dependencies look incomplete. Reinstalling desktop dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)
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
echo Please open Docker Desktop manually and wait until it shows Running.
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
exit /b 0

:start_backend
cd /d "%DOCKER_DIR%"
docker compose up -d mysql redis minio backend
if errorlevel 1 exit /b 1
call :wait_container_healthy "agentchat-backend" "Backend container" 120
if errorlevel 1 exit /b 1
call :wait_http "http://127.0.0.1:7860/health" "Backend API" 45
if errorlevel 1 exit /b 1
exit /b 0

:start_frontend
cd /d "%FRONTEND_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$env:VITE_API_BASE_URL='http://127.0.0.1:7860';" ^
  "$p = Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev','--','--host','127.0.0.1','--port','%DESKTOP_FRONTEND_PORT%','--strictPort' -WorkingDirectory '%FRONTEND_DIR%' -WindowStyle Hidden -RedirectStandardOutput '%FRONTEND_LOG%' -RedirectStandardError '%FRONTEND_ERR_LOG%' -PassThru;" ^
  "Set-Content -Path '%FRONTEND_PID_FILE%' -Value $p.Id"
if errorlevel 1 exit /b 1
call :wait_http "http://127.0.0.1:%DESKTOP_FRONTEND_PORT%" "Desktop frontend" 45
if errorlevel 1 exit /b 1
exit /b 0

:start_electron
cd /d "%DESKTOP_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$env:DESKTOP_FRONTEND_URL='http://127.0.0.1:%DESKTOP_FRONTEND_PORT%';" ^
  "$env:DESKTOP_API_BASE_URL='http://127.0.0.1:7860';" ^
  "$p = Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory '%DESKTOP_DIR%' -WindowStyle Hidden -RedirectStandardOutput '%DESKTOP_LOG%' -RedirectStandardError '%DESKTOP_ERR_LOG%' -PassThru;" ^
  "Set-Content -Path '%DESKTOP_PID_FILE%' -Value $p.Id"
if errorlevel 1 exit /b 1
exit /b 0

:start_sequence
echo [0/5] Cleaning old desktop background processes...
call :cleanup_processes
call :cleanup_logs

echo [1/5] Ensuring Docker backend services are available...
call :ensure_docker
if errorlevel 1 exit /b 1
call :ensure_local_config
if errorlevel 1 exit /b 1
cd /d "%DOCKER_DIR%"
docker compose stop frontend >nul 2>nul

echo [2/5] Starting desktop backend services...
call :start_backend
if errorlevel 1 exit /b 1

echo [3/5] Ensuring frontend and desktop dependencies...
call :ensure_deps
if errorlevel 1 exit /b 1

echo [4/5] Starting desktop frontend dev server on port %DESKTOP_FRONTEND_PORT%...
call :start_frontend
if errorlevel 1 exit /b 1

echo [5/5] Launching Electron client...
call :start_electron
if errorlevel 1 exit /b 1

echo.
echo Zuno Desktop started.
echo Backend:  http://127.0.0.1:7860
echo Frontend: http://127.0.0.1:%DESKTOP_FRONTEND_PORT%
echo Logs:
echo   %FRONTEND_LOG%
echo   %FRONTEND_ERR_LOG%
echo   %DESKTOP_LOG%
echo   %DESKTOP_ERR_LOG%
echo.
echo If the client does not appear, check desktop.err.log and frontend.err.log.
exit /b 0

:start
call :config
call :start_sequence
if errorlevel 1 (
  echo.
  echo Zuno Desktop start failed.
)
echo.
pause
exit /b 0

:stop
call :config
echo Stopping Zuno Desktop client and backend services...
call :cleanup_processes
call :stop_backend
echo.
echo Zuno Desktop stopped.
echo.
pause
exit /b 0

:rebuild
call :config
echo Rebuilding desktop backend image and restarting Zuno Desktop...
echo.
call :cleanup_processes
call :cleanup_logs
cd /d "%DOCKER_DIR%"
call :ensure_docker
if errorlevel 1 (
  echo Docker is not ready, cannot rebuild desktop backend.
  echo.
  pause
  exit /b 1
)
call :ensure_local_config
if errorlevel 1 (
  echo Missing desktop Docker config.
  echo.
  pause
  exit /b 1
)
docker compose stop frontend backend mysql redis minio >nul 2>nul
docker compose build backend
if errorlevel 1 (
  echo Desktop backend rebuild failed.
  echo.
  pause
  exit /b 1
)
call :start_sequence
if errorlevel 1 (
  echo.
  echo Zuno Desktop rebuild failed.
)
echo.
pause
exit /b 0

:full_rebuild
call :config
echo Running full rebuild for Zuno Desktop...
echo.
call :cleanup_processes
call :cleanup_logs
cd /d "%DOCKER_DIR%"
call :ensure_docker
if errorlevel 1 (
  echo Docker is not ready, cannot run full rebuild.
  echo.
  pause
  exit /b 1
)
call :ensure_local_config
if errorlevel 1 (
  echo Missing desktop Docker config.
  echo.
  pause
  exit /b 1
)
docker compose stop frontend backend mysql redis minio >nul 2>nul
echo Removing desktop dependency folders and Vite cache...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$paths = @('%PROJECT_ROOT%\\src\\frontend\\node_modules','%PROJECT_ROOT%\\desktop\\node_modules','%PROJECT_ROOT%\\src\\frontend\\dist','%PROJECT_ROOT%\\src\\frontend\\node_modules\\.vite');" ^
  "foreach ($path in $paths) { if (Test-Path $path) { Remove-Item -LiteralPath $path -Recurse -Force } }"
if errorlevel 1 (
  echo Failed to clean desktop dependency folders.
  echo.
  pause
  exit /b 1
)
docker compose build --no-cache backend
if errorlevel 1 (
  echo Desktop backend full rebuild failed.
  echo.
  pause
  exit /b 1
)
call :start_sequence
if errorlevel 1 (
  echo.
  echo Zuno Desktop full rebuild failed.
)
echo.
pause
exit /b 0
