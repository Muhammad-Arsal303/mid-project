@echo off
title Klondike Solitaire - Tekken 8 Edition (GUI)
cd /d "%~dp0"

if exist "%~dp0.python\python.exe" (
    "%~dp0.python\python.exe" main.py --gui
) else if exist "%~dp0..\Uni prjects\.python\python.exe" (
    "%~dp0..\Uni prjects\.python\python.exe" main.py --gui
) else if exist "%~dp0..\.python\python.exe" (
    "%~dp0..\.python\python.exe" main.py --gui
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        py main.py --gui
    ) else (
        where python >nul 2>nul
        if %errorlevel% equ 0 (
            python main.py --gui
        ) else (
            echo [!] Python executable was not detected. Opening Browser Game directly...
            start "" "%~dp0web\index.html"
        )
    )
)
pause
