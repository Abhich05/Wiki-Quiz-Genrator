@echo off
echo ========================================
echo Starting Wiki Quiz Generator with Docker
echo ========================================
echo.

echo [1/2] Starting containers...
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Docker Compose failed to start!
    pause
    exit /b 1
)

echo.
echo [2/2] Containers started successfully!
echo.
echo ========================================
echo Application Running!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop:
echo   docker-compose down
echo.
pause
