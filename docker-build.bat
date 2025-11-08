@echo off
echo ========================================
echo Building Wiki Quiz Generator Docker Image
echo ========================================
echo.

cd backend

echo [1/3] Building Docker image...
docker build -t wiki-quiz-generator .

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Docker image built successfully!
echo.
echo [3/3] To run the container, use one of these commands:
echo.
echo   Option 1: Run with .env file
echo   docker run -p 8000:8000 --env-file .env wiki-quiz-generator
echo.
echo   Option 2: Run with environment variable
echo   docker run -p 8000:8000 -e GOOGLE_API_KEY=your-key wiki-quiz-generator
echo.
echo   Option 3: Use docker-compose
echo   docker-compose up -d
echo.
echo ========================================
echo Docker image ready!
echo ========================================
pause
