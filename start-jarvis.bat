@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%scripts\start-jarvis.bat" %*
exit /b %errorlevel%
