#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地部署測試
Local Deployment Test
"""

import os
import sys

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # 嘗試導入我們的應用
    from wsgi import app
    
    print("✅ 應用導入成功")
    print(f"📍 Flask 版本: {app.config.get('VERSION', '未知')}")
    print(f"🗃️ 資料庫: {app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')}")
    
    print("\n🎉 部署測試完成！應用可以正常啟動")
    print("💡 本地測試指令: python wsgi.py")
    print("🚀 雲端部署指令: git push (推送到已連接的雲端平台)")
    
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("💡 請檢查依賴是否正確安裝: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    print("🧪 開始部署測試...")
    # 如果需要，可以在這裡啟動測試伺服器
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        print("🌐 啟動測試伺服器...")
        from wsgi import app
        app.run(host='0.0.0.0', port=5000, debug=True)
