# Docker Build Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Wiki Quiz Generator Docker Image" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

Write-Host "[1/3] Building Docker image..." -ForegroundColor Yellow
docker build -t wiki-quiz-generator .

if ($LASTEXITCODE -ne 0) {
    Write-Host "" -ForegroundColor Red
    Write-Host "ERROR: Docker build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/3] Docker image built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "[3/3] To run the container, use one of these commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option 1: Run with .env file" -ForegroundColor Cyan
Write-Host "  docker run -p 8000:8000 --env-file .env wiki-quiz-generator" -ForegroundColor White
Write-Host ""
Write-Host "  Option 2: Run with environment variable" -ForegroundColor Cyan
Write-Host "  docker run -p 8000:8000 -e GOOGLE_API_KEY=your-key wiki-quiz-generator" -ForegroundColor White
Write-Host ""
Write-Host "  Option 3: Use docker-compose (from root)" -ForegroundColor Cyan
Write-Host "  docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Docker image ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
