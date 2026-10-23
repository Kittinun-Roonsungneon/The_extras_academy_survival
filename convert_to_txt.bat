@echo off
chcp 65001 >nul
title The Extra''s Academy Survival Guide - Markdown to TXT Converter

echo ========================================================
echo   The Extra's Academy Survival Guide - Convert MD to TXT
echo ========================================================
echo.

set PYTHON_CMD=

:: 1. ลองคำสั่ง python
where python >nul 2>nul
if %errorlevel% equ 0 (
    python -c "import sys" >nul 2>nul
    if %errorlevel% equ 0 set PYTHON_CMD=python
)

:: 2. ลองคำสั่ง py launcher
if "%PYTHON_CMD%"=="" (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        py -c "import sys" >nul 2>nul
        if %errorlevel% equ 0 set PYTHON_CMD=py
    )
)

:: 3. ลองตรวจหา Python ใน Local AppData
if "%PYTHON_CMD%"=="" (
    if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Python\bin\python.exe"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] ไม่พบการติดตั้ง Python ในระบบ!
    echo กรุณาติดตั้ง Python จาก https://www.python.org/
    pause
    exit /b 1
)

echo [OK] ใช้ Python: %PYTHON_CMD%
echo.

%PYTHON_CMD% convert_to_txt.py %*
echo.
pause