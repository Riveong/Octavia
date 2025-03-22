@echo off
title Octavia Ocashy Tools

cd /d C:\Users\i5\Desktop\Octavia\ocashy\backend\api
start uvicorn main:app --reload

cd /d C:\Users\i5\Desktop\Octavia\ocashy\svelte-app
start npm run dev

timeout /t 10 /nobreak >nul
start msedge http://localhost:8080