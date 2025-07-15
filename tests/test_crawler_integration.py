#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬蟲模組測試
Crawler Module Test

測試真實爬蟲功能與管理器整合
"""

import os
import sys
import logging
import json
from datetime import datetime
import time

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

# 設置詳細日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'crawler_test.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('crawler_test')

def test_crawlers():
    """測試爬蟲功能"""
    from crawler.manager import CrawlerManager
    
    print("\n" + "="*60)
    print("🧪 爬蟲功能測試開始")
    print("="*60)
    
    # 初始化爬蟲管理器
    manager = CrawlerManager()
    
    print("\n📋 可用爬蟲清單:")
    for name in manager.crawlers.keys():
        print(f"  - {name}")
    
    # 1. 測試模擬數據生成
    print("\n\n🤖 測試1: 模擬數據生成")
    try:
        mock_result = manager.run_crawlers(source_name='mock', limit=5)
        mock_news = mock_result.get('news', [])
        print(f"✅ 模擬數據生成成功: {len(mock_news)} 則新聞")
        for i, news in enumerate(mock_news[:2], 1):
            print(f"  📰 模擬新聞 {i}: {news.get('title', '無標題')}")
    except Exception as e:
        print(f"❌ 模擬數據生成失敗: {e}")
    
    # 2. 測試真實爬蟲
    print("\n\n🔍 測試2: 真實爬蟲")
    if 'real' in manager.crawlers:
        try:
            print("  正在執行真實爬蟲...")
            real_crawler = manager.crawlers['real']
            real_news = real_crawler.crawl_google_news()
            print(f"  ✅ Google新聞爬取成功: {len(real_news)} 則新聞")
            for i, news in enumerate(real_news[:2], 1):
                print(f"    📰 真實新聞 {i}: {news.get('title', '無標題')}")
        except Exception as e:
            print(f"  ❌ 真實爬蟲執行失敗: {e}")
    else:
        print("  ⚠️ 真實爬蟲未在管理器中註冊")
    
    # 3. 測試RSS爬蟲
    print("\n\n📡 測試3: RSS爬蟲")
    if 'rss' in manager.crawlers:
        try:
            print("  正在執行RSS爬蟲...")
            rss_crawler = manager.crawlers['rss']
            rss_news = rss_crawler.crawl_all_feeds()
            print(f"  ✅ RSS爬取成功: {len(rss_news)} 則新聞")
            for i, news in enumerate(rss_news[:2], 1):
                print(f"    📰 RSS新聞 {i}: {news.get('title', '無標題')}")
        except Exception as e:
            print(f"  ❌ RSS爬蟲執行失敗: {e}")
    else:
        print("  ⚠️ RSS爬蟲未在管理器中註冊")
    
    # 4. 測試整合爬蟲功能 (最關鍵測試)
    print("\n\n🚀 測試4: 整合爬蟲測試 (run_all_crawlers)")
    try:
        print("  正在執行整合爬蟲...")
        
        # 使用真實爬蟲
        start_time = time.time()
        result = manager.run_all_crawlers(use_real=True)
        elapsed = time.time() - start_time
        
        if result.get('status') == 'success':
            news_count = result.get('total', 0)
            print(f"  ✅ 整合爬蟲成功: 獲取 {news_count} 則新聞，耗時 {elapsed:.1f} 秒")
            print("  📊 爬取結果統計:")
            for crawl_result in result.get('results', []):
                status = '✅' if crawl_result.get('success') else '❌'
                print(f"    {status} {crawl_result.get('source', '未知')}: {crawl_result.get('news_count', 0)} 則新聞")
        else:
            print(f"  ❌ 整合爬蟲失敗: {result.get('message', '未知錯誤')}")
    except Exception as e:
        print(f"  ❌ 整合爬蟲測試失敗: {e}")
    
    print("\n" + "="*60)
    print("🏁 爬蟲功能測試完成")
    print("="*60)

if __name__ == "__main__":
    os.makedirs(os.path.join(project_root, 'logs'), exist_ok=True)
    test_crawlers()
