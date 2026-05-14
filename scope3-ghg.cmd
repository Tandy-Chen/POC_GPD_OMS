@echo off
setlocal

:: ============================================================
::  Scope 3 GHG ?????
::  ?????
::    ????   -> ???? inputs/ ?????
::    ????? -> scope3-ghg.cmd [validate|process] [??]
:: ============================================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%scope3_ghg"
set "PYTHON_EXE="

:: ---- ?? Python ----
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%..\.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

if "%~1"=="" (
    echo.
    echo  ================================================
    echo   Scope 3 GHG ?????
    echo  ================================================
    echo   Python : %PYTHON_EXE%
    echo   ????: %PROJECT_DIR%
    echo   inputs  : %PROJECT_DIR%\inputs
    echo   outputs : %PROJECT_DIR%\outputs
    echo  ------------------------------------------------
    echo   ???? process ...
    echo.
)

pushd "%PROJECT_DIR%"
set "PYTHONPATH=%PROJECT_DIR%\src"
if "%~1"=="" (
    "%PYTHON_EXE%" -m scope3_ghg.cli process
) else (
    "%PYTHON_EXE%" -m scope3_ghg.cli %*
)
set "EXIT_CODE=%ERRORLEVEL%"
popd

if "%~1"=="" (
    echo.
    if "%EXIT_CODE%"=="0" (
        echo  [??] ?????? scope3_ghg\outputs\
    ) else (
        echo  [??] ???????? inputs\ ?????????????
        echo         ????????? .xlsx ???????????????
    )
    echo.
    pause
)

exit /b %EXIT_CODE%
