#!/usr/bin/env python3
"""
簡化的資料庫測試
"""

from sqlalchemy import create_engine, text
import os

# 使用絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'insurance_news.db')
DATABASE_URI = f"sqlite:///{DB_PATH}"

print(f"🔍 測試資料庫連接")
print(f"📁 資料庫路徑: {DB_PATH}")
print(f"🔗 連接字串: {DATABASE_URI}")
print("=" * 50)

try:
    # 直接使用SQLAlchemy連接
    engine = create_engine(DATABASE_URI)
    
    with engine.connect() as conn:
        # 檢查新聞表
        result = conn.execute(text("SELECT COUNT(*) FROM news"))
        total_news = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM news WHERE status = 'active'"))
        active_news = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM news_sources"))
        total_sources = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM news_sources WHERE status = 'active'"))
        active_sources = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM news_categories"))
        total_categories = result.scalar()
        
        print(f"📰 總新聞數量: {total_news}")
        print(f"✅ 活躍新聞數量: {active_news}")
        print(f"🌐 總來源數量: {total_sources}")
        print(f"✅ 活躍來源數量: {active_sources}")
        print(f"📁 分類數量: {total_categories}")
        
        # 檢查前5筆新聞
        print("\n📑 前5筆新聞:")
        result = conn.execute(text("""
            SELECT n.id, n.title, ns.name as source_name 
            FROM news n 
            LEFT JOIN news_sources ns ON n.source_id = ns.id 
            WHERE n.status = 'active' 
            ORDER BY n.crawled_date DESC 
            LIMIT 5
        """))
        
        for i, row in enumerate(result, 1):
            print(f"{i}. {row.title[:50]}...")
            print(f"   來源: {row.source_name or '無'}")
            print()
        
        print("✅ 資料庫連接測試成功")
        
except Exception as e:
    print(f"❌ 資料庫連接失敗: {e}")
