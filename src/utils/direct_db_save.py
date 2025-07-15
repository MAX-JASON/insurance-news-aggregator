"""
直接資料庫操作工具
Direct Database Operations Tool

使用原生 SQLite 操作儲存 RSS 新聞
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path

def save_news_directly(news_items):
    """直接儲存新聞到 SQLite 資料庫"""
    print("💾 使用直接資料庫操作儲存新聞...")
    
    # 資料庫路徑 - 使用專案根目錄的 instance 資料夾
    current_dir = Path(__file__).parent.absolute()  # src/utils
    project_root = current_dir.parent.parent  # 回到專案根目錄
    db_path = project_root / "instance" / "insurance_news.db"
    
    print(f"📁 資料庫路徑: {db_path}")
    
    try:
        # 連接資料庫
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        saved_count = 0
        duplicate_count = 0
        
        for item in news_items:
            # 檢查是否已存在
            cursor.execute("SELECT id FROM news WHERE title = ?", (item.title,))
            if cursor.fetchone():
                duplicate_count += 1
                continue
            
            # 獲取或創建新聞來源
            cursor.execute("SELECT id FROM news_sources WHERE name = ?", (item.source,))
            source_row = cursor.fetchone()
            
            if source_row:
                source_id = source_row[0]
            else:
                cursor.execute(
                    "INSERT INTO news_sources (name, url, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (item.source, "", "active", datetime.now(), datetime.now())
                )
                source_id = cursor.lastrowid
            
            # 獲取或創建分類
            cursor.execute("SELECT id FROM news_categories WHERE name = ?", (item.category,))
            category_row = cursor.fetchone()
            
            if category_row:
                category_id = category_row[0]
            else:
                cursor.execute(
                    "INSERT INTO news_categories (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (item.category, "RSS新聞分類", datetime.now(), datetime.now())
                )
                category_id = cursor.lastrowid
            
            # 插入新聞
            cursor.execute("""
                INSERT INTO news (
                    title, content, summary, url, source_id, category_id,
                    published_date, crawled_date, created_at, updated_at,
                    status, importance_score, sentiment_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.title,
                item.summary,  # RSS 通常只有摘要，作為內容
                item.summary[:200],  # 截取前200字作為摘要
                item.url,
                source_id,
                category_id,
                item.published_date,
                datetime.now(),  # crawled_date
                datetime.now(),  # created_at
                datetime.now(),  # updated_at
                "active",
                0.6,  # importance_score
                0.0   # sentiment_score
            ))
            
            saved_count += 1
        
        # 提交事務
        conn.commit()
        conn.close()
        
        print(f"✅ 直接儲存成功!")
        print(f"   新增: {saved_count} 篇")
        print(f"   重複: {duplicate_count} 篇")
        
        return {
            'status': 'success',
            'saved_count': saved_count,
            'duplicate_count': duplicate_count
        }
        
    except Exception as e:
        print(f"❌ 直接儲存失敗: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    # 測試用假資料
    from dataclasses import dataclass
    from datetime import datetime
    
    @dataclass
    class TestNewsItem:
        title: str
        summary: str
        url: str
        source: str
        category: str
        published_date: datetime
    
    test_items = [
        TestNewsItem(
            title="測試保險新聞",
            summary="這是一個測試保險新聞的摘要",
            url="https://test.com/news/1",
            source="測試來源",
            category="人壽保險",
            published_date=datetime.now()
        )
    ]
    
    result = save_news_directly(test_items)
    print(f"測試結果: {result}")
