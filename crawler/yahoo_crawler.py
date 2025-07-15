"""
Yahoo新聞保險版爬蟲
Yahoo News Insurance Crawler

專門爬取Yahoo新聞的保險相關內容
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urljoin, urlparse
import time
import random

logger = logging.getLogger('crawler.yahoo')

class YahooInsuranceCrawler:
    """Yahoo新聞保險版爬蟲"""
    
    def __init__(self):
        self.base_url = "https://tw.news.yahoo.com"
        self.search_url = "https://tw.news.yahoo.com/tag/保險"
        self.session = requests.Session()
        
        # 設置User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def crawl_news_list(self, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        爬取新聞列表
        
        Args:
            max_pages: 最大頁數
            
        Returns:
            新聞列表
        """
        news_list = []
        
        try:
            logger.info(f"🔍 開始爬取Yahoo保險新聞，最大頁數: {max_pages}")
            
            for page in range(1, max_pages + 1):
                logger.info(f"📄 正在爬取第 {page} 頁...")
                
                # 構建URL (Yahoo新聞的分頁機制)
                if page == 1:
                    url = self.search_url
                else:
                    url = f"{self.search_url}?offset={(page-1)*10}"
                
                # 發送請求
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 解析HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 尋找新聞項目
                news_items = self._parse_news_items(soup)
                
                if not news_items:
                    logger.warning(f"⚠️ 第 {page} 頁沒有找到新聞項目")
                    break
                
                news_list.extend(news_items)
                logger.info(f"✅ 第 {page} 頁找到 {len(news_items)} 則新聞")
                
                # 隨機延遲
                time.sleep(random.uniform(2, 4))
            
            logger.info(f"🎉 總共爬取到 {len(news_list)} 則新聞")
            return news_list
            
        except Exception as e:
            logger.error(f"❌ 爬取Yahoo新聞失敗: {e}")
            return []
    
    def _parse_news_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """解析新聞項目"""
        news_items = []
        
        try:
            # Yahoo新聞的結構可能會變化，這裡提供一個基本的解析邏輯
            # 尋找可能的新聞容器
            containers = soup.find_all(['div', 'article'], class_=re.compile(r'(story|news|item|card)', re.I))
            
            for container in containers[:20]:  # 限制每頁最多20則
                try:
                    news_item = self._extract_news_data(container)
                    if news_item and self._is_insurance_related(news_item['title']):
                        news_items.append(news_item)
                except Exception as e:
                    logger.debug(f"⚠️ 解析單則新聞失敗: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ 解析新聞項目失敗: {e}")
        
        return news_items
    
    def _extract_news_data(self, container) -> Optional[Dict[str, Any]]:
        """從容器中提取新聞數據"""
        try:
            # 尋找標題
            title_elem = container.find(['h1', 'h2', 'h3', 'h4'], string=re.compile(r'.+'))
            if not title_elem:
                title_elem = container.find('a', string=re.compile(r'.+'))
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if len(title) < 10:  # 標題太短可能不是真正的新聞
                return None
            
            # 尋找連結
            link_elem = title_elem.find_parent('a') or title_elem if title_elem.name == 'a' else container.find('a')
            url = ""
            if link_elem and link_elem.get('href'):
                url = urljoin(self.base_url, link_elem['href'])
            
            # 尋找摘要
            summary = ""
            summary_elem = container.find(['p', 'div'], string=re.compile(r'.+'))
            if summary_elem:
                summary = summary_elem.get_text(strip=True)[:200]
            
            # 尋找時間
            published_date = self._extract_date(container)
            
            return {
                'title': title,
                'url': url,
                'summary': summary,
                'published_date': published_date,
                'source': 'Yahoo新聞',
                'raw_html': str(container)
            }
            
        except Exception as e:
            logger.debug(f"提取新聞數據失敗: {e}")
            return None
    
    def _extract_date(self, container) -> Optional[datetime]:
        """提取發布時間"""
        try:
            # 尋找時間相關的元素
            date_patterns = [
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
                r'(\d+)\s*小時前',
                r'(\d+)\s*分鐘前',
                r'今天',
                r'昨天'
            ]
            
            # 在容器文本中搜索日期
            text = container.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    # 這裡可以添加更複雜的日期解析邏輯
                    return datetime.now(timezone.utc)
            
            return datetime.now(timezone.utc)
            
        except Exception:
            return datetime.now(timezone.utc)
    
    def _is_insurance_related(self, title: str) -> bool:
        """檢查標題是否與保險相關"""
        insurance_keywords = [
            '保險', '保費', '保單', '理賠', '投保', '承保',
            '壽險', '產險', '健康險', '意外險', '醫療險',
            '金管會', '保險公司', '保險業', '保障',
            '年金', '退休金', '保險金'
        ]
        
        return any(keyword in title for keyword in insurance_keywords)
    
    def get_article_content(self, url: str) -> Optional[str]:
        """獲取文章完整內容"""
        try:
            if not url:
                return None
                
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尋找文章內容
            content_selectors = [
                'div[data-type="story-body"]',
                '.story-body',
                '.article-body',
                '.content-body',
                'article',
                '.post-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            # 如果沒找到特定容器，嘗試提取主要段落
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            return content[:2000] if content else None  # 限制內容長度
            
        except Exception as e:
            logger.error(f"❌ 獲取文章內容失敗 {url}: {e}")
            return None

def test_yahoo_crawler():
    """測試Yahoo爬蟲"""
    crawler = YahooInsuranceCrawler()
    
    print("🧪 測試Yahoo保險新聞爬蟲...")
    news_list = crawler.crawl_news_list(max_pages=1)
    
    if news_list:
        print(f"✅ 成功爬取 {len(news_list)} 則新聞")
        for i, news in enumerate(news_list[:3], 1):
            print(f"\n📰 新聞 {i}:")
            print(f"標題: {news['title']}")
            print(f"網址: {news['url']}")
            print(f"摘要: {news['summary'][:100]}...")
            
            # 測試獲取完整內容
            if news['url']:
                content = crawler.get_article_content(news['url'])
                if content:
                    print(f"內容: {content[:150]}...")
    else:
        print("❌ 沒有爬取到任何新聞")

if __name__ == "__main__":
    test_yahoo_crawler()
