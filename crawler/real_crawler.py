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
        
        # 可用的新聞來源
        self.sources = [
            {
                'name': '自由時報財經',
                'base_url': 'https://ec.ltn.com.tw',
                'search_url': 'https://ec.ltn.com.tw/list/finance',
                'type': 'web'
            },
            {
                'name': '工商時報',
                'base_url': 'https://www.chinatimes.com',
                'search_url': 'https://www.chinatimes.com/finance',
                'type': 'web'
            }        ]
    
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
                    
                    # 提取時間
                    time_elem = item.find('span', class_='time')
                    published_date = self._parse_date(time_elem.get_text() if time_elem else '')
                    
                    # 提取摘要
                    summary_elem = item.find('p')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    news_item = {
                        'title': title,
                        'url': url,
                        'summary': summary[:200],
                        'published_date': published_date,
                        'source': '自由時報財經',
                        'content': ''
                    }
                    
                    # 嘗試獲取完整內容
                    content = self._get_article_content(url)
                    if content:
                        news_item['content'] = content
                    
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
                    
                    # 提取時間和摘要
                    time_elem = item.find('time')
                    if not time_elem:
                        time_elem = item.find('span', class_='story-list__time')
                    
                    published_date = self._parse_date(time_elem.get_text() if time_elem else '')
                    
                    # 提取摘要
                    summary_elem = item.find('p', class_='story-list__summary')
                    if not summary_elem:
                        summary_elem = item.find('p')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    news_item = {
                        'title': title,
                        'url': url,
                        'summary': summary[:200],
                        'published_date': published_date,
                        'source': '聯合新聞網',
                        'content': ''
                    }
                    
                    # 嘗試獲取完整內容
                    content = self._get_article_content(url)
                    if content:
                        news_item['content'] = content
                    
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
    
    def crawl_yahoo_news(self) -> List[Dict[str, Any]]:
        """爬取Yahoo新聞的保險關鍵字搜索結果"""
        news_list = []
        
        try:
            print("🔍 正在搜索Yahoo新聞保險內容...")
            
            # 簡化Yahoo新聞搜索
            search_url = "https://tw.news.yahoo.com/tag/保險"
            
            response = self.session.get(search_url, timeout=15)
            if response.status_code != 200:
                print(f"Yahoo新聞回應狀態: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尋找新聞項目
            news_items = soup.find_all(['h3', 'h4', 'div'], class_=['Mb(5px)', 'title', 'StreamMegaItem'])
            
            for item in news_items[:10]:
                try:
                    # 提取標題和連結
                    title_elem = item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    # 只處理保險相關新聞
                    if not self._is_insurance_related(title):
                        continue
                    
                    # 確保URL是完整的
                    if url.startswith('/'):
                        url = 'https://tw.news.yahoo.com' + url
                    elif not url.startswith('http'):
                        continue
                    
                    news_item = {
                        'title': title,
                        'url': url,
                        'summary': '',
                        'published_date': datetime.now(timezone.utc),
                        'source': 'Yahoo新聞',
                        'content': ''
                    }
                    
                    news_list.append(news_item)
                    print(f"  ✅ 找到Yahoo新聞: {title[:30]}...")
                    
                except Exception as e:
                    logger.debug(f"處理Yahoo新聞項目失敗: {e}")
                    continue
            
            print(f"✅ Yahoo新聞共找到 {len(news_list)} 則相關新聞")
            return news_list
            
        except Exception as e:
            print(f"❌ 搜索Yahoo新聞失敗: {e}")
            return []
        """爬取Yahoo新聞的保險關鍵字搜索結果"""
        news_list = []
        
        try:
            print("🔍 正在搜索Yahoo新聞保險內容...")
            
            # Yahoo新聞搜索API或網頁
            search_keywords = ['保險', '保費', '理賠', '壽險', '產險']
            
            for keyword in search_keywords[:2]:  # 限制搜索關鍵字
                try:
                    # 使用Yahoo新聞搜索
                    search_url = f"https://tw.news.yahoo.com/tag/{keyword}"
                    
                    response = self.session.get(search_url, timeout=15)
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 尋找新聞項目（Yahoo的結構可能變化）
                    # 這裡使用通用的標籤搜索
                    potential_links = soup.find_all('a', href=True)
                    
                    for link in potential_links[:20]:
                        try:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # 過濾明顯的新聞連結
                            if (len(text) > 10 and 
                                any(word in text for word in ['保險', '保費', '理賠']) and
                                'news' in href and
                                len(text) < 100):
                                
                                # 確保URL完整
                                if href.startswith('/'):
                                    href = 'https://tw.news.yahoo.com' + href
                                elif not href.startswith('http'):
                                    continue
                                
                                news_item = {
                                    'title': text,
                                    'url': href,
                                    'summary': '',
                                    'published_date': datetime.now(timezone.utc),
                                    'source': 'Yahoo新聞',
                                    'content': ''
                                }
                                
                                # 避免重複
                                if not any(n['title'] == text for n in news_list):
                                    news_list.append(news_item)
                                    print(f"  ✅ 找到Yahoo新聞: {text[:30]}...")
                                
                                if len(news_list) >= 5:  # 限制數量
                                    break
                        except:
                            continue
                    
                    time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    logger.debug(f"搜索Yahoo關鍵字 {keyword} 失敗: {e}")
                    continue
            
            print(f"✅ Yahoo新聞共找到 {len(news_list)} 則相關新聞")
            return news_list
            
        except Exception as e:
            print(f"❌ 搜索Yahoo新聞失敗: {e}")
            return []
      def crawl_google_news(self) -> List[Dict[str, Any]]:
        """搜索Google新聞中的保險相關內容"""
        news_list = []
        
        try:
            print("🔍 正在搜索Google新聞保險內容...")
            
            # 使用Google新聞搜索 - 修復URL編碼問題
            import urllib.parse
            search_query = "台灣保險"
            encoded_query = urllib.parse.quote(search_query)
            search_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            # 嘗試RSS方式
            import feedparser
            
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
    
    def _is_insurance_related(self, title: str) -> bool:
        """檢查標題是否與保險相關"""
        insurance_keywords = [
            '保險', '保費', '保單', '理賠', '投保', '承保', '保障',
            '壽險', '產險', '健康險', '意外險', '醫療險', '癌症險',
            '金管會', '保險公司', '保險業', '保險法', '保險金',
            '年金', '退休金', '保險科技', 'Insurtech', '再保險'
        ]
        
        return any(keyword in title for keyword in insurance_keywords)
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字串"""
        try:
            # 處理常見的日期格式
            if '小時前' in date_str:
                return datetime.now(timezone.utc)
            elif '分鐘前' in date_str:
                return datetime.now(timezone.utc)
            elif '今天' in date_str or '今日' in date_str:
                return datetime.now(timezone.utc)
            elif '昨天' in date_str or '昨日' in date_str:
                return datetime.now(timezone.utc)
            else:
                return datetime.now(timezone.utc)
        except:
            return datetime.now(timezone.utc)
    
    def _parse_feed_date(self, entry) -> datetime:
        """解析RSS feed的日期"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                return datetime.now(timezone.utc)
        except:
            return datetime.now(timezone.utc)
    
    def _get_article_content(self, url: str) -> str:
        """獲取文章完整內容"""
        try:
            if not url:
                return ""
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除不需要的元素
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()
            
            # 尋找內容容器
            content_selectors = [
                'div.news_content',
                'div.article-body',
                'div.post-content',
                'article',
                '.content',
                '.newstext'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 10])
                    break
            
            # 如果沒找到，提取所有段落
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            return content[:2000] if content else ""
            
        except Exception as e:
            logger.debug(f"獲取文章內容失敗 {url}: {e}")
            return ""
      def crawl_all_sources(self) -> List[Dict[str, Any]]:
        """爬取所有來源的新聞"""
        all_news = []
        
        print("🚀 開始爬取真實保險新聞...")
        
        # 爬取各種來源
        crawlers = [
            ('Google新聞', self.crawl_google_news),
            ('聯合新聞網', self.crawl_udn_finance),
            ('自由時報', self.crawl_ltn_finance),
            ('Yahoo新聞', self.crawl_yahoo_news),
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
            if news['content']:
                print(f"內容: {news['content'][:100]}...")
    else:
        print("❌ 沒有成功爬取到任何真實新聞")
    
    return news_list

if __name__ == "__main__":
    test_real_crawler()
