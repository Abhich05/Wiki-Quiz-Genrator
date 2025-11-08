@echo off
REM Update Frontend API URL for Render Deployment

echo.
echo ========================================
echo   Update Frontend for Render Deployment
echo ========================================
echo.

set /p BACKEND_URL="Enter your Render backend URL (e.g., https://wiki-quiz-api.onrender.com): "

if "%BACKEND_URL%"=="" (
    echo Error: Backend URL cannot be empty!
    pause
    exit /b 1
)

echo.
echo Updating frontend/app.html with backend URL: %BACKEND_URL%
echo.

REM Create backup
copy frontend\app.html frontend\app.html.backup >nul

REM Update the API URL using PowerShell
powershell -Command "(Get-Content frontend\app.html) -replace 'const API_URL = ''.*'';', 'const API_URL = ''%BACKEND_URL%'';' | Set-Content frontend\app.html"

echo ✓ Frontend updated successfully!
echo.
echo Backup saved to: frontend\app.html.backup
echo.
echo Next steps:
echo 1. Review changes in frontend/app.html
echo 2. Commit and push:
echo    git add frontend/app.html
echo    git commit -m "Update API URL for Render"
echo    git push origin main
echo.
echo Render will automatically redeploy your frontend!
echo.
pause
