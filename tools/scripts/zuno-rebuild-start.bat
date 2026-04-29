@echo off
setlocal
chcp 65001 >nul
title Zuno Rebuild

for %%I in ("%~dp0..\..") do set "REPO_ROOT=%%~fI"
set "DESKTOP_BAT=%REPO_ROOT%\launchers\Zuno-Desktop-Rebuild.cmd"
echo This script now forwards to the current desktop-mode rebuild launcher.
echo.
if exist "%DESKTOP_BAT%" (
  call "%DESKTOP_BAT%"
  exit /b %ERRORLEVEL%
)
echo [ERROR] Missing desktop launcher:
echo %DESKTOP_BAT%
pause
exit /b 1
