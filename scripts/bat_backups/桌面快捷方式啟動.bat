@echo off
chcp 65001 >nul
echo 正在啟動台灣保險新聞聚合器...
echo.

:: 使用絕對路徑運行啟動批處理檔
start "" "D:\insurance-news-aggregator\UI啟動.bat"
exit
