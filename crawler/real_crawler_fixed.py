"""
真實新聞爬蟲實作
Real News Crawler Implementation

實作能夠抓取真實保險新聞的爬蟲
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
import time
import random
import re
import urllib.parse
import feedparser

logger = logging.getLogger('crawler.real')

class RealInsuranceNewsCrawler:
    """真實保險新聞爬蟲"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def crawl_google_news(self) -> List[Dict[str, Any]]:
        """搜索Google新聞中的保險相關內容"""
        news_list = []
        
        try:
            print("🔍 正在搜索Google新聞保險內容...")
            
            # 使用Google新聞搜索 - 修復URL編碼問題
            search_query = "台灣保險"
            encoded_query = urllib.parse.quote(search_query)
            search_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            # 嘗試RSS方式
            feed = feedparser.parse(search_url)
            
            if not feed.bozo and hasattr(feed, 'entries'):
                for entry in feed.entries[:8]:  # 限制8則新聞
                    try:
                        title = entry.get('title', '')
                        if not self._is_insurance_related(title):
                            continue
                        
                        news_item = {
                            'title': title,
                            'url': entry.get('link', ''),
                            'summary': entry.get('summary', '')[:200],
                            'published_date': self._parse_feed_date(entry),
                            'source': 'Google新聞',
                            'content': ''
                        }
                        
                        news_list.append(news_item)
                        print(f"  ✅ 找到Google新聞: {title[:30]}...")
                        
                    except Exception as e:
                        logger.debug(f"處理Google新聞項目失敗: {e}")
                        continue
            
            print(f"✅ Google新聞共找到 {len(news_list)} 則保險新聞")
            return news_list
            
        except Exception as e:
            print(f"❌ 搜索Google新聞失敗: {e}")
            return []
    
    def crawl_udn_finance(self) -> List[Dict[str, Any]]:
        """爬取聯合新聞網經濟日報財經新聞"""
        news_list = []
        
        try:
            print("🔍 正在爬取聯合新聞網經濟日報...")
            url = "https://udn.com/news/cate/2/6644"  # 經濟日報金融要聞
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尋找新聞項目
            news_items = soup.find_all(['div', 'li'], class_=['story-list__item', 'titleicon', 'story-headline'])
            
            for item in news_items[:15]:
                try:
                    # 提取標題和連結
                    title_elem = item.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    
                    if title_elem.name == 'a':
                        link_elem = title_elem
                        title = title_elem.get_text(strip=True)
                    else:
                        link_elem = title_elem.find('a')
                        if not link_elem:
                            continue
                        title = link_elem.get_text(strip=True)
                    
                    url = link_elem.get('href', '')
                    
                    # 只處理保險相關新聞
                    if not self._is_insurance_related(title):
                        continue
                    
                    # 確保URL是完整的
                    if url.startswith('/'):
                        url = 'https://udn.com' + url
                    
                    news_item = {
                        'title': title,
                        'url': url,
                        'summary': '',
                        'published_date': datetime.now(timezone.utc),
                        'source': '聯合新聞網',
                        'content': ''
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✅ 找到保險新聞: {title[:30]}...")
                    
                    # 延遲避免過快請求
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.debug(f"處理聯合新聞網項目失敗: {e}")
                    continue
            
            print(f"✅ 聯合新聞網共找到 {len(news_list)} 則保險新聞")
            return news_list
            
        except Exception as e:
            print(f"❌ 爬取聯合新聞網失敗: {e}")
            return []
    
    def crawl_ltn_finance(self) -> List[Dict[str, Any]]:
        """爬取自由時報財經新聞"""
        news_list = []
        
        try:
            print("🔍 正在爬取自由時報財經新聞...")
            url = "https://ec.ltn.com.tw/list/finance"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 更新選擇器來匹配自由時報的結構
            news_items = soup.find_all(['div', 'li'], class_=['tit', 'boxTitle', 'listItem'])
            
            for item in news_items[:15]:  # 增加檢查數量
                try:
                    # 提取標題和連結
                    title_elem = item.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    
                    # 如果是連結直接取用，否則找連結
                    if title_elem.name == 'a':
                        link_elem = title_elem
                        title = title_elem.get_text(strip=True)
                    else:
                        link_elem = title_elem.find('a')
                        if not link_elem:
                            continue
                        title = link_elem.get_text(strip=True)
                    
                    url = link_elem.get('href', '')
                    
                    # 只處理保險相關新聞
                    if not self._is_insurance_related(title):
                        continue
                    
                    # 確保URL是完整的
                    if url.startswith('/'):
                        url = 'https://ec.ltn.com.tw' + url
                    
                    news_item = {
                        'title': title,
                        'url': url,
                        'summary': '',
                        'published_date': datetime.now(timezone.utc),
                        'source': '自由時報財經',
                        'content': ''
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✅ 找到保險新聞: {title[:30]}...")
                    
                    # 延遲避免過快請求
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.debug(f"處理自由時報新聞項目失敗: {e}")
                    continue
            
            print(f"✅ 自由時報共找到 {len(news_list)} 則保險新聞")
            return news_list
            
        except Exception as e:
            print(f"❌ 爬取自由時報失敗: {e}")
            return []
    
    def _is_insurance_related(self, title: str) -> bool:
        """檢查標題是否與保險相關"""
        insurance_keywords = [
            '保險', '保費', '保單', '理賠', '投保', '承保', '保障',
            '壽險', '產險', '健康險', '意外險', '醫療險', '癌症險',
            '保險公司', '保險業', '金管會', '金融', '理財',
            '退休金', '年金', '儲蓄險', '投資型保單'
        ]
        
        title_lower = title.lower()
        return any(keyword in title for keyword in insurance_keywords)
    
    def _parse_feed_date(self, entry) -> datetime:
        """解析RSS feed的日期"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except:
            pass
        return datetime.now(timezone.utc)
    
    def crawl_all_sources(self) -> List[Dict[str, Any]]:
        """爬取所有來源的新聞"""
        all_news = []
        
        print("🚀 開始爬取真實保險新聞...")
        
        # 爬取各種來源
        crawlers = [
            ('Google新聞', self.crawl_google_news),
            ('聯合新聞網', self.crawl_udn_finance),
            ('自由時報', self.crawl_ltn_finance),
        ]
        
        for name, crawler in crawlers:
            try:
                print(f"\n📡 爬取來源: {name}")
                news_list = crawler()
                all_news.extend(news_list)
                print(f"✅ {name} 完成，獲得 {len(news_list)} 則新聞")
                time.sleep(random.uniform(3, 5))  # 來源間延遲
            except Exception as e:
                print(f"❌ 爬蟲 {name} 執行失敗: {e}")
                continue
        
        # 去重
        unique_news = []
        seen_titles = set()
        
        for news in all_news:
            title_key = news['title'][:50]  # 使用前50字符作為去重標準
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        print(f"\n🎉 總共爬取到 {len(unique_news)} 則獨特的保險新聞")
        return unique_news

def test_real_crawler():
    """測試真實爬蟲"""
    crawler = RealInsuranceNewsCrawler()
    
    print("🧪 測試真實保險新聞爬蟲...")
    news_list = crawler.crawl_all_sources()
    
    if news_list:
        print(f"\n✅ 成功爬取 {len(news_list)} 則真實新聞:")
        for i, news in enumerate(news_list[:5], 1):
            print(f"\n📰 新聞 {i}:")
            print(f"標題: {news['title']}")
            print(f"來源: {news['source']}")
            print(f"網址: {news['url']}")
            if news['summary']:
                print(f"摘要: {news['summary'][:100]}...")
    else:
        print("❌ 沒有成功爬取到任何真實新聞")
    
    return news_list

if __name__ == "__main__":
    test_real_crawler()
