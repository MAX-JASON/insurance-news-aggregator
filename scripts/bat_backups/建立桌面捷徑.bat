@echo off
chcp 65001 >nul
title 建立台灣保險新聞聚合器桌面捷徑
color 0A
echo ===================================================
echo   建立台灣保險新聞聚合器桌面捷徑
echo   Create Taiwan Insurance News Aggregator Desktop Shortcut
echo ===================================================
echo.

:: 創建桌面捷徑的VBS腳本
echo Set WshShell = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo strDesktop = WshShell.SpecialFolders("Desktop") >> "%TEMP%\CreateShortcut.vbs"
echo Set objShortcut = WshShell.CreateShortcut(strDesktop ^& "\台灣保險新聞聚合器.lnk") >> "%TEMP%\CreateShortcut.vbs"
echo objShortcut.TargetPath = "D:\insurance-news-aggregator\UI啟動.bat" >> "%TEMP%\CreateShortcut.vbs"
echo objShortcut.WorkingDirectory = "D:\insurance-news-aggregator" >> "%TEMP%\CreateShortcut.vbs"
echo objShortcut.WindowStyle = 1 >> "%TEMP%\CreateShortcut.vbs"
echo objShortcut.Description = "Taiwan Insurance News Aggregator" >> "%TEMP%\CreateShortcut.vbs"
:: 如果有圖示文件就設置圖示
echo If WshShell.FileExists("D:\insurance-news-aggregator\web\static\favicon.ico") Then >> "%TEMP%\CreateShortcut.vbs"
echo     objShortcut.IconLocation = "D:\insurance-news-aggregator\web\static\favicon.ico" >> "%TEMP%\CreateShortcut.vbs"
echo End If >> "%TEMP%\CreateShortcut.vbs"
echo objShortcut.Save >> "%TEMP%\CreateShortcut.vbs"
echo WScript.Echo "桌面捷徑已建立成功!" >> "%TEMP%\CreateShortcut.vbs"

:: 執行VBS腳本
echo 正在建立桌面捷徑...
wscript "%TEMP%\CreateShortcut.vbs"

:: 刪除暫存檔案
del "%TEMP%\CreateShortcut.vbs"

echo.
echo 快捷方式建立完成，按任意鍵退出...
pause >nul
exit
