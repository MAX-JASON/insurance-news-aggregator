@echo off
chcp 65001 >nul
echo ===================================================
echo   Taiwan Insurance News Crawler Startup
echo   台灣保險新聞爬蟲啟動程序
echo ===================================================
echo.
echo Starting crawler system, please wait...
echo 正在啟動爬蟲系統，請稍候...
echo.

:: Check Python virtual environment
set PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    echo [Error] Cannot find virtual environment Python! Path: %PYTHON_PATH%
    echo [錯誤] 無法找到虛擬環境Python！路徑：%PYTHON_PATH%
    echo Please ensure virtual environment is properly installed.
    echo 請確保虛擬環境已正確安裝。
    echo.
    pause
    exit /b 1
)

:: Change to correct directory
cd /d "D:\insurance-news-aggregator"

:: Set color
color 0B

:: Display crawler startup information
echo [Starting] Insurance News Crawler...
echo [啟動] 保險新聞爬蟲...
echo [Python Path] %PYTHON_PATH%
echo [Python路徑] %PYTHON_PATH%
echo.
echo Crawler will run in background, fetched news will be stored in database
echo 爬蟲將在後台運行，爬取的新聞將存入資料庫
echo.
echo Please wait patiently for the crawler to complete...
echo 請耐心等待爬蟲完成工作...
echo.

:: Run crawler command
"%PYTHON_PATH%" -c "from crawler.manager import get_crawler_manager; print('Crawler initializing...'); manager = get_crawler_manager(); print('Starting crawler execution...'); result = manager.crawl_all_sources(use_mock=True); print('Crawler result:', result.get('message', 'completed')); print('Total news collected:', result.get('total', 0))"

:: Check execution result
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo [Error] Crawler execution failed, please check logs for details
    echo [錯誤] 爬蟲執行失敗，請查看日誌獲取詳細信息
    echo Error code: %ERRORLEVEL%
    echo 錯誤代碼：%ERRORLEVEL%
) else (
    color 0A
    echo.
    echo [Success] Crawler has completed its work!
    echo [成功] 爬蟲已完成工作！
    echo.
    echo You can now view the fetched news
    echo 您現在可以查看爬取的新聞
    echo.
    echo Launch system to view news immediately? (Y/N)
    echo 是否立即啟動系統查看新聞？(Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        start "" "start_system.bat"
        if not exist "start_system.bat" (
            start "" "啟動系統.bat"
        )
        exit
    )
)

echo.
echo ===================================================
pause
color 07
exit /b %ERRORLEVEL%
