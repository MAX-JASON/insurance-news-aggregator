"""
獨立的爬蟲執行腳本
Standalone Crawler Execution Script

避免Flask應用重複註冊問題
"""

import sys
import os
import logging
from datetime import datetime, timezone, timedelta

# 添加專案根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def save_news_to_database_directly(news_list):
    """直接保存新聞到資料庫，避免Flask應用重複註冊問題"""
    import sqlite3
    from datetime import datetime, timezone
    
    try:
        # 連接SQLite資料庫
        db_path = "instance/insurance_news.db"
        if not os.path.exists(db_path):
            db_path = "instance/dev_insurance_news.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for news_data in news_list:
            try:
                # 檢查重複 - 使用標題檢查
                title = news_data.get('title', '')
                if not title:
                    continue
                
                cursor.execute("SELECT id FROM news WHERE title = ?", (title,))
                if cursor.fetchone():
                    print(f"  跳過重複新聞: {title[:50]}...")
                    continue
                
                # 處理來源 - 簡化處理，使用固定來源ID
                source_id = 4  # 使用Google新聞的來源ID
                
                # 處理分類 - 使用預設分類
                category_id = 1  # 使用預設分類
                
                # 準備插入數據
                now = datetime.now(timezone.utc).isoformat()
                published_date = news_data.get('published_date')
                if isinstance(published_date, datetime):
                    published_date = published_date.isoformat()
                elif published_date is None:
                    published_date = now
                
                # 插入新聞
                cursor.execute("""
                    INSERT INTO news (
                        title, content, summary, url, source_id, category_id,
                        published_date, crawled_date, importance_score, 
                        sentiment_score, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    title,
                    news_data.get('content', ''),
                    news_data.get('summary', '')[:500],  # 限制摘要長度
                    news_data.get('url', ''),
                    source_id,
                    category_id,
                    published_date,
                    now,
                    news_data.get('importance_score', 0.5),
                    news_data.get('sentiment_score', 0.0),
                    'active',
                    now,
                    now
                ))
                
                saved_count += 1
                print(f"  ✅ 保存新聞: {title[:50]}...")
                
            except Exception as e:
                print(f"  ❌ 保存單則新聞失敗: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return saved_count
        
    except Exception as e:
        print(f"❌ 資料庫操作失敗: {e}")
        return 0

def execute_crawler():
    """執行爬蟲"""
    try:
        # 設置日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        print("🚀 開始執行獨立爬蟲...")
        
        # 直接使用真實爬蟲
        from crawler.real_crawler_fixed import RealInsuranceNewsCrawler
        
        crawler = RealInsuranceNewsCrawler()
        
        print("🕷️ 正在抓取新聞...")
        all_news = crawler.crawl_all_sources()
        
        if not all_news:
            print("❌ 沒有抓取到任何新聞")
            return False
        
        print(f"📰 總共抓取到 {len(all_news)} 則新聞")
        
        # 應用7天過濾
        print("🔍 應用7天日期過濾...")
        from crawler.date_filter import create_date_filter
        
        date_filter = create_date_filter(max_age_days=7, enable_filter=True)
        filtered_news = date_filter.filter_news_list(all_news)
        
        print(f"✅ 過濾後保留 {len(filtered_news)} 則新聞")
        
        # 直接保存到資料庫
        if filtered_news:
            print("💾 正在保存到資料庫...")
            saved_count = save_news_to_database_directly(filtered_news)
            print(f"✅ 成功保存 {saved_count} 則新聞到資料庫")
            
            if saved_count > 0:
                print("🎉 新聞已更新！現在重新整理網頁應該能看到最新新聞")
                return True
            else:
                print("⚠️ 沒有新的新聞被保存（可能都是重複的）")
                return False
        else:
            print("⚠️ 經過過濾後沒有新聞需要保存")
            return False
            
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主程式"""
    print("🎯 獨立爬蟲執行器")
    print("=" * 50)
    
    if execute_crawler():
        print("\n" + "=" * 50)
        print("🎉 爬蟲執行成功！")
        print("💡 提示: 請重新整理網頁查看最新新聞")
        
        # 顯示最新保存的新聞
        print("\n📰 檢查最新保存的新聞...")
        import sqlite3
        try:
            conn = sqlite3.connect("instance/insurance_news.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, crawled_date 
                FROM news 
                WHERE crawled_date >= datetime('now', '-1 hour')
                ORDER BY crawled_date DESC 
                LIMIT 5
            """)
            recent_news = cursor.fetchall()
            
            if recent_news:
                print("最新保存的新聞:")
                for i, (title, crawled_date) in enumerate(recent_news, 1):
                    print(f"  {i}. {title[:60]}...")
                    print(f"     保存時間: {crawled_date}")
            else:
                print("⚠️ 最近1小時內沒有新保存的新聞")
                
            conn.close()
        except Exception as e:
            print(f"❌ 檢查失敗: {e}")
    else:
        print("\n❌ 爬蟲執行失敗")

if __name__ == "__main__":
    main()
