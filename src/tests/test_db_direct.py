#!/usr/bin/env python3
"""
直接測試資料庫連接
"""

from app import create_app
from database.models import News, NewsSource, NewsCategory

app = create_app()

with app.app_context():
    print("🔍 資料庫直接測試")
    print("=" * 50)
    
    total_news = News.query.count()
    active_news = News.query.filter_by(status='active').count()
    total_sources = NewsSource.query.count()
    active_sources = NewsSource.query.filter_by(status='active').count()
    total_categories = NewsCategory.query.count()
    
    print(f"📰 總新聞數量: {total_news}")
    print(f"✅ 活躍新聞數量: {active_news}")
    print(f"🌐 總來源數量: {total_sources}")
    print(f"✅ 活躍來源數量: {active_sources}")
    print(f"📁 分類數量: {total_categories}")
    
    # 檢查前幾筆新聞
    print("\n📑 前5筆新聞:")
    latest_news = News.query.filter_by(status='active').limit(5).all()
    for i, news in enumerate(latest_news, 1):
        print(f"{i}. {news.title[:50]}...")
        print(f"   來源: {news.source.name if news.source else '無'}")
        print(f"   分類: {news.category.name if news.category else '無'}")
        print()
    
    print("✅ 測試完成")
