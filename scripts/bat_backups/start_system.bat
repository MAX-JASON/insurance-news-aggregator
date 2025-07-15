@echo off
title Taiwan Insurance News Aggregator
echo ===================================================
echo   Taiwan Insurance News Aggregator
echo   台灣保險新聞聚合器啟動程序
echo ===================================================
echo.

:: Set color
color 0A

:: Change to correct directory
cd /d "D:\insurance-news-aggregator"

echo Starting system, please wait...
echo 正在啟動系統，請稍候...
echo.

:: Check Python environment
set PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    color 0C
    echo [Error] Cannot find Python virtual environment!
    echo [錯誤] 找不到Python虛擬環境！
    echo Path: %PYTHON_PATH%
    echo 路徑: %PYTHON_PATH%
    echo.
    echo Please ensure virtual environment is properly installed
    echo 請確保虛擬環境已正確安裝
    echo.
    pause
    exit /b 1
)

:: Open webpage
echo System starting... will automatically open webpage
echo 系統啟動中...將自動打開網頁
echo.
start "" "http://127.0.0.1:5000"

:: Start application
echo Starting backend service...
echo 正在啟動後端服務...
echo.
%PYTHON_PATH% apps\start_app.py

:: If application exits, show message
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Error] Application startup failed, error code: %ERRORLEVEL%
    echo [錯誤] 應用啟動失敗，錯誤代碼：%ERRORLEVEL%
    echo Please check logs directory for more information.
    echo 請檢查logs目錄下的日誌文件以獲取更多信息。
) else (
    echo.
    echo [Info] Application closed normally.
    echo [信息] 應用已正常關閉。
)

echo.
pause
exit /b %ERRORLEVEL%
