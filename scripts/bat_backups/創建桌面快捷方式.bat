@echo off
echo 創建桌面快捷方式中...

:: 創建VBS腳本來生成快捷方式
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo strDesktop = WshShell.SpecialFolders("Desktop") >> "%TEMP%\CreateShortcut.vbs"
echo Set oShellLink = WshShell.CreateShortcut(strDesktop ^& "\台灣保險新聞聚合器.lnk") >> "%TEMP%\CreateShortcut.vbs"
echo oShellLink.TargetPath = "D:\insurance-news-aggregator\桌面快捷方式啟動.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oShellLink.WorkingDirectory = "D:\insurance-news-aggregator" >> "%TEMP%\CreateShortcut.vbs"
echo oShellLink.Description = "台灣保險新聞聚合器" >> "%TEMP%\CreateShortcut.vbs"
echo oShellLink.Save >> "%TEMP%\CreateShortcut.vbs"

:: 運行VBS腳本
cscript //nologo "%TEMP%\CreateShortcut.vbs"

:: 刪除臨時VBS腳本
del "%TEMP%\CreateShortcut.vbs"

echo 桌面快捷方式已創建完成!
pause
