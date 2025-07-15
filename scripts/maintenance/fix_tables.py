#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修復資料庫表格結構
Fix Database Tables
"""

import os
import sys
import logging
from flask import Flask
from datetime import datetime

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 設置基本日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('fix_tables')

def main():
    """修復資料庫表格"""
    logger.info("開始修復資料庫表格...")
    
    # 設置模板和靜態文件目錄
    template_dir = os.path.join(current_dir, 'web', 'templates')
    static_dir = os.path.join(current_dir, 'web', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # 基本配置
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(current_dir, "instance", "insurance_news.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化資料庫
    from app import db
    db.init_app(app)
    
    try:
        with app.app_context():
            # 導入所有模型確保所有表都被創建
            from database.models import (
                BaseModel, User, News, NewsCategory, NewsSource, 
                Feedback, SavedNews, CrawlLog, ErrorLog, AnalysisLog,
                SystemConfig
            )
            
            # 嘗試刪除並重新創建特定表格
            logger.info("嘗試重建 crawl_logs 表格...")
            try:
                db.engine.execute('DROP TABLE IF EXISTS crawl_logs')
                logger.info("crawl_logs 表格已刪除")
            except Exception as e:
                logger.warning(f"無法刪除 crawl_logs 表格: {e}")
            
            logger.info("嘗試重建 error_logs 表格...")
            try:
                db.engine.execute('DROP TABLE IF EXISTS error_logs')
                logger.info("error_logs 表格已刪除")
            except Exception as e:
                logger.warning(f"無法刪除 error_logs 表格: {e}")
            
            # 創建所有表格
            db.create_all()
            logger.info("✅ 資料庫表格已成功創建/更新")
            
            # 嘗試查詢這些表以確認它們存在
            try:
                db.session.query(CrawlLog).first()
                logger.info("✅ crawl_logs 表格可以正常查詢")
            except Exception as e:
                logger.error(f"❌ crawl_logs 表格查詢失敗: {e}")
            
            try:
                db.session.query(ErrorLog).first()
                logger.info("✅ error_logs 表格可以正常查詢")
            except Exception as e:
                logger.error(f"❌ error_logs 表格查詢失敗: {e}")
    
    except Exception as e:
        logger.error(f"❌ 修復資料庫表格失敗: {e}")
        return 1
    
    logger.info("資料庫表格修復完成，請重啟應用程式")
    return 0

if __name__ == '__main__':
    sys.exit(main())
