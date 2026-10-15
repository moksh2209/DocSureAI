@echo off
setlocal

cd /d "F:\project\DocSureAI"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at venv\Scripts\python.exe.
    echo Please ensure the python virtual environment is configured correctly.
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [ERROR] frontend\package.json not found.
    echo Please ensure the frontend files are configured correctly.
    pause
    exit /b 1
)

echo Starting FastAPI Backend in a new window...
start "DocSureAI Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn src.api:app --host 127.0.0.1 --port 8000"

echo Starting Vite Frontend in a new window...
start "DocSureAI Frontend" cmd /k "cd frontend && set VITE_API_BASE_URL=http://127.0.0.1:8000&& npm run dev"

echo Waiting for frontend server to start...
timeout /t 8 /nobreak >nul

echo Opening DocSureAI in your default browser...
start http://localhost:5173

echo.
echo ============================================================
echo DocSureAI is now running!
echo.
echo IMPORTANT: The Backend and Frontend command windows must 
echo remain open while using the application.
echo ============================================================
echo.
pause
