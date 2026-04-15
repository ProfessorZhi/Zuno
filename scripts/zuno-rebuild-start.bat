@echo off
setlocal
chcp 65001 >nul
title Zuno Rebuild

set "DESKTOP_BAT=C:\Users\Administrator\Desktop\bat\Zuno-Rebuild.cmd"
echo This script now forwards to the desktop-mode rebuild to avoid stale web frontend conflicts.
echo.
if exist "%DESKTOP_BAT%" (
  call "%DESKTOP_BAT%"
  exit /b %ERRORLEVEL%
)
echo [ERROR] Missing desktop launcher:
echo %DESKTOP_BAT%
pause
exit /b 1
