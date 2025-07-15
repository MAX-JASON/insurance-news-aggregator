"""
模組化結構測試腳本
"""

import os
import sys
from pathlib import Path

def main():
    """測試主函數"""
    
    print("🧪 測試模組化結構...")
    root_dir = Path(__file__).parent.absolute()
    src_dir = os.path.join(root_dir, "src")
    
    print(f"📂 根目錄: {root_dir}")
    print(f"📁 源碼目錄: {src_dir}")
    
    # 檢查目錄結構
    directories = [
        "src/core",
        "src/crawlers",
        "src/tests",
        "src/utils",
        "src/maintenance",
        "src/frontend"
    ]
    
    print("\n📋 檢查目錄結構:")
    for directory in directories:
        dir_path = os.path.join(root_dir, directory)
        if os.path.exists(dir_path):
            print(f"✅ {directory} - 存在")
        else:
            print(f"❌ {directory} - 不存在")
    
    # 測試各模組下的文件數量
    print("\n📊 檢查各模組文件數量:")
    for directory in directories:
        dir_path = os.path.join(root_dir, directory)
        if os.path.exists(dir_path):
            py_files = [f for f in os.listdir(dir_path) if f.endswith('.py')]
            print(f"📁 {directory}: {len(py_files)} 個Python文件")
    
    print("\n🎉 模組化結構檢查完成！")
    return True

if __name__ == "__main__":
    main()
