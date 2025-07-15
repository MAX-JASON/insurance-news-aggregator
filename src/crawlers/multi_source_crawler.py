"""
多來源新聞爬蟲系統
Multi-Source News Crawler System

整合台灣主要財經媒體的保險新聞爬取
"""

import os
import sys
import requests
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('multi_source_crawler')

@dataclass
class NewsArticle:
    """新聞文章數據結構"""
    title: str
    url: str
    summary: str
    content: str
    published_date: datetime
    source: str
    category: str = "保險新聞"
    author: str = ""
    tags: List[str] = None

class MultiSourceNewsCrawler:
    """多來源新聞爬蟲"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 新聞來源配置
        self.sources = {
            'ctee': {
                'name': '工商時報',
                'base_url': 'https://ctee.com.tw',
                'insurance_url': 'https://ctee.com.tw/category/insurance',
                'parser': self._parse_ctee_news
            },
            'udn_money': {
                'name': '經濟日報',
                'base_url': 'https://money.udn.com',
                'insurance_url': 'https://money.udn.com/money/cate/5636',
                'parser': self._parse_udn_news
            },
            'chinatimes_money': {
                'name': '中時新聞網財經',
                'base_url': 'https://www.chinatimes.com',
                'insurance_url': 'https://www.chinatimes.com/money/?chdtv',
                'parser': self._parse_chinatimes_news
            },
            'ltn_ec': {
                'name': '自由時報財經',
                'base_url': 'https://ec.ltn.com.tw',
                'insurance_url': 'https://ec.ltn.com.tw/list/paper',
                'parser': self._parse_ltn_news
            }
        }
        
        self.delay_between_requests = 2.0  # 請求間隔
        self.timeout = 15  # 請求超時
        
        logger.info(f"🕷️ 多來源新聞爬蟲初始化完成，支援 {len(self.sources)} 個來源")
    
    def crawl_all_sources(self, max_articles_per_source: int = 10) -> List[NewsArticle]:
        """爬取所有來源的新聞"""
        logger.info("🚀 開始爬取所有新聞來源...")
        
        all_articles = []
        
        for source_id, source_config in self.sources.items():
            try:
                logger.info(f"📰 正在爬取: {source_config['name']}")
                articles = self._crawl_source(source_id, source_config, max_articles_per_source)
                
                if articles:
                    all_articles.extend(articles)
                    logger.info(f"✅ {source_config['name']} 成功獲取 {len(articles)} 篇文章")
                else:
                    logger.warning(f"⚠️ {source_config['name']} 未獲取到文章")
                
                # 請求間隔
                time.sleep(self.delay_between_requests)
                
            except Exception as e:
                logger.error(f"❌ {source_config['name']} 爬取失敗: {e}")
                continue
        
        logger.info(f"🎉 爬取完成，總共獲得 {len(all_articles)} 篇文章")
        return all_articles
    
    def _crawl_source(self, source_id: str, config: Dict, max_articles: int) -> List[NewsArticle]:
        """爬取單個來源的新聞"""
        try:
            response = self.session.get(config['insurance_url'], timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 使用對應的解析器
            parser = config['parser']
            articles = parser(soup, config, max_articles)
            
            return articles
            
        except Exception as e:
            logger.error(f"爬取 {config['name']} 失敗: {e}")
            return []
    
    def _parse_ctee_news(self, soup: BeautifulSoup, config: Dict, max_articles: int) -> List[NewsArticle]:
        """解析工商時報新聞"""
        articles = []
        
        try:
            # 查找新聞列表
            news_items = soup.select('.archive-list-item, .post-item, article')[:max_articles]
            
            for item in news_items:
                try:
                    # 標題和連結
                    title_elem = item.select_one('h2 a, h3 a, .title a, a[title]')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = urljoin(config['base_url'], title_elem.get('href', ''))
                    
                    # 檢查是否為保險相關
                    if not self._is_insurance_related(title):
                        continue
                    
                    # 摘要
                    summary_elem = item.select_one('.excerpt, .summary, p')
                    summary = summary_elem.get_text(strip=True) if summary_elem else title[:100]
                    
                    # 時間
                    time_elem = item.select_one('.date, .time, time')
                    published_date = self._parse_date(time_elem.get_text(strip=True) if time_elem else '')
                    
                    # 獲取完整內容
                    content = self._fetch_article_content(url)
                    
                    article = NewsArticle(
                        title=title,
                        url=url,
                        summary=summary,
                        content=content,
                        published_date=published_date,
                        source=config['name'],
                        category="保險新聞"
                    )
                    
                    articles.append(article)
                    logger.info(f"✅ 工商時報: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"解析工商時報文章失敗: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"解析工商時報頁面失敗: {e}")
        
        return articles
    
    def _parse_udn_news(self, soup: BeautifulSoup, config: Dict, max_articles: int) -> List[NewsArticle]:
        """解析經濟日報新聞"""
        articles = []
        
        try:
            # 查找新聞列表
            news_items = soup.select('.story-list__item, .listing__item, article')[:max_articles]
            
            for item in news_items:
                try:
                    title_elem = item.select_one('h2 a, h3 a, .story-list__title a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = urljoin(config['base_url'], title_elem.get('href', ''))
                    
                    if not self._is_insurance_related(title):
                        continue
                    
                    summary_elem = item.select_one('.story-list__summary, .summary')
                    summary = summary_elem.get_text(strip=True) if summary_elem else title[:100]
                    
                    time_elem = item.select_one('.story-list__time, .time')
                    published_date = self._parse_date(time_elem.get_text(strip=True) if time_elem else '')
                    
                    content = self._fetch_article_content(url)
                    
                    article = NewsArticle(
                        title=title,
                        url=url,
                        summary=summary,
                        content=content,
                        published_date=published_date,
                        source=config['name'],
                        category="保險新聞"
                    )
                    
                    articles.append(article)
                    logger.info(f"✅ 經濟日報: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"解析經濟日報文章失敗: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"解析經濟日報頁面失敗: {e}")
        
        return articles
    
    def _parse_chinatimes_news(self, soup: BeautifulSoup, config: Dict, max_articles: int) -> List[NewsArticle]:
        """解析中時新聞網財經新聞"""
        articles = []
        
        try:
            news_items = soup.select('.article-list li, .news-list li')[:max_articles]
            
            for item in news_items:
                try:
                    title_elem = item.select_one('h3 a, h2 a, a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = urljoin(config['base_url'], title_elem.get('href', ''))
                    
                    if not self._is_insurance_related(title):
                        continue
                    
                    summary = title[:100]  # 簡化摘要
                    published_date = datetime.now()  # 簡化時間處理
                    
                    content = self._fetch_article_content(url)
                    
                    article = NewsArticle(
                        title=title,
                        url=url,
                        summary=summary,
                        content=content,
                        published_date=published_date,
                        source=config['name'],
                        category="保險新聞"
                    )
                    
                    articles.append(article)
                    logger.info(f"✅ 中時財經: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"解析中時財經文章失敗: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"解析中時財經頁面失敗: {e}")
        
        return articles
    
    def _parse_ltn_news(self, soup: BeautifulSoup, config: Dict, max_articles: int) -> List[NewsArticle]:
        """解析自由時報財經新聞"""
        articles = []
        
        try:
            news_items = soup.select('.content li, .list li')[:max_articles]
            
            for item in news_items:
                try:
                    title_elem = item.select_one('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = urljoin(config['base_url'], title_elem.get('href', ''))
                    
                    if not self._is_insurance_related(title):
                        continue
                    
                    summary = title[:100]
                    published_date = datetime.now()
                    
                    content = self._fetch_article_content(url)
                    
                    article = NewsArticle(
                        title=title,
                        url=url,
                        summary=summary,
                        content=content,
                        published_date=published_date,
                        source=config['name'],
                        category="保險新聞"
                    )
                    
                    articles.append(article)
                    logger.info(f"✅ 自由財經: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"解析自由財經文章失敗: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"解析自由財經頁面失敗: {e}")
        
        return articles
    
    def _is_insurance_related(self, title: str) -> bool:
        """檢查標題是否與保險相關"""
        insurance_keywords = [
            '保險', '保費', '保單', '理賠', '投保', '承保',
            '壽險', '產險', '車險', '健康險', '意外險', '醫療險',
            '保險公司', '保險業', '保險法', '保險金',
            '金管會', '保險局', '保險市場', '保障',
            '南山', '國泰', '富邦', '新光', '台灣人壽',
            '中國信託', '第一金', '兆豐', '玉山'
        ]
        
        title_lower = title.lower()
        return any(keyword in title for keyword in insurance_keywords)
    
    def _fetch_article_content(self, url: str) -> str:
        """獲取文章完整內容"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 通用內容選擇器
            content_selectors = [
                '.article-content',
                '.story-body',
                '.post-content',
                '.content',
                '.article-body',
                '.news-content',
                'main article',
                '.entry-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            # 如果沒找到內容，嘗試所有p標籤
            if not content:
                paragraphs = soup.select('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
            
            # 清理內容
            content = re.sub(r'\s+', ' ', content)
            return content[:1000]  # 限制長度
            
        except Exception as e:
            logger.warning(f"獲取文章內容失敗 {url}: {e}")
            return ""
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            # 嘗試各種日期格式
            date_patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',
                r'(\d{4})/(\d{2})/(\d{2})',
                r'(\d{2})-(\d{2})-(\d{4})',
                r'(\d{2})/(\d{2})/(\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD format
                        return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                    else:  # DD-MM-YYYY format
                        return datetime(int(groups[2]), int(groups[1]), int(groups[0]))
            
            # 如果無法解析，返回當前時間
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def save_to_database(self, articles: List[NewsArticle]) -> Dict[str, Any]:
        """儲存文章到資料庫"""
        try:
            from app import create_app
            from database.models import News, NewsSource, NewsCategory, db
            from config.settings import Config
            
            app = create_app(Config)
            
            with app.app_context():
                saved_count = 0
                duplicate_count = 0
                
                for article in articles:
                    # 檢查是否已存在
                    existing = News.query.filter_by(title=article.title).first()
                    if existing:
                        duplicate_count += 1
                        continue
                    
                    # 獲取或創建新聞來源
                    source = NewsSource.query.filter_by(name=article.source).first()
                    if not source:
                        source = NewsSource(
                            name=article.source,
                            url="",
                            status='active'
                        )
                        db.session.add(source)
                        db.session.flush()
                    
                    # 獲取或創建分類
                    category = NewsCategory.query.filter_by(name=article.category).first()
                    if not category:
                        category = NewsCategory(
                            name=article.category,
                            description="保險相關新聞"
                        )
                        db.session.add(category)
                        db.session.flush()
                    
                    # 創建新聞記錄
                    news = News(
                        title=article.title,
                        content=article.content,
                        summary=article.summary,
                        url=article.url,
                        published_date=article.published_date,
                        source_id=source.id,
                        category_id=category.id,
                        status='active',
                        importance_score=0.5,
                        sentiment_score=0.0
                    )
                    
                    db.session.add(news)
                    saved_count += 1
                
                db.session.commit()
                
                result = {
                    'status': 'success',
                    'saved_count': saved_count,
                    'duplicate_count': duplicate_count,
                    'total_processed': len(articles)
                }
                
                logger.info(f"💾 資料庫儲存完成: 新增 {saved_count} 篇，重複 {duplicate_count} 篇")
                return result
                
        except Exception as e:
            logger.error(f"❌ 資料庫儲存失敗: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'saved_count': 0
            }

def main():
    """主執行函數"""
    print("🕷️ 啟動多來源新聞爬蟲系統...")
    
    crawler = MultiSourceNewsCrawler()
    
    # 爬取所有來源
    articles = crawler.crawl_all_sources(max_articles_per_source=5)
    
    if articles:
        print(f"\n📰 成功爬取 {len(articles)} 篇保險相關新聞:")
        for i, article in enumerate(articles, 1):
            print(f"{i}. [{article.source}] {article.title[:60]}...")
        
        # 儲存到資料庫
        print("\n💾 正在儲存到資料庫...")
        result = crawler.save_to_database(articles)
        
        print(f"\n📊 儲存結果:")
        print(f"  狀態: {result['status']}")
        print(f"  新增: {result.get('saved_count', 0)} 篇")
        print(f"  重複: {result.get('duplicate_count', 0)} 篇")
        
    else:
        print("⚠️ 未能獲取到任何新聞文章")

if __name__ == "__main__":
    main()
