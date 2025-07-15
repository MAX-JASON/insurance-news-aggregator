# 創建ICO文件的Python腳本
# 台灣保險新聞聚合器圖標轉換器

import os
try:
    from PIL import Image
    print("✓ 已找到PIL庫")
except ImportError:
    print("! 正在安裝PIL庫...")
    os.system("pip install pillow")
    from PIL import Image
    print("✓ 成功安裝PIL庫")

# 檢查是否存在PNG檔案
png_path = "insurance_icon.png"
if not os.path.exists(png_path):
    print(f"✗ 找不到PNG圖標文件: {png_path}")
    exit(1)

# 轉換為ICO
ico_path = "insurance_icon.ico"
try:
    # 打開PNG圖標
    img = Image.open(png_path)
    
    # 保存為ICO格式
    img.save(ico_path, format='ICO', sizes=[(32, 32)])
    print(f"✓ ICO圖標已創建: {ico_path}")
except Exception as e:
    print(f"✗ 轉換失敗: {e}")
    exit(1)

print("✓ 圖標轉換完成")
