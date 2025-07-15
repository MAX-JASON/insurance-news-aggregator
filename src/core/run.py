"""
台灣保險新聞聚合器 - 主應用入口
Insurance News Aggregator - Main Application Entry Point

Author: Development Team
Date: 2025-06-30
Version: 2.1.0 (模組化重構)
"""

import sys
import os
import click
from app import create_app
from config.settings import Config

# 添加模組路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函數 - 啟動應用"""
    app = create_app(Config)
    
    print("🚀 台灣保險新聞聚合器 v2.1.0 啟動中...")
    print(f"📍 服務地址: http://localhost:{Config.PORT}")
    print(f"🌐 API 文檔: http://localhost:{Config.PORT}/api/v1/health")
    print(f"🔧 管理後台: http://localhost:{Config.PORT}/admin")
    print(f"🏠 首頁: http://localhost:{Config.PORT}/")
    print(f"📂 模組化結構已載入")
    
    try:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
    except Exception as e:
        print(f"❌ 應用啟動失敗: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
