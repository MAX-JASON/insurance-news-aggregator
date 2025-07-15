#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試圖片抓取功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_image_extraction():
    print("=== 測試圖片抓取功能 ===")
    
    try:
        from utils.image_extractor import extract_image_from_url
        print("✅ 圖片抓取模組載入成功")
        
        # 測試用的新聞網址
        test_urls = [
            "https://finance.yahoo.com.tw/news/",
            "https://www.chinatimes.com/",
            "https://ctee.com.tw/",
            "https://udn.com/news/index"
        ]
        
        print("\n開始測試圖片抓取...")
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. 測試URL: {url}")
            try:
                image_url = extract_image_from_url(url)
                if image_url:
                    print(f"   ✅ 成功抓取圖片: {image_url}")
                else:
                    print(f"   ⚠️ 未找到圖片")
            except Exception as e:
                print(f"   ❌ 抓取失敗: {e}")
                
    except ImportError as e:
        print(f"❌ 圖片抓取模組載入失敗: {e}")
        print("檢查模組依賴...")
        
        try:
            import requests
            print("✅ requests 可用")
        except ImportError:
            print("❌ requests 不可用")
            
        try:
            from bs4 import BeautifulSoup
            print("✅ BeautifulSoup 可用")
        except ImportError:
            print("❌ BeautifulSoup 不可用")

def test_simple_extraction():
    """簡單的圖片抓取測試"""
    print("\n=== 簡單圖片抓取測試 ===")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        
        # 測試抓取雅虎新聞的圖片
        url = "https://tw.finance.yahoo.com/"
        print(f"測試URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"HTTP狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尋找圖片
            images = soup.find_all('img', limit=5)
            print(f"找到 {len(images)} 張圖片")
            
            for i, img in enumerate(images, 1):
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(url, src)
                    print(f"  {i}. {full_url}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_image_extraction()
    test_simple_extraction()
