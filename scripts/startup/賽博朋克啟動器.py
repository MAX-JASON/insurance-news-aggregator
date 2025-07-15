#!/usr/bin/env python3
"""
保險新聞聚合器 - 賽博朋克界面啟動器
Insurance News Aggregator - Cyberpunk Interface Launcher
"""

import os
import sys
import time
import webbrowser
import subprocess
from threading import Timer

def print_banner():
    """顯示賽博朋克風格橫幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║  🤖 保險新聞聚合器 - 賽博朋克業務員界面 v2.0             ║
    ║  Insurance News Aggregator - Cyberpunk Business UI       ║
    ║                                                          ║
    ║  🌃 未來風格 • 霓虹美學 • 智能分析                        ║
    ║  Future Style • Neon Aesthetics • AI Analysis           ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def kill_existing_processes():
    """停止現有的Python進程"""
    print("🔄 停止現有進程...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/T'], 
                         capture_output=True, text=True)
        else:  # Linux/Mac
            subprocess.run(['pkill', '-f', 'python'], 
                         capture_output=True, text=True)
        time.sleep(1)
        print("✅ 現有進程已停止")
    except Exception as e:
        print(f"⚠️ 停止進程時發生錯誤: {e}")

def start_server():
    """啟動服務器"""
    print("🚀 啟動賽博朋克服務器...")
    
    # 檢查啟動文件
    start_files = [
        'test_cyberpunk_ui.py',
        'apps/start_app.py', 
        'start_app.py'
    ]
    
    start_file = None
    for file in start_files:
        if os.path.exists(file):
            start_file = file
            break
    
    if not start_file:
        print("❌ 未找到啟動檔案")
        print("請確認以下檔案之一存在：")
        for file in start_files:
            print(f"   - {file}")
        return False
    
    print(f"📂 使用啟動檔案: {start_file}")
    
    try:
        # 啟動服務器
        if os.name == 'nt':  # Windows
            subprocess.Popen(['python', start_file], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen(['python3', start_file])
        
        print("✅ 服務器啟動成功")
        return True
    except Exception as e:
        print(f"❌ 服務器啟動失敗: {e}")
        return False

def open_browsers():
    """開啟瀏覽器"""
    print("🌐 開啟賽博朋克界面...")
    
    # 等待服務器啟動
    print("⏳ 等待服務器啟動...")
    for i in range(5):
        print(f"   載入中 {'●' * (i + 1)}")
        time.sleep(1)
    
    urls = [
        ("🏠 業務員主頁", "http://localhost:5000/business/"),
        ("🎮 賽博新聞中心", "http://localhost:5000/business/cyber-news"),
        ("📊 業務儀表板", "http://localhost:5000/business/dashboard")
    ]
    
    for name, url in urls:
        try:
            print(f"   開啟 {name}...")
            webbrowser.open(url)
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️ 無法開啟 {name}: {e}")

def main():
    """主函數"""
    print_banner()
    
    # 停止現有進程
    kill_existing_processes()
    
    # 啟動服務器
    if not start_server():
        input("按 Enter 鍵退出...")
        return
    
    # 開啟瀏覽器
    Timer(3, open_browsers).start()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║  ✨ 賽博朋克系統啟動完成！                                ║
║                                                          ║
║  🔗 可用界面：                                           ║
║    🏠 業務員主頁：http://localhost:5000/business/        ║
║    🎮 賽博新聞中心：http://localhost:5000/business/cyber-news ║
║    📊 業務儀表板：http://localhost:5000/business/dashboard    ║
║                                                          ║
║  🎨 特色功能：                                           ║
║    ✨ 霓虹色彩系統    🌊 動態粒子效果                    ║
║    🔮 玻璃質感界面    ⚡ 即時數據更新                    ║
║    🤖 AI智能分析     👥 客戶關係管理                     ║
║                                                          ║
║  💡 使用提示：                                           ║
║    - 服務器將在新視窗中運行                              ║
║    - 關閉服務器視窗將停止應用程式                        ║
║    - 支援拖拽操作和鍵盤快捷鍵                            ║
╚══════════════════════════════════════════════════════════╝

🌟 歡迎進入賽博朋克業務世界！
    """)
    
    input("按 Enter 鍵退出啟動器...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 啟動器已停止")
    except Exception as e:
        print(f"\n❌ 啟動器發生錯誤: {e}")
        input("按 Enter 鍵退出...")
