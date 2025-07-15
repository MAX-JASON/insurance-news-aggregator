"""
工商時報保險版爬蟲
Commercial Times Insurance Section Crawler

專門爬取工商時報保險相關新聞
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup

from crawler.engine import CrawlerEngine, NewsSourceCrawler

logger = logging.getLogger('crawler')

class CTeeInsuranceCrawler:
    """工商時報保險版爬蟲"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.engine = CrawlerEngine(delay_range=(2, 4))  # 較長延遲，避免被封
        self.base_url = 'https://ctee.com.tw'
        self.category_url = 'https://ctee.com.tw/category/insurance'  # 保險版塊
        self.source_name = '工商時報'
    
    def crawl_list(self, pages: int = 3) -> List[Dict[str, Any]]:
        """
        爬取新聞列表
        
        Args:
            pages: 爬取的頁數
            
        Returns:
            新聞列表
        """
        all_news = []
        
        for page in range(1, pages + 1):
            try:
                url = f"{self.category_url}/page/{page}"
                logger.info(f"正在爬取工商時報保險版第 {page} 頁: {url}")
                
                response = self.engine.fetch_page(url)
                if not response:
                    logger.warning(f"無法獲取第 {page} 頁列表")
                    continue
                
                soup = self.engine.parse_html(response.text)
                
                # 文章列表
                articles = soup.select('article.post')
                
                if not articles:
                    logger.warning(f"未在第 {page} 頁找到文章")
                    break
                    
                for article in articles:
                    try:
                        news_item = self._extract_list_item(article)
                        if news_item:
                            all_news.append(news_item)
                    except Exception as e:
                        logger.error(f"提取文章信息時出錯: {e}")
                        continue
                
                logger.info(f"成功從第 {page} 頁提取了 {len(articles)} 篇文章")
                
            except Exception as e:
                logger.error(f"爬取第 {page} 頁時發生錯誤: {e}")
                continue
        
        logger.info(f"工商時報保險版共爬取 {len(all_news)} 篇文章")
        return all_news
    
    def _extract_list_item(self, article) -> Optional[Dict[str, Any]]:
        """
        從文章元素中提取信息
        
        Args:
            article: 文章元素
            
        Returns:
            新聞字典
        """
        # 獲取標題和連結
        title_elem = article.select_one('.entry-title a')
        if not title_elem:
            return None
            
        title = title_elem.get_text(strip=True)
        url = title_elem.get('href', '')
        
        if not title or not url:
            return None
        
        # 獲取發布時間
        date_elem = article.select_one('.posted-date')
        published_date = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            try:
                # 處理日期格式，通常為 "2025-07-03"
                published_date = datetime.strptime(date_text, '%Y-%m-%d')
            except Exception as e:
                logger.warning(f"日期解析失敗: {date_text}, {e}")
        
        # 獲取摘要
        summary_elem = article.select_one('.entry-content')
        summary = ''
        if summary_elem:
            summary = summary_elem.get_text(strip=True)
            # 限制摘要長度
            summary = summary[:200] + '...' if len(summary) > 200 else summary
        
        # 獲取圖片
        thumbnail = ''
        img_elem = article.select_one('.wp-post-image')
        if img_elem:
            thumbnail = img_elem.get('src', '')
        
        # 獲取類別
        category = '保險'
        category_elem = article.select_one('.cat-links a')
        if category_elem:
            category = category_elem.get_text(strip=True)
        
        return {
            'title': title,
            'url': url,
            'source': self.source_name,
            'category': category,
            'published_date': published_date,
            'summary': summary,
            'thumbnail': thumbnail,
            'crawled_at': datetime.now()
        }
    
    def crawl_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """
        爬取新聞詳情
        
        Args:
            url: 新聞URL
            
        Returns:
            詳情字典
        """
        logger.info(f"正在爬取工商時報文章: {url}")
        
        try:
            response = self.engine.fetch_page(url)
            if not response:
                logger.warning(f"無法獲取文章詳情: {url}")
                return None
            
            soup = self.engine.parse_html(response.text)
            
            # 獲取標題
            title_elem = soup.select_one('h1.entry-title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # 獲取發布時間
            date_elem = soup.select_one('.posted-date')
            published_date = None
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                try:
                    published_date = datetime.strptime(date_text, '%Y-%m-%d')
                except Exception as e:
                    logger.warning(f"日期解析失敗: {date_text}, {e}")
            
            # 獲取作者
            author = ''
            author_elem = soup.select_one('.author-name')
            if author_elem:
                author = author_elem.get_text(strip=True)
            
            # 獲取內容
            content_elem = soup.select_one('.entry-content')
            content = ''
            if content_elem:
                # 移除不需要的元素
                for elem in content_elem.select('.sharedaddy, .jp-relatedposts, script, .ads-area'):
                    elem.decompose()
                
                # 獲取純文本
                paragraphs = content_elem.select('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            
            # 獲取關鍵詞
            keywords = []
            tag_elems = soup.select('.tags-links a')
            if tag_elems:
                keywords = [tag.get_text(strip=True) for tag in tag_elems]
            
            return {
                'title': title,
                'url': url,
                'source': self.source_name,
                'author': author,
                'published_date': published_date,
                'content': content,
                'keywords': keywords,
                'crawled_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"爬取文章詳情時發生錯誤: {e}")
            return None
    
    def crawl(self, max_pages: int = 3, max_details: int = 10) -> Dict[str, Any]:
        """
        執行爬蟲
        
        Args:
            max_pages: 最大爬取頁數
            max_details: 最大爬取詳情數
            
        Returns:
            爬取結果統計
        """
        logger.info(f"開始爬取工商時報保險版新聞: 頁數={max_pages}, 詳情數={max_details}")
        
        start_time = time.time()
        
        # 爬取列表
        news_list = self.crawl_list(pages=max_pages)
        
        # 爬取詳情
        detailed_count = 0
        for i, news in enumerate(news_list[:max_details]):
            if detailed_count >= max_details:
                break
                
            try:
                detail = self.crawl_detail(news['url'])
                if detail:
                    # 更新新聞詳情
                    news.update(detail)
                    detailed_count += 1
            except Exception as e:
                logger.error(f"爬取詳情失敗: {news['url']}, {e}")
                continue
        
        duration = time.time() - start_time
        
        result = {
            'source': self.source_name,
            'total_found': len(news_list),
            'detailed': detailed_count,
            'duration': round(duration, 2),
            'timestamp': datetime.now(),
            'news': news_list
        }
        
        logger.info(f"工商時報爬蟲完成: 找到 {len(news_list)} 篇文章，獲取 {detailed_count} 篇詳情，耗時 {duration:.2f} 秒")
        
        return result


# 配置為可通過通用引擎調用的爬蟲
CTEE_SOURCE_CONFIG = {
    'name': '工商時報',
    'base_url': 'https://ctee.com.tw',
    'list_urls': [
        'https://ctee.com.tw/category/insurance'
    ],
    'list_item_selector': 'article.post',
    'item_selectors': {
        'title': '.entry-title a',
        'link': '.entry-title a',
        'summary': '.entry-content',
        'date': '.posted-date',
        'category': '.cat-links a'
    },
    'detail_selectors': {
        'title': 'h1.entry-title',
        'content': '.entry-content',
        'date': '.posted-date',
        'author': '.author-name'
    }
}


def register_ctee_crawler():
    """註冊工商時報爬蟲到通用引擎"""
    from crawler.engine import NEWS_SOURCES_CONFIG
    NEWS_SOURCES_CONFIG['ctee'] = CTEE_SOURCE_CONFIG


if __name__ == "__main__":
    # 測試爬蟲功能
    logging.basicConfig(level=logging.INFO)
    
    crawler = CTeeInsuranceCrawler()
    result = crawler.crawl(max_pages=1, max_details=3)
    
    print(f"共爬取 {len(result['news'])} 篇文章")
    for i, news in enumerate(result['news']):
        print(f"\n[{i+1}] {news['title']}")
        print(f"    日期: {news.get('published_date')}")
        print(f"    網址: {news['url']}")
        print(f"    摘要: {news.get('summary', '')[:100]}")
        if 'content' in news:
            print(f"    正文長度: {len(news['content'])} 字")
