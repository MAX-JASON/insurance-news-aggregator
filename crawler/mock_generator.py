"""
模擬新聞生成器
Mock News Generator

生成保險相關的模擬新聞數據用於測試
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import random

class MockNewsGenerator:
    """模擬新聞生成器"""
    
    def __init__(self):
        self.news_templates = [
            {
                'title': '金管會發布{year}年保險業數位轉型新指引',
                'content': '金融監督管理委員會今日發布{year}年保險業數位轉型指引，要求保險公司加強數位化服務能力，提升客戶體驗。指引中特別強調人工智慧、大數據分析在保險業務中的應用，並對資訊安全、個資保護提出更嚴格要求。',
                'category': '法規',
                'keywords': '金管會,數位轉型,人工智慧,資訊安全'
            },
            {
                'title': '台灣壽險業前{month}月保費收入創新高',
                'content': '根據保險事業發展中心統計，台灣壽險業今年前{month}月保費收入達新台幣{amount}億元，較去年同期成長{growth}%。其中投資型保險商品表現亮眼，反映民眾對退休理財規劃需求增加。',
                'category': '壽險',
                'keywords': '壽險,保費收入,投資型保險,退休理財'
            },
            {
                'title': '健康險理賠金額年增{growth}% 疫情影響持續',
                'content': '受到新冠疫情持續影響，今年健康險理賠金額較去年同期增加{growth}%。保險公司表示，民眾健康意識提升，投保意願增強，但同時理賠案件也明顯增加，特別是住院醫療和重大疾病理賠。',
                'category': '健康險',
                'keywords': '健康險,理賠,疫情,住院醫療'
            },
            {
                'title': '產險業推出新型態氣候變遷保障商品',
                'content': '面對全球氣候變遷挑戰，國內主要產險公司聯合推出新型態氣候風險保障商品。商品涵蓋極端天氣、海平面上升、溫度變化等風險，為企業和個人提供更全面的保障。',
                'category': '產險',
                'keywords': '產險,氣候變遷,極端天氣,風險保障'
            },
            {
                'title': '保險科技新創獲{amount}億元投資',
                'content': '台灣保險科技新創公司「{company}」宣布完成{amount}億元新台幣的B輪融資。該公司專注於利用人工智慧和區塊鏈技術，提供創新的保險服務解決方案，預計將擴大市場布局。',
                'category': '保險科技',
                'keywords': '保險科技,新創,人工智慧,區塊鏈,融資'
            }
        ]
        
        self.sources = [
            {'id': 1, 'name': '工商時報'},
            {'id': 2, 'name': '經濟日報'},
            {'id': 3, 'name': '聯合新聞網'},
            {'id': 4, 'name': '自由時報'}
        ]
        
        self.companies = ['智保科技', '數位保險', '創新保科', '未來保險']
    
    def generate_news(self, count: int = 10) -> List[Dict[str, Any]]:
        """生成指定數量的模擬新聞"""
        news_list = []
        
        for i in range(count):
            template = random.choice(self.news_templates)
            source = random.choice(self.sources)
            
            # 生成隨機數據
            year = 2025
            month = random.randint(1, 12)
            amount = random.randint(50, 500)
            growth = random.randint(5, 25)
            company = random.choice(self.companies)
            
            # 填充模板
            title = template['title'].format(
                year=year, month=month, amount=amount, 
                growth=growth, company=company
            )
            content = template['content'].format(
                year=year, month=month, amount=amount,
                growth=growth, company=company
            )
            
            # 生成隨機發布時間(過去30天內)
            days_ago = random.randint(0, 30)
            published_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            news_item = {
                'title': title,
                'content': content,
                'summary': content[:150] + '...',
                'url': f'https://example.com/news/{i+1}',
                'source': source['name'],
                'source_id': source['id'],
                'category': template['category'],
                'keywords': template['keywords'],
                'published_date': published_date,
                'importance_score': random.uniform(0.3, 1.0),
                'sentiment_score': random.uniform(-0.2, 0.8)
            }
            
            news_list.append(news_item)
        
        return news_list
    
    def save_to_database(self, news_list: List[Dict[str, Any]]):
        """將模擬新聞儲存到資料庫"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import create_app
        from config.settings import Config
        from database.models import db, News, NewsCategory
        
        app = create_app(Config)
        
        with app.app_context():
            saved_count = 0
            
            for news_data in news_list:
                try:
                    # 檢查是否已存在相同標題的新聞
                    existing = News.query.filter_by(title=news_data['title']).first()
                    if existing:
                        continue
                    
                    # 尋找或創建分類
                    category = NewsCategory.query.filter_by(name=news_data['category']).first()
                    if not category:
                        category = NewsCategory(
                            name=news_data['category'],
                            description=f"{news_data['category']}相關新聞"
                        )
                        db.session.add(category)
                        db.session.flush()
                    
                    # 創建新聞記錄
                    news = News(
                        title=news_data['title'],
                        content=news_data['content'],
                        summary=news_data['summary'],
                        url=news_data['url'],
                        source_id=news_data['source_id'],
                        category_id=category.id,
                        published_date=news_data['published_date'],
                        crawled_date=datetime.now(timezone.utc),
                        keywords=news_data['keywords'],
                        importance_score=news_data['importance_score'],
                        sentiment_score=news_data['sentiment_score'],
                        status='active'
                    )
                    
                    db.session.add(news)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"❌ 儲存新聞失敗: {e}")
                    continue
            
            try:
                db.session.commit()
                print(f"✅ 成功儲存 {saved_count} 則模擬新聞到資料庫")
            except Exception as e:
                db.session.rollback()
                print(f"❌ 儲存到資料庫失敗: {e}")

def test_mock_generator():
    """測試模擬新聞生成器"""
    generator = MockNewsGenerator()
    
    print("🧪 測試模擬新聞生成器...")
    news_list = generator.generate_news(count=15)
    
    print(f"✅ 成功生成 {len(news_list)} 則模擬新聞")
    
    for i, news in enumerate(news_list[:3], 1):
        print(f"\n📰 新聞 {i}:")
        print(f"標題: {news['title']}")
        print(f"分類: {news['category']}")
        print(f"來源: {news['source']}")
        print(f"摘要: {news['summary']}")
    
    # 儲存到資料庫
    print("\n💾 正在儲存到資料庫...")
    generator.save_to_database(news_list)

if __name__ == "__main__":
    test_mock_generator()
