@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul 2>nul

set "ACTION=%~1"
if /I "%ACTION%"=="start" goto :launcher_start
if /I "%ACTION%"=="stop" goto :launcher_stop
if /I "%ACTION%"=="rebuild" goto :launcher_rebuild
if /I "%ACTION%"=="full-rebuild" goto :launcher_full_rebuild

echo Unsupported action: %ACTION%
exit /b 1

:config
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "DOCKER_DIR=%PROJECT_ROOT%\infra\docker"
set "FRONTEND_DIR=%PROJECT_ROOT%\src\frontend"
set "DESKTOP_DIR=%PROJECT_ROOT%\apps\desktop"
set "DESKTOP_ELECTRON_EXE=%DESKTOP_DIR%\node_modules\electron\dist\electron.exe"
set "LAUNCHER_DIR=%PROJECT_ROOT%\launchers"
set "RUNTIME_DIR=%TEMP%\zuno-desktop-runtime"
set "FRONTEND_LOG=%RUNTIME_DIR%\frontend.log"
set "FRONTEND_ERR_LOG=%RUNTIME_DIR%\frontend.err.log"
set "DESKTOP_LOG=%RUNTIME_DIR%\desktop.log"
set "DESKTOP_ERR_LOG=%RUNTIME_DIR%\desktop.err.log"
set "FRONTEND_PID_FILE=%RUNTIME_DIR%\frontend.pid"
set "DESKTOP_PID_FILE=%RUNTIME_DIR%\desktop.pid"
set "START_ELECTRON_HELPER=%LAUNCHER_DIR%\_Zuno-Desktop-StartElectron.ps1"
set "CLEANUP_HELPER=%LAUNCHER_DIR%\_Zuno-Desktop-Cleanup.ps1"
set "DESKTOP_FRONTEND_PORT=8091"
exit /b 0

:cleanup_logs
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
del /q "%FRONTEND_LOG%" "%FRONTEND_ERR_LOG%" "%DESKTOP_LOG%" "%DESKTOP_ERR_LOG%" >nul 2>nul
exit /b 0

:cleanup_processes
if not exist "%CLEANUP_HELPER%" (
  echo Missing cleanup helper:
  echo %CLEANUP_HELPER%
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%CLEANUP_HELPER%" ^
  -ProjectRoot "%PROJECT_ROOT%" ^
  -FrontendRoot "%FRONTEND_DIR%" ^
  -DesktopRoot "%DESKTOP_DIR%" ^
  -FrontendPidFile "%FRONTEND_PID_FILE%" ^
  -DesktopPidFile "%DESKTOP_PID_FILE%"
exit /b 0

:stopBackend
cd /d "%DOCKER_DIR%"
docker compose down --remove-orphans >nul 2>nul
exit /b 0

:waitHttp
set "WAIT_URL=%~1"
set "WAIT_NAME=%~2"
set "WAIT_SECONDS=%~3"
if "%WAIT_SECONDS%"=="" set "WAIT_SECONDS=30"
for /L %%I in (1,1,%WAIT_SECONDS%) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { $r = Invoke-WebRequest -UseBasicParsing '%WAIT_URL%'; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 exit /b 0
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 1"
)
echo %WAIT_NAME% did not become ready in time.
exit /b 1

:recordListeningPid
set "LISTEN_PORT=%~1"
set "LISTEN_PID_FILE=%~2"
set "LISTEN_PID="
for /L %%I in (1,1,10) do (
  set "LISTEN_PID="
  for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$listener = Get-NetTCPConnection -LocalPort %LISTEN_PORT% -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($listener) { Write-Output $listener }"`) do (
    set "LISTEN_PID=%%P"
  )
  if not "!LISTEN_PID!"=="" (
    >"%LISTEN_PID_FILE%" echo !LISTEN_PID!
    exit /b 0
  )
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 1"
)
echo Could not determine the listening process for port %LISTEN_PORT%.
exit /b 1

:waitContainerHealthy
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
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 1"
)
echo %WAIT_NAME% did not become healthy in time.
exit /b 1

:ensureDeps
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

:ensureDocker
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
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2"
)

echo Docker Desktop did not become ready in time.
echo Please open Docker Desktop manually and wait until it shows Running.
exit /b 1

:ensureLocalConfig
cd /d "%DOCKER_DIR%"
if exist "docker_config.local.yaml" exit /b 0
if not exist "docker_config.example.yaml" (
  echo Missing docker_config.example.yaml
  exit /b 1
)
copy /Y "docker_config.example.yaml" "docker_config.local.yaml" >nul
exit /b 0

:startBackend
cd /d "%DOCKER_DIR%"
docker compose up -d --remove-orphans postgres redis neo4j minio backend
if errorlevel 1 exit /b 1
call :waitHttp "http://127.0.0.1:7860/health" "Backend API" 90
if errorlevel 1 exit /b 1
exit /b 0

:startFrontend
cd /d "%FRONTEND_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$env:VITE_API_BASE_URL='http://127.0.0.1:7860';" ^
  "$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','\"%FRONTEND_DIR%\node_modules\.bin\vite.cmd\" --host 127.0.0.1 --port %DESKTOP_FRONTEND_PORT% --strictPort' -WorkingDirectory '%FRONTEND_DIR%' -WindowStyle Hidden -RedirectStandardOutput '%FRONTEND_LOG%' -RedirectStandardError '%FRONTEND_ERR_LOG%' -PassThru;" ^
  "Set-Content -Path '%FRONTEND_PID_FILE%' -Value $p.Id"
if errorlevel 1 exit /b 1
call :waitHttp "http://127.0.0.1:%DESKTOP_FRONTEND_PORT%" "Desktop frontend" 45
if errorlevel 1 exit /b 1
call :recordListeningPid "%DESKTOP_FRONTEND_PORT%" "%FRONTEND_PID_FILE%"
if errorlevel 1 exit /b 1
exit /b 0

:startSequence
echo [0/5] Cleaning old desktop background processes...
call :cleanup_processes
call :cleanup_logs

echo [1/5] Ensuring Docker backend services are available...
call :ensureDocker
if errorlevel 1 exit /b 1
call :ensureLocalConfig
if errorlevel 1 exit /b 1

echo [2/5] Starting desktop backend services...
call :startBackend
if errorlevel 1 exit /b 1

echo [3/5] Ensuring frontend and desktop dependencies...
call :ensureDeps
if errorlevel 1 exit /b 1

echo [4/5] Starting desktop frontend dev server on port %DESKTOP_FRONTEND_PORT%...
call :startFrontend
if errorlevel 1 exit /b 1

echo [5/5] Launching Electron client...
if not exist "%START_ELECTRON_HELPER%" (
  echo Missing Electron launcher helper:
  echo %START_ELECTRON_HELPER%
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%START_ELECTRON_HELPER%" ^
  -DesktopDir "%DESKTOP_DIR%" ^
  -DesktopFrontendPort "%DESKTOP_FRONTEND_PORT%" ^
  -DesktopLog "%DESKTOP_LOG%" ^
  -DesktopErrLog "%DESKTOP_ERR_LOG%" ^
  -DesktopPidFile "%DESKTOP_PID_FILE%"
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

:launcher_start
call :config
call :startSequence
if errorlevel 1 (
  echo.
  echo Zuno Desktop start failed.
  echo.
  pause
  exit /b 1
)
exit /b 0

:launcher_stop
call :config
echo Stopping Zuno Desktop client and backend services...
call :cleanup_processes
if errorlevel 1 (
  echo.
  echo Zuno Desktop stop failed.
  echo.
  pause
  exit /b 1
)
call :stopBackend
if errorlevel 1 (
  echo.
  echo Zuno Desktop stop failed.
  echo.
  pause
  exit /b 1
)
echo.
echo Zuno Desktop stopped.
exit /b 0

:launcher_rebuild
call :config
echo Rebuilding desktop backend image and restarting Zuno Desktop...
echo.
call :cleanup_processes
call :cleanup_logs
cd /d "%DOCKER_DIR%"
call :ensureDocker
if errorlevel 1 (
  echo Docker is not ready, cannot rebuild desktop backend.
  echo.
  pause
  exit /b 1
)
call :ensureLocalConfig
if errorlevel 1 (
  echo Missing desktop Docker config.
  echo.
  pause
  exit /b 1
)
docker compose down --remove-orphans >nul 2>nul
docker compose build backend
if errorlevel 1 (
  echo Desktop backend rebuild failed.
  echo.
  pause
  exit /b 1
)
call :startSequence
if errorlevel 1 (
  echo.
  echo Zuno Desktop rebuild failed.
  echo.
  pause
  exit /b 1
)
exit /b 0

:launcher_full_rebuild
call :config
echo Running full rebuild for Zuno Desktop...
echo.
call :cleanup_processes
call :cleanup_logs
cd /d "%DOCKER_DIR%"
call :ensureDocker
if errorlevel 1 (
  echo Docker is not ready, cannot run full rebuild.
  echo.
  pause
  exit /b 1
)
call :ensureLocalConfig
if errorlevel 1 (
  echo Missing desktop Docker config.
  echo.
  pause
  exit /b 1
)
docker compose down --remove-orphans >nul 2>nul
echo Removing desktop dependency folders and Vite cache...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$paths = @('%PROJECT_ROOT%\\src\\frontend\\node_modules','%PROJECT_ROOT%\\apps\\desktop\\node_modules','%PROJECT_ROOT%\\src\\frontend\\dist','%PROJECT_ROOT%\\src\\frontend\\node_modules\\.vite');" ^
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
call :startSequence
if errorlevel 1 (
  echo.
  echo Zuno Desktop full rebuild failed.
  echo.
  pause
  exit /b 1
)
exit /b 0
