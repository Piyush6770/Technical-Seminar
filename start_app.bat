@echo off
title Scholarly Integrity Audit System - Launcher
echo ======================================================================
echo Starting Scholarly Integrity Audit System (Backend + Frontend)
echo ======================================================================

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FastAPI Backend Server" cmd /k "python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Vite Frontend on http://localhost:5173 ...
cd frontend
start "Vite Dev Server" cmd /k "npm run dev"

echo ======================================================================
echo Both servers started!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo ======================================================================
