@echo off
:: 設置UTF-8編碼
chcp 65001 >nul 2>&1
cls
title Taiwan Insurance News Crawler

echo ===================================================
echo   Taiwan Insurance News Crawler
echo ===================================================
echo.
echo Starting crawler system...
echo.

:: 檢查虛擬環境Python
set "PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe"
if not exist "%PYTHON_PATH%" (
    color 0C
    echo [ERROR] Cannot find virtual environment Python!
    echo [PATH] %PYTHON_PATH%
    echo Please ensure the virtual environment is properly installed.
    echo.
    pause
    exit /b 1
)

:: 切換到正確目錄
cd /d "D:\insurance-news-aggregator"

:: 設置顏色
color 0A

:: 顯示爬蟲啟動信息
echo [STARTING] Insurance news crawler...
echo [Python Path] %PYTHON_PATH%
echo.
echo Crawler will run and save news to database
echo.
echo Please wait for crawler to complete...
echo.

:: 執行爬蟲命令
echo [EXECUTING] Starting crawler program...

"%PYTHON_PATH%" -c "import sys; sys.path.append('.'); from crawler.manager import get_crawler_manager; manager = get_crawler_manager(); result = manager.crawl_all_sources(use_mock=True); print('Crawler result:', result.get('message', 'completed')); print('Total news:', result.get('total', 0))"

:: 檢查執行結果
if %ERRORLEVEL% EQU 0 (
    color 0B
    echo.
    echo [SUCCESS] Crawler has completed its work!
    echo.
    echo You can now view the collected news
    echo.
    echo Launch system to view news immediately? (Y/N)
    set /p "choice="
    if /i "%choice%"=="Y" (
        echo Starting system...
        start "" "%~dp0啟動系統.bat"
        exit /b 0
    )
) else (
    color 0C
    echo.
    echo [ERROR] Crawler execution failed
    echo Error code: %ERRORLEVEL%
)

echo.
echo ===================================================
pause
color 07
exit /b %ERRORLEVEL%
