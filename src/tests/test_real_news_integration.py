"""
真實新聞抓取與整合測試
Real News Crawling and Integration Test

將真實新聞爬蟲整合到主系統並寫入資料庫
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.real_crawler_fixed import RealInsuranceNewsCrawler
from database.models import News, NewsSource, NewsCategory, db
from app import create_app
from config.settings import Config
from datetime import datetime, timezone
import logging

logger = logging.getLogger('real_news_integration')

def crawl_and_save_real_news():
    """爬取真實新聞並儲存到資料庫"""
    
    print("🚀 開始真實新聞抓取與整合測試...")
    
    # 建立Flask應用
    app = create_app(Config)
    
    # 初始化爬蟲
    crawler = RealInsuranceNewsCrawler()
    
    # 爬取新聞
    print("\n📡 正在爬取真實新聞...")
    news_list = crawler.crawl_all_sources()
    
    if not news_list:
        print("❌ 沒有爬取到任何真實新聞")
        return
    
    print(f"\n✅ 成功爬取 {len(news_list)} 則真實新聞")
    
    # 儲存到資料庫
    with app.app_context():
        saved_count = 0
        for news in news_list:
            try:                # 檢查是否已存在
                existing = News.query.filter_by(title=news['title']).first()
                if existing:
                    print(f"  📝 新聞已存在: {news['title'][:30]}...")
                    continue
                
                # 建立新的新聞記錄
                article = News(
                    title=news['title'],
                    url=news['url'],
                    content=news.get('content', ''),
                    summary=news.get('summary', ''),
                    source=news['source'],
                    category='保險',
                    published_date=news.get('published_date', datetime.now(timezone.utc)),
                    is_active=True
                )
                
                db.session.add(article)
                saved_count += 1
                print(f"  ✅ 新增真實新聞: {news['title'][:30]}...")
                
            except Exception as e:
                print(f"  ❌ 儲存新聞失敗 {news['title'][:30]}: {e}")
                continue
        
        try:
            db.session.commit()
            print(f"\n🎉 成功儲存 {saved_count} 則真實新聞到資料庫")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 資料庫提交失敗: {e}")
            return
      # 檢查結果
    with app.app_context():
        total_news = News.query.count()
        real_news = News.query.filter(
            News.source.in_(['Google新聞', '聯合新聞網', '自由時報財經'])
        ).count()
        mock_news = total_news - real_news
        
        print(f"\n📊 資料庫狀況更新:")
        print(f"  總新聞數: {total_news}")
        print(f"  真實新聞: {real_news} 則")
        print(f"  模擬新聞: {mock_news} 則")
        
        if real_news > 0:
            print("\n🎉 恭喜！系統現在可以抓取真實新聞了！")
            
            # 顯示最新的真實新聞
            latest_real_news = News.query.filter(
                News.source.in_(['Google新聞', '聯合新聞網', '自由時報財經'])
            ).order_by(News.published_date.desc()).limit(3).all()
            
            print("\n📰 最新真實新聞:")
            for i, article in enumerate(latest_real_news, 1):
                print(f"  {i}. {article.title[:50]}...")
                print(f"     來源: {article.source}")
                print(f"     時間: {article.published_date}")
                print()
        else:
            print("\n⚠️ 尚未成功抓取到真實新聞")

if __name__ == "__main__":
    crawl_and_save_real_news()
