"""
簡單的資料庫檢查腳本
Simple Database Check Script
"""

import sqlite3
import os
from datetime import datetime

def check_database():
    """檢查SQLite資料庫"""
    try:
        # 找到資料庫檔案
        db_path = "instance/insurance_news.db"
        if not os.path.exists(db_path):
            print(f"❌ 資料庫檔案不存在: {db_path}")
            # 嘗試其他可能的路徑
            alt_paths = [
                "instance/dev_insurance_news.db",
                "database/insurance_news.db"
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    db_path = alt_path
                    print(f"✅ 找到資料庫: {db_path}")
                    break
            else:
                print("❌ 找不到任何資料庫檔案")
                return
        
        # 連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 檢查新聞表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news';")
        if not cursor.fetchone():
            print("❌ 新聞表不存在")
            return
        
        # 查看最新的新聞
        print("📰 最新10則新聞:")
        cursor.execute("""
            SELECT id, title, crawled_date, published_date, source_id 
            FROM news 
            ORDER BY crawled_date DESC 
            LIMIT 10
        """)
        
        news_list = cursor.fetchall()
        if not news_list:
            print("❌ 資料庫中沒有任何新聞")
        else:
            for i, (news_id, title, crawled_date, published_date, source_id) in enumerate(news_list, 1):
                print(f"{i}. ID:{news_id} - {title[:50]}...")
                print(f"   爬取時間: {crawled_date}")
                print(f"   發布時間: {published_date}")
                print(f"   來源ID: {source_id}")
                print()
        
        # 統計信息
        cursor.execute("SELECT COUNT(*) FROM news")
        total_count = cursor.fetchone()[0]
        print(f"📊 總新聞數量: {total_count}")
        
        # 檢查最近的新聞
        cursor.execute("""
            SELECT COUNT(*) FROM news 
            WHERE crawled_date >= datetime('now', '-1 hour')
        """)
        recent_count = cursor.fetchone()[0]
        print(f"📊 最近1小時內的新聞: {recent_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 檢查資料庫失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 檢查資料庫...")
    check_database()
