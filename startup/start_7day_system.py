#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保險新聞聚合器 - 完整啟動腳本
Insurance News Aggregator - Complete Startup Script

一鍵啟動所有必要的服務：
1. 清理超過7天的舊新聞
2. 啟動Flask網站
3. 可選：啟動自動清理服務
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

def print_banner():
    """顯示啟動橫幅"""
    print("=" * 80)
    print("🏢 保險新聞聚合器 - 7天過濾版本")
    print("📅 Insurance News Aggregator - 7-Day Filter Edition")
    print("=" * 80)
    print(f"🕐 啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📋 功能特色:")
    print("  ✅ 自動清理超過7天的舊新聞")
    print("  ✅ 爬蟲只抓取7天內的新聞")
    print("  ✅ 網站只顯示7天內的新聞")
    print("  ✅ 定期自動清理服務")
    print("=" * 80)

def cleanup_old_news():
    """清理舊新聞"""
    print("\n🧹 第一步：清理超過7天的舊新聞...")
    try:
        result = subprocess.run([
            sys.executable, "../management/auto_cleanup_service.py", "--run-once", "--days", "7"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ 舊新聞清理完成")
        else:
            print(f"⚠️ 清理過程中有警告: {result.stderr}")
    except Exception as e:
        print(f"❌ 清理失敗: {e}")

def start_flask_app():
    """啟動Flask應用"""
    print("\n🚀 第二步：啟動Flask網站...")
    try:
        # 啟動Flask應用 (指向apps目錄的start_app.py)
        subprocess.Popen([
            sys.executable, "../apps/start_app.py"
        ], cwd=os.getcwd())
        
        print("✅ Flask網站正在啟動...")
        print("🌐 網站地址: http://localhost:5000")
        time.sleep(3)  # 等待啟動
        
    except Exception as e:
        print(f"❌ Flask啟動失敗: {e}")

def start_cleanup_service():
    """啟動自動清理服務"""
    print("\n🤖 第三步：啟動自動清理服務...")
    try:
        # 在背景啟動清理服務
        subprocess.Popen([
            sys.executable, "../management/auto_cleanup_service.py"
        ], cwd=os.getcwd())
        
        print("✅ 自動清理服務已啟動")
        print("📅 將在每日 02:00 自動清理舊新聞")
        
    except Exception as e:
        print(f"❌ 清理服務啟動失敗: {e}")

def show_status():
    """顯示系統狀態"""
    print("\n📊 系統狀態檢查...")
    try:
        result = subprocess.run([
            sys.executable, "../management/auto_cleanup_service.py", "--status"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ 無法獲取狀態")
            
    except Exception as e:
        print(f"❌ 狀態檢查失敗: {e}")

def main():
    """主程式"""
    print_banner()
    
    # 詢問用戶要執行哪些步驟
    print("\n🔧 請選擇要執行的操作:")
    print("1. 完整啟動 (清理+網站+自動服務)")
    print("2. 只清理舊新聞")
    print("3. 只啟動網站")
    print("4. 檢查系統狀態")
    print("5. 手動執行爬蟲")
    print("6. 每日爬蟲 (60篇精選新聞)")
    print("7. 清理重複新聞")
    
    choice = input("\n請輸入選項 (1-7): ").strip()
    
    if choice == "1":
        # 完整啟動
        cleanup_old_news()
        start_flask_app()
        start_cleanup_service()
        show_status()
        
        print("\n🎉 系統啟動完成！")
        print("💡 使用說明:")
        print("  - 訪問 http://localhost:5000 查看新聞")
        print("  - 所有新聞都在7天以內")
        print("  - 系統會自動清理舊新聞")
        print("  - 按 Ctrl+C 停止服務")
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 系統已停止")
            
    elif choice == "2":
        # 只清理
        cleanup_old_news()
        show_status()
        
    elif choice == "3":
        # 只啟動網站
        start_flask_app()
        print("\n🌐 網站已啟動: http://localhost:5000")
        input("按 Enter 停止網站...")
        
    elif choice == "4":
        # 檢查狀態
        show_status()
        
    elif choice == "5":
        # 手動執行爬蟲
        print("\n🕷️ 手動執行爬蟲...")
        try:
            result = subprocess.run([
                sys.executable, "../crawlers/standalone_crawler.py"
            ], cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ 爬蟲執行完成")
                show_status()
            else:
                print("❌ 爬蟲執行失敗")
        except Exception as e:
            print(f"❌ 爬蟲執行失敗: {e}")
    
    elif choice == "6":
        # 每日爬蟲 (60篇)
        print("\n📰 執行每日爬蟲 (60篇精選新聞)...")
        try:
            result = subprocess.run([
                sys.executable, "../crawlers/daily_crawler_60.py"
            ], cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ 每日爬蟲執行完成")
                show_status()
            else:
                print("❌ 每日爬蟲執行失敗")
        except Exception as e:
            print(f"❌ 每日爬蟲執行失敗: {e}")
    
    elif choice == "7":
        # 清理重複新聞
        print("\n🧹 清理重複新聞...")
        try:
            result = subprocess.run([
                sys.executable, "../management/cleanup_old_news.py", "--execute"
            ], cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ 重複新聞清理完成")
                show_status()
            else:
                print("❌ 清理失敗")
        except Exception as e:
            print(f"❌ 清理失敗: {e}")
    
    else:
        print("❌ 無效的選項")

if __name__ == "__main__":
    main()
