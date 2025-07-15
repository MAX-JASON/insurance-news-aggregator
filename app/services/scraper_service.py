"""
爬蟲服務模組
Scraper Service Module

負責管理和執行新聞爬蟲任務
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import yaml
import time
import random
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class ScraperService:
    """新聞爬蟲服務類"""
    
    def __init__(self, config_path: str = "config/sources.yaml"):
        """
        初始化爬蟲服務
        
        Args:
            config_path: 新聞來源配置檔案路徑
        """
        self.config_path = config_path
        self.sources = self._load_sources()
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
    def _load_sources(self) -> List[Dict]:
        """
        載入新聞來源配置
        
        Returns:
            新聞來源列表
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('sources', [])
        except FileNotFoundError:
            logger.warning(f"Sources config file not found: {self.config_path}")
            return self._get_default_sources()
    
    def _get_default_sources(self) -> List[Dict]:
        """
        獲取預設新聞來源
        
        Returns:
            預設新聞來源列表
        """
        return [
            {
                "name": "工商時報保險",
                "url": "https://www.chinatimes.com/money/insurance",
                "selector": ".article-list article",
                "title_selector": "h3",
                "link_selector": "a",
                "category": "insurance"
            },
            {
                "name": "經濟日報保險",
                "url": "https://money.udn.com/money/story/5617",
                "selector": ".story-list__item",
                "title_selector": ".story-list__title",
                "link_selector": "a",
                "category": "insurance"
            }
        ]
    
    async def create_session(self):
        """創建 HTTP 會話"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """關閉 HTTP 會話"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_random_user_agent(self) -> str:
        """獲取隨機 User-Agent"""
        return random.choice(self.user_agents)
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        獲取網頁內容
        
        Args:
            url: 網頁URL
            
        Returns:
            網頁HTML內容
        """
        try:
            headers = {"User-Agent": self.get_random_user_agent()}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def parse_articles(self, html: str, source: Dict) -> List[Dict]:
        """
        解析文章列表
        
        Args:
            html: 網頁HTML內容
            source: 新聞來源配置
            
        Returns:
            文章列表
        """
        articles = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            article_elements = soup.select(source['selector'])
            
            for element in article_elements:
                try:
                    # 提取標題
                    title_elem = element.select_one(source['title_selector'])
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # 提取連結
                    link_elem = element.select_one(source['link_selector'])
                    if link_elem:
                        link = link_elem.get('href', '')
                        if link and not link.startswith('http'):
                            link = urljoin(source['url'], link)
                    else:
                        link = ""
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'url': link,
                            'source': source['name'],
                            'category': source.get('category', 'general'),
                            'scraped_at': datetime.utcnow().isoformat()
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing article element: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
        
        return articles
    
    async def scrape_source(self, source: Dict) -> List[Dict]:
        """
        爬取單個新聞來源
        
        Args:
            source: 新聞來源配置
            
        Returns:
            文章列表
        """
        logger.info(f"Scraping source: {source['name']}")
        
        html = await self.fetch_page(source['url'])
        if not html:
            return []
        
        articles = self.parse_articles(html, source)
        logger.info(f"Found {len(articles)} articles from {source['name']}")
        
        return articles
    
    async def scrape_all_sources(self) -> List[Dict]:
        """
        爬取所有新聞來源
        
        Returns:
            所有文章列表
        """
        await self.create_session()
        
        all_articles = []
        
        try:
            for source in self.sources:
                articles = await self.scrape_source(source)
                all_articles.extend(articles)
                
                # 添加延遲避免被封鎖
                await asyncio.sleep(random.uniform(1, 3))
                
        finally:
            await self.close_session()
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles
    
    def filter_articles(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        根據關鍵字過濾文章
        
        Args:
            articles: 文章列表
            keywords: 關鍵字列表
            
        Returns:
            過濾後的文章列表
        """
        filtered_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            
            # 檢查是否包含關鍵字
            if any(keyword.lower() in title for keyword in keywords):
                filtered_articles.append(article)
        
        return filtered_articles
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        去除重複文章
        
        Args:
            articles: 文章列表
            
        Returns:
            去重後的文章列表
        """
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            title = article.get('title', '')
            
            if url not in seen_urls and title not in seen_titles:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles

# 全域爬蟲服務實例
scraper_service = ScraperService()
