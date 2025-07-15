#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
每日保險新聞爬蟲 - 60篇限定版
Daily Insurance News Crawler - 60 Articles Limit

專門為每日閱讀設計，控制在60篇精選新聞
"""

import requests
import feedparser
import sqlite3
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import re
import hashlib
import time
import random
import sys
import uuid

# 添加項目根目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 導入圖片提取工具
try:
    from utils.image_extractor import extract_image_from_url
    IMAGE_EXTRACTION_ENABLED = True
    print("✅ 圖片提取功能已啟用")
except ImportError as e:
    print(f"⚠️ 圖片提取功能未啟用: {e}")
    IMAGE_EXTRACTION_ENABLED = False

class DailyInsuranceCrawler:
    def __init__(self, target_count=60):
        self.db_path = self.find_database()
        self.target_count = target_count
        self.search_terms = self.get_focused_search_terms()
        
    def find_database(self):
        """找到資料庫檔案"""
        for db_name in ["instance/insurance_news.db", "instance/dev_insurance_news.db"]:
            if os.path.exists(db_name):
                return db_name
        return "instance/insurance_news.db"
    
    def get_focused_search_terms(self):
        """獲取精選的搜索關鍵字（專注於重要新聞）"""
        # 精選關鍵字，優先獲取重要新聞
        terms = [
            # 核心保險（高優先級）
            '保險 台灣', '人壽保險 台灣', '產險 台灣', 
            '車險 台灣', '健康險 台灣', '醫療險 台灣',
            
            # 監管政策（高優先級）
            '金管會 保險', '保險局 台灣', '保險法修正',
            
            # 主要保險公司（中優先級）
            '國泰人壽', '富邦人壽', '新光人壽', '南山人壽',
            '台灣人壽', '全球人壽', '國泰產險', '富邦產險',
            
            # 重要議題（中優先級）
            '長照險 台灣', '年金險 台灣', '保險科技 台灣',
            '保險理賠', '保險糾紛', '數位保險',
            
            # 社會相關（低優先級）
            '高齡化 保險', '退休規劃 台灣', '醫療 保險 台灣'
        ]
        
        print(f"🎯 使用 {len(terms)} 個精選關鍵字，目標 {self.target_count} 篇新聞")
        return terms
    
    def normalize_title(self, title):
        """標準化標題"""
        if not title:
            return ""
        
        # 移除常見的前後綴
        title = re.sub(r'^【.*?】', '', title)
        title = re.sub(r'\s*[-|]\s*.*?(新聞網|時報|日報).*$', '', title)
        title = re.sub(r'[^\w\s]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title.lower()
    
    def get_content_hash(self, title, content=""):
        """生成內容哈希值"""
        combined = self.normalize_title(title) + " " + content[:100].lower()
        combined = re.sub(r'\s+', ' ', combined).strip()
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def is_insurance_related(self, title, content=""):
        """檢查是否與保險相關"""
        text = (title + " " + content).lower()
        
        # 核心保險關鍵字（必須包含）
        core_keywords = ['保險', '保單', '保費', '理賠', '投保']
        if not any(keyword in text for keyword in core_keywords):
            return False
        
        # 計算相關性分數
        score = 0
        
        # 保險類型 (+2分)
        insurance_types = ['壽險', '產險', '車險', '健康險', '醫療險', '意外險', '年金險', '長照險']
        score += sum(2 for keyword in insurance_types if keyword in text)
        
        # 保險公司 (+1分)
        companies = ['國泰', '富邦', '新光', '南山', '台灣人壽', '全球人壽']
        score += sum(1 for keyword in companies if keyword in text)
        
        # 監管相關 (+3分)
        regulatory = ['金管會', '保險局']
        score += sum(3 for keyword in regulatory if keyword in text)
        
        return score >= 2
    
    def fetch_news_for_term(self, search_term, max_results):
        """為單個搜索詞抓取新聞"""
        news_list = []
        
        try:
            encoded_term = quote(search_term)
            search_url = f"https://news.google.com/rss/search?q={encoded_term}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            time.sleep(random.uniform(0.5, 1.5))
            
            feed = feedparser.parse(search_url)
            
            if hasattr(feed, 'entries'):
                count = 0
                for entry in feed.entries:
                    if count >= max_results:
                        break
                    
                    title = entry.title
                    summary = entry.get('summary', '')
                    
                    if self.is_insurance_related(title, summary):
                        news_list.append({
                            'title': title,
                            'url': entry.link,
                            'summary': summary[:300],
                            'content': summary,
                            'published_date': datetime.now(timezone.utc),
                            'source': 'Google新聞',
                            'search_term': search_term
                        })
                        count += 1
                
                return news_list
            else:
                return []
                
        except Exception as e:
            print(f"  ❌ 搜索 '{search_term}' 失敗: {e}")
            return []
    
    def fetch_daily_news(self):
        """抓取每日新聞（智能分配）"""
        all_news = []
        
        print("📰 開始抓取每日保險新聞...")
        print("=" * 50)
        
        # 根據關鍵字重要性分配數量
        high_priority = self.search_terms[:6]      # 前6個高優先級，每個8篇 = 48篇
        medium_priority = self.search_terms[6:14]  # 中8個中優先級，每個1篇 = 8篇  
        low_priority = self.search_terms[14:]      # 其餘低優先級，每個1篇 = 4篇
        
        # 高優先級關鍵字
        print("🔥 抓取高優先級新聞...")
        for i, term in enumerate(high_priority, 1):
            print(f"  {i}/6: {term}")
            news = self.fetch_news_for_term(term, 8)
            all_news.extend(news)
            if len(all_news) >= 48:
                break
        
        # 如果還沒達到目標，抓取中優先級
        if len(all_news) < self.target_count:
            print("📊 抓取中優先級新聞...")
            remaining = self.target_count - len(all_news)
            per_term = max(1, remaining // len(medium_priority))
            
            for term in medium_priority:
                if len(all_news) >= self.target_count:
                    break
                news = self.fetch_news_for_term(term, per_term)
                all_news.extend(news)
        
        # 如果還不夠，抓取低優先級
        if len(all_news) < self.target_count:
            print("📈 抓取補充新聞...")
            remaining = self.target_count - len(all_news)
            
            for term in low_priority:
                if len(all_news) >= self.target_count:
                    break
                news = self.fetch_news_for_term(term, 1)
                all_news.extend(news)
        
        print(f"📊 總共抓取到 {len(all_news)} 則新聞")
        return all_news
    
    def deduplicate_and_limit(self, news_list):
        """去重並限制數量"""
        print("🔄 正在去重並限制數量...")
        
        seen_hashes = set()
        unique_news = []
        
        for news in news_list:
            content_hash = self.get_content_hash(news['title'], news['content'])
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_news.append(news)
                
                # 達到目標數量就停止
                if len(unique_news) >= self.target_count:
                    break
        
        print(f"✅ 去重完成，最終保留 {len(unique_news)} 則新聞")
        return unique_news
    
    def save_to_database(self, news_list):
        """保存新聞到資料庫"""
        if not news_list:
            print("❌ 沒有新聞要保存")
            return False
        
        print("💾 正在保存到資料庫...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 獲取現有新聞的內容哈希值
            cursor.execute("SELECT title, content FROM news WHERE status = 'active'")
            existing_hashes = set()
            for title, content in cursor.fetchall():
                existing_hashes.add(self.get_content_hash(title, content or ""))
            
            saved_count = 0
            duplicate_count = 0
            
            for news_data in news_list:
                try:
                    title = news_data.get('title', '').strip()
                    content = news_data.get('content', '')
                    
                    if not title:
                        continue
                    
                    # 檢查重複
                    content_hash = self.get_content_hash(title, content)
                    if content_hash in existing_hashes:
                        duplicate_count += 1
                        continue
                    
                    # 生成唯一URL
                    import uuid
                    original_url = news_data.get('url', '')
                    unique_url = f"{original_url}#daily_{uuid.uuid4().hex[:8]}"
                    
                    # 提取圖片 URL
                    image_url = None
                    if IMAGE_EXTRACTION_ENABLED and original_url:
                        try:
                            print(f"  🖼️ 正在提取圖片: {title[:30]}...")
                            image_url = extract_image_from_url(original_url)
                            if image_url:
                                print(f"  ✅ 圖片已獲取: {image_url[:50]}...")
                            else:
                                print(f"  ⚠️ 未找到合適圖片")
                        except Exception as img_e:
                            print(f"  ❌ 圖片提取失敗: {img_e}")
                    
                    # 準備插入數據
                    now = datetime.now(timezone.utc).isoformat()
                    
                    cursor.execute("""
                        INSERT INTO news (
                            title, content, summary, url, source_id, category_id,
                            published_date, crawled_date, importance_score, 
                            sentiment_score, status, created_at, updated_at, image_url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        title,
                        content,
                        news_data.get('summary', '')[:400],
                        unique_url,
                        4,  # 來源ID
                        1,  # 分類ID
                        now,
                        now,
                        0.8,  # 重要性分數
                        0.1,  # 情感分數
                        'active',
                        now,
                        now,
                        image_url  # 圖片URL
                    ))
                    
                    existing_hashes.add(content_hash)
                    saved_count += 1
                    
                    if saved_count <= 5 or saved_count % 10 == 0:
                        print(f"  ✅ 已保存 {saved_count} 則新聞...")
                    
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
            
            conn.close()
            return {'active_news': active_count}
        except Exception as e:
            print(f"❌ 獲取統計失敗: {e}")
            return {'active_news': 0}
    
    def run(self):
        """執行每日爬蟲"""
        print("☀️ 每日保險新聞爬蟲啟動")
        print(f"🎯 目標數量: {self.target_count} 篇新聞")
        print(f"🗄️ 資料庫: {self.db_path}")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 顯示當前狀態
            before_stats = self.get_database_stats()
            print(f"📊 執行前: {before_stats['active_news']} 則活躍新聞")
            
            # 1. 抓取每日新聞
            news_list = self.fetch_daily_news()
            
            if not news_list:
                print("❌ 沒有抓取到任何新聞")
                return False
            
            # 2. 去重並限制數量
            final_news = self.deduplicate_and_limit(news_list)
            
            if not final_news:
                print("❌ 去重後沒有新聞")
                return False
            
            # 3. 保存到資料庫
            success = self.save_to_database(final_news)
            
            # 4. 顯示結果
            after_stats = self.get_database_stats()
            added_count = after_stats['active_news'] - before_stats['active_news']
            execution_time = time.time() - start_time
            
            print("=" * 50)
            print("📈 每日爬蟲執行結果:")
            print(f"  ⏱️ 執行時間: {execution_time:.1f} 秒")
            print(f"  📡 抓取新聞: {len(news_list)} 則")
            print(f"  🎯 目標數量: {self.target_count} 則")
            print(f"  ✅ 實際新增: {added_count} 則")
            print(f"  📈 總活躍新聞: {after_stats['active_news']} 則")
            
            if success and added_count > 0:
                print(f"\n🎉 每日新聞更新完成！新增了 {added_count} 則精選保險新聞")
                print("💡 現在可以查看網站獲得今日最新保險資訊")
                return True
            else:
                print("\n⚠️ 執行完成，但沒有新增新聞（可能都是重複的）")
                return False
            
        except Exception as e:
            print(f"❌ 每日爬蟲執行失敗: {e}")
            return False

def main():
    """主程式"""
    print("請選擇每日新聞數量:")
    print("1. 60篇新聞 (推薦)")
    print("2. 30篇新聞 (精簡)")
    print("3. 100篇新聞 (完整)")
    print("4. 自訂數量")
    
    choice = input("\n請選擇 (1-4): ").strip()
    
    if choice == "1":
        target_count = 60
    elif choice == "2":
        target_count = 30
    elif choice == "3":
        target_count = 100
    elif choice == "4":
        try:
            target_count = int(input("請輸入目標新聞數量: "))
            if target_count <= 0 or target_count > 200:
                print("❌ 數量必須在1-200之間")
                return
        except ValueError:
            print("❌ 請輸入有效數字")
            return
    else:
        print("❌ 無效選擇")
        return
    
    crawler = DailyInsuranceCrawler(target_count)
    crawler.run()

if __name__ == "__main__":
    main()
