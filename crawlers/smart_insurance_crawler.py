#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能保險新聞爬蟲 - 最終版
Smart Insurance News Crawler - Final Version

解決URL重複問題，使用智能去重算法
"""

import requests
import feedparser
import sqlite3
import os
import yaml
from datetime import datetime, timezone, timedelta
from urllib.parse import quote, urlparse
import re
import hashlib
import time
import random
import uuid

class SmartInsuranceCrawler:
    def __init__(self):
        self.db_path = self.find_database()
        self.search_terms = self.get_expanded_search_terms()
        
    def find_database(self):
        """找到資料庫檔案"""
        for db_name in ["instance/insurance_news.db", "instance/dev_insurance_news.db"]:
            if os.path.exists(db_name):
                return db_name
        return "instance/insurance_news.db"
    
    def get_expanded_search_terms(self):
        """獲取擴展的搜索關鍵字"""
        # 超級擴展的保險相關關鍵字
        terms = [
            # 核心保險類型
            '保險 台灣', '人壽保險 台灣', '產險 台灣', '車險 台灣', 
            '健康險 台灣', '醫療險 台灣', '意外險 台灣', '年金險 台灣',
            '長照險 台灣', '失能險 台灣', '重大疾病險', '癌症險 台灣',
            
            # 監管與政策
            '金管會 保險', '保險局 台灣', '保險法修正', '保險業法',
            '金融檢查 保險', '保險監理', '保險政策', '保險改革',
            
            # 保險科技與創新
            '保險科技 台灣', '數位保險', '網路投保', 'AI保險',
            '區塊鏈保險', '保險創新', 'InsurTech台灣', '金融科技保險',
            
            # 主要保險公司
            '國泰人壽', '富邦人壽', '新光人壽', '南山人壽', 
            '台灣人壽', '全球人壽', '三商美邦', '中國人壽台灣',
            '國泰產險', '富邦產險', '新光產險', '明台產險',
            
            # 業務與服務
            '保險理賠', '保險糾紛', '保險申訴', '保險評議',
            '保險詐騙 台灣', '銀行保險', '保險通路', '保險業績',
            
            # 社會議題相關
            '高齡化 保險', '少子化 保險', '長照 保險', '退休規劃 台灣',
            '醫療 保險 台灣', '健保 保險', '職災 保險', '交通事故 保險',
            
            # 經濟與市場
            '保險市場 台灣', '保險併購', '保險投資', '保險準備金',
            '保險資本', '保險獲利', '保險股價', '保險分紅',
            
            # 特殊險種
            '旅平險 台灣', '寵物保險 台灣', '住宅險', '火險 台灣',
            '地震險 台灣', '颱風險', '企業保險', '董監事責任險',
            
            # 國際與趨勢
            'ESG保險', '永續保險', '氣候保險', '綠色保險',
            '疫情保險', 'COVID保險', '防疫保險 台灣',
            
            # 專業服務
            '保險代理人', '保險經紀人', '保險公證人', '保險精算',
            '保險法務', '保險稅務', '保險會計', '保險顧問'
        ]
        
        print(f"🎯 準備使用 {len(terms)} 個擴展搜索關鍵字")
        return terms
    
    def clean_url(self, url):
        """清理和標準化URL"""
        if not url:
            return ""
        
        # 移除Google新聞的重定向參數
        if 'news.google.com' in url and 'url=' in url:
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'url' in params:
                    url = params['url'][0]
            except:
                pass
        
        # 移除常見的追蹤參數
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'ref', 'source']
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # 移除追蹤參數
            for param in tracking_params:
                query_params.pop(param, None)
            
            # 重建URL
            new_query = urlencode(query_params, doseq=True)
            cleaned_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))
            
            return cleaned_url
        except:
            return url
    
    def normalize_title(self, title):
        """標準化標題"""
        if not title:
            return ""
        
        # 移除常見的前後綴
        title = re.sub(r'^【.*?】', '', title)  # 移除【】標記
        title = re.sub(r'\s*[-|]\s*.*?新聞網.*$', '', title)  # 移除來源標記
        title = re.sub(r'\s*[-|]\s*.*?時報.*$', '', title)  # 移除時報標記
        title = re.sub(r'\s*[-|]\s*.*?日報.*$', '', title)  # 移除日報標記
        title = re.sub(r'[^\w\s]', '', title)  # 移除標點符號
        title = re.sub(r'\s+', ' ', title).strip()  # 標準化空格
        return title.lower()
    
    def get_content_hash(self, title, content=""):
        """生成內容哈希值用於智能去重"""
        # 合併標題和內容的前200字
        combined = self.normalize_title(title) + " " + content[:200].lower()
        combined = re.sub(r'\s+', ' ', combined).strip()
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def is_insurance_related(self, title, content=""):
        """增強的保險相關性檢測"""
        text = (title + " " + content).lower()
        
        # 核心保險關鍵字（必須包含至少一個）
        core_keywords = ['保險', '保單', '保費', '理賠', '投保']
        has_core = any(keyword in text for keyword in core_keywords)
        
        if not has_core:
            return False
        
        # 計算相關性分數
        score = 0
        
        # 保險類型 (+2分每個)
        insurance_types = [
            '壽險', '產險', '車險', '健康險', '醫療險', '意外險', 
            '年金險', '長照險', '失能險', '重大疾病險', '癌症險'
        ]
        score += sum(2 for keyword in insurance_types if keyword in text)
        
        # 保險公司 (+1分每個)
        companies = [
            '國泰', '富邦', '新光', '南山', '台灣人壽', '全球人壽',
            '三商美邦', '宏泰', '遠雄', '中國人壽', '明台', '產險'
        ]
        score += sum(1 for keyword in companies if keyword in text)
        
        # 監管機構 (+3分每個)
        regulatory = ['金管會', '保險局', '金融監督管理委員會']
        score += sum(3 for keyword in regulatory if keyword in text)
        
        # 業務相關 (+1分每個)
        business_terms = ['理賠', '投保', '續保', '退保', '保費', '保額', '給付']
        score += sum(1 for keyword in business_terms if keyword in text)
        
        # 如果分數達到3分以上，認為高度相關
        return score >= 3
    
    def fetch_news_for_term(self, search_term, max_results=8):
        """為單個搜索詞抓取新聞"""
        news_list = []
        
        try:
            # 構建搜索URL
            encoded_term = quote(search_term)
            search_url = f"https://news.google.com/rss/search?q={encoded_term}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            # 隨機延遲
            time.sleep(random.uniform(0.3, 1.5))
            
            feed = feedparser.parse(search_url)
            
            if hasattr(feed, 'entries'):
                count = 0
                for entry in feed.entries:
                    if count >= max_results:
                        break
                    
                    title = entry.title
                    summary = entry.get('summary', '')
                    url = self.clean_url(entry.link)
                    
                    # 檢查是否與保險相關
                    if self.is_insurance_related(title, summary):
                        news_list.append({
                            'title': title,
                            'url': url,
                            'summary': summary[:400],
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
    
    def fetch_all_news(self):
        """抓取所有新聞"""
        all_news = []
        
        print("🔍 開始智能保險新聞抓取...")
        print("=" * 60)
        
        total_terms = len(self.search_terms)
        
        for i, search_term in enumerate(self.search_terms, 1):
            print(f"📊 進度: {i}/{total_terms} - {search_term}")
            
            # 根據關鍵字重要性決定抓取數量
            if any(x in search_term for x in ['金管會', '保險局', '保險法']):
                max_results = 10  # 監管新聞很重要
            elif any(x in search_term for x in ['保險', '人壽', '產險']):
                max_results = 8   # 核心保險關鍵字
            else:
                max_results = 6   # 其他關鍵字
            
            news = self.fetch_news_for_term(search_term, max_results)
            all_news.extend(news)
            
            # 進度提示
            if i % 10 == 0:
                print(f"  📈 已完成 {i} 個關鍵字，累計 {len(all_news)} 則新聞")
        
        print(f"📊 總共抓取到 {len(all_news)} 則新聞")
        return all_news
    
    def deduplicate_news(self, news_list):
        """智能去重"""
        print("🔄 正在進行智能去重...")
        
        seen_hashes = set()
        seen_urls = set()
        unique_news = []
        
        for news in news_list:
            # 檢查URL重複
            clean_url = self.clean_url(news['url'])
            if clean_url in seen_urls:
                continue
            
            # 檢查內容重複
            content_hash = self.get_content_hash(news['title'], news['content'])
            if content_hash in seen_hashes:
                continue
            
            # 如果都不重複，加入結果
            seen_urls.add(clean_url)
            seen_hashes.add(content_hash)
            unique_news.append(news)
        
        removed_count = len(news_list) - len(unique_news)
        print(f"✅ 去重完成，移除 {removed_count} 則重複新聞，保留 {len(unique_news)} 則")
        
        return unique_news
    
    def save_to_database(self, news_list):
        """保存新聞到資料庫（解決URL重複問題）"""
        if not news_list:
            print("❌ 沒有新聞要保存")
            return False
        
        print("💾 正在保存到資料庫...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 獲取現有新聞的內容哈希值（而不是URL）
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
                    
                    # 使用內容哈希檢查重複
                    content_hash = self.get_content_hash(title, content)
                    if content_hash in existing_hashes:
                        duplicate_count += 1
                        continue
                    
                    # 生成唯一URL（如果URL重複）
                    original_url = news_data.get('url', '')
                    unique_url = original_url
                    
                    # 檢查URL是否已存在
                    cursor.execute("SELECT COUNT(*) FROM news WHERE url = ?", (original_url,))
                    if cursor.fetchone()[0] > 0:
                        # 生成唯一URL
                        unique_url = f"{original_url}#duplicate_{uuid.uuid4().hex[:8]}"
                    
                    # 準備插入數據
                    now = datetime.now(timezone.utc).isoformat()
                    search_term = news_data.get('search_term', '')
                    
                    # 智能標題處理
                    enhanced_title = title
                    if search_term and len(search_term) <= 15:
                        # 只為短關鍵字添加標籤
                        if not any(company in search_term for company in ['國泰', '富邦', '新光', '南山']):
                            enhanced_title = f"[{search_term}] {title}"
                    
                    cursor.execute("""
                        INSERT INTO news (
                            title, content, summary, url, source_id, category_id,
                            published_date, crawled_date, importance_score, 
                            sentiment_score, status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        enhanced_title,
                        content,
                        news_data.get('summary', '')[:500],
                        unique_url,
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
                    existing_hashes.add(content_hash)
                    saved_count += 1
                    
                    # 顯示保存進度
                    if saved_count <= 10 or saved_count % 20 == 0:
                        print(f"  ✅ 保存第{saved_count}則: {title[:50]}...")
                    
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
        """執行智能爬蟲"""
        print("🧠 智能保險新聞爬蟲啟動")
        print(f"🔍 搜索範圍: {len(self.search_terms)} 個關鍵字")
        print(f"🗄️ 資料庫: {self.db_path}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # 顯示當前資料庫狀態
            before_stats = self.get_database_stats()
            print(f"📊 執行前統計: {before_stats['active_news']} 則活躍新聞")
            
            # 1. 抓取所有新聞
            news_list = self.fetch_all_news()
            
            if not news_list:
                print("❌ 沒有抓取到任何新聞")
                return False
            
            # 2. 智能去重
            unique_news = self.deduplicate_news(news_list)
            
            if not unique_news:
                print("❌ 去重後沒有新聞")
                return False
            
            # 3. 保存到資料庫
            success = self.save_to_database(unique_news)
            
            # 4. 顯示結果統計
            after_stats = self.get_database_stats()
            added_count = after_stats['active_news'] - before_stats['active_news']
            execution_time = time.time() - start_time
            
            print("=" * 60)
            print("🎯 智能爬蟲執行結果:")
            print(f"  ⏱️ 執行時間: {execution_time:.1f} 秒")
            print(f"  🔍 搜索關鍵字: {len(self.search_terms)} 個")
            print(f"  📡 抓取新聞: {len(news_list)} 則")
            print(f"  🔄 去重後: {len(unique_news)} 則")
            print(f"  ✅ 新增新聞: {added_count} 則")
            print(f"  📈 總活躍新聞: {after_stats['active_news']} 則")
            print(f"  ⚡ 處理速度: {len(news_list)/execution_time:.1f} 則/秒")
            
            if success and added_count > 0:
                print("\n🎉 智能爬蟲執行成功！")
                print("💡 保險新聞庫已大幅擴展，涵蓋更多相關領域")
                print("🌟 包含了監管政策、科技創新、公司動態、社會議題等多個面向")
                return True
            else:
                print("\n⚠️ 執行完成，但沒有新增新聞（內容可能已覆蓋）")
                return False
            
        except Exception as e:
            print(f"❌ 智能爬蟲執行失敗: {e}")
            return False

def main():
    """主程式"""
    crawler = SmartInsuranceCrawler()
    return crawler.run()

if __name__ == "__main__":
    main()
