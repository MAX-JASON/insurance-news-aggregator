# 台灣保險新聞爬蟲啟動程序 (PowerShell版本)
# 設定控制台編碼為UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "台灣保險新聞爬蟲啟動程序"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   台灣保險新聞爬蟲啟動程序                     " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "正在啟動爬蟲系統，請稍候..." -ForegroundColor Yellow
Write-Host ""

# 檢查虛擬環境Python
$PythonPath = "D:\insurance-news-aggregator\venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    Write-Host "[錯誤] 無法找到虛擬環境Python！" -ForegroundColor Red
    Write-Host "[路徑] $PythonPath" -ForegroundColor Red
    Write-Host "請確保虛擬環境已正確安裝。" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 鍵退出"
    exit 1
}

# 切換到正確目錄
Set-Location "D:\insurance-news-aggregator"

# 顯示爬蟲啟動信息
Write-Host "[啟動] 保險新聞爬蟲..." -ForegroundColor Green
Write-Host "[Python路徑] $PythonPath" -ForegroundColor Green
Write-Host ""
Write-Host "爬蟲將在後台運行，爬取的新聞將存入資料庫" -ForegroundColor Yellow
Write-Host ""
Write-Host "請耐心等待爬蟲完成工作..." -ForegroundColor Yellow
Write-Host ""

# 執行爬蟲命令
Write-Host "[執行] 正在啟動爬蟲程序..." -ForegroundColor Magenta

try {
    $result = & $PythonPath -c "import sys; sys.path.append('.'); from crawler.manager import get_crawler_manager; manager = get_crawler_manager(); result = manager.crawl_all_sources(use_mock=True); print('爬蟲執行結果:', result.get('message', '完成')); print('總共抓取新聞數量:', result.get('total', 0))" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[成功] 爬蟲已完成工作！" -ForegroundColor Green
        Write-Host ""
        Write-Host "您現在可以查看爬取的新聞" -ForegroundColor Green
        Write-Host ""
        $choice = Read-Host "是否立即啟動系統查看新聞？(Y/N)"
        if ($choice -eq "Y" -or $choice -eq "y") {
            Write-Host "正在啟動主系統..." -ForegroundColor Green
            Start-Process -FilePath "D:\insurance-news-aggregator\啟動系統.bat"
            exit 0
        }
    } else {
        Write-Host ""
        Write-Host "[錯誤] 爬蟲執行失敗" -ForegroundColor Red
        Write-Host "錯誤代碼：$LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
        Write-Host "執行輸出：" -ForegroundColor Yellow
        Write-Host $result -ForegroundColor Gray
    }
} catch {
    Write-Host ""
    Write-Host "[錯誤] 執行過程中發生異常" -ForegroundColor Red
    Write-Host "錯誤信息：$($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Read-Host "按 Enter 鍵退出"
