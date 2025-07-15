@echo off
chcp 65001 >nul 2>&1
title 台灣保險新聞聚合器

echo ===================================================
echo   台灣保險新聞聚合器啟動程序 (簡化版)
echo   Taiwan Insurance News Aggregator
echo   (已更新：支援重組後的檔案結構)
echo ===================================================
echo.

color 0A
cd /d "%~dp0"

echo 正在啟動系統，請稍候...
echo.

:: 檢查Python環境
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    color 0C
    echo [錯誤] 找不到Python虛擬環境！
    echo 路徑: %PYTHON_PATH%
    echo.
    pause
    exit /b 1
)

echo [檢查] Python環境正常
echo.

:: 設置Python模塊搜索路徑
set PYTHONPATH=%~dp0

:: 執行每日爬蟲收集最新新聞 (60篇精選)
echo 正在執行每日爬蟲收集最新新聞 (60篇精選)...
echo.
"%PYTHON_PATH%" crawlers\daily_crawler_60.py

:: 檢查爬蟲執行結果
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 爬蟲執行遇到問題，但仍將繼續啟動系統
    echo.
) else (
    echo [成功] 爬蟲已完成工作，新聞已更新！共獲取60篇精選新聞
    echo.
)

:: 啟動應用服務器
echo 正在啟動後端服務...
echo.
start /B "" "%PYTHON_PATH%" apps\start_app.py

:: 簡單等待
echo 等待服務器啟動中...
ping 127.0.0.1 -n 4 >nul

:: 打開網頁
echo 系統啟動完成，正在打開網頁...
echo.
start "" "http://127.0.0.1:5000"

:: 等待用戶關閉
echo.
echo 系統已啟動！網頁應該會自動打開。
echo 如果網頁沒有自動打開，請手動訪問: http://127.0.0.1:5000
echo.
echo 💡 其他啟動方式：
echo    - 使用 quick_start.py 獲得更多選項
echo    - 使用 startup\start_7day_system.py 獲得完整控制
echo.
echo 按任意鍵關閉此視窗（這不會關閉服務器）
pause >nul

exit /b 0
