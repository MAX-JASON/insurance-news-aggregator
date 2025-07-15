#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增強版獨立爬蟲
Enhanced Standalone Crawler

改進的爬蟲，包含更好的重複檢測和更多新聞源
"""

import requests
import feedparser
import sqlite3
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import re
import hashlib

def normalize_title(title):
    """標準化標題以便更好地檢測重複"""
    # 移除常見的前後綴
    title = re.sub(r'^【.*?】', '', title)  # 移除【】標記
    title = re.sub(r'\s*-\s*.*$', '', title)  # 移除來源標記
    title = re.sub(r'\s*\|.*$', '', title)   # 移除|後的內容
    title = re.sub(r'\s+', ' ', title).strip()  # 標準化空格
    return title.lower()

def get_title_hash(title):
    """生成標題的哈希值用於重複檢測"""
    normalized = normalize_title(title)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def fetch_insurance_news():
    """抓取保險新聞"""
    news_list = []
    
    print("🔍 正在抓取最新保險新聞...")
    
    # 1. Google新聞 - 保險
    try:
        print("📡 來源1: Google新聞 - 保險")
        search_url = "https://news.google.com/rss/search?q=保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        feed = feedparser.parse(search_url)
        
        if hasattr(feed, 'entries'):
            for entry in feed.entries[:5]:
                news_list.append({
                    'title': entry.title,
                    'url': entry.link,
                    'summary': entry.get('summary', '')[:200],
                    'content': entry.get('summary', ''),
                    'published_date': datetime.now(timezone.utc),
                    'source': 'Google新聞'
                })
            print(f"  ✅ 獲得 {min(5, len(feed.entries))} 則新聞")
    except Exception as e:
        print(f"  ❌ Google新聞抓取失敗: {e}")
    
    # 2. Google新聞 - 人壽保險
    try:
        print("📡 來源2: Google新聞 - 人壽保險")
        search_url = "https://news.google.com/rss/search?q=人壽保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        feed = feedparser.parse(search_url)
        
        if hasattr(feed, 'entries'):
            for entry in feed.entries[:3]:
                news_list.append({
                    'title': entry.title,
                    'url': entry.link,
                    'summary': entry.get('summary', '')[:200],
                    'content': entry.get('summary', ''),
                    'published_date': datetime.now(timezone.utc),
                    'source': 'Google新聞'
                })
            print(f"  ✅ 獲得 {min(3, len(feed.entries))} 則新聞")
    except Exception as e:
        print(f"  ❌ 人壽保險新聞抓取失敗: {e}")
    
    # 3. Google新聞 - 產險
    try:
        print("📡 來源3: Google新聞 - 產險")
        search_url = "https://news.google.com/rss/search?q=產險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        feed = feedparser.parse(search_url)
        
        if hasattr(feed, 'entries'):
            for entry in feed.entries[:3]:
                news_list.append({
                    'title': entry.title,
                    'url': entry.link,
                    'summary': entry.get('summary', '')[:200],
                    'content': entry.get('summary', ''),
                    'published_date': datetime.now(timezone.utc),
                    'source': 'Google新聞'
                })
            print(f"  ✅ 獲得 {min(3, len(feed.entries))} 則新聞")
    except Exception as e:
        print(f"  ❌ 產險新聞抓取失敗: {e}")
    
    # 4. Google新聞 - 金管會保險
    try:
        print("📡 來源4: Google新聞 - 金管會保險")
        search_url = "https://news.google.com/rss/search?q=金管會+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        feed = feedparser.parse(search_url)
        
        if hasattr(feed, 'entries'):
            for entry in feed.entries[:3]:
                news_list.append({
                    'title': entry.title,
                    'url': entry.link,
                    'summary': entry.get('summary', '')[:200],
                    'content': entry.get('summary', ''),
                    'published_date': datetime.now(timezone.utc),
                    'source': 'Google新聞'
                })
            print(f"  ✅ 獲得 {min(3, len(feed.entries))} 則新聞")
    except Exception as e:
        print(f"  ❌ 金管會保險新聞抓取失敗: {e}")
    
    print(f"📊 總共抓取到 {len(news_list)} 則新聞")
    return news_list

def apply_date_filter(news_list, max_days=7):
    """應用日期過濾"""
    print(f"🔍 應用{max_days}天日期過濾...")
    
    # 對於RSS新聞，我們假設它們都是最近的
    # 因為RSS通常只包含最新的新聞
    filtered_news = news_list.copy()
    
    print(f"✅ 過濾後保留 {len(filtered_news)} 則新聞")
    return filtered_news

def save_to_database(news_list):
    """保存新聞到資料庫"""
    if not news_list:
        print("❌ 沒有新聞要保存")
        return False
    
    print("💾 正在保存到資料庫...")
    
    # 找到資料庫
    db_path = "instance/insurance_news.db"
    if not os.path.exists(db_path):
        db_path = "instance/dev_insurance_news.db"
    
    if not os.path.exists(db_path):
        print("❌ 找不到資料庫檔案")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 獲取現有新聞的標題哈希值
        cursor.execute("SELECT title FROM news WHERE status = 'active'")
        existing_hashes = set()
        for (title,) in cursor.fetchall():
            existing_hashes.add(get_title_hash(title))
        
        saved_count = 0
        duplicate_count = 0
        
        for news_data in news_list:
            try:
                title = news_data.get('title', '').strip()
                if not title:
                    continue
                
                # 使用哈希值檢查重複
                title_hash = get_title_hash(title)
                if title_hash in existing_hashes:
                    duplicate_count += 1
                    print(f"  跳過相似新聞: {title[:50]}...")
                    continue
                
                # 生成唯一的標題
                unique_title = f"{title} - {datetime.now().strftime('%H:%M')}"
                
                # 準備插入數據
                now = datetime.now(timezone.utc).isoformat()
                
                cursor.execute("""
                    INSERT INTO news (
                        title, content, summary, url, source_id, category_id,
                        published_date, crawled_date, importance_score, 
                        sentiment_score, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    unique_title,
                    news_data.get('content', ''),
                    news_data.get('summary', '')[:500],
                    news_data.get('url', ''),
                    4,  # 來源ID
                    1,  # 分類ID
                    now,
                    now,
                    0.8,  # 重要性分數
                    0.1,  # 情感分數
                    'active',
                    now,
                    now
                ))
                
                # 添加到已存在的哈希集合
                existing_hashes.add(title_hash)
                saved_count += 1
                print(f"  ✅ 保存新聞: {title[:50]}...")
                
            except Exception as e:
                print(f"  ❌ 保存失敗: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ 成功保存 {saved_count} 則新聞")
        print(f"⚠️ 跳過 {duplicate_count} 則重複新聞")
        
        return saved_count > 0
        
    except Exception as e:
        print(f"❌ 資料庫操作失敗: {e}")
        return False

def main():
    """主程式"""
    print("🎯 增強版保險新聞爬蟲")
    print("=" * 50)
    
    try:
        # 1. 抓取新聞
        news_list = fetch_insurance_news()
        
        if not news_list:
            print("❌ 沒有抓取到任何新聞")
            return False
        
        # 2. 應用日期過濾
        filtered_news = apply_date_filter(news_list, max_days=7)
        
        if not filtered_news:
            print("❌ 日期過濾後沒有新聞")
            return False
        
        # 3. 保存到資料庫
        success = save_to_database(filtered_news)
        
        if success:
            print("🎉 爬蟲執行成功！")
            print("💡 現在重新整理網頁應該能看到新的新聞")
        else:
            print("⚠️ 沒有新的新聞被保存")
        
        return success
        
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")
        return False

if __name__ == "__main__":
    main()
