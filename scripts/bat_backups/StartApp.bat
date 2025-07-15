@echo off
chcp 65001 >nul
title Insurance News Aggregator - Quick Start

:: 設定彩色輸出
color 0A

echo.
echo     ████████████████████████████████████████████████
echo     █                                              █
echo     █    台灣保險新聞聚合器 快速啟動               █ 
echo     █    Taiwan Insurance News Aggregator          █
echo     █    Quick Start                               █
echo     █                                              █
echo     ████████████████████████████████████████████████
echo.

:: 檢查Python虛擬環境
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    echo [自動修復] 檢查系統Python...
    python --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_PATH=python
        echo [OK] 使用系統Python
    ) else (
        echo [錯誤] 無法找到Python！
        pause
        exit /b 1
    )
) else (
    echo [OK] 虛擬環境正常
)

echo.
echo     🚀 啟動中...
echo     📍 http://127.0.0.1:5000
echo     ⏳ 3秒後自動開啟瀏覽器
echo.

:: 3秒後開啟瀏覽器
start /b timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000

:: 啟動應用
"%PYTHON_PATH%" apps\start_app.py

echo.
echo     服務已停止 - 按任意鍵退出
pause >nul
