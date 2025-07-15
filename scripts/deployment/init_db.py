#!/usr/bin/env python3
"""
資料庫初始化腳本
"""

import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import Config
from database.models import db, News, NewsSource, NewsCategory, CrawlLog
import sqlite3

def init_database():
    """初始化資料庫"""
    try:
        print("🔧 正在初始化資料庫...")
        
        # 建立Flask應用
        app = create_app(Config)
        
        with app.app_context():
            # 建立所有表格
            db.create_all()
            print("✅ 所有資料表已建立")
            
            # 檢查表格是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 建立的表格: {tables}")
            
            # 插入一些測試資料
            create_sample_data()
            
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        return False
    
    return True

def create_sample_data():
    """建立範例資料"""
    try:
        # 檢查是否已有資料
        if NewsCategory.query.first():
            print("📝 資料庫已有資料，跳過範例資料建立")
            return
        
        print("📝 正在建立範例資料...")
          # 建立新聞分類
        categories = [
            NewsCategory(name="壽險", description="人壽保險相關新聞"),
            NewsCategory(name="產險", description="產險相關新聞"), 
            NewsCategory(name="健康險", description="健康保險相關新聞"),
            NewsCategory(name="法規", description="保險法規新聞")
        ]
        
        for category in categories:
            db.session.add(category)
        
        # 建立新聞來源
        sources = [
            NewsSource(
                name="工商時報保險版",
                url="https://ctee.com.tw/category/insurance",
                description="工商時報保險新聞",
                status="active"
            ),
            NewsSource(
                name="經濟日報保險",  
                url="https://money.udn.com/money/cate/5636",
                description="經濟日報保險新聞",
                status="active"
            )
        ]
        
        for source in sources:
            db.session.add(source)
        
        db.session.commit()
          # 建立範例新聞
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        sample_news = [
            News(
                title="台灣保險業數位轉型新趨勢",
                content="隨著科技發展，台灣保險業正積極投入數位轉型，透過人工智慧和大數據分析，提供更精準的保險服務...",
                summary="保險業透過AI和大數據推動數位轉型，提升服務品質",
                url="https://example.com/news/1",
                source_id=1,
                category_id=1,
                published_date=now,
                crawled_date=now,
                status="active",
                keywords="數位轉型,人工智慧,大數據",
                importance_score=0.8
            ),
            News(
                title="金管會發布新版保險法規",
                content="金融監督管理委員會今日發布新版保險相關法規，針對數位保險服務提出更明確的規範...",
                summary="金管會發布新保險法規，規範數位保險服務",
                url="https://example.com/news/2", 
                source_id=2,
                category_id=4,
                published_date=now,
                crawled_date=now,
                status="active",
                keywords="金管會,法規,數位保險",
                importance_score=0.9
            ),
            News(
                title="健康險市場成長創新高",
                content="受到疫情影響，民眾對健康保障需求大幅提升，健康險市場呈現強勁成長態勢...",
                summary="疫情推動健康險需求，市場成長創新高",
                url="https://example.com/news/3",
                source_id=1, 
                category_id=3,
                published_date=now,
                crawled_date=now,
                status="active",
                keywords="健康險,市場成長,疫情",
                importance_score=0.7
            )
        ]
        
        for news in sample_news:
            db.session.add(news)
        
        db.session.commit()
        print(f"✅ 已建立 {len(categories)} 個分類、{len(sources)} 個來源、{len(sample_news)} 則範例新聞")
        
    except Exception as e:
        print(f"❌ 建立範例資料失敗: {e}")
        db.session.rollback()

if __name__ == "__main__":
    init_database()
