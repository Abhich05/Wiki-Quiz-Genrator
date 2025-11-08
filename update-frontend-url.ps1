# Update Frontend API URL for Render Deployment

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Update Frontend for Render Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendUrl = Read-Host "Enter your Render backend URL (e.g., https://wiki-quiz-api.onrender.com)"

if ([string]::IsNullOrWhiteSpace($backendUrl)) {
    Write-Host "Error: Backend URL cannot be empty!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Updating frontend/app.html with backend URL: $backendUrl" -ForegroundColor Yellow
Write-Host ""

# Create backup
Copy-Item "frontend\app.html" "frontend\app.html.backup" -Force

# Update the API URL
$content = Get-Content "frontend\app.html" -Raw
$updatedContent = $content -replace "const API_URL = '.*';", "const API_URL = '$backendUrl';"
Set-Content "frontend\app.html" -Value $updatedContent

Write-Host "✓ Frontend updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Backup saved to: frontend\app.html.backup" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review changes in frontend/app.html" -ForegroundColor White
Write-Host "2. Commit and push:" -ForegroundColor White
Write-Host "   git add frontend/app.html" -ForegroundColor Cyan
Write-Host "   git commit -m 'Update API URL for Render'" -ForegroundColor Cyan
Write-Host "   git push origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Render will automatically redeploy your frontend!" -ForegroundColor Green
Write-Host ""
pause
