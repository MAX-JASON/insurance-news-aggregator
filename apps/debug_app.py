#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
調試版應用啟動器
Debug Application Launcher
"""

import os
import sys

print("🔍 開始檢查環境...")
print(f"Python 版本: {sys.version}")
print(f"當前工作目錄: {os.getcwd()}")

try:
    import flask
    print(f"✅ Flask 版本: {flask.__version__}")
except ImportError:
    print("❌ Flask 未安裝")
    sys.exit(1)

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    print("✅ Flask-SQLAlchemy 可用")
except ImportError:
    print("❌ Flask-SQLAlchemy 未安裝")
    sys.exit(1)

# 檢查目錄結構
required_dirs = ['web', 'web/templates', 'database', 'app']
for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"✅ 目錄存在: {dir_path}")
    else:
        print(f"❌ 目錄不存在: {dir_path}")

# 創建基本 Flask 應用測試
try:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    
    @app.route('/')
    def hello():
        return """
        <h1>🎉 台灣保險新聞聚合器測試頁面</h1>
        <p>如果您看到這個頁面，表示 Flask 應用已成功啟動！</p>
        <ul>
            <li><a href="/test">測試頁面</a></li>
            <li><a href="/feedback">反饋頁面</a> (如果可用)</li>
        </ul>
        """
    
    @app.route('/test')
    def test():
        return """
        <h1>🧪 測試頁面</h1>
        <p>這是一個簡單的測試頁面，確認路由正常工作。</p>
        <p><a href="/">返回首頁</a></p>
        """
    
    print("✅ Flask 應用創建成功")
    print("🚀 啟動測試服務器...")
    print("📍 服務地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服務")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except Exception as e:
    print(f"❌ 啟動失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
