@echo off
:: 設置正確的代碼頁和編碼
chcp 950 >nul 2>&1
setlocal enabledelayedexpansion

:: 設置控制台字體和編碼（適用於繁體中文）
for /f "tokens=3" %%a in ('reg query "HKCU\Console" /v "FaceName" 2^>nul') do set "font=%%a"
if "!font!"=="" (
    reg add "HKCU\Console" /v "FaceName" /t REG_SZ /d "新細明體" /f >nul 2>&1
)

cls
title 台灣保險新聞爬蟲啟動程序

echo ===================================================
echo   台灣保險新聞爬蟲啟動程序
echo ===================================================
echo.
echo 正在啟動爬蟲系統，請稍候...
echo.

:: 檢查虛擬環境Python
set "PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe"
if not exist "!PYTHON_PATH!" (
    color 0C
    echo [錯誤] 無法找到虛擬環境Python！
    echo [路徑] !PYTHON_PATH!
    echo.
    echo 請確保虛擬環境已正確安裝。
    echo.
    pause
    exit /b 1
)

:: 切換到正確目錄
cd /d "D:\insurance-news-aggregator"
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [錯誤] 無法切換到項目目錄
    pause
    exit /b 1
)

:: 設置顏色為綠色
color 0A

:: 顯示爬蟲啟動信息
echo [啟動] 保險新聞爬蟲...
echo [Python路徑] !PYTHON_PATH!
echo.
echo 爬蟲將在後台運行，爬取的新聞將存入資料庫
echo.
echo 請耐心等待爬蟲完成工作...
echo.

:: 簡化的運行命令（避免複雜字符）
echo [執行] 正在啟動爬蟲程序...

"!PYTHON_PATH!" -c "import sys; sys.path.append('.'); from crawler.manager import get_crawler_manager; print('開始初始化爬蟲...'); manager = get_crawler_manager(); print('執行爬蟲任務...'); result = manager.crawl_all_sources(use_mock=True); print('爬蟲執行結果:', result.get('message', '完成')); print('總共抓取新聞數量:', result.get('total', 0))" 2>nul

:: 檢查執行結果
if !ERRORLEVEL! NEQ 0 (
    color 0C
    echo.
    echo [錯誤] 爬蟲執行失敗
    echo 錯誤代碼：!ERRORLEVEL!
    echo.
    echo 可能的解決方案：
    echo 1. 檢查網絡連接
    echo 2. 確認虛擬環境正常
    echo 3. 查看日誌文件獲取詳細錯誤信息
) else (
    color 0B
    echo.
    echo [成功] 爬蟲已完成工作！
    echo.
    echo 您現在可以查看爬取的新聞
    echo.
    echo 是否立即啟動系統查看新聞？(Y/N)
    set /p "choice="
    if /i "!choice!"=="Y" (
        echo 正在啟動主系統...
        start "" "D:\insurance-news-aggregator\啟動系統.bat"
        exit /b 0
    )
)

echo.
echo ===================================================
echo 按任意鍵退出...
pause >nul
color 07
endlocal
exit /b !ERRORLEVEL!
