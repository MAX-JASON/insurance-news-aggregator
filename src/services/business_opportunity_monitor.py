"""
商業機會監測模塊
Business Opportunity Monitor

監測保險新聞中的商業機會，自動偵測並推送通知
"""

import os
import re
import logging
import json
import time
import pickle
import threading
import datetime
from pathlib import Path
import hashlib
from collections import defaultdict
import sqlite3
import traceback

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'business_monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('business.monitor')

# 商業機會類型定義
OPPORTUNITY_TYPES = {
    'new_product': '新產品發布',
    'policy_change': '政策變化',
    'market_trend': '市場趨勢',
    'company_action': '公司行動',
    'partnership': '合作關係',
    'investment': '投資機會',
    'risk_alert': '風險提醒',
    'regulatory': '監管變化'
}

class BusinessOpportunityMonitor:
    """商業機會監測器"""
    
    def __init__(self, db_path=None, cache_dir=None):
        """初始化監測器
        
        Args:
            db_path: 數據庫路徑，None使用默認路徑
            cache_dir: 緩存目錄，None使用默認路徑
        """
        # 設置路徑
        if db_path is None:
            self.db_path = os.path.join(BASE_DIR, 'instance', 'insurance_news.db')
        else:
            self.db_path = db_path
        
        if cache_dir is None:
            self.cache_dir = os.path.join(BASE_DIR, 'cache', 'business_monitor')
        else:
            self.cache_dir = cache_dir
        
        # 確保緩存目錄存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 加載機會模式數據
        self.patterns_file = os.path.join(BASE_DIR, 'config', 'business_patterns.json')
        self.load_patterns()
        
        # 關鍵詞索引
        self.keyword_index = {}
        
        # 已處理新聞緩存
        self.processed_cache_file = os.path.join(self.cache_dir, 'processed_news.pkl')
        self.processed_news = self.load_processed_news()
        
        # 機會評分閾值
        self.score_threshold = 0.6
        
        # 緩存字典
        self.opportunity_cache = {}
        
        # 線程鎖
        self.lock = threading.RLock()
    
    def load_patterns(self):
        """載入機會模式數據"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
                logger.info(f"已載入 {len(self.patterns)} 組商業機會模式")
            else:
                # 創建默認模式
                self.patterns = self.create_default_patterns()
                # 保存默認模式
                self.save_patterns()
                logger.info(f"已創建默認商業機會模式")
            
            # 建立關鍵詞索引
            self.build_keyword_index()
        
        except Exception as e:
            logger.error(f"載入機會模式失敗: {e}")
            self.patterns = self.create_default_patterns()
    
    def create_default_patterns(self):
        """創建默認機會模式
        
        Returns:
            默認模式字典
        """
        return {
            "new_product": {
                "keywords": ["新產品", "新保險", "新方案", "新推出", "上市", "發布", "首推", "首款", "創新產品"],
                "patterns": [
                    r"推出[^，。；]+新[^，。；]*產品",
                    r"發布[^，。；]+新[^，。；]*保險",
                    r"上市[^，。；]+新[^，。；]*(產品|方案)",
                    r"首款[^，。；]+(產品|保險)"
                ],
                "importance": 1.5,
                "companies": {}
            },
            "policy_change": {
                "keywords": ["政策", "法規", "監管", "規定", "修訂", "調整", "變化", "改革", "法案", "修法"],
                "patterns": [
                    r"政策[^，。；]*(調整|變化|修訂)",
                    r"(頒布|發布)[^，。；]*新[^，。；]*(政策|法規)",
                    r"保險法[^，。；]*(修訂|修正|修改)",
                    r"監管[^，。；]*(加強|調整|規定)"
                ],
                "importance": 1.8,
                "companies": {}
            },
            "market_trend": {
                "keywords": ["趨勢", "成長", "增長", "市場", "需求", "潛力", "熱點", "風向", "前景"],
                "patterns": [
                    r"市場[^，。；]*(趨勢|走向)",
                    r"(行業|產業)[^，。；]*(發展|前景)",
                    r"需求[^，。；]*(增長|提升|上升)",
                    r"新興[^，。；]*(市場|領域)"
                ],
                "importance": 1.2,
                "companies": {}
            },
            "company_action": {
                "keywords": ["併購", "收購", "重組", "轉型", "戰略", "計劃", "布局", "升級", "調整", "變革"],
                "patterns": [
                    r"(併購|收購)[^，。；]*(公司|業務)",
                    r"戰略[^，。；]*(轉型|調整|升級)",
                    r"(宣布|公布)[^，。；]*重組",
                    r"業務[^，。；]*(擴張|拓展)"
                ],
                "importance": 1.4,
                "companies": {}
            },
            "partnership": {
                "keywords": ["合作", "夥伴", "聯盟", "簽約", "協議", "結盟", "戰略合作", "共同開發"],
                "patterns": [
                    r"(簽署|達成)[^，。；]*合作(協議|備忘錄)",
                    r"戰略[^，。；]*合作",
                    r"(建立|組建)[^，。；]*(聯盟|夥伴關係)",
                    r"合作[^，。；]*(開發|推出|銷售)"
                ],
                "importance": 1.3,
                "companies": {}
            },
            "investment": {
                "keywords": ["投資", "融資", "基金", "注資", "入股", "股權", "輪融資", "戰略投資"],
                "patterns": [
                    r"(完成|獲得)[^，。；]*(輪融資|投資)",
                    r"(投資|注資)[^，。；]*(億元|萬元|千萬)",
                    r"(設立|成立)[^，。；]*基金",
                    r"(收購|購入)[^，。；]*股權"
                ],
                "importance": 1.6,
                "companies": {}
            },
            "risk_alert": {
                "keywords": ["風險", "警示", "提醒", "隱患", "挑戰", "問題", "糾紛", "詐騙", "漏洞"],
                "patterns": [
                    r"風險[^，。；]*(提示|警示|提醒)",
                    r"防範[^，。；]*(風險|詐騙|陷阱)",
                    r"(存在|潛藏)[^，。；]*隱患",
                    r"(問題|糾紛)[^，。；]*(頻發|增多)"
                ],
                "importance": 1.7,
                "companies": {}
            },
            "regulatory": {
                "keywords": ["監管", "合規", "金融監管", "保監會", "銀保監", "檢查", "合規", "指導意見"],
                "patterns": [
                    r"監管[^，。；]*(要求|規定|政策)",
                    r"(保監會|銀保監)[^，。；]*(發布|頒布)",
                    r"合規[^，。；]*(檢查|審核)",
                    r"(下發|發布)[^，。；]*(指導意見|通知)"
                ],
                "importance": 1.9,
                "companies": {}
            }
        }
    
    def save_patterns(self):
        """保存機會模式數據"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=4)
            logger.info("商業機會模式已保存")
        except Exception as e:
            logger.error(f"保存機會模式失敗: {e}")
    
    def build_keyword_index(self):
        """建立關鍵詞索引"""
        with self.lock:
            keyword_index = {}
            
            for opp_type, data in self.patterns.items():
                for keyword in data.get('keywords', []):
                    if keyword in keyword_index:
                        keyword_index[keyword].append(opp_type)
                    else:
                        keyword_index[keyword] = [opp_type]
            
            self.keyword_index = keyword_index
            logger.info(f"已建立 {len(keyword_index)} 個關鍵詞索引")
    
    def load_processed_news(self):
        """載入已處理新聞記錄
        
        Returns:
            已處理新聞ID集合
        """
        try:
            if os.path.exists(self.processed_cache_file):
                with open(self.processed_cache_file, 'rb') as f:
                    return pickle.load(f)
            return set()
        except Exception as e:
            logger.error(f"載入已處理新聞記錄失敗: {e}")
            return set()
    
    def save_processed_news(self):
        """保存已處理新聞記錄"""
        try:
            with open(self.processed_cache_file, 'wb') as f:
                pickle.dump(self.processed_news, f)
        except Exception as e:
            logger.error(f"保存已處理新聞記錄失敗: {e}")
    
    def get_recent_news(self, days=7):
        """獲取最近的新聞
        
        Args:
            days: 最近天數
            
        Returns:
            新聞列表
        """
        try:
            # 計算時間範圍
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查詢最近的新聞
            cursor.execute(
                """
                SELECT 
                    id, title, content, summary, published_at, source, url, importance_score 
                FROM 
                    news 
                WHERE 
                    published_at > ? 
                ORDER BY 
                    published_at DESC
                """,
                (cutoff_str,)
            )
            
            news_list = []
            for row in cursor.fetchall():
                news = {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'summary': row[3],
                    'published_at': row[4],
                    'source': row[5],
                    'url': row[6],
                    'importance_score': row[7]
                }
                news_list.append(news)
            
            conn.close()
            logger.info(f"獲取最近 {days} 天的新聞 {len(news_list)} 條")
            return news_list
        
        except Exception as e:
            logger.error(f"獲取最近新聞失敗: {e}")
            return []
    
    def detect_opportunities(self, news):
        """檢測新聞中的商業機會
        
        Args:
            news: 新聞字典
            
        Returns:
            機會列表
        """
        opportunities = []
        
        try:
            # 提取新聞文本
            news_id = news['id']
            title = news.get('title', '')
            content = news.get('content', '')
            summary = news.get('summary', '')
            
            # 如果已經處理過，直接返回緩存結果
            if news_id in self.processed_news:
                cached = self.opportunity_cache.get(news_id)
                if cached:
                    return cached
            
            # 合併文本
            text = f"{title}\n{summary}\n{content}"
            
            # 檢測每種機會類型
            for opp_type, data in self.patterns.items():
                keywords = data.get('keywords', [])
                patterns = data.get('patterns', [])
                importance = data.get('importance', 1.0)
                
                # 關鍵詞匹配
                keyword_matches = []
                for keyword in keywords:
                    if keyword in text:
                        keyword_matches.append(keyword)
                
                # 沒有關鍵詞匹配，跳過
                if not keyword_matches:
                    continue
                
                # 正則表達式匹配
                pattern_matches = []
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        pattern_matches.extend(matches)
                
                # 計算匹配分數
                keyword_score = len(keyword_matches) / len(keywords)
                pattern_score = len(pattern_matches) / max(1, len(patterns))
                
                # 加權分數
                score = (keyword_score * 0.4) + (pattern_score * 0.6)
                
                # 如果分數超過閾值，記錄機會
                if score > self.score_threshold:
                    opportunity = {
                        'news_id': news_id,
                        'type': opp_type,
                        'type_name': OPPORTUNITY_TYPES.get(opp_type, opp_type),
                        'score': score,
                        'importance': importance,
                        'keyword_matches': keyword_matches,
                        'pattern_matches': pattern_matches,
                        'title': title,
                        'summary': summary,
                        'detected_at': datetime.datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)
            
            # 記錄已處理
            with self.lock:
                self.processed_news.add(news_id)
                if opportunities:
                    self.opportunity_cache[news_id] = opportunities
            
            return opportunities
        
        except Exception as e:
            logger.error(f"檢測商業機會失敗 (新聞ID: {news.get('id')}): {e}")
            return []
    
    def scan_news(self, days=7):
        """掃描新聞尋找商業機會
        
        Args:
            days: 最近天數
            
        Returns:
            機會列表
        """
        all_opportunities = []
        
        try:
            # 獲取最近的新聞
            news_list = self.get_recent_news(days=days)
            
            # 處理每條新聞
            for news in news_list:
                news_id = news['id']
                
                # 跳過已處理的新聞
                if news_id in self.processed_news:
                    continue
                
                # 檢測機會
                opportunities = self.detect_opportunities(news)
                if opportunities:
                    all_opportunities.extend(opportunities)
            
            # 保存已處理新聞記錄
            self.save_processed_news()
            
            # 保存機會到數據庫
            self.save_opportunities(all_opportunities)
            
            logger.info(f"掃描完成，共發現 {len(all_opportunities)} 個商業機會")
            return all_opportunities
        
        except Exception as e:
            logger.error(f"掃描新聞失敗: {traceback.format_exc()}")
            return []
    
    def save_opportunities(self, opportunities):
        """保存機會到數據庫
        
        Args:
            opportunities: 機會列表
        """
        if not opportunities:
            return
        
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 檢查表是否存在，不存在則創建
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_id INTEGER,
                    type TEXT,
                    type_name TEXT,
                    score REAL,
                    importance REAL,
                    keyword_matches TEXT,
                    pattern_matches TEXT,
                    title TEXT,
                    summary TEXT,
                    detected_at TEXT,
                    status TEXT DEFAULT 'new',
                    processed_at TEXT,
                    FOREIGN KEY (news_id) REFERENCES news (id)
                )
            ''')
            conn.commit()
            
            # 插入數據
            for opp in opportunities:
                cursor.execute(
                    '''
                    INSERT INTO business_opportunities 
                    (news_id, type, type_name, score, importance, 
                     keyword_matches, pattern_matches, title, summary, detected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        opp['news_id'],
                        opp['type'],
                        opp['type_name'],
                        opp['score'],
                        opp['importance'],
                        json.dumps(opp['keyword_matches'], ensure_ascii=False),
                        json.dumps(opp['pattern_matches'], ensure_ascii=False),
                        opp['title'],
                        opp['summary'],
                        opp['detected_at']
                    )
                )
            
            conn.commit()
            conn.close()
            logger.info(f"已保存 {len(opportunities)} 個商業機會到數據庫")
        
        except Exception as e:
            logger.error(f"保存商業機會失敗: {e}")
    
    def get_opportunity_stats(self):
        """獲取商業機會統計
        
        Returns:
            統計數據字典
        """
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 獲取機會類型統計
            cursor.execute('''
                SELECT type, type_name, COUNT(*) as count
                FROM business_opportunities
                GROUP BY type, type_name
                ORDER BY count DESC
            ''')
            
            type_stats = []
            for row in cursor.fetchall():
                type_stats.append({
                    'type': row[0],
                    'type_name': row[1],
                    'count': row[2]
                })
            
            # 獲取狀態統計
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM business_opportunities
                GROUP BY status
                ORDER BY count DESC
            ''')
            
            status_stats = []
            for row in cursor.fetchall():
                status_stats.append({
                    'status': row[0],
                    'count': row[1]
                })
            
            # 獲取總數
            cursor.execute('SELECT COUNT(*) FROM business_opportunities')
            total_count = cursor.fetchone()[0]
            
            # 獲取最近一週的趨勢
            one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT date(detected_at) as day, COUNT(*) as count
                FROM business_opportunities
                WHERE detected_at >= ?
                GROUP BY day
                ORDER BY day
            ''', (one_week_ago,))
            
            trend = []
            for row in cursor.fetchall():
                trend.append({
                    'date': row[0],
                    'count': row[1]
                })
            
            conn.close()
            
            return {
                'total': total_count,
                'by_type': type_stats,
                'by_status': status_stats,
                'trend': trend
            }
        
        except Exception as e:
            logger.error(f"獲取商業機會統計失敗: {e}")
            return {
                'total': 0,
                'by_type': [],
                'by_status': [],
                'trend': []
            }

def create_default_config():
    """創建默認配置文件"""
    config_dir = os.path.join(BASE_DIR, 'config')
    patterns_file = os.path.join(config_dir, 'business_patterns.json')
    
    # 創建配置目錄
    os.makedirs(config_dir, exist_ok=True)
    
    # 檢查配置文件是否已存在
    if os.path.exists(patterns_file):
        return
    
    # 創建默認配置
    monitor = BusinessOpportunityMonitor()
    patterns = monitor.create_default_patterns()
    
    # 保存配置文件
    with open(patterns_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=4)
    
    logger.info(f"已創建默認商業機會模式配置文件: {patterns_file}")

def main():
    """主函數"""
    logger.info("啟動商業機會監測")
    
    # 創建默認配置文件
    create_default_config()
    
    # 創建監測器
    monitor = BusinessOpportunityMonitor()
    
    # 掃描新聞
    opportunities = monitor.scan_news(days=7)
    
    # 獲取統計數據
    stats = monitor.get_opportunity_stats()
    
    return {
        'status': 'success',
        'new_opportunities': len(opportunities),
        'stats': stats
    }

if __name__ == "__main__":
    main()
