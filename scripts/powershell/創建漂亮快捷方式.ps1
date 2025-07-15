# 創建漂亮快捷方式的PowerShell腳本
# 台灣保險新聞聚合器快捷方式生成器 Pro

# 顯示橫幅
function Show-Banner {
    Write-Host ""
    Write-Host "  台灣保險新聞聚合器 - 快捷方式生成器" -ForegroundColor Cyan
    Write-Host "  ===================================" -ForegroundColor DarkCyan
    Write-Host ""
}

# 設定變數
$projectPath = $PSScriptRoot
$iconPath = Join-Path $projectPath "insurance_icon.ico"
$targetFile = Join-Path $projectPath "台灣保險新聞聚合器-旗艦版.bat"
$shortcutName = "台灣保險新聞聚合器"
$description = "台灣保險新聞聚合器 - 旗艦版 2025"

# 顯示開始訊息
Show-Banner
Write-Host "開始創建桌面快捷方式..." -ForegroundColor Yellow
Write-Host ""

# 檢查檔案
Write-Host "檢查必要檔案:" -ForegroundColor White
if (Test-Path $iconPath) {
    Write-Host "  ✓ 圖標檔案: $iconPath" -ForegroundColor Green
} else {
    Write-Host "  ! 找不到圖標檔案，將使用系統圖標" -ForegroundColor Yellow
    # 使用Windows內建圖標
    $iconPath = "imageres.dll,154"
}

if (Test-Path $targetFile) {
    Write-Host "  ✓ 目標檔案: $targetFile" -ForegroundColor Green
} else {
    Write-Host "  ! 找不到目標檔案" -ForegroundColor Red
    Write-Host "嘗試尋找替代檔案..." -ForegroundColor Yellow
    
    # 尋找替代檔案
    $alternativeFiles = @(
        "台灣保險新聞聚合器-專業版.bat",
        "StartApp.bat",
        "🚀一鍵啟動保險新聞聚合器.bat",
        "UI啟動.bat"
    )
    
    $fileFound = $false
    foreach ($file in $alternativeFiles) {
        $altFilePath = Join-Path $projectPath $file
        if (Test-Path $altFilePath) {
            $targetFile = $altFilePath
            Write-Host "  ✓ 找到替代檔案: $file" -ForegroundColor Green
            $fileFound = $true
            break
        }
    }
    
    if (-not $fileFound) {
        Write-Host "  ✗ 無法找到任何可用的啟動檔案!" -ForegroundColor Red
        Write-Host "創建快捷方式失敗，按任意鍵退出..." -ForegroundColor Red
        $null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# 創建桌面快捷方式
try {
    Write-Host ""
    Write-Host "創建桌面快捷方式中..." -ForegroundColor Cyan
    
    # 獲取桌面路徑
    $desktopPath = [System.Environment]::GetFolderPath("Desktop")
    $shortcutFullPath = Join-Path $desktopPath "$shortcutName.lnk"
    
    # 創建快捷方式
    $WshShell = New-Object -comObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut($shortcutFullPath)
    $shortcut.TargetPath = $targetFile
    $shortcut.WorkingDirectory = $projectPath
    $shortcut.Description = $description
    $shortcut.IconLocation = $iconPath
    $shortcut.Save()
    
    Write-Host "  ✓ 快捷方式創建成功!" -ForegroundColor Green
    Write-Host "    路徑: $shortcutFullPath" -ForegroundColor DarkGray
    
    # 顯示使用方法
    Write-Host ""
    Write-Host "快捷方式詳情:" -ForegroundColor White
    Write-Host "  名稱: $shortcutName" -ForegroundColor White
    Write-Host "  描述: $description" -ForegroundColor White
    Write-Host "  圖標: $iconPath" -ForegroundColor White
    Write-Host ""
    Write-Host "使用方法:" -ForegroundColor Magenta
    Write-Host "  1. 雙擊桌面上的「$shortcutName」圖標" -ForegroundColor White
    Write-Host "  2. 系統將自動啟動並開啟瀏覽器" -ForegroundColor White
    Write-Host "  3. 關閉命令窗口可停止服務" -ForegroundColor White
    
} catch {
    Write-Host "  ✗ 創建快捷方式時出錯: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "按任意鍵退出..." -ForegroundColor DarkGray
$null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
