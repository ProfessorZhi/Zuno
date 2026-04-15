@echo off
setlocal

echo Starting Zuno Docker services...

REM Create directories
echo Creating directories...
if not exist "mysql\init" mkdir mysql\init
if not exist "docker_config.local.yaml" (
  echo Creating local Docker config from template...
  copy /Y "docker_config.example.yaml" "docker_config.local.yaml" >nul
  echo Please edit docker_config.local.yaml before running Docker again.
  pause
  exit /b 1
)

REM Start services
echo Building and starting services...
docker compose up --build -d

REM Wait for startup
echo Waiting for services to start...
timeout /t 10 >nul

REM Show status
echo Checking service status...
docker compose ps

echo.
echo Zuno started successfully!
echo.
echo Access URLs:
echo Frontend: http://localhost:8090
echo Backend API: http://localhost:7860
echo API Docs: http://localhost:7860/docs
echo.
echo View logs:
echo docker compose logs -f
echo.
echo Stop services:
echo docker compose down
echo.

pause
