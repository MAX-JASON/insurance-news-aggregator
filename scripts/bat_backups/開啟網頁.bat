@echo off
echo ===================================================
echo   開啟保險新聞聚合器網頁
echo ===================================================
echo.

:: 檢查服務是否正在運行
curl -s http://127.0.0.1:5000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [成功] 檢測到服務正在運行
    echo [開啟] 正在開啟瀏覽器...
    echo.
    start http://127.0.0.1:5000
    echo 可用的頁面：
    echo   首頁：        http://127.0.0.1:5000/
    echo   業務員區：    http://127.0.0.1:5000/business/
    echo   智能分析：    http://127.0.0.1:5000/analysis
    echo   反饋頁面：    http://127.0.0.1:5000/feedback
    echo   系統監控：    http://127.0.0.1:5000/monitor
) else (
    echo [警告] 服務可能尚未啟動
    echo [提示] 請先執行 "UI啟動.bat" 啟動服務
    echo [嘗試] 仍然開啟瀏覽器...
    echo.
    start http://127.0.0.1:5000
)

echo.
pause
