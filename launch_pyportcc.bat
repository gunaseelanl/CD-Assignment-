@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
pushd "%ROOT%" >nul

if "%~1"=="" (
    call :run_compiler --ide
) else (
    call :run_compiler %*
)
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
    echo.
    echo Launcher failed with exit code %RC%.
    pause
)

popd >nul
exit /b %RC%

:run_compiler
python -m pyportcc %*
if not errorlevel 1 exit /b 0
py -3 -m pyportcc %*
exit /b %ERRORLEVEL%
