@echo off
title Octavia Ocashy Tools

netstat -o -n -a | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo FastAPI is already running on port 8000.
) else (
    echo Starting FastAPI backend...
    cd /d "%~dp0ocashy\backend\api"
    start uvicorn main:app --reload
)

echo Starting Neutralino app...
cd /d "%~dp0ocashy\neu"
npm run run