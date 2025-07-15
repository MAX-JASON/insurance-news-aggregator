# Taiwan Insurance News Crawler Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Taiwan Insurance News Crawler                  " -ForegroundColor Cyan  
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting crawler system, please wait..." -ForegroundColor Yellow
Write-Host ""

# Check Python virtual environment
$PythonPath = "D:\insurance-news-aggregator\venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    Write-Host "[Error] Cannot find virtual environment Python!" -ForegroundColor Red
    Write-Host "[Path] $PythonPath" -ForegroundColor Red
    Write-Host "Please ensure the virtual environment is properly installed." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Change to correct directory
Set-Location "D:\insurance-news-aggregator"

# Display crawler startup information
Write-Host "[Starting] Insurance news crawler..." -ForegroundColor Green
Write-Host "[Python Path] $PythonPath" -ForegroundColor Green
Write-Host ""
Write-Host "Crawler will run in background and save news to database" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please wait patiently for crawler to complete..." -ForegroundColor Yellow
Write-Host ""

# Execute crawler command
Write-Host "[Executing] Starting crawler program..." -ForegroundColor Magenta

$command = "import sys; sys.path.append('.'); from crawler.manager import get_crawler_manager; manager = get_crawler_manager(); result = manager.crawl_all_sources(use_mock=True); print('Crawler execution result:', result.get('message', 'completed')); print('Total news collected:', result.get('total', 0))"

try {
    & $PythonPath -c $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[Success] Crawler has completed its work!" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now view the collected news" -ForegroundColor Green
        Write-Host ""
        $choice = Read-Host "Launch system to view news immediately? (Y/N)"
        if ($choice -eq "Y" -or $choice -eq "y") {
            Write-Host "Starting main system..." -ForegroundColor Green
            Start-Process -FilePath "D:\insurance-news-aggregator\啟動系統.bat"
            exit 0
        }
    } else {
        Write-Host ""
        Write-Host "[Error] Crawler execution failed" -ForegroundColor Red
        Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "[Error] Exception occurred during execution" -ForegroundColor Red
    Write-Host "Error message: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
