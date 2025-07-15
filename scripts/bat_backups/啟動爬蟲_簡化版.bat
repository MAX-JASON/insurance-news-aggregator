@echo off
chcp 65001 >nul 2>&1
cls
title Taiwan Insurance News Crawler

echo ===================================================
echo   Taiwan Insurance News Crawler
echo ===================================================
echo.
echo Starting crawler system...
echo.

set "PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe"
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

cd /d "D:\insurance-news-aggregator"
color 0A

echo [STARTING] Insurance news crawler...
echo [Python Path] %PYTHON_PATH%
echo.
echo Please wait for crawler to complete...
echo.

"%PYTHON_PATH%" -c "import sys; sys.path.append('.'); from crawler.manager import get_crawler_manager; manager = get_crawler_manager(); result = manager.crawl_all_sources(use_mock=True); print('Crawler result:', result.get('message', 'completed')); print('Total news:', result.get('total', 0))"

if %ERRORLEVEL% EQU 0 (
    color 0B
    echo.
    echo [SUCCESS] Crawler completed!
    echo.
    echo Launch system to view news? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        if exist "啟動系統.bat" (
            start "" "啟動系統.bat"
        ) else (
            start "" "http://127.0.0.1:5000"
        )
    )
) else (
    color 0C
    echo.
    echo [ERROR] Crawler failed!
)

echo.
pause
exit
