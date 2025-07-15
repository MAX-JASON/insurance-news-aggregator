"""
RSS新聞爬蟲
RSS News Crawler

通過RSS feed獲取保險相關新聞
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger('crawler.rss')

class RSSNewsCrawler:
    """RSS新聞爬蟲"""
    
    def __init__(self):
        self.rss_feeds = [
            {
                'name': '經濟日報 - 保險',
                'url': 'https://money.udn.com/rssfeed/news/1001/5636?ch=money',
                'source_id': 2
            },
            {
                'name': '工商時報 - 保險',
                'url': 'https://ctee.com.tw/feed',
                'source_id': 1  
            }
        ]
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def crawl_all_feeds(self) -> List[Dict[str, Any]]:
        """爬取所有RSS feeds"""
        all_news = []
        
        for feed_info in self.rss_feeds:
            try:
                logger.info(f"🔍 正在爬取 {feed_info['name']} RSS...")
                news_list = self.crawl_rss_feed(feed_info)
                all_news.extend(news_list)
                logger.info(f"✅ {feed_info['name']} 爬取到 {len(news_list)} 則新聞")
            except Exception as e:
                logger.error(f"❌ 爬取 {feed_info['name']} 失敗: {e}")
        
        return all_news
    
    def crawl_rss_feed(self, feed_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """爬取單個RSS feed"""
        try:
            # 解析RSS
            feed = feedparser.parse(feed_info['url'])
            
            if feed.bozo:
                logger.warning(f"⚠️ RSS解析有警告: {feed.bozo_exception}")
            
            news_list = []
            
            for entry in feed.entries[:20]:  # 限制最多20則新聞
                try:
                    # 檢查是否與保險相關
                    title = entry.get('title', '')
                    if not self._is_insurance_related(title):
                        continue
                    
                    # 提取新聞數據
                    news_item = {
                        'title': title,
                        'url': entry.get('link', ''),
                        'summary': self._clean_summary(entry.get('summary', '')),
                        'published_date': self._parse_date(entry),
                        'source': feed_info['name'],
                        'source_id': feed_info['source_id'],
                        'author': entry.get('author', ''),
                        'tags': self._extract_tags(entry)
                    }
                    
                    # 獲取完整內容
                    if news_item['url']:
                        content = self.get_article_content(news_item['url'])
                        news_item['content'] = content
                    
                    news_list.append(news_item)
                    
                except Exception as e:
                    logger.debug(f"⚠️ 處理RSS條目失敗: {e}")
                    continue
            
            return news_list
            
        except Exception as e:
            logger.error(f"❌ 爬取RSS feed失敗: {e}")
            return []
    
    def _is_insurance_related(self, title: str) -> bool:
        """檢查標題是否與保險相關"""
        insurance_keywords = [
            '保險', '保費', '保單', '理賠', '投保', '承保', '保障',
            '壽險', '產險', '健康險', '意外險', '醫療險', '癌症險',
            '金管會', '保險公司', '保險業', '保險法', '保險金',
            '年金', '退休金', '退休規劃', '保險科技', 'Insurtech'
        ]
        
        return any(keyword in title for keyword in insurance_keywords)
    
    def _clean_summary(self, summary: str) -> str:
        """清理摘要文本"""
        if not summary:
            return ""
        
        # 移除HTML標籤
        soup = BeautifulSoup(summary, 'html.parser')
        text = soup.get_text(strip=True)
        
        # 限制長度
        return text[:300] if text else ""
    
    def _parse_date(self, entry) -> datetime:
        """解析發布日期"""
        try:
            # 嘗試多種日期格式
            date_fields = ['published_parsed', 'updated_parsed']
            
            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    parsed_time = getattr(entry, field)
                    return datetime(*parsed_time[:6], tzinfo=timezone.utc)
            
            # 如果沒有找到，使用當前時間
            return datetime.now(timezone.utc)
            
        except Exception:
            return datetime.now(timezone.utc)
    
    def _extract_tags(self, entry) -> str:
        """提取標籤"""
        tags = []
        
        try:
            if hasattr(entry, 'tags'):
                tags.extend([tag.term for tag in entry.tags])
            
            # 從分類中提取
            if hasattr(entry, 'category'):
                tags.append(entry.category)
            
            return ','.join(tags[:5])  # 限制最多5個標籤
            
        except Exception:
            return ""
    
    def get_article_content(self, url: str) -> Optional[str]:
        """獲取文章完整內容"""
        try:
            if not url:
                return None
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除不需要的元素
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # 尋找文章內容的多種選擇器
            content_selectors = [
                'article',
                '[role="main"]',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content-body',
                '.story-body',
                '#article-content',
                '.article-body'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 提取段落文本
                    paragraphs = content_elem.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 10])
                        break
            
            # 如果還是沒找到，嘗試提取所有段落
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            return content[:3000] if content else None  # 限制內容長度
            
        except Exception as e:
            logger.debug(f"❌ 獲取文章內容失敗 {url}: {e}")
            return None

def test_rss_crawler():
    """測試RSS爬蟲"""
    crawler = RSSNewsCrawler()
    
    print("🧪 測試RSS新聞爬蟲...")
    news_list = crawler.crawl_all_feeds()
    
    if news_list:
        print(f"✅ 成功爬取 {len(news_list)} 則保險相關新聞")
        for i, news in enumerate(news_list[:3], 1):
            print(f"\n📰 新聞 {i}:")
            print(f"標題: {news['title']}")
            print(f"來源: {news['source']}")
            print(f"網址: {news['url']}")
            print(f"摘要: {news['summary'][:100]}...")
            if news.get('content'):
                print(f"內容: {news['content'][:150]}...")
    else:
        print("❌ 沒有爬取到任何新聞")

if __name__ == "__main__":
    test_rss_crawler()
