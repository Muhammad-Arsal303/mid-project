@echo off
title Klondike Solitaire - Console CLI
cd /d "%~dp0"

if exist "%~dp0.python\python.exe" (
    "%~dp0.python\python.exe" main.py --cli
) else if exist "%~dp0..\Uni prjects\.python\python.exe" (
    "%~dp0..\Uni prjects\.python\python.exe" main.py --cli
) else if exist "%~dp0..\.python\python.exe" (
    "%~dp0..\.python\python.exe" main.py --cli
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        py main.py --cli
    ) else (
        where python >nul 2>nul
        if %errorlevel% equ 0 (
            python main.py --cli
        ) else (
            echo Python executable was not found. Please install Python or ensure .python directory is present.
        )
    )
)
pause
