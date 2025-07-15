@echo off
chcp 65001 >nul
title 📰 Taiwan Insurance News Aggregator Pro
mode con: cols=90 lines=35
color 0B

:: ANSI 轉義序列啟用
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
  exit /B 0
)
call :setESC

:: 設定文字色彩 (使用ANSI轉義序列)
set "BLUE=%ESC%[94m"
set "CYAN=%ESC%[96m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "MAGENTA=%ESC%[95m"
set "WHITE=%ESC%[97m"
set "BOLD=%ESC%[1m"
set "RESET=%ESC%[0m"
set "BG_BLUE=%ESC%[44m"
set "BG_BLACK=%ESC%[40m"

:: 清除畫面
cls

:: 動畫顯示
echo %CYAN%
echo.
echo   ████████╗ █████╗ ██╗██╗    ██╗ █████╗ ███╗   ██╗    ██╗███╗   ██╗███████╗
echo   ╚══██╔══╝██╔══██╗██║██║    ██║██╔══██╗████╗  ██║    ██║████╗  ██║██╔════╝
echo      ██║   ███████║██║██║ █╗ ██║███████║██╔██╗ ██║    ██║██╔██╗ ██║███████╗
echo      ██║   ██╔══██║██║██║███╗██║██╔══██║██║╚██╗██║    ██║██║╚██╗██║╚════██║
echo      ██║   ██║  ██║██║╚███╔███╔╝██║  ██║██║ ╚████║    ██║██║ ╚████║███████║
echo      ╚═╝   ╚═╝  ╚═╝╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝╚═╝  ╚═══╝╚══════╝
echo %RESET%
echo %YELLOW%
echo   ██╗███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ███╗   ██╗ ██████╗███████╗
echo   ██║████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝
echo   ██║██╔██╗ ██║███████╗██║   ██║██████╔╝███████║██╔██╗ ██║██║     █████╗  
echo   ██║██║╚██╗██║╚════██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║██║     ██╔══╝  
echo   ██║██║ ╚████║███████║╚██████╔╝██║  ██║██║  ██║██║ ╚████║╚██████╗███████╗
echo   ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
echo %RESET%
echo   %MAGENTA%保險新聞聚合器 %WHITE%· %GREEN%專業版 %WHITE%· %BOLD%2025 %RESET%
echo.
echo   %BG_BLUE%%WHITE%                         系統啟動精靈                                  %RESET%
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

echo   %BOLD%%WHITE%▶ 啟動時間:%RESET% %timestamp%
echo   %BOLD%%WHITE%▶ 系統檢查中...%RESET%
ping localhost -n 2 >nul

:: 檢查Python虛擬環境
echo   %BOLD%%WHITE%▶ 檢查Python環境...%RESET%
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
if exist "%PYTHON_PATH%" (
    echo   %GREEN%✓ 虛擬環境檢查通過%RESET%
    ping localhost -n 2 >nul
) else (
    echo   %YELLOW%⚠ 未找到虛擬環境，嘗試使用系統Python%RESET%
    ping localhost -n 2 >nul
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
echo   %BOLD%%WHITE%▶ 檢查應用檔案...%RESET%
ping localhost -n 2 >nul
if exist "apps\start_app.py" (
    echo   %GREEN%✓ 應用檔案檢查通過%RESET%
    ping localhost -n 2 >nul
) else (
    echo   %RED%✗ 找不到應用啟動檔案！%RESET%
    echo.
    echo   %RED%▶ 啟動失敗！按任意鍵退出...%RESET%
    pause >nul
    exit /b 1
)

:: 顯示系統資訊
echo.
echo   %BG_BLUE%%WHITE%                         系統資訊                                     %RESET%
echo   %CYAN%▶ Python路徑:%RESET% %PYTHON_PATH%
echo   %CYAN%▶ 工作目錄:%RESET% %CD%
echo   %CYAN%▶ 程式版本:%RESET% 2.5.0 專業版
echo.
echo   %BG_BLUE%%WHITE%                        可用服務網址                                  %RESET%
echo   %YELLOW%▶ 主頁:%RESET%      http://127.0.0.1:5000/
echo   %YELLOW%▶ 業務員區:%RESET%  http://127.0.0.1:5000/business/
echo   %YELLOW%▶ 智能分析:%RESET%  http://127.0.0.1:5000/analysis
echo   %YELLOW%▶ 反饋頁面:%RESET%  http://127.0.0.1:5000/feedback
echo   %YELLOW%▶ 系統監控:%RESET%  http://127.0.0.1:5000/monitor
echo.
echo   %GREEN%%BOLD%系統準備就緒! 即將啟動服務...%RESET%

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
echo %BLUE%
echo.
echo   ████████╗ █████╗ ██╗██╗    ██╗ █████╗ ███╗   ██╗    ██╗███╗   ██╗███████╗
echo   ╚══██╔══╝██╔══██╗██║██║    ██║██╔══██╗████╗  ██║    ██║████╗  ██║██╔════╝
echo      ██║   ███████║██║██║ █╗ ██║███████║██╔██╗ ██║    ██║██╔██╗ ██║███████╗
echo      ██║   ██╔══██║██║██║███╗██║██╔══██║██║╚██╗██║    ██║██║╚██╗██║╚════██║
echo      ██║   ██║  ██║██║╚███╔███╔╝██║  ██║██║ ╚████║    ██║██║ ╚████║███████║
echo      ╚═╝   ╚═╝  ╚═╝╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝╚═╝  ╚═══╝╚══════╝
echo %RESET%
echo %CYAN%
echo   ██╗███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ███╗   ██╗ ██████╗███████╗
echo   ██║████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝
echo   ██║██╔██╗ ██║███████╗██║   ██║██████╔╝███████║██╔██╗ ██║██║     █████╗  
echo   ██║██║╚██╗██║╚════██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║██║     ██╔══╝  
echo   ██║██║ ╚████║███████║╚██████╔╝██║  ██║██║  ██║██║ ╚████║╚██████╗███████╗
echo   ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
echo %RESET%
echo   %GREEN%%BOLD%服務啟動中... %RESET%%YELLOW%瀏覽器將自動開啟%RESET%
echo.
echo   %BG_BLACK%%WHITE% 首頁 http://127.0.0.1:5000/ %RESET%
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
exit /b

:setESC
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
  exit /B 0
)
