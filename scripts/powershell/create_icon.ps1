# 創建自定義圖標的PowerShell腳本
# 台灣保險新聞聚合器圖標生成器

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

# 創建 32x32 的圖標
$size = 32
$bitmap = New-Object System.Drawing.Bitmap($size, $size)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# 設置高質量渲染
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

# 背景色 (深藍色)
$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(25, 118, 210))
$graphics.FillRectangle($bgBrush, 0, 0, $size, $size)

# 邊框 (金色)
$borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 193, 7), 2)
$graphics.DrawRectangle($borderPen, 1, 1, $size-2, $size-2)

# 繪製新聞圖標 (白色)
$whiteBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)

# 新聞紙圖標
$graphics.FillRectangle($whiteBrush, 6, 8, 20, 16)
$graphics.FillRectangle($whiteBrush, 8, 12, 16, 2)
$graphics.FillRectangle($whiteBrush, 8, 16, 12, 1)
$graphics.FillRectangle($whiteBrush, 8, 18, 10, 1)
$graphics.FillRectangle($whiteBrush, 8, 20, 14, 1)

# 台灣符號 (紅色小點)
$redBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(244, 67, 54))
$graphics.FillEllipse($redBrush, 22, 6, 4, 4)

# 釋放資源
$graphics.Dispose()

# 保存為PNG (因為直接創建ICO比較複雜)
$iconPath = Join-Path $PWD "insurance_icon.png"
$bitmap.Save($iconPath, [System.Drawing.Imaging.ImageFormat]::Png)

Write-Host "✅ 圖標已創建: $iconPath" -ForegroundColor Green

# 釋放資源
$bitmap.Dispose()
$bgBrush.Dispose()
$borderPen.Dispose()
$whiteBrush.Dispose()
$redBrush.Dispose()

return $iconPath
