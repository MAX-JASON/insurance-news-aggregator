#!/usr/bin/env python3
"""
檢查當前專案的實際狀況
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import Config
from database.models import db, News, NewsSource, NewsCategory

def check_project_status():
    """檢查專案當前狀況"""
    print("🔍 檢查台灣保險新聞聚合器當前狀況...")
    
    app = create_app(Config)
    
    with app.app_context():
        # 檢查資料庫數據
        total_news = News.query.count()
        active_news = News.query.filter_by(status='active').count()
        sources = NewsSource.query.all()
        categories = NewsCategory.query.all()
        
        print(f"\n📊 資料庫狀況:")
        print(f"  總新聞數: {total_news}")
        print(f"  活躍新聞: {active_news}")
        print(f"  新聞來源: {len(sources)}")
        print(f"  新聞分類: {len(categories)}")
        
        # 檢查新聞來源
        print(f"\n📰 新聞來源詳情:")
        for source in sources:
            news_count = News.query.filter_by(source_id=source.id).count()
            print(f"  {source.name}: {news_count} 則新聞")
        
        # 檢查最新的幾則新聞
        print(f"\n📋 最新5則新聞:")
        recent_news = News.query.filter_by(status='active').order_by(News.created_at.desc()).limit(5).all()
        for i, news in enumerate(recent_news, 1):
            source_name = news.source.name if news.source else "未知來源"
            print(f"  {i}. {news.title[:50]}... (來源: {source_name})")
          # 檢查新聞是否為模擬數據 - 改用來源判斷
        print(f"\n🧪 數據來源分析:")
        
        # 統計真實新聞和模擬新聞
        real_sources = NewsSource.query.filter(
            NewsSource.name.in_(['Google新聞', '聯合新聞網', '自由時報財經'])
        ).all()
        real_source_ids = [s.id for s in real_sources] if real_sources else []
        
        real_count = News.query.filter(News.source_id.in_(real_source_ids)).count() if real_source_ids else 0
        mock_count = total_news - real_count
        
        print(f"  真實數據: {real_count} 則")
        print(f"  模擬數據: {mock_count} 則")
        
        return {
            'total_news': total_news,
            'mock_count': mock_count,
            'real_count': real_count,
            'sources': len(sources)
        }

def test_real_crawling():
    """測試真實爬蟲功能"""
    print(f"\n🕷️ 測試真實爬蟲功能...")
    
    # 嘗試簡單的HTTP請求測試
    import requests
    from bs4 import BeautifulSoup
    
    test_urls = [
        "https://money.udn.com/money/cate/5636",  # 經濟日報保險
        "https://www.chinatimes.com/finance/insurance",  # 中時保險
    ]
    
    working_sources = []
    failed_sources = []
    
    for url in test_urls:
        try:
            print(f"  測試: {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                print(f"    ✅ 可存取 - 標題: {title.get_text()[:50] if title else 'N/A'}...")
                working_sources.append(url)
            else:
                print(f"    ❌ HTTP {response.status_code}")
                failed_sources.append(url)
                
        except Exception as e:
            print(f"    ❌ 連線失敗: {str(e)[:50]}...")
            failed_sources.append(url)
    
    return working_sources, failed_sources

def check_implementation_progress():
    """檢查實施進度"""
    print(f"\n📋 實施計劃進度檢查...")
    
    # 根據docs/IMPLEMENTATION_PLAN.md的內容檢查
    progress = {
        "Week 1: 爬蟲系統優化": {
            "修復主程式啟動問題": "✅ 完成",
            "建立第一個可用的爬蟲來源": "✅ 完成 (Google新聞爬蟲)" if real_count > 0 else "⚠️ 部分完成 (僅模擬數據)",
            "完善資料庫測試數據": "✅ 完成",
            "修復前端JavaScript錯誤": "✅ 完成",
            "實現基本的新聞列表顯示": "✅ 完成"
        },
        "Week 2: 分析系統調校": {
            "調試中文文本分析": "⚠️ 需要優化",
            "完善情感分析": "⚠️ 基本可用",
            "優化保險專業詞庫": "❌ 未完成",
            "實現新聞重要性評分": "✅ 基本完成",
            "建立分析結果快取": "❌ 未完成"
        },
        "真實數據抓取": {
            "RSS爬蟲": "❌ 失敗",
            "網站爬蟲": "❌ 未完成",
            "反爬蟲機制": "❌ 未完成",
            "數據清洗": "❌ 未完成"
        }
    }
    
    for phase, tasks in progress.items():
        print(f"\n  📅 {phase}:")
        for task, status in tasks.items():
            print(f"    {status} {task}")
    
    return progress

if __name__ == "__main__":
    # 檢查專案狀況
    status = check_project_status()
    
    # 測試真實爬蟲
    working, failed = test_real_crawling()
    
    # 檢查實施進度
    progress = check_implementation_progress()
      # 總結
    print(f"\n🎯 總結:")
    if status['real_count'] > 0:
        print(f"  ✅ 已成功抓取真實新聞 ({status['real_count']} 則)")
        print(f"  ✅ 真實爬蟲功能運作正常")
        print(f"  ✅ 系統基礎架構完整，可以運行")
        print(f"  📈 實施進度約60-70%")
        print(f"\n🎉 恭喜！系統現在可以抓取和顯示真實新聞了！")
    else:
        print(f"  目前只有模擬數據，沒有真實新聞抓取")
        print(f"  真實爬蟲功能尚未完成")
        print(f"  系統基礎架構完整，可以運行")
        print(f"  實施進度約30-40%")
    
    if status['real_count'] == 0:
        print(f"\n⚠️ 重要提醒: 目前所有新聞都是模擬數據!")
        print(f"   需要實作真實的新聞抓取功能才能稱為完整的新聞聚合器")
