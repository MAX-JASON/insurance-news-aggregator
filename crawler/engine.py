"""
爬蟲引擎核心模組
Crawler Engine Core Module

提供通用的網頁爬蟲功能
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timezone

# 設置日誌
logger = logging.getLogger('crawler')

class CrawlerEngine:
    """通用爬蟲引擎"""
    
    def __init__(self, delay_range: tuple = (1, 3), timeout: int = 30):
        """
        初始化爬蟲引擎
        
        Args:
            delay_range: 請求間隔範圍(秒)
            timeout: 請求超時時間(秒)
        """
        self.ua = UserAgent()
        self.session = requests.Session()
        self.delay_range = delay_range
        self.timeout = timeout
        self.last_request_time = 0
        
        # 設置默認 headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _wait_for_delay(self):
        """實現請求延遲"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        delay = random.uniform(*self.delay_range)
        
        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.debug(f"等待 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_random_user_agent(self) -> str:
        """獲取隨機 User-Agent"""
        try:
            return self.ua.random
        except Exception:
            # 備用 User-Agent
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def fetch_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        獲取網頁內容
        
        Args:
            url: 目標網址
            **kwargs: 額外的 requests 參數
            
        Returns:
            Response 物件或 None
        """
        self._wait_for_delay()
        
        # 設置隨機 User-Agent
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = self._get_random_user_agent()
        kwargs['headers'] = headers
        
        # 設置超時
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            logger.info(f"正在抓取: {url}")
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            logger.info(f"抓取成功: {url} (狀態碼: {response.status_code})")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"抓取失敗: {url} - {str(e)}")
            return None
    
    def parse_html(self, html_content: str, parser: str = 'lxml') -> BeautifulSoup:
        """
        解析 HTML 內容
        
        Args:
            html_content: HTML 內容
            parser: 解析器類型
            
        Returns:
            BeautifulSoup 物件
        """
        return BeautifulSoup(html_content, parser)
    
    def extract_links(self, soup: BeautifulSoup, base_url: str, 
                     selector: str = 'a[href]') -> List[str]:
        """
        提取連結
        
        Args:
            soup: BeautifulSoup 物件
            base_url: 基礎網址
            selector: CSS 選擇器
            
        Returns:
            連結列表
        """
        links = []
        for link in soup.select(selector):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                links.append(full_url)
        return list(set(links))  # 去重
    
    def crawl_page(self, url: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        爬取單個頁面
        
        Args:
            url: 目標網址
            config: 爬蟲配置
            
        Returns:
            提取的數據字典
        """
        response = self.fetch_page(url)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'crawled_at': datetime.now(timezone.utc).isoformat(),
            'data': {}
        }
        
        # 根據配置提取數據
        for field, selector in config.get('selectors', {}).items():
            try:
                if isinstance(selector, str):
                    # 簡單選擇器
                    element = soup.select_one(selector)
                    if element:
                        result['data'][field] = element.get_text(strip=True)
                elif isinstance(selector, dict):
                    # 複雜選擇器配置
                    element = soup.select_one(selector['selector'])
                    if element:
                        if selector.get('attr'):
                            result['data'][field] = element.get(selector['attr'])
                        else:
                            result['data'][field] = element.get_text(strip=True)
            except Exception as e:
                logger.warning(f"提取字段 {field} 失敗: {str(e)}")
                result['data'][field] = None
        
        return result


class NewsSourceCrawler:
    """新聞來源專用爬蟲"""
    
    def __init__(self, source_config: Dict[str, Any]):
        """
        初始化新聞來源爬蟲
        
        Args:
            source_config: 新聞來源配置
        """
        self.config = source_config
        self.engine = CrawlerEngine()
        self.source_name = source_config.get('name', 'Unknown')
    
    def crawl_news_list(self, list_url: str) -> List[Dict[str, Any]]:
        """
        爬取新聞列表頁
        
        Args:
            list_url: 新聞列表頁網址
            
        Returns:
            新聞項目列表
        """
        logger.info(f"正在爬取 {self.source_name} 新聞列表: {list_url}")
        
        response = self.engine.fetch_page(list_url)
        if not response:
            return []
        
        soup = self.engine.parse_html(response.text)
        news_items = []
        
        # 獲取新聞項目選擇器
        item_selector = self.config.get('list_item_selector', '.news-item')
        
        for item in soup.select(item_selector):
            try:
                news_item = self._extract_news_item(item, list_url)
                if news_item:
                    news_items.append(news_item)
            except Exception as e:
                logger.warning(f"提取新聞項目失敗: {str(e)}")
                continue
        
        logger.info(f"從 {self.source_name} 提取了 {len(news_items)} 則新聞")
        return news_items
    
    def _extract_news_item(self, item_element, base_url: str) -> Optional[Dict[str, Any]]:
        """
        從新聞項目元素提取數據
        
        Args:
            item_element: 新聞項目 BeautifulSoup 元素
            base_url: 基礎網址
            
        Returns:
            新聞數據字典
        """
        selectors = self.config.get('item_selectors', {})
        
        news_data = {
            'source': self.source_name,
            'crawled_at': datetime.now(timezone.utc).isoformat()
        }
        
        # 標題
        title_selector = selectors.get('title', 'h3, .title')
        title_elem = item_element.select_one(title_selector)
        if title_elem:
            news_data['title'] = title_elem.get_text(strip=True)
        
        # 連結
        link_selector = selectors.get('link', 'a')
        link_elem = item_element.select_one(link_selector)
        if link_elem:
            href = link_elem.get('href')
            if href:
                news_data['url'] = urljoin(base_url, href)
        
        # 摘要
        summary_selector = selectors.get('summary', '.summary, .excerpt')
        summary_elem = item_element.select_one(summary_selector)
        if summary_elem:
            news_data['summary'] = summary_elem.get_text(strip=True)
        
        # 發布時間
        date_selector = selectors.get('date', '.date, .time')
        date_elem = item_element.select_one(date_selector)
        if date_elem:
            news_data['published_date'] = date_elem.get_text(strip=True)
        
        # 分類
        category_selector = selectors.get('category', '.category, .tag')
        category_elem = item_element.select_one(category_selector)
        if category_elem:
            news_data['category'] = category_elem.get_text(strip=True)
        
        return news_data if news_data.get('title') and news_data.get('url') else None
    
    def crawl_news_detail(self, news_url: str) -> Optional[Dict[str, Any]]:
        """
        爬取新聞詳情頁
        
        Args:
            news_url: 新聞詳情頁網址
            
        Returns:
            新聞詳情數據
        """
        logger.info(f"正在爬取 {self.source_name} 新聞詳情: {news_url}")
        
        config = {
            'selectors': self.config.get('detail_selectors', {
                'title': 'h1, .article-title',
                'content': '.article-content, .content, .post-content',
                'date': '.date, .publish-time',
                'author': '.author, .writer'
            })
        }
        
        return self.engine.crawl_page(news_url, config)


# 預定義的新聞來源配置
NEWS_SOURCES_CONFIG = {
    'insurance_cloud': {
        'name': '保險雲世代',
        'base_url': 'https://www.insurance-cloud.com.tw',
        'list_urls': [
            'https://www.insurance-cloud.com.tw/news',
            'https://www.insurance-cloud.com.tw/industry'
        ],
        'list_item_selector': '.news-list li, .article-item',
        'item_selectors': {
            'title': '.title a, h3 a',
            'link': '.title a, h3 a',
            'summary': '.summary, .excerpt',
            'date': '.date, .time',
            'category': '.category'
        },
        'detail_selectors': {
            'title': 'h1.article-title, .post-title h1',
            'content': '.article-content, .post-content',
            'date': '.publish-time, .article-date',
            'author': '.author-name, .writer'
        }
    },
    'modern_insurance': {
        'name': '現代保險',
        'base_url': 'https://www.rmim.com.tw',
        'list_urls': [
            'https://www.rmim.com.tw/news'
        ],
        'list_item_selector': '.news-item, .article-list li',
        'item_selectors': {
            'title': '.news-title a, h4 a',
            'link': '.news-title a, h4 a',
            'summary': '.news-summary',
            'date': '.news-date',
            'category': '.news-category'
        },
        'detail_selectors': {
            'title': 'h1.news-title',
            'content': '.news-content',
            'date': '.news-date',
            'author': '.news-author'
        }
    }
}


def get_crawler_for_source(source_name: str) -> Optional[NewsSourceCrawler]:
    """
    獲取指定來源的爬蟲實例
    
    Args:
        source_name: 新聞來源名稱
        
    Returns:
        爬蟲實例或 None
    """
    config = NEWS_SOURCES_CONFIG.get(source_name)
    if config:
        return NewsSourceCrawler(config)
    return None


if __name__ == "__main__":
    # 測試爬蟲功能
    logging.basicConfig(level=logging.INFO)
    
    # 測試保險雲世代爬蟲
    crawler = get_crawler_for_source('insurance_cloud')
    if crawler:
        # 這裡可以添加測試代碼
        print("爬蟲引擎初始化成功")
    else:
        print("找不到指定的新聞來源配置")
