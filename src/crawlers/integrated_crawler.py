"""
整合真實新聞爬取與數據清洗
Integrated Real News Crawling with Data Cleaning

整合真實新聞爬取、數據清洗、去重和資料庫儲存的完整流程
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import difflib

from crawler.real_crawler_fixed import RealInsuranceNewsCrawler
from database.models import News, NewsSource, NewsCategory, db
from app import create_app
from config.settings import Config
from analyzer.insurance_dictionary import (
    is_insurance_related,
    calculate_insurance_relevance_score,
    extract_insurance_keywords
)

logger = logging.getLogger('integrated_crawler')

class IntegratedNewsCrawler:
    """整合新聞爬蟲系統"""
    
    def __init__(self):
        """初始化整合爬蟲"""
        self.app = create_app(Config)
        self.real_crawler = RealInsuranceNewsCrawler()
        self.similarity_threshold = 0.85
        self.min_content_length = 50
        self.min_insurance_score = 0.1
        
        logger.info("🔧 整合新聞爬蟲系統初始化完成")
    
    def clean_text(self, text: str) -> str:
        """清洗文本內容"""
        if not text:
            return ""
        
        import re
        # 移除多餘空白和換行
        text = re.sub(r'\s+', ' ', text.strip())
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', text)
        # 移除特殊字符
        text = re.sub(r'[^\u4e00-\u9fff\w\s\.\,\!\?\:\;\-\(\)\[\]「」『』、。，！？：；]', '', text)
        
        return text.strip()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """計算文本相似度"""
        if not text1 or not text2:
            return 0.0
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def validate_news(self, news: Dict[str, Any]) -> tuple:
        """驗證新聞有效性"""
        errors = []
        
        title = news.get('title', '')
        content = news.get('content', '')
        
        if not title or len(title.strip()) < 5:
            errors.append("標題太短")
        
        if not content or len(content.strip()) < self.min_content_length:
            errors.append("內容太短")
        
        # 檢查保險相關性
        full_text = f"{title} {content}"
        insurance_score = calculate_insurance_relevance_score(full_text)
        if insurance_score < self.min_insurance_score:
            errors.append(f"保險相關性過低: {insurance_score:.3f}")
        
        return len(errors) == 0, errors
    
    def find_duplicates(self, news_list: List[Dict[str, Any]]) -> List[int]:
        """找出重複新聞的索引"""
        to_remove = set()
        
        for i in range(len(news_list)):
            if i in to_remove:
                continue
                
            for j in range(i + 1, len(news_list)):
                if j in to_remove:
                    continue
                
                title_similarity = self.calculate_similarity(
                    news_list[i].get('title', ''),
                    news_list[j].get('title', '')
                )
                
                if title_similarity >= self.similarity_threshold:
                    # 保留較新的或內容較豐富的
                    if len(news_list[i].get('content', '')) >= len(news_list[j].get('content', '')):
                        to_remove.add(j)
                    else:
                        to_remove.add(i)
        
        return list(to_remove)
    
    def crawl_and_process(self) -> Dict[str, Any]:
        """爬取並處理新聞的完整流程"""
        try:
            logger.info("🚀 開始整合新聞爬取與處理流程...")
            
            # 1. 爬取真實新聞
            print("📡 步驟1: 爬取真實新聞...")
            raw_news = self.real_crawler.crawl_all_sources()
            
            if not raw_news:
                return {
                    'status': 'no_news',
                    'message': '沒有爬取到新聞',
                    'stats': {'raw': 0, 'cleaned': 0, 'valid': 0, 'unique': 0, 'saved': 0}
                }
            
            print(f"✅ 爬取到 {len(raw_news)} 則原始新聞")
            
            # 2. 清洗數據
            print("🧹 步驟2: 清洗新聞數據...")
            cleaned_news = []
            for news in raw_news:
                cleaned_news.append({
                    'title': self.clean_text(news.get('title', '')),
                    'content': self.clean_text(news.get('content', '')),
                    'summary': self.clean_text(news.get('summary', '')),
                    'url': news.get('url', ''),
                    'source': news.get('source', ''),
                    'published_date': news.get('published_date', datetime.now(timezone.utc))
                })
            
            print(f"✅ 清洗完成")
            
            # 3. 驗證有效性
            print("✅ 步驟3: 驗證新聞有效性...")
            valid_news = []
            invalid_count = 0
            
            for news in cleaned_news:
                is_valid, errors = self.validate_news(news)
                if is_valid:
                    valid_news.append(news)
                else:
                    invalid_count += 1
                    logger.debug(f"無效新聞: {news.get('title', '')[:30]} - {errors}")
            
            print(f"✅ 有效新聞: {len(valid_news)} 則，無效: {invalid_count} 則")
            
            # 4. 去重處理
            print("🔍 步驟4: 去重處理...")
            duplicate_indices = self.find_duplicates(valid_news)
            unique_news = [news for i, news in enumerate(valid_news) if i not in duplicate_indices]
            
            print(f"✅ 去重完成，移除 {len(duplicate_indices)} 則重複，剩餘 {len(unique_news)} 則")
            
            # 5. 儲存到資料庫
            print("💾 步驟5: 儲存到資料庫...")
            saved_count = 0
            
            with self.app.app_context():
                for news in unique_news:
                    try:
                        # 檢查是否已存在
                        existing = News.query.filter_by(title=news['title']).first()
                        if existing:
                            continue
                        
                        # 取得或建立新聞來源
                        source = NewsSource.query.filter_by(name=news['source']).first()
                        if not source:
                            source = NewsSource(
                                name=news['source'],
                                url=news.get('url', ''),
                                description=f"來自{news['source']}的新聞"
                            )
                            db.session.add(source)
                            db.session.flush()
                        
                        # 取得或建立新聞分類
                        category = NewsCategory.query.filter_by(name='保險').first()
                        if not category:
                            category = NewsCategory(
                                name='保險',
                                description='保險相關新聞'
                            )
                            db.session.add(category)
                            db.session.flush()
                        
                        # 計算保險相關性和重要性
                        full_text = f"{news['title']} {news['content']}"
                        insurance_score = calculate_insurance_relevance_score(full_text)
                        importance_score = min(insurance_score * 1.2, 1.0)
                        
                        # 建立新聞記錄
                        article = News(
                            title=news['title'],
                            url=news['url'],
                            content=news['content'],
                            summary=news['summary'],
                            source_id=source.id,
                            category_id=category.id,
                            published_date=news['published_date'],
                            importance_score=importance_score
                        )
                        
                        db.session.add(article)
                        saved_count += 1
                        
                    except Exception as e:
                        logger.error(f"儲存新聞失敗: {news.get('title', '')[:30]} - {e}")
                        continue
                
                try:
                    db.session.commit()
                    print(f"✅ 成功儲存 {saved_count} 則新聞到資料庫")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"資料庫提交失敗: {e}")
                    saved_count = 0
            
            # 6. 統計結果
            stats = {
                'raw': len(raw_news),
                'cleaned': len(cleaned_news),
                'valid': len(valid_news),
                'unique': len(unique_news),
                'saved': saved_count,
                'invalid': invalid_count,
                'duplicates': len(duplicate_indices)
            }
            
            logger.info(f"🎉 整合爬取完成: {stats}")
            
            return {
                'status': 'success',
                'message': f'成功處理 {saved_count} 則新聞',
                'stats': stats,
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ 整合爬取失敗: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'stats': {'raw': 0, 'cleaned': 0, 'valid': 0, 'unique': 0, 'saved': 0}
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """取得資料庫統計"""
        with self.app.app_context():
            total_news = News.query.count()
            
            # 統計真實新聞和模擬新聞
            real_sources = NewsSource.query.filter(
                NewsSource.name.in_(['Google新聞', '聯合新聞網', '自由時報財經'])
            ).all()
            real_source_ids = [s.id for s in real_sources] if real_sources else []
            
            real_count = News.query.filter(News.source_id.in_(real_source_ids)).count() if real_source_ids else 0
            mock_count = total_news - real_count
            
            return {
                'total_news': total_news,
                'real_news': real_count,
                'mock_news': mock_count,
                'sources': len(NewsSource.query.all())
            }

def main():
    """主執行函數"""
    print("🚀 啟動整合新聞爬取系統...")
    
    crawler = IntegratedNewsCrawler()
    
    # 顯示當前統計
    print("\n📊 當前資料庫狀況:")
    stats = crawler.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 執行爬取
    print("\n🔄 開始執行整合爬取...")
    result = crawler.crawl_and_process()
    
    print(f"\n📋 執行結果:")
    print(f"  狀態: {result['status']}")
    print(f"  訊息: {result['message']}")
    
    if 'stats' in result:
        print(f"  統計:")
        for key, value in result['stats'].items():
            print(f"    {key}: {value}")
    
    # 顯示更新後統計
    print("\n📊 更新後資料庫狀況:")
    stats = crawler.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
