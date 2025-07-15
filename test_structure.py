#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
專案結構測試腳本
檢查重新整理後的專案結構是否完整
"""

import os
import sys

def test_project_structure():
    """測試專案結構完整性"""
    print("🔍 檢查專案結構...")
    
    # 關鍵資料夾
    required_folders = [
        "crawlers",
        "management", 
        "startup",
        "tools",
        "apps",
        "instance",
        "logs"
    ]
    
    # 關鍵檔案
    required_files = [
        "apps/start_app.py",
        "startup/start_7day_system.py",
        "crawlers/daily_crawler_60.py",
        "management/auto_cleanup_service.py",
        "tools/check_database.py",
        "instance/insurance_news.db"
    ]
    
    print("\n📁 檢查資料夾:")
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"  ✅ {folder}")
        else:
            print(f"  ❌ {folder}")
    
    print("\n📄 檢查關鍵檔案:")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    print("\n🗂️ 資料夾內容統計:")
    for folder in required_folders:
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.endswith('.py')]
            print(f"  📂 {folder}: {len(files)} 個Python檔案")
    
    print("\n✅ 專案結構檢查完成")

if __name__ == "__main__":
    test_project_structure()
