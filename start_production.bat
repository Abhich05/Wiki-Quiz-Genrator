@echo off
echo ========================================
echo Wiki Quiz Generator - Starting Server
echo ========================================
echo.

cd backend

echo [1/3] Checking Python...
python --version
echo.

echo [2/3] Installing dependencies...
pip install -r requirements_prod.txt
echo.

echo [3/3] Starting server...
echo.
echo Server will start on http://localhost:8000
echo Open frontend/app.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py

pause
