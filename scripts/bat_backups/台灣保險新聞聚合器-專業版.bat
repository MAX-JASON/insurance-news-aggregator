@echo off
chcp 65001 >nul
title 📰 台灣保險新聞聚合器 - 專業版
mode con: cols=80 lines=30
color 1F

:: 設定文字色彩 (使用ANSI轉義序列)
set "ESC="
set "BLUE=%ESC%[36m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "WHITE=%ESC%[37m"
set "RESET=%ESC%[0m"

cls
echo.
echo   %BLUE%█████████████████████████████████████████████████████████████████████%RESET%
echo   %BLUE%█                                                                 █%RESET%
echo   %BLUE%█  %WHITE%       台灣保險新聞聚合器 %YELLOW%· %GREEN%專業版%WHITE% %YELLOW%· %RED%2025                    %BLUE%█%RESET%
echo   %BLUE%█  %WHITE%       Taiwan Insurance News Aggregator %YELLOW%Pro                %BLUE%█%RESET%
echo   %BLUE%█                                                                 █%RESET%
echo   %BLUE%█████████████████████████████████████████████████████████████████████%RESET%
echo.
echo   %YELLOW%系統初始化中，請稍候...%RESET%
echo.

:: 設置時間戳
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

echo   %WHITE%▶ 啟動時間:%RESET% %timestamp%
echo   %WHITE%▶ 系統檢查中...%RESET%

:: 檢查Python環境
echo   %WHITE%▶ 檢查虛擬環境...%RESET%
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
if exist "%PYTHON_PATH%" (
    echo   %GREEN%✓ 虛擬環境檢查通過%RESET%
) else (
    echo   %YELLOW%⚠ 未找到虛擬環境，嘗試使用系統Python%RESET%
    python --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   %GREEN%✓ 找到系統Python%RESET%
        set PYTHON_PATH=python
    ) else (
        echo   %RED%✗ 無法找到Python！請安裝Python或設置正確的虛擬環境%RESET%
        echo.
        echo   %RED%▶ 啟動失敗！按任意鍵退出...%RESET%
        pause >nul
        exit /b 1
    )
)

:: 切換到正確目錄
cd /d "%~dp0"

:: 檢查應用文件
echo   %WHITE%▶ 檢查應用文件...%RESET%
if exist "apps\start_app.py" (
    echo   %GREEN%✓ 應用文件檢查通過%RESET%
) else (
    echo   %RED%✗ 找不到應用啟動文件！%RESET%
    echo.
    echo   %RED%▶ 啟動失敗！按任意鍵退出...%RESET%
    pause >nul
    exit /b 1
)

:: 顯示系統資訊
echo.
echo   %BLUE%████████████████████████ %WHITE%系統資訊 %BLUE%█████████████████████████%RESET%
echo   %WHITE%▶ Python路徑:%RESET% %PYTHON_PATH%
echo   %WHITE%▶ 工作目錄:%RESET% %CD%
echo.
echo   %BLUE%████████████████████████ %WHITE%可用網址 %BLUE%█████████████████████████%RESET%
echo   %YELLOW%▶ 主頁:%RESET%      http://127.0.0.1:5000/
echo   %YELLOW%▶ 業務員區:%RESET%  http://127.0.0.1:5000/business/
echo   %YELLOW%▶ 智能分析:%RESET%  http://127.0.0.1:5000/analysis
echo   %YELLOW%▶ 反饋頁面:%RESET%  http://127.0.0.1:5000/feedback
echo   %YELLOW%▶ 系統監控:%RESET%  http://127.0.0.1:5000/monitor
echo.
echo   %GREEN%系統準備就緒! 3秒後啟動...%RESET%

:: 倒數計時
ping localhost -n 2 >nul
echo   %WHITE%▶ 3...%RESET%
ping localhost -n 2 >nul
echo   %WHITE%▶ 2...%RESET%
ping localhost -n 2 >nul
echo   %WHITE%▶ 1...%RESET%
ping localhost -n 2 >nul

:: 清理畫面
cls
echo.
echo   %BLUE%█████████████████████████████████████████████████████████████████████%RESET%
echo   %BLUE%█                                                                 █%RESET%
echo   %BLUE%█  %WHITE%       台灣保險新聞聚合器 %YELLOW%· %GREEN%專業版%WHITE% %YELLOW%· %RED%2025                    %BLUE%█%RESET%
echo   %BLUE%█  %WHITE%       Taiwan Insurance News Aggregator %YELLOW%Pro                %BLUE%█%RESET%
echo   %BLUE%█                                                                 █%RESET%
echo   %BLUE%█████████████████████████████████████████████████████████████████████%RESET%
echo.
echo   %GREEN%▶ 系統啟動中! 請勿關閉此窗口%RESET%
echo   %WHITE%▶ 正在開啟瀏覽器...%RESET%
echo.

:: 延遲3秒後開啟瀏覽器
start /b timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000

:: 啟動應用
"%PYTHON_PATH%" apps\start_app.py

:: 應用退出處理
echo.
if %ERRORLEVEL% NEQ 0 (
    echo   %RED%▶ 應用異常退出，錯誤代碼：%ERRORLEVEL%%RESET%
    echo   %YELLOW%▶ 請檢查logs目錄下的日誌文件以獲取詳細信息%RESET%
) else (
    echo   %GREEN%▶ 服務已正常關閉%RESET%
)

echo.
echo   %WHITE%按任意鍵退出...%RESET%
pause >nul
