#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保險新聞聚合器 - 快速啟動器
Insurance News Aggregator - Quick Launcher

根目錄快速啟動腳本，自動導向正確的啟動程式
"""

import os
import sys
import subprocess

def main():
    """主程式 - 啟動位於startup資料夾的主要啟動腳本"""
    print("🚀 保險新聞聚合器快速啟動器")
    print("=" * 50)
    
    # 確保我們在正確的目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    startup_script = os.path.join(current_dir, "startup", "start_7day_system.py")
    
    if not os.path.exists(startup_script):
        print("❌ 找不到啟動腳本！")
        print(f"預期位置: {startup_script}")
        print("請確認專案結構完整")
        return
    
    print("📁 專案已重新整理，檔案結構更清晰")
    print("🎯 正在啟動主要系統...")
    print("=" * 50)
    
    try:
        # 切換到startup目錄並執行主要啟動腳本
        os.chdir(os.path.join(current_dir, "startup"))
        subprocess.run([sys.executable, "start_7day_system.py"])
        
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        print("\n💡 您也可以手動啟動：")
        print("   cd startup")
        print("   python start_7day_system.py")

if __name__ == "__main__":
    main()
