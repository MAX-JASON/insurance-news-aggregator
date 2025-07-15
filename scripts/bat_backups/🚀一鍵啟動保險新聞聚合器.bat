@echo off
chcp 65001 >nul
title 台灣保險新聞聚合器 - 一鍵啟動

:: 設定彩色輸出
color 0A

echo.
echo     ████████████████████████████████████████████████
echo     █                                              █
echo     █    台灣保險新聞聚合器 一鍵啟動程序            █
echo     █    Taiwan Insurance News Aggregator          █
echo     █    One-Click Startup                         █
echo     █                                              █
echo     ████████████████████████████████████████████████
echo.
echo     正在檢查系統環境...
echo.

:: 檢查是否在正確目錄
if not exist "apps\start_app.py" (
    echo [錯誤] 無法找到啟動檔案！
    echo [提示] 請將此檔案放在 insurance-news-aggregator 目錄中
    echo.
    pause
    exit /b 1
)

:: 檢查Python虛擬環境
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    echo [錯誤] 虛擬環境不存在！
    echo [自動修復] 正在檢查系統Python...
    
    :: 嘗試使用系統Python
    python --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [發現] 找到系統Python，將使用系統Python啟動
        set PYTHON_PATH=python
    ) else (
        echo [錯誤] 無法找到Python！請安裝Python或虛擬環境
        echo.
        pause
        exit /b 1
    )
) else (
    echo [確認] 虛擬環境存在：%PYTHON_PATH%
)

echo.
echo     ████████████████████████████████████████████████
echo     █                 系統啟動中...                █
echo     ████████████████████████████████████████████████
echo.
echo     📍 服務地址: http://127.0.0.1:5000
echo     🏠 首頁:     http://127.0.0.1:5000/
echo     📊 業務員區: http://127.0.0.1:5000/business/
echo     📈 智能分析: http://127.0.0.1:5000/analysis
echo     📝 反饋頁面: http://127.0.0.1:5000/feedback
echo     🖥️  系統監控: http://127.0.0.1:5000/monitor
echo.
echo     [提示] 系統啟動後會自動開啟瀏覽器
echo     [注意] 請保持此視窗開啟，關閉即停止服務
echo.

:: 延遲3秒後自動開啟瀏覽器
start /b timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000

:: 啟動應用
"%PYTHON_PATH%" apps\start_app.py

:: 應用關閉後的處理
echo.
echo     ████████████████████████████████████████████████
echo     █                 服務已停止                  █
echo     ████████████████████████████████████████████████
echo.

if %ERRORLEVEL% NEQ 0 (
    echo     [錯誤] 啟動失敗，錯誤代碼：%ERRORLEVEL%
    echo     [提示] 請檢查 logs 目錄中的日誌檔案
) else (
    echo     [信息] 服務已正常關閉
)

echo.
echo     按任意鍵退出...
pause >nul
exit /b %ERRORLEVEL%
