#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
雲端部署啟動器
Cloud Deployment Launcher
"""

import os
import sys
import logging

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 設置基本日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('cloud_app')

def create_app():
    """創建雲端應用"""
    from apps.start_app import create_simple_app
    
    app = create_simple_app()
    
    # 雲端環境配置
    if 'PORT' in os.environ:
        port = int(os.environ.get('PORT', 5000))
        app.config['PORT'] = port
    
    # 生產環境配置
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # 資料庫配置（適合 Heroku 等平台）
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # 使用 SQLite（適合小型部署）
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    return app

# 創建應用實例（供 WSGI 伺服器使用）
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
