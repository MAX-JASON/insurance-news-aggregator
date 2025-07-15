"""
RSS新聞聚合器
RSS News Aggregator

使用RSS源獲取台灣財經保險新聞，繞過反爬蟲限制
"""

import os
import sys
import feedparser
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
import requests
from dataclasses import dataclass

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('rss_aggregator')

@dataclass
class RSSNewsItem:
    """RSS新聞項目"""
    title: str
    url: str
    summary: str
    published_date: datetime
    source: str
    category: str = "財經新聞"
    
class RSSNewsAggregator:
    """RSS新聞聚合器"""
    
    def __init__(self):
        """初始化聚合器"""
        # 導入台灣新聞源配置
        try:
            from config.taiwan_sources import TAIWAN_INSURANCE_SOURCES, TAIWAN_INSURANCE_KEYWORDS
            
            # RSS新聞源配置（專注台灣保險）
            self.rss_sources = {}
            
            # 加載RSS源
            rss_sources = TAIWAN_INSURANCE_SOURCES.get('rss_sources', {})
            for source_id, source_info in rss_sources.items():
                self.rss_sources[source_id] = {
                    'name': source_info['name'],
                    'url': source_info['rss_url'],
                    'category': source_info['category']
                }
            
            # 加載有RSS的財經媒體
            financial_sources = TAIWAN_INSURANCE_SOURCES.get('financial_media', {})
            for source_id, source_info in financial_sources.items():
                if source_info.get('rss_url'):
                    self.rss_sources[source_id] = {
                        'name': source_info['name'],
                        'url': source_info['rss_url'],
                        'category': source_info['category']
                    }
            
            # 使用擴充的台灣保險關鍵詞
            self.insurance_keywords = []
            for category_keywords in TAIWAN_INSURANCE_KEYWORDS.values():
                self.insurance_keywords.extend(category_keywords)
                
        except ImportError:
            logger.warning("無法導入台灣新聞源配置，使用預設配置")
            # 預設配置（保留原有的作為備用）
            self.rss_sources = {
                'google_insurance_tw': {
                    'name': 'Google新聞-台灣保險',
                    'url': 'https://news.google.com/rss/search?q=台灣+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
                    'category': 'RSS新聞'
                },
                'google_financial_tw': {
                    'name': 'Google新聞-台灣金融',
                    'url': 'https://news.google.com/rss/search?q=台灣+金融+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
                    'category': 'RSS新聞'
                },
                'ctee_rss': {
                    'name': '工商時報財經',
                    'url': 'https://www.ctee.com.tw/rss/ctee-fm.xml',
                    'category': '財經新聞'
                },
                'storm_finance': {
                    'name': '風傳媒財經',
                    'url': 'https://www.storm.mg/feeds/finance',
                    'category': '網路媒體'
                }
            }
            
            # 台灣保險相關關鍵詞
            self.insurance_keywords = [
                '保險', '保費', '保單', '理賠', '投保', '承保',
                '壽險', '產險', '車險', '健康險', '意外險', '醫療險',
                '保險公司', '保險業', '保險法', '保險金', '保障',
                '南山', '國泰', '富邦', '新光', '台灣人壽',
                '中國信託', '第一金', '兆豐', '玉山', '金管會', '保險局',
                '全民健保', '勞保', '勞退', '國民年金', '長照', '失能'
            ]
        
        logger.info(f"📡 RSS新聞聚合器初始化完成，支援 {len(self.rss_sources)} 個RSS源")
    
    def fetch_all_news(self, max_items_per_source: int = 20) -> List[RSSNewsItem]:
        """獲取所有RSS源的新聞"""
        logger.info("🚀 開始獲取RSS新聞...")
        
        all_news = []
        
        for source_id, source_config in self.rss_sources.items():
            try:
                logger.info(f"📡 正在獲取: {source_config['name']}")
                news_items = self._fetch_rss_news(source_config, max_items_per_source)
                
                if news_items:
                    all_news.extend(news_items)
                    logger.info(f"✅ {source_config['name']} 獲取 {len(news_items)} 篇文章")
                else:
                    logger.warning(f"⚠️ {source_config['name']} 未獲取到文章")
                
                # 避免請求過於頻繁
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ {source_config['name']} 獲取失敗: {e}")
                continue
        
        # 篩選保險相關新聞
        insurance_news = self._filter_insurance_news(all_news)
        
        logger.info(f"🎉 RSS聚合完成，總共獲得 {len(all_news)} 篇文章，其中 {len(insurance_news)} 篇保險相關")
        return insurance_news
    
    def _fetch_rss_news(self, source_config: Dict, max_items: int) -> List[RSSNewsItem]:
        """獲取單個RSS源的新聞"""
        try:
            # 使用feedparser解析RSS
            feed = feedparser.parse(source_config['url'])
            
            if feed.bozo:
                logger.warning(f"RSS解析警告: {source_config['name']}")
            
            news_items = []
            
            for entry in feed.entries[:max_items]:
                try:
                    # 基本信息
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')
                    summary = entry.get('summary', title)
                    
                    # 清理HTML標籤
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = re.sub(r'\s+', ' ', summary).strip()
                    
                    # 解析發布時間
                    published_date = self._parse_entry_date(entry)
                    
                    # 創建新聞項目
                    news_item = RSSNewsItem(
                        title=title,
                        url=url,
                        summary=summary[:300],  # 限制摘要長度
                        published_date=published_date,
                        source=source_config['name'],
                        category=source_config['category']
                    )
                    
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.warning(f"解析RSS條目失敗: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"獲取RSS失敗 {source_config['name']}: {e}")
            return []
    
    def _parse_entry_date(self, entry) -> datetime:
        """解析RSS條目的時間"""
        try:
            # 嘗試各種時間欄位
            time_fields = ['published_parsed', 'updated_parsed']
            
            for field in time_fields:
                time_struct = getattr(entry, field, None)
                if time_struct:
                    return datetime(*time_struct[:6])
            
            # 如果都沒有，使用當前時間
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def _filter_insurance_news(self, news_items: List[RSSNewsItem]) -> List[RSSNewsItem]:
        """篩選保險相關新聞"""
        insurance_news = []
        
        for item in news_items:
            # 檢查標題和摘要是否包含保險關鍵詞
            text_to_check = f"{item.title} {item.summary}".lower()
            
            is_insurance_related = any(
                keyword in text_to_check for keyword in self.insurance_keywords
            )
            
            if is_insurance_related:
                item.category = "保險新聞"  # 更新分類
                insurance_news.append(item)
                logger.info(f"🔍 保險相關: {item.title[:50]}...")
        
        return insurance_news
    
    def save_to_database(self, news_items: List[RSSNewsItem]) -> Dict[str, Any]:
        """儲存新聞到資料庫"""
        try:
            # 使用直接 SQLite 操作儲存
            from direct_db_save import save_news_directly
            return save_news_directly(news_items)
            
        except Exception as e:
            logger.error(f"❌ 資料庫儲存失敗: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'saved_count': 0
            }
    
    def generate_summary_report(self, news_items: List[RSSNewsItem]) -> Dict[str, Any]:
        """生成摘要報告"""
        if not news_items:
            return {'message': '沒有新聞數據'}
        
        # 按來源統計
        source_stats = {}
        for item in news_items:
            source_stats[item.source] = source_stats.get(item.source, 0) + 1
        
        # 按日期統計
        today = datetime.now().date()
        today_count = sum(1 for item in news_items if item.published_date.date() == today)
        
        # 關鍵詞統計
        keyword_counts = {}
        for item in news_items:
            text = f"{item.title} {item.summary}".lower()
            for keyword in self.insurance_keywords:
                if keyword in text:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # 取前5個關鍵詞
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_news': len(news_items),
            'today_news': today_count,
            'source_distribution': source_stats,
            'top_keywords': top_keywords,
            'latest_news': [
                {'title': item.title, 'source': item.source}
                for item in sorted(news_items, key=lambda x: x.published_date, reverse=True)[:3]
            ]
        }

def main():
    """主執行函數"""
    print("📡 啟動RSS新聞聚合器...")
    
    aggregator = RSSNewsAggregator()
    
    # 獲取RSS新聞
    news_items = aggregator.fetch_all_news(max_items_per_source=15)
    
    if news_items:
        print(f"\n📰 成功獲取 {len(news_items)} 篇保險相關新聞:")
        
        for i, item in enumerate(news_items[:10], 1):  # 只顯示前10篇
            print(f"{i}. [{item.source}] {item.title}")
        
        if len(news_items) > 10:
            print(f"... 還有 {len(news_items) - 10} 篇新聞")
        
        # 生成摘要報告
        report = aggregator.generate_summary_report(news_items)
        
        print(f"\n📊 新聞摘要:")
        print(f"  總數: {report['total_news']} 篇")
        print(f"  今日: {report['today_news']} 篇")
        print(f"  來源分布: {report['source_distribution']}")
        print(f"  熱門關鍵詞: {dict(report['top_keywords'])}")
        
        # 儲存到資料庫
        print("\n💾 正在儲存到資料庫...")
        result = aggregator.save_to_database(news_items)
        
        print(f"\n📋 儲存結果:")
        print(f"  狀態: {result['status']}")
        if result['status'] == 'success':
            print(f"  新增: {result['saved_count']} 篇")
            print(f"  重複: {result['duplicate_count']} 篇")
        else:
            print(f"  錯誤: {result.get('error', '未知錯誤')}")
        
    else:
        print("⚠️ 未能獲取到任何保險相關新聞")

if __name__ == "__main__":
    main()
