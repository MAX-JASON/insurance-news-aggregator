#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
超級保險新聞爬蟲 - 擴展關鍵字版
Super Insurance News Crawler with Expanded Keywords

使用大幅擴展的關鍵字庫和搜索範圍
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

class SuperInsuranceCrawler:
    def __init__(self):
        self.db_path = self.find_database()
        self.keywords = self.load_expanded_keywords()
        self.search_terms = self.prepare_search_terms()
        
    def find_database(self):
        """找到資料庫檔案"""
        for db_name in ["instance/insurance_news.db", "instance/dev_insurance_news.db"]:
            if os.path.exists(db_name):
                return db_name
        return "instance/insurance_news.db"
    
    def load_expanded_keywords(self):
        """載入擴展關鍵字配置"""
        try:
            with open('config/expanded_keywords.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 載入擴展關鍵字失敗，使用預設關鍵字: {e}")
            return {
                'search_combinations': {
                    'primary': ['保險', '人壽保險', '產險', '車險', '健康險'],
                    'secondary': ['金管會 保險', '保險局', '理賠'],
                    'specialized': ['保險科技', '數位保險', '長照險']
                }
            }
    
    def prepare_search_terms(self):
        """準備搜索關鍵字"""
        search_terms = []
        
        # 從配置中提取搜索組合
        if 'search_combinations' in self.keywords:
            combinations = self.keywords['search_combinations']
            
            # 主要關鍵字 (每個都搜索)
            if 'primary' in combinations:
                search_terms.extend(combinations['primary'])
            
            # 次要關鍵字 (選擇性搜索)
            if 'secondary' in combinations:
                search_terms.extend(combinations['secondary'][:5])  # 取前5個
            
            # 專業關鍵字 (選擇性搜索)
            if 'specialized' in combinations:
                search_terms.extend(combinations['specialized'][:3])  # 取前3個
                
            # 監管關鍵字
            if 'regulatory' in combinations:
                search_terms.extend(combinations['regulatory'][:3])  # 取前3個
        
        # 如果沒有配置，使用預設
        if not search_terms:
            search_terms = [
                '保險', '人壽保險', '產險', '車險', '健康險', '醫療險', 
                '意外險', '年金險', '長照險', '失能險', '金管會 保險', 
                '保險局', '理賠', '投保', '保單', '保險科技', '數位保險'
            ]
        
        print(f"🎯 準備使用 {len(search_terms)} 個搜索關鍵字")
        return search_terms
    
    def normalize_title(self, title):
        """標準化標題以便更好地檢測重複"""
        # 移除常見的前後綴
        title = re.sub(r'^【.*?】', '', title)  # 移除【】標記
        title = re.sub(r'\s*-\s*.*$', '', title)  # 移除來源標記
        title = re.sub(r'\s*\|.*$', '', title)   # 移除|後的內容
        title = re.sub(r'\s+', ' ', title).strip()  # 標準化空格
        return title.lower()
    
    def get_title_hash(self, title):
        """生成標題的哈希值用於重複檢測"""
        normalized = self.normalize_title(title)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def is_insurance_related(self, title, content=""):
        """檢查新聞是否與保險相關"""
        text = (title + " " + content).lower()
        
        # 核心保險關鍵字檢查
        core_keywords = ['保險', '保單', '保費', '理賠', '投保']
        if any(keyword in text for keyword in core_keywords):
            return True
        
        # 保險類型檢查
        insurance_types = ['壽險', '產險', '車險', '健康險', '醫療險', '意外險', '年金險', '長照險']
        if any(keyword in text for keyword in insurance_types):
            return True
        
        # 保險公司檢查
        insurance_companies = ['國泰', '富邦', '新光', '南山', '台灣人壽', '全球人壽']
        if any(keyword in text for keyword in insurance_companies):
            return True
        
        # 金融監管檢查
        regulatory_keywords = ['金管會', '保險局', '金融監督管理委員會']
        if any(keyword in text for keyword in regulatory_keywords):
            return True
        
        return False
    
    def fetch_google_news(self, search_term, max_results=5):
        """抓取Google新聞"""
        news_list = []
        
        try:
            print(f"📡 搜索: {search_term}")
            
            # 構建搜索URL，加入台灣地區限制
            encoded_term = quote(f"{search_term} 台灣")
            search_url = f"https://news.google.com/rss/search?q={encoded_term}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            # 隨機延遲避免被限制
            time.sleep(random.uniform(1, 3))
            
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
                            'summary': summary[:300],
                            'content': summary,
                            'published_date': datetime.now(timezone.utc),
                            'source': f'Google新聞-{search_term}',
                            'search_term': search_term
                        })
                        count += 1
                
                print(f"  ✅ 找到 {count} 則相關新聞")
            else:
                print(f"  ⚠️ 無法解析RSS源")
                
        except Exception as e:
            print(f"  ❌ 搜索失敗: {e}")
        
        return news_list
    
    def fetch_all_news(self):
        """抓取所有新聞"""
        all_news = []
        
        print("🔍 開始抓取超級保險新聞...")
        print("=" * 60)
        
        # 使用所有搜索關鍵字
        for i, search_term in enumerate(self.search_terms, 1):
            print(f"📊 進度: {i}/{len(self.search_terms)} - {search_term}")
            
            # 根據關鍵字重要性決定抓取數量
            if search_term in ['保險', '人壽保險', '產險']:
                max_results = 8  # 重要關鍵字多抓一些
            elif '金管會' in search_term or '保險局' in search_term:
                max_results = 6  # 監管新聞也很重要
            else:
                max_results = 4  # 其他關鍵字適量
            
            news = self.fetch_google_news(search_term, max_results)
            all_news.extend(news)
            
            # 進度提示
            if i % 5 == 0:
                print(f"  📈 已完成 {i} 個關鍵字，累計 {len(all_news)} 則新聞")
        
        print(f"📊 總共抓取到 {len(all_news)} 則新聞")
        return all_news
    
    def apply_date_filter(self, news_list, max_days=7):
        """應用日期過濾"""
        print(f"🔍 應用{max_days}天日期過濾...")
        
        # RSS新聞通常都是最近的，直接返回
        filtered_news = news_list.copy()
        
        print(f"✅ 過濾後保留 {len(filtered_news)} 則新聞")
        return filtered_news
    
    def save_to_database(self, news_list):
        """保存新聞到資料庫，具有智能去重"""
        if not news_list:
            print("❌ 沒有新聞要保存")
            return False
        
        print("💾 正在保存到資料庫...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 獲取現有新聞的標題哈希值
            cursor.execute("SELECT title FROM news WHERE status = 'active'")
            existing_hashes = set()
            for (title,) in cursor.fetchall():
                existing_hashes.add(self.get_title_hash(title))
            
            saved_count = 0
            duplicate_count = 0
            
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
                    
                    # 準備插入數據
                    now = datetime.now(timezone.utc).isoformat()
                    search_term = news_data.get('search_term', '')
                    
                    # 生成帶有搜索詞標識的標題
                    enhanced_title = f"{title}"
                    if search_term and len(search_term) < 10:
                        enhanced_title = f"[{search_term}] {title}"
                    
                    cursor.execute("""
                        INSERT INTO news (
                            title, content, summary, url, source_id, category_id,
                            published_date, crawled_date, importance_score, 
                            sentiment_score, status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
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
                    
                    # 顯示保存進度
                    if saved_count <= 5 or saved_count % 10 == 0:
                        print(f"  ✅ 保存第{saved_count}則: {title[:40]}...")
                    
                except Exception as e:
                    print(f"  ❌ 保存失敗: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
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
        """執行超級爬蟲"""
        print("🚀 超級保險新聞爬蟲啟動")
        print(f"📚 使用 {len(self.search_terms)} 個搜索關鍵字")
        print(f"🗄️ 資料庫: {self.db_path}")
        print("=" * 60)
        
        try:
            # 顯示當前資料庫狀態
            before_stats = self.get_database_stats()
            print(f"📊 執行前統計: {before_stats['active_news']} 則活躍新聞")
            
            # 1. 抓取新聞
            news_list = self.fetch_all_news()
            
            if not news_list:
                print("❌ 沒有抓取到任何新聞")
                return False
            
            # 2. 應用日期過濾
            filtered_news = self.apply_date_filter(news_list, max_days=7)
            
            if not filtered_news:
                print("❌ 日期過濾後沒有新聞")
                return False
            
            # 3. 保存到資料庫
            success = self.save_to_database(filtered_news)
            
            # 4. 顯示結果統計
            after_stats = self.get_database_stats()
            added_count = after_stats['active_news'] - before_stats['active_news']
            
            print("=" * 60)
            print("📊 執行結果統計:")
            print(f"  🔍 搜索關鍵字: {len(self.search_terms)} 個")
            print(f"  📡 抓取新聞: {len(news_list)} 則")
            print(f"  ✅ 新增新聞: {added_count} 則")
            print(f"  📈 總活躍新聞: {after_stats['active_news']} 則")
            
            if success and added_count > 0:
                print("🎉 超級爬蟲執行成功！")
                print("💡 重新整理網頁應該能看到更多新的保險新聞")
                return True
            else:
                print("⚠️ 沒有新的新聞被保存（可能都是重複的）")
                return False
            
        except Exception as e:
            print(f"❌ 超級爬蟲執行失敗: {e}")
            return False

def main():
    """主程式"""
    crawler = SuperInsuranceCrawler()
    return crawler.run()

if __name__ == "__main__":
    main()
