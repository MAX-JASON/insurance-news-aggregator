#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
為現有新聞添加圖片
"""

import sys
import os
import sqlite3
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

def update_news_images():
    print("=== 為現有新聞添加圖片 ===")
    
    try:
        from utils.image_extractor import extract_image_from_url
        print("✅ 圖片抓取模組載入成功")
        
        # 連接資料庫
        os.chdir("d:/insurance-news-aggregator")
        conn = sqlite3.connect("instance/insurance_news.db")
        cursor = conn.cursor()
        
        # 獲取沒有圖片的新聞
        cursor.execute("""
            SELECT id, title, url FROM news 
            WHERE (image_url IS NULL OR image_url = '') 
            AND url IS NOT NULL 
            AND url != '' 
            ORDER BY id DESC 
            LIMIT 20
        """)
        
        news_list = cursor.fetchall()
        print(f"找到 {len(news_list)} 則需要添加圖片的新聞")
        
        updated_count = 0
        
        for news_id, title, url in news_list:
            print(f"\n處理: {title[:50]}...")
            print(f"URL: {url}")
            
            try:
                # 跳過重複的URL標識符
                if "#daily_" in url:
                    original_url = url.split("#daily_")[0]
                else:
                    original_url = url
                
                # 嘗試抓取圖片
                image_url = extract_image_from_url(original_url)
                
                if image_url:
                    # 更新資料庫
                    cursor.execute(
                        "UPDATE news SET image_url = ? WHERE id = ?",
                        (image_url, news_id)
                    )
                    print(f"✅ 圖片已添加: {image_url[:60]}...")
                    updated_count += 1
                else:
                    # 添加預設圖片
                    default_img = "/static/images/news-placeholder.jpg"
                    cursor.execute(
                        "UPDATE news SET image_url = ? WHERE id = ?", 
                        (default_img, news_id)
                    )
                    print(f"⚠️ 使用預設圖片")
                    updated_count += 1
                    
            except Exception as e:
                print(f"❌ 處理失敗: {e}")
                # 添加預設圖片
                default_img = "/static/images/news-placeholder.jpg"
                cursor.execute(
                    "UPDATE news SET image_url = ? WHERE id = ?", 
                    (default_img, news_id)
                )
                updated_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ 完成！更新了 {updated_count} 則新聞的圖片")
        
    except ImportError as e:
        print(f"❌ 模組載入失敗: {e}")
    except Exception as e:
        print(f"❌ 執行失敗: {e}")

def add_sample_images():
    """為最新的幾則新聞添加示例圖片"""
    print("\n=== 添加示例圖片 ===")
    
    try:
        os.chdir("d:/insurance-news-aggregator")
        conn = sqlite3.connect("instance/insurance_news.db")
        cursor = conn.cursor()
        
        # 示例圖片URL
        sample_images = [
            "https://s.yimg.com/cv/apiv2/twstock/logo2024/PC/Yahoo_Stock.png",
            "https://udn.com/static/img/UDN_BABY.png",
            "/static/images/news-placeholder.jpg",
            "https://finance.yahoo.com.tw/img/logo.png",
            "/static/images/news-placeholder.svg"
        ]
        
        # 獲取最新的10則新聞
        cursor.execute("""
            SELECT id, title FROM news 
            WHERE image_url IS NULL OR image_url = ''
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        news_list = cursor.fetchall()
        print(f"為 {len(news_list)} 則新聞添加示例圖片")
        
        for i, (news_id, title) in enumerate(news_list):
            # 循環使用示例圖片
            img_url = sample_images[i % len(sample_images)]
            
            cursor.execute(
                "UPDATE news SET image_url = ? WHERE id = ?",
                (img_url, news_id)
            )
            
            print(f"{i+1}. {title[:40]}... -> {img_url}")
        
        conn.commit()
        conn.close()
        
        print("✅ 示例圖片添加完成")
        
    except Exception as e:
        print(f"❌ 添加示例圖片失敗: {e}")

if __name__ == "__main__":
    # 先嘗試真實圖片抓取
    update_news_images()
    
    # 然後添加示例圖片
    add_sample_images()
    
    # 最後檢查結果
    print("\n=== 檢查結果 ===")
    try:
        os.chdir("d:/insurance-news-aggregator")
        conn = sqlite3.connect("instance/insurance_news.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM news WHERE image_url IS NOT NULL AND image_url != ''")
        count = cursor.fetchone()[0]
        print(f"✅ 現在有 {count} 則新聞有圖片")
        
        conn.close()
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
