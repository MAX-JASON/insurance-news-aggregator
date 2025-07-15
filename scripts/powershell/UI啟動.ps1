# 台灣保險新聞聚合器 PowerShell 啟動腳本
# Taiwan Insurance News Aggregator PowerShell Startup Script

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Taiwan Insurance News Aggregator Startup" -ForegroundColor Green
Write-Host "   台灣保險新聞聚合器啟動程序" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# 設定編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Starting system, please wait..." -ForegroundColor Yellow
Write-Host "正在啟動系統，請稍候..." -ForegroundColor Yellow
Write-Host ""

# 檢查虛擬環境Python
$PYTHON_PATH = "D:\insurance-news-aggregator\venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "[Error] Cannot find virtual environment Python!" -ForegroundColor Red
    Write-Host "[錯誤] 無法找到虛擬環境Python！" -ForegroundColor Red
    Write-Host "Path: $PYTHON_PATH" -ForegroundColor Red
    Write-Host "路徑：$PYTHON_PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure virtual environment is properly installed." -ForegroundColor Yellow
    Write-Host "請確保虛擬環境已正確安裝。" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit / 按Enter鍵退出"
    exit 1
}

# 切換到正確目錄
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 啟動應用
Write-Host "[Starting] Insurance News Aggregator..." -ForegroundColor Green
Write-Host "[執行] 正在啟動保險新聞聚合器..." -ForegroundColor Green
Write-Host "[Path] Python: $PYTHON_PATH" -ForegroundColor Cyan
Write-Host "[路徑] 使用Python：$PYTHON_PATH" -ForegroundColor Cyan
Write-Host ""
Write-Host "After startup, visit these URLs:" -ForegroundColor Yellow
Write-Host "啟動後請訪問以下網址：" -ForegroundColor Yellow
Write-Host "  • Home Page / 首頁:         http://127.0.0.1:5000/" -ForegroundColor White
Write-Host "  • Business Area / 業務員區:  http://127.0.0.1:5000/business/" -ForegroundColor White
Write-Host "  • Analysis / 智能分析:      http://127.0.0.1:5000/analysis" -ForegroundColor White
Write-Host "  • Feedback / 反饋頁面:      http://127.0.0.1:5000/feedback" -ForegroundColor White
Write-Host "  • Monitor / 系統監控:       http://127.0.0.1:5000/monitor" -ForegroundColor White
Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host "正在啟動Flask應用程序..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop / 按Ctrl+C停止服務" -ForegroundColor Yellow
Write-Host ""

try {
    & $PYTHON_PATH "apps\start_app.py"
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "[Error] Application startup failed, error code: $exitCode" -ForegroundColor Red
        Write-Host "[錯誤] 應用啟動失敗，錯誤代碼：$exitCode" -ForegroundColor Red
        Write-Host "Please check log files in logs directory for more information." -ForegroundColor Yellow
        Write-Host "請檢查logs目錄下的日誌文件以獲取更多信息。" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "[Info] Application closed normally." -ForegroundColor Green
        Write-Host "[信息] 應用已正常關閉。" -ForegroundColor Green
    }
} catch {
    Write-Host ""
    Write-Host "[Error] Exception occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[錯誤] 發生異常：$($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Read-Host "Press Enter to exit / 按Enter鍵退出"
exit $exitCode
