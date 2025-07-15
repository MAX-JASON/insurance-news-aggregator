#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查資料庫image_url欄位
"""

import sqlite3
import os

def check_database():
    print("=== 資料庫檢查 ===")
    
    # 檢查資料庫檔案
    import os
    os.chdir("d:/insurance-news-aggregator")
    db_path = "instance/insurance_news.db"
    
    print(f"當前目錄: {os.getcwd()}")
    
    if not os.path.exists(db_path):
        print(f"❌ 資料庫檔案不存在: {db_path}")
        return
    
    print(f"✅ 資料庫檔案存在: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 檢查表結構
        cursor.execute("PRAGMA table_info(news)")
        columns = cursor.fetchall()
        
        print(f"\n📋 news表有 {len(columns)} 個欄位:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 檢查是否有image_url欄位
        has_image_url = any(col[1] == 'image_url' for col in columns)
        print(f"\n🖼️ 是否有image_url欄位: {has_image_url}")
        
        if not has_image_url:
            print("正在添加image_url欄位...")
            cursor.execute("ALTER TABLE news ADD COLUMN image_url TEXT")
            conn.commit()
            print("✅ image_url欄位已添加")
        
        # 檢查新聞數量
        cursor.execute("SELECT COUNT(*) FROM news")
        total_news = cursor.fetchone()[0]
        print(f"\n📰 總新聞數量: {total_news}")
        
        # 檢查有圖片的新聞
        cursor.execute("SELECT COUNT(*) FROM news WHERE image_url IS NOT NULL AND image_url != ''")
        with_images = cursor.fetchone()[0]
        print(f"🖼️ 有圖片的新聞: {with_images}")
        
        # 顯示最新幾則新聞的圖片狀況
        cursor.execute("SELECT title, image_url FROM news ORDER BY id DESC LIMIT 5")
        results = cursor.fetchall()
        
        print(f"\n📰 最新5則新聞的圖片狀況:")
        for i, (title, img_url) in enumerate(results, 1):
            title_short = title[:40] + "..." if len(title) > 40 else title
            img_status = "有圖片" if img_url else "無圖片"
            print(f"  {i}. {title_short}")
            print(f"     圖片: {img_status} {img_url[:50] + '...' if img_url and len(img_url) > 50 else img_url or ''}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 資料庫操作錯誤: {e}")

if __name__ == "__main__":
    check_database()
