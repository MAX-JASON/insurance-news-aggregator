@echo off
chcp 65001 >nul
title 台灣保險新聞聚合器
echo ===================================================
echo   Taiwan Insurance News Aggregator Startup
echo   台灣保險新聞聚合器啟動程序
echo ===================================================
echo.
echo Starting system, please wait...
echo 正在啟動系統，請稍候...
echo.

:: 檢查虛擬環境Python
set PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    echo [Error] Cannot find virtual environment Python!
    echo [錯誤] 無法找到虛擬環境Python！路徑：%PYTHON_PATH%
    echo Please ensure virtual environment is properly installed.
    echo 請確保虛擬環境已正確安裝。
    echo.
    pause
    exit /b 1
)

:: 確保切換到正確目錄
cd /d "D:\insurance-news-aggregator"

:: 啟動應用
echo [Starting] Insurance News Aggregator...
echo [執行] 正在啟動保險新聞聚合器...
echo [Path] Python: %PYTHON_PATH%
echo [路徑] 使用Python：%PYTHON_PATH%
echo [URL] After startup visit: http://127.0.0.1:5000
echo [網址] 啟動後請訪問：http://127.0.0.1:5000
echo.
echo Starting Flask application...
echo 正在啟動Flask應用程序...
echo.

:: 嘗試啟動瀏覽器
start "" "http://127.0.0.1:5000"

:: 使用絕對路徑啟動應用
"%PYTHON_PATH%" "D:\insurance-news-aggregator\apps\start_app.py"

:: 如果應用退出，則顯示訊息
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [錯誤] 應用啟動失敗，錯誤代碼：%ERRORLEVEL%
    echo 請檢查logs目錄下的日誌文件以獲取更多信息。
) else (
    echo.
    echo [信息] 應用已正常關閉。
)

echo.
pause
exit /b %ERRORLEVEL%
