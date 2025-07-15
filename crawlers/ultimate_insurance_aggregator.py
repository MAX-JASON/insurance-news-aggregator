#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
終極保險新聞聚合器
Ultimate Insurance News Aggregator

使用最全面的新聞源和關鍵字配置
"""

import requests
import feedparser
import sqlite3
import os
import yaml
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import re
import hashlib
import time
import random
import concurrent.futures
from threading import Lock

class UltimateInsuranceAggregator:
    def __init__(self):
        self.db_path = self.find_database()
        self.sources_config = self.load_comprehensive_sources()
        self.search_terms = self.prepare_comprehensive_search_terms()
        self.db_lock = Lock()
        self.results = {
            'total_searched': 0,
            'total_found': 0,
            'total_saved': 0,
            'duplicates': 0,
            'errors': 0
        }
        
    def find_database(self):
        """找到資料庫檔案"""
        for db_name in ["instance/insurance_news.db", "instance/dev_insurance_news.db"]:
            if os.path.exists(db_name):
                return db_name
        return "instance/insurance_news.db"
    
    def load_comprehensive_sources(self):
        """載入全面新聞源配置"""
        try:
            with open('config/comprehensive_sources.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 載入全面配置失敗，使用備用配置: {e}")
            return self.get_fallback_config()
    
    def get_fallback_config(self):
        """備用配置"""
        return {
            'google_news_searches': {
                'primary_insurance': ['保險', '人壽保險', '產險', '車險', '健康險'],
                'regulatory': ['金管會 保險', '保險局'],
                'market_trends': ['保險科技', '數位保險'],
                'companies': ['國泰人壽', '富邦人壽', '新光人壽']
            }
        }
    
    def prepare_comprehensive_search_terms(self):
        """準備全面的搜索關鍵字"""
        search_terms = []
        
        # 從配置中提取Google新聞搜索
        if 'google_news_searches' in self.sources_config:
            searches = self.sources_config['google_news_searches']
            
            for category, terms in searches.items():
                if isinstance(terms, list):
                    search_terms.extend(terms)
        
        # 如果沒有配置，使用預設
        if not search_terms:
            search_terms = [
                '保險 台灣', '人壽保險 台灣', '產險 台灣', '車險 台灣',
                '健康險 台灣', '醫療險 台灣', '意外險 台灣', '年金險 台灣',
                '長照險 台灣', '失能險 台灣', '金管會 保險', '保險局',
                '保險科技 台灣', '數位保險', '網路投保', '保險理賠',
                '保險糾紛', '保險詐騙', '國泰人壽', '富邦人壽'
            ]
        
        # 去重並限制數量（避免過度請求）
        search_terms = list(set(search_terms))[:50]  # 最多50個關鍵字
        
        print(f"🎯 準備使用 {len(search_terms)} 個搜索關鍵字")
        return search_terms
    
    def normalize_title(self, title):
        """標準化標題以便更好地檢測重複"""
        # 移除常見的前後綴和標點
        title = re.sub(r'^【.*?】', '', title)  # 移除【】標記
        title = re.sub(r'\s*[-|]\s*.*$', '', title)  # 移除來源標記
        title = re.sub(r'[^\w\s]', '', title)  # 移除標點符號
        title = re.sub(r'\s+', ' ', title).strip()  # 標準化空格
        return title.lower()
    
    def get_title_hash(self, title):
        """生成標題的哈希值用於重複檢測"""
        normalized = self.normalize_title(title)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def is_insurance_related(self, title, content="", threshold=0.7):
        """檢查新聞是否與保險相關（增強版）"""
        text = (title + " " + content).lower()
        
        # 核心保險關鍵字 (權重3)
        core_keywords = ['保險', '保單', '保費', '理賠', '投保', '續保', '退保']
        core_score = sum(3 for keyword in core_keywords if keyword in text)
        
        # 保險類型 (權重2)
        insurance_types = [
            '壽險', '產險', '車險', '健康險', '醫療險', '意外險', 
            '年金險', '長照險', '失能險', '重大疾病險', '癌症險'
        ]
        type_score = sum(2 for keyword in insurance_types if keyword in text)
        
        # 保險公司 (權重2)
        companies = [
            '國泰', '富邦', '新光', '南山', '台灣人壽', '全球人壽',
            '三商美邦', '宏泰', '遠雄', '中國人壽'
        ]
        company_score = sum(2 for keyword in companies if keyword in text)
        
        # 金融監管 (權重3)
        regulatory = ['金管會', '保險局', '金融監督管理委員會', '保險安定基金']
        regulatory_score = sum(3 for keyword in regulatory if keyword in text)
        
        # 相關術語 (權重1)
        related_terms = [
            '銀行保險', '銀保', '財富管理', '理財', '風險管理',
            '資產配置', '退休規劃', '長照', '醫療', '健康'
        ]
        related_score = sum(1 for keyword in related_terms if keyword in text)
        
        # 計算總分和相關性
        total_score = core_score + type_score + company_score + regulatory_score + related_score
        max_possible = len(core_keywords) * 3 + len(insurance_types) * 2 + len(companies) * 2 + len(regulatory) * 3 + len(related_terms) * 1
        
        relevance = total_score / max_possible if max_possible > 0 else 0
        
        return relevance >= threshold or total_score >= 3
    
    def fetch_google_news_batch(self, search_term, max_results=6):
        """批量抓取Google新聞"""
        news_list = []
        
        try:
            # 構建搜索URL
            encoded_term = quote(search_term)
            search_url = f"https://news.google.com/rss/search?q={encoded_term}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            # 隨機延遲避免被限制
            time.sleep(random.uniform(0.5, 2.0))
            
            feed = feedparser.parse(search_url)
            
            if hasattr(feed, 'entries'):
                count = 0
                for entry in feed.entries:
                    if count >= max_results:
                        break
                    
                    title = entry.title
                    summary = entry.get('summary', '')
                    
                    # 檢查是否與保險相關
                    if self.is_insurance_related(title, summary):
                        news_list.append({
                            'title': title,
                            'url': entry.link,
                            'summary': summary[:400],
                            'content': summary,
                            'published_date': datetime.now(timezone.utc),
                            'source': f'Google新聞',
                            'search_term': search_term
                        })
                        count += 1
                
                self.results['total_found'] += count
                return news_list
            else:
                self.results['errors'] += 1
                return []
                
        except Exception as e:
            print(f"  ❌ 搜索 '{search_term}' 失敗: {e}")
            self.results['errors'] += 1
            return []
    
    def fetch_rss_source(self, source_name, rss_url):
        """抓取RSS新聞源"""
        news_list = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            if hasattr(feed, 'entries'):
                count = 0
                for entry in feed.entries[:10]:  # RSS源最多取10則
                    title = entry.title
                    summary = entry.get('summary', '')
                    
                    # 檢查是否與保險相關
                    if self.is_insurance_related(title, summary):
                        news_list.append({
                            'title': title,
                            'url': entry.link,
                            'summary': summary[:400],
                            'content': entry.get('content', [{'value': summary}])[0].get('value', summary),
                            'published_date': datetime.now(timezone.utc),
                            'source': source_name,
                            'search_term': 'RSS'
                        })
                        count += 1
                
                print(f"  📰 {source_name}: {count} 則保險相關新聞")
                return news_list
            else:
                return []
                
        except Exception as e:
            print(f"  ❌ RSS源 '{source_name}' 抓取失敗: {e}")
            return []
    
    def fetch_all_news_parallel(self):
        """並行抓取所有新聞"""
        all_news = []
        
        print("🚀 啟動終極保險新聞聚合器")
        print(f"📊 將使用 {len(self.search_terms)} 個搜索關鍵字")
        print("=" * 70)
        
        # 並行處理搜索關鍵字
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有搜索任務
            future_to_search = {}
            
            for search_term in self.search_terms:
                future = executor.submit(self.fetch_google_news_batch, search_term)
                future_to_search[future] = search_term
                self.results['total_searched'] += 1
            
            # 收集結果
            completed = 0
            for future in concurrent.futures.as_completed(future_to_search):
                search_term = future_to_search[future]
                try:
                    news_list = future.result()
                    all_news.extend(news_list)
                    completed += 1
                    
                    if completed % 10 == 0:
                        print(f"📈 已完成 {completed}/{len(self.search_terms)} 個搜索，累計 {len(all_news)} 則新聞")
                        
                except Exception as e:
                    print(f"❌ 搜索 '{search_term}' 處理失敗: {e}")
                    self.results['errors'] += 1
        
        # 檢查是否有RSS源配置
        rss_sources = self.extract_rss_sources()
        if rss_sources:
            print(f"\n📡 開始抓取 {len(rss_sources)} 個RSS源...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                rss_futures = []
                for source_name, rss_url in rss_sources.items():
                    future = executor.submit(self.fetch_rss_source, source_name, rss_url)
                    rss_futures.append(future)
                
                for future in concurrent.futures.as_completed(rss_futures):
                    try:
                        rss_news = future.result()
                        all_news.extend(rss_news)
                    except Exception as e:
                        print(f"❌ RSS抓取失敗: {e}")
        
        print(f"\n📊 總共抓取到 {len(all_news)} 則新聞")
        return all_news
    
    def extract_rss_sources(self):
        """提取RSS源配置"""
        rss_sources = {}
        
        # 從配置中提取RSS源
        try:
            for category, sources in self.sources_config.items():
                if isinstance(sources, dict):
                    for subcategory, source_list in sources.items():
                        if isinstance(source_list, list):
                            for source in source_list:
                                if isinstance(source, dict) and source.get('rss'):
                                    rss_sources[source['name']] = source['rss']
        except Exception as e:
            print(f"⚠️ 提取RSS源失敗: {e}")
        
        # 添加一些已知的RSS源
        default_rss = {
            '經濟日報': 'https://udn.com/rssfeed/news/1/6644',
            'Heho健康': 'https://heho.com.tw/feed/',
            '風傳媒財經': 'https://www.storm.mg/feeds/finance.xml'
        }
        
        rss_sources.update(default_rss)
        return rss_sources
    
    def save_to_database_batch(self, news_list):
        """批量保存新聞到資料庫"""
        if not news_list:
            print("❌ 沒有新聞要保存")
            return False
        
        print("💾 正在批量保存到資料庫...")
        
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 獲取現有新聞的標題哈希值
                cursor.execute("SELECT title FROM news WHERE status = 'active'")
                existing_hashes = set()
                for (title,) in cursor.fetchall():
                    existing_hashes.add(self.get_title_hash(title))
                
                saved_count = 0
                duplicate_count = 0
                batch_data = []
                
                for news_data in news_list:
                    try:
                        title = news_data.get('title', '').strip()
                        if not title:
                            continue
                        
                        # 使用哈希值檢查重複
                        title_hash = self.get_title_hash(title)
                        if title_hash in existing_hashes:
                            duplicate_count += 1
                            continue
                        
                        # 準備批量插入數據
                        now = datetime.now(timezone.utc).isoformat()
                        search_term = news_data.get('search_term', '')
                        
                        # 優化標題顯示
                        enhanced_title = title
                        if search_term and search_term != 'RSS' and len(search_term) < 15:
                            enhanced_title = f"[{search_term}] {title}"
                        
                        batch_data.append((
                            enhanced_title,
                            news_data.get('content', ''),
                            news_data.get('summary', '')[:500],
                            news_data.get('url', ''),
                            4,  # 來源ID
                            1,  # 分類ID
                            now,
                            now,
                            0.8,  # 重要性分數
                            0.1,  # 情感分數
                            'active',
                            now,
                            now
                        ))
                        
                        # 添加到已存在的哈希集合
                        existing_hashes.add(title_hash)
                        saved_count += 1
                        
                        # 批量處理，每100筆提交一次
                        if len(batch_data) >= 100:
                            cursor.executemany("""
                                INSERT INTO news (
                                    title, content, summary, url, source_id, category_id,
                                    published_date, crawled_date, importance_score, 
                                    sentiment_score, status, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, batch_data)
                            conn.commit()
                            batch_data = []
                            print(f"  💾 已保存 {saved_count} 則新聞...")
                        
                    except Exception as e:
                        print(f"  ❌ 處理新聞失敗: {e}")
                        continue
                
                # 保存剩餘的數據
                if batch_data:
                    cursor.executemany("""
                        INSERT INTO news (
                            title, content, summary, url, source_id, category_id,
                            published_date, crawled_date, importance_score, 
                            sentiment_score, status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch_data)
                    conn.commit()
                
                conn.close()
                
                self.results['total_saved'] = saved_count
                self.results['duplicates'] = duplicate_count
                
                print(f"✅ 成功保存 {saved_count} 則新聞")
                print(f"⚠️ 跳過 {duplicate_count} 則重複新聞")
                
                return saved_count > 0
                
        except Exception as e:
            print(f"❌ 資料庫操作失敗: {e}")
            return False
    
    def get_database_stats(self):
        """獲取資料庫統計"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(created_at) FROM news WHERE status = 'active'")
            latest_news = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'active_news': active_count,
                'latest_news': latest_news
            }
        except Exception as e:
            print(f"❌ 獲取統計失敗: {e}")
            return {'active_news': 0, 'latest_news': None}
    
    def run(self):
        """執行終極聚合器"""
        print("🌟 終極保險新聞聚合器啟動")
        print(f"🔍 搜索範圍: {len(self.search_terms)} 個關鍵字")
        print(f"🗄️ 資料庫: {self.db_path}")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            # 顯示當前資料庫狀態
            before_stats = self.get_database_stats()
            print(f"📊 執行前統計: {before_stats['active_news']} 則活躍新聞")
            
            # 1. 並行抓取所有新聞
            news_list = self.fetch_all_news_parallel()
            
            if not news_list:
                print("❌ 沒有抓取到任何新聞")
                return False
            
            # 2. 批量保存到資料庫
            success = self.save_to_database_batch(news_list)
            
            # 3. 顯示詳細結果統計
            after_stats = self.get_database_stats()
            added_count = after_stats['active_news'] - before_stats['active_news']
            execution_time = time.time() - start_time
            
            print("=" * 70)
            print("🎯 終極聚合器執行結果:")
            print(f"  ⏱️ 執行時間: {execution_time:.1f} 秒")
            print(f"  🔍 搜索關鍵字: {self.results['total_searched']} 個")
            print(f"  📡 抓取新聞: {self.results['total_found']} 則")
            print(f"  ✅ 新增新聞: {added_count} 則")
            print(f"  ⚠️ 重複新聞: {self.results['duplicates']} 則")
            print(f"  ❌ 錯誤數量: {self.results['errors']} 個")
            print(f"  📈 總活躍新聞: {after_stats['active_news']} 則")
            print(f"  ⚡ 平均速度: {self.results['total_found']/execution_time:.1f} 則/秒")
            
            if success and added_count > 0:
                print("\n🎉 終極聚合器執行成功！")
                print("💡 您的保險新聞庫已大幅擴展，重新整理網頁即可查看")
                return True
            else:
                print("\n⚠️ 執行完成，但沒有新增新聞（可能都是重複的）")
                return False
            
        except Exception as e:
            print(f"❌ 終極聚合器執行失敗: {e}")
            return False

def main():
    """主程式"""
    aggregator = UltimateInsuranceAggregator()
    return aggregator.run()

if __name__ == "__main__":
    main()
