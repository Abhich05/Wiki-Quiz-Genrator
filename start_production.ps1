# Wiki Quiz Generator - Production Startup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Wiki Quiz Generator - Starting Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow
python --version
Write-Host ""

Write-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements_prod.txt
Write-Host ""

Write-Host "[3/3] Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server starting on http://localhost:8000" -ForegroundColor Green
Write-Host "Open frontend/app.html in your browser" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python main.py
