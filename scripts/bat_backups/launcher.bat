@echo off
title Taiwan Insurance News System
echo ===================================================
echo   Taiwan Insurance News System
echo   台灣保險新聞聚合系統
echo ===================================================
echo.
echo [1] Start Crawler - 啟動爬蟲
echo [2] Start System - 啟動系統
echo [3] Both - 兩者都啟動
echo.
set /p choice=Please select an option (1-3): 

if "%choice%"=="1" (
    call start_crawler.bat
) else if "%choice%"=="2" (
    call start_system.bat
) else if "%choice%"=="3" (
    echo Starting crawler first...
    echo 首先啟動爬蟲...
    call start_crawler.bat
    echo.
    echo Now starting system...
    echo 現在啟動系統...
    call start_system.bat
) else (
    echo Invalid choice. Starting system by default...
    echo 無效選擇。預設啟動系統...
    call start_system.bat
)

pause
