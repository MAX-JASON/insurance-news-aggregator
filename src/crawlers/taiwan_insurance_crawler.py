"""
台灣保險新聞專業爬蟲引擎
Taiwan Insurance News Professional Crawler Engine

專門爬取台灣保險業相關新聞的高級爬蟲系統
"""

import os
import sys
import requests
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import re
from dataclasses import dataclass
import sqlite3

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('taiwan_insurance_crawler')

@dataclass
class NewsArticle:
    """新聞文章數據結構"""
    title: str
    content: str
    summary: str
    url: str
    source: str
    category: str
    published_date: datetime
    author: Optional[str] = None
    tags: List[str] = None
    importance_score: float = 0.0

class TaiwanInsuranceCrawler:
    """台灣保險新聞專業爬蟲"""
    
    def __init__(self):
        """初始化爬蟲"""
        
        # 台灣保險專業新聞源配置
        self.news_sources = {
            # 保險專業類
            'goodins': {
                'name': '保險雲雜誌',
                'base_url': 'https://www.goodins.life',
                'news_url': 'https://www.goodins.life/news',
                'category': '保險專業',
                'selectors': {
                    'title': '.article-title, h1, h2',
                    'content': '.article-content, .content, .post-content',
                    'summary': '.excerpt, .summary',
                    'date': '.date, .publish-time, time'
                }
            },
            'rmim': {
                'name': '保險事業發展中心',
                'base_url': 'https://www.rmim.com.tw',
                'news_url': 'https://www.rmim.com.tw/news',
                'category': '保險專業',
                'selectors': {
                    'title': '.news-title, h1',
                    'content': '.news-content, .content',
                    'date': '.news-date, .date'
                }
            },
            'lia_roc': {
                'name': '中華民國人壽保險商業同業公會',
                'base_url': 'https://www.lia-roc.org.tw',
                'news_url': 'https://www.lia-roc.org.tw/news',
                'category': '保險公會',
                'selectors': {
                    'title': '.title, h1, h2',
                    'content': '.content, .article-content',
                    'date': '.date, .time'
                }
            },
            'tii': {
                'name': '中華民國產物保險商業同業公會',
                'base_url': 'https://www.tii.org.tw',
                'news_url': 'https://www.tii.org.tw/news',
                'category': '保險公會',
                'selectors': {
                    'title': '.news-title, h1',
                    'content': '.news-content, .content',
                    'date': '.news-date, .date'
                }
            },
            
            # 財經理財類
            'udn_money': {
                'name': '經濟日報理財',
                'base_url': 'https://money.udn.com',
                'news_url': 'https://money.udn.com/money/cate/5591',
                'category': '財經理財',
                'selectors': {
                    'title': '.story-list__text h3, h1',
                    'content': '.article-content__editor, #story_body',
                    'date': '.story-list__time, time',
                    'link': '.story-list__text a'
                }
            },
            'ctee': {
                'name': '工商時報財經',
                'base_url': 'https://www.ctee.com.tw',
                'news_url': 'https://www.ctee.com.tw/livenews/fm',
                'category': '財經理財',
                'selectors': {
                    'title': '.title a, h1',
                    'content': '.article-content, .content',
                    'date': '.date, time',
                    'link': '.title a'
                }
            },
            'wealth': {
                'name': '財訊雜誌',
                'base_url': 'https://www.wealth.com.tw',
                'news_url': 'https://www.wealth.com.tw/lists/money',
                'category': '財經理財',
                'selectors': {
                    'title': '.article-title, h1, h2',
                    'content': '.article-content, .content',
                    'date': '.article-date, .date'
                }
            },
            'businesstoday': {
                'name': '今周刊',
                'base_url': 'https://www.businesstoday.com.tw',
                'news_url': 'https://www.businesstoday.com.tw/list-content.aspx?id=308021',
                'category': '財經理財',
                'selectors': {
                    'title': '.article-title, h1',
                    'content': '.article-content, .content',
                    'date': '.article-date, .date'
                }
            },
            
            # 醫療長照類  
            'heho': {
                'name': 'Heho健康',
                'base_url': 'https://heho.com.tw',
                'news_url': 'https://heho.com.tw/category/長照',
                'category': '醫療長照',
                'selectors': {
                    'title': '.entry-title, h1',
                    'content': '.entry-content, .content',
                    'date': '.entry-date, time'
                }
            },
            'edh': {
                'name': '早安健康',
                'base_url': 'https://www.edh.tw',
                'news_url': 'https://www.edh.tw/cancer',
                'category': '醫療長照',
                'selectors': {
                    'title': '.article-title, h1',
                    'content': '.article-content, .content',
                    'date': '.article-date, .date'
                }
            },
            'commonhealth': {
                'name': '康健雜誌',
                'base_url': 'https://www.commonhealth.com.tw',
                'news_url': 'https://www.commonhealth.com.tw/insurance',
                'category': '醫療長照',
                'selectors': {
                    'title': '.article-title, h1',
                    'content': '.article-content, .content',
                    'date': '.article-date, .date'
                }
            }
        }
        
        # 台灣保險關鍵詞（擴充版）
        self.taiwan_insurance_keywords = [
            # 基本保險詞彙
            '保險', '保費', '保單', '理賠', '投保', '承保', '續保', '退保',
            '壽險', '產險', '車險', '健康險', '意外險', '醫療險', '癌症險',
            '失能險', '長照險', '年金險', '儲蓄險', '投資型保單',
            
            # 台灣保險公司
            '南山人壽', '國泰人壽', '富邦人壽', '新光人壽', '台灣人壽',
            '中國信託', '第一金人壽', '兆豐人壽', '玉山人壽', '宏泰人壽',
            '保德信人壽', '安聯人壽', '三商美邦', '遠雄人壽', '康健人壽',
            '新安東京海上', '富邦產險', '國泰產險', '新光產險', '南山產險',
            
            # 監理機關
            '金管會', '保險局', '金融監督管理委員會', '保險監理',
            
            # 法規制度
            '保險法', '保險業法', '保險代理人', '保險經紀人', '保險公證人',
            'RBC', '清償能力', '資本適足率', '準備金', '責任準備金',
            
            # 台灣特有
            '全民健保', '勞保', '勞退', '國民年金', '農保', '軍公教保險',
            '二代健保', '補充保費', '健保卡', '健保署',
            
            # 長照相關
            '長期照顧', '長照2.0', '失智症', '失能', '居家照護', '日照中心',
            
            # 保險科技
            'InsurTech', '數位保險', '線上投保', '保險科技', 'AI理賠',
            
            # 投資理財
            '利變型', '分紅保單', '投資連結', '萬能壽險', '變額年金'
        ]
        
        # User-Agent 輪換池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # 請求配置
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info(f"🚀 台灣保險新聞爬蟲初始化完成，支援 {len(self.news_sources)} 個新聞源")
    
    def get_random_user_agent(self) -> str:
        """獲取隨機 User-Agent"""
        return random.choice(self.user_agents)
    
    def make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """發送HTTP請求，包含重試機制"""
        for attempt in range(retries):
            try:
                # 隨機延遲
                time.sleep(random.uniform(1, 3))
                
                # 設置隨機 User-Agent
                self.session.headers['User-Agent'] = self.get_random_user_agent()
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                logger.info(f"✅ 成功請求: {url}")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ 請求失敗 (嘗試 {attempt + 1}/{retries}): {url} - {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(2, 5))
                
        logger.error(f"❌ 請求最終失敗: {url}")
        return None
    
    def extract_article_links(self, source_key: str) -> List[str]:
        """提取文章連結列表"""
        source = self.news_sources[source_key]
        news_url = source['news_url']
        
        logger.info(f"📡 正在獲取文章列表: {source['name']}")
        
        response = self.make_request(news_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # 根據不同網站調整連結提取邏輯
        if source_key == 'udn_money':
            # 經濟日報特殊處理
            link_elements = soup.select('.story-list__text a, .story__headline a')
        elif source_key == 'ctee':
            # 工商時報特殊處理
            link_elements = soup.select('.title a, .headline a')
        else:
            # 通用處理
            link_elements = soup.select('a[href*="/news/"], a[href*="/article/"], a[href*="/post/"]')
        
        for link in link_elements:
            href = link.get('href')
            if href:
                # 處理相對連結
                if href.startswith('/'):
                    full_url = urljoin(source['base_url'], href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # 過濾掉非新聞連結
                if self.is_news_link(full_url):
                    links.append(full_url)
        
        logger.info(f"📋 {source['name']} 發現 {len(links)} 個文章連結")
        return links[:20]  # 限制數量
    
    def is_news_link(self, url: str) -> bool:
        """判斷是否為新聞文章連結"""
        # 排除不需要的連結
        exclude_patterns = [
            '/tag/', '/category/', '/author/', '/search/',
            '/login', '/register', '/about', '/contact',
            '.pdf', '.jpg', '.png', '.gif', '/video/',
            'javascript:', 'mailto:', '#'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def extract_article_content(self, url: str, source_key: str) -> Optional[NewsArticle]:
        """提取單篇文章內容"""
        source = self.news_sources[source_key]
        
        response = self.make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        selectors = source['selectors']
        
        try:
            # 提取標題
            title_element = soup.select_one(selectors['title'])
            title = title_element.get_text(strip=True) if title_element else "無標題"
            
            # 檢查是否包含保險關鍵詞
            if not self.contains_insurance_keywords(title):
                return None
            
            # 提取內容
            content_elements = soup.select(selectors['content'])
            content = ""
            for element in content_elements:
                content += element.get_text(strip=True) + "\n"
            
            if not content.strip():
                logger.warning(f"⚠️ 無法提取內容: {url}")
                return None
            
            # 檢查內容是否包含保險關鍵詞
            if not self.contains_insurance_keywords(content):
                return None
            
            # 提取摘要
            summary_element = soup.select_one(selectors.get('summary', ''))
            summary = summary_element.get_text(strip=True) if summary_element else content[:200]
            
            # 提取發布日期
            date_element = soup.select_one(selectors.get('date', ''))
            published_date = self.parse_date(date_element.get_text(strip=True) if date_element else "")
            
            # 計算重要性評分
            importance_score = self.calculate_importance_score(title, content)
            
            return NewsArticle(
                title=title,
                content=content.strip(),
                summary=summary,
                url=url,
                source=source['name'],
                category=source['category'],
                published_date=published_date,
                importance_score=importance_score
            )
            
        except Exception as e:
            logger.error(f"❌ 內容提取失敗: {url} - {e}")
            return None
    
    def contains_insurance_keywords(self, text: str) -> bool:
        """檢查文本是否包含保險關鍵詞"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.taiwan_insurance_keywords)
    
    def parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return datetime.now()
        
        # 常見的台灣日期格式
        date_patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # 2024/12/15 或 2024-12-15
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # 15/12/2024
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',      # 2024年12月15日
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        # 判斷年月日順序
                        if len(groups[0]) == 4:  # 年在前
                            year, month, day = map(int, groups)
                        else:  # 年在後
                            day, month, year = map(int, groups)
                        
                        return datetime(year, month, day)
                except ValueError:
                    continue
        
        return datetime.now()
    
    def calculate_importance_score(self, title: str, content: str) -> float:
        """計算新聞重要性評分"""
        score = 0.0
        
        # 標題中的關鍵詞權重更高
        for keyword in self.taiwan_insurance_keywords:
            if keyword in title:
                score += 0.3
            if keyword in content:
                score += 0.1
        
        # 特別重要的關鍵詞
        important_keywords = ['金管會', '保險局', '法規', '修法', '重大', '緊急', '警示']
        for keyword in important_keywords:
            if keyword in title:
                score += 0.5
            if keyword in content:
                score += 0.2
        
        return min(score, 1.0)  # 最大值為1.0
    
    def crawl_source(self, source_key: str, max_articles: int = 10) -> List[NewsArticle]:
        """爬取指定新聞源"""
        logger.info(f"🕷️ 開始爬取: {self.news_sources[source_key]['name']}")
        
        articles = []
        
        try:
            # 獲取文章連結
            links = self.extract_article_links(source_key)
            
            # 爬取文章內容
            for i, link in enumerate(links[:max_articles]):
                logger.info(f"📰 處理文章 {i+1}/{min(len(links), max_articles)}: {link}")
                
                article = self.extract_article_content(link, source_key)
                if article:
                    articles.append(article)
                    logger.info(f"✅ 成功提取: {article.title}")
                
                # 隨機延遲避免被封
                time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.error(f"❌ 爬取失敗: {self.news_sources[source_key]['name']} - {e}")
        
        logger.info(f"🎉 {self.news_sources[source_key]['name']} 完成，獲得 {len(articles)} 篇文章")
        return articles
    
    def crawl_all_sources(self, max_articles_per_source: int = 5) -> List[NewsArticle]:
        """爬取所有新聞源"""
        logger.info("🚀 開始全源爬取...")
        
        all_articles = []
        
        for source_key in self.news_sources:
            try:
                articles = self.crawl_source(source_key, max_articles_per_source)
                all_articles.extend(articles)
                
                # 源間延遲
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"❌ 源爬取失敗: {source_key} - {e}")
                continue
        
        logger.info(f"🎉 全源爬取完成，總共獲得 {len(all_articles)} 篇文章")
        return all_articles
    
    def save_to_database(self, articles: List[NewsArticle]) -> Dict[str, Any]:
        """儲存文章到資料庫"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "instance", "insurance_news.db")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            duplicate_count = 0
            
            for article in articles:
                # 檢查是否已存在
                cursor.execute("SELECT id FROM news WHERE url = ?", (article.url,))
                if cursor.fetchone():
                    duplicate_count += 1
                    continue
                
                # 插入新文章
                cursor.execute("""
                    INSERT INTO news (
                        title, content, summary, url, source_id, category_id,
                        published_date, crawled_date, importance_score,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 1, 1, ?, ?, ?, 'active', ?, ?)
                """, (
                    article.title,
                    article.content,
                    article.summary,
                    article.url,
                    article.published_date,
                    datetime.now(),
                    article.importance_score,
                    datetime.now(),
                    datetime.now()
                ))
                
                saved_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 資料庫儲存完成: 新增 {saved_count} 篇，重複 {duplicate_count} 篇")
            
            return {
                'status': 'success',
                'saved_count': saved_count,
                'duplicate_count': duplicate_count
            }
            
        except Exception as e:
            logger.error(f"❌ 資料庫儲存失敗: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    """主執行函數"""
    print("🇹🇼 台灣保險新聞專業爬蟲引擎啟動")
    print("=" * 50)
    
    crawler = TaiwanInsuranceCrawler()
    
    # 爬取所有新聞源
    articles = crawler.crawl_all_sources(max_articles_per_source=3)
    
    if articles:
        print(f"\n📊 爬取結果:")
        print(f"  總文章數: {len(articles)} 篇")
        
        # 按來源統計
        source_stats = {}
        for article in articles:
            source_stats[article.source] = source_stats.get(article.source, 0) + 1
        
        print(f"  來源分布:")
        for source, count in source_stats.items():
            print(f"    {source}: {count} 篇")
        
        # 儲存到資料庫
        print(f"\n💾 儲存到資料庫...")
        result = crawler.save_to_database(articles)
        
        if result['status'] == 'success':
            print(f"✅ 儲存成功: 新增 {result['saved_count']} 篇，重複 {result['duplicate_count']} 篇")
        else:
            print(f"❌ 儲存失敗: {result.get('error', '未知錯誤')}")
    
    else:
        print("⚠️ 未能獲取到任何文章")

if __name__ == "__main__":
    main()
