@echo off
setlocal
chcp 65001 >nul
title Zuno Stop

for %%I in ("%~dp0..\..") do set "REPO_ROOT=%%~fI"
set "DESKTOP_BAT=%REPO_ROOT%\launchers\Zuno-Desktop-Stop.cmd"
echo This script now forwards to the current desktop-mode launcher.
echo.
if exist "%DESKTOP_BAT%" (
  call "%DESKTOP_BAT%"
  exit /b %ERRORLEVEL%
)
echo [ERROR] Missing desktop launcher:
echo %DESKTOP_BAT%
pause
exit /b 1
