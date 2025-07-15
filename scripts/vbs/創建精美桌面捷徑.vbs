' 創建精美桌面快捷方式的VBS腳本
' 台灣保險新聞聚合器 - 高級快捷方式生成器

Option Explicit

' 定義常量
Const DESKTOP_SHORTCUT_NAME = "台灣保險新聞聚合器"
Const SHORTCUT_DESCRIPTION = "台灣保險新聞聚合器 - 一鍵啟動"
Const APP_NAME = "Insurance News Aggregator"

' 主程序
Main

Sub Main()
    ' 創建系統對象
    Dim objShell, objFSO
    Set objShell = CreateObject("WScript.Shell")
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    
    ' 獲取當前路徑
    Dim currentPath, iconFile, targetFile
    currentPath = objFSO.GetAbsolutePathName(".")
    iconFile = currentPath & "\insurance_icon.ico"
    targetFile = currentPath & "\StartApp.bat"
    
    ' 檢查文件是否存在
    If Not objFSO.FileExists(targetFile) Then
        ShowError "找不到目標啟動文件: " & targetFile
        Exit Sub
    End If
    
    If Not objFSO.FileExists(iconFile) Then
        ' 嘗試使用備用圖標
        iconFile = "imageres.dll,154"  ' 漂亮的藍色文檔圖標
    End If
    
    ' 獲取桌面路徑
    Dim desktopPath, shortcutFile
    desktopPath = objShell.SpecialFolders("Desktop")
    shortcutFile = desktopPath & "\" & DESKTOP_SHORTCUT_NAME & ".lnk"
    
    ' 創建快捷方式
    CreateShortcutWithIcon shortcutFile, targetFile, currentPath, SHORTCUT_DESCRIPTION, iconFile
    
    ' 顯示成功訊息
    ShowSuccess "桌面快捷方式已創建！", shortcutFile
End Sub

' 創建帶圖標的快捷方式
Sub CreateShortcutWithIcon(shortcutPath, targetPath, workingDir, description, iconPath)
    On Error Resume Next
    
    ' 創建快捷方式對象
    Dim objShortcut
    Set objShortcut = CreateObject("WScript.Shell").CreateShortcut(shortcutPath)
    
    ' 設置快捷方式屬性
    objShortcut.TargetPath = targetPath
    objShortcut.WorkingDirectory = workingDir
    objShortcut.Description = description
    objShortcut.IconLocation = iconPath
    objShortcut.WindowStyle = 1  ' 正常窗口
    
    ' 保存快捷方式
    objShortcut.Save
    
    ' 檢查錯誤
    If Err.Number <> 0 Then
        ShowError "創建快捷方式時發生錯誤: " & Err.Description
        Err.Clear
    End If
End Sub

' 顯示成功訊息
Sub ShowSuccess(title, details)
    Dim message
    message = vbCrLf & _
              "✅ " & title & vbCrLf & vbCrLf & _
              "📝 快捷方式資訊:" & vbCrLf & _
              "   • 位置: " & details & vbCrLf & _
              "   • 名稱: " & DESKTOP_SHORTCUT_NAME & vbCrLf & _
              "   • 描述: " & SHORTCUT_DESCRIPTION & vbCrLf & vbCrLf & _
              "📋 使用方法:" & vbCrLf & _
              "   • 雙擊桌面圖標啟動系統" & vbCrLf & _
              "   • 系統將自動開啟瀏覽器" & vbCrLf & _
              "   • 關閉命令窗口可停止服務" & vbCrLf
    
    MsgBox message, vbInformation, "✨ " & APP_NAME & " - 快捷方式創建成功"
End Sub

' 顯示錯誤訊息
Sub ShowError(errorMsg)
    MsgBox errorMsg, vbExclamation, "❌ " & APP_NAME & " - 錯誤"
End Sub
