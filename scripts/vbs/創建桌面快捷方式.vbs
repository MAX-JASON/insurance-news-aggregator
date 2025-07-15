' 創建桌面快捷方式腳本
' 台灣保險新聞聚合器快捷方式創建器

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 獲取當前目錄
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
batFile = currentDir & "\🚀一鍵啟動保險新聞聚合器.bat"

' 檢查批次檔是否存在
If Not fso.FileExists(batFile) Then
    MsgBox "錯誤：找不到啟動檔案！" & vbCrLf & "路徑：" & batFile, vbCritical, "檔案不存在"
    WScript.Quit 1
End If

' 獲取桌面路徑
desktopPath = WshShell.SpecialFolders("Desktop")
shortcutPath = desktopPath & "\🚀台灣保險新聞聚合器.lnk"

' 創建快捷方式
Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = batFile
shortcut.WorkingDirectory = currentDir
shortcut.Description = "台灣保險新聞聚合器 - 一鍵啟動"
shortcut.IconLocation = "shell32.dll,13"  ' 使用Windows內建圖標
shortcut.WindowStyle = 1  ' 正常視窗
shortcut.Save

' 顯示結果
MsgBox "✅ 快捷方式創建成功！" & vbCrLf & vbCrLf & _
       "桌面快捷方式：" & vbCrLf & _
       "🚀台灣保險新聞聚合器.lnk" & vbCrLf & vbCrLf & _
       "現在您可以：" & vbCrLf & _
       "1. 點擊桌面上的快捷方式啟動系統" & vbCrLf & _
       "2. 系統會自動開啟瀏覽器到首頁" & vbCrLf & _
       "3. 關閉命令視窗即可停止服務", _
       vbInformation, "快捷方式創建完成"

WScript.Quit 0
