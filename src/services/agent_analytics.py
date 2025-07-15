"""
業務員數據分析模塊
Agent Data Analytics Module

提供個人化的業務員數據分析功能
"""

import os
import json
import logging
import sqlite3
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import traceback

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'agent_analytics.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agent.analytics')

class AgentDataAnalyzer:
    """業務員數據分析器"""
    
    def __init__(self, db_path=None, cache_dir=None):
        """初始化分析器
        
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
            self.cache_dir = os.path.join(BASE_DIR, 'cache', 'agent_analytics')
        else:
            self.cache_dir = cache_dir
        
        # 確保緩存目錄存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 圖表輸出目錄
        self.charts_dir = os.path.join(BASE_DIR, 'static', 'charts', 'agents')
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # 緩存文件
        self.cache_file = os.path.join(self.cache_dir, 'analytics_cache.pkl')
        self.analytics_cache = self.load_cache()
        
        # 加載用戶數據
        self.users = self.load_users()
    
    def load_cache(self):
        """載入分析緩存
        
        Returns:
            緩存字典
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache = pickle.load(f)
                logger.info(f"已載入分析緩存，包含 {len(cache)} 條記錄")
                return cache
            return {}
        except Exception as e:
            logger.error(f"載入分析緩存失敗: {e}")
            return {}
    
    def save_cache(self):
        """保存分析緩存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.analytics_cache, f)
            logger.debug("分析緩存已更新")
        except Exception as e:
            logger.error(f"保存分析緩存失敗: {e}")
    
    def load_users(self):
        """載入用戶數據
        
        Returns:
            用戶字典
        """
        users = {}
        
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查詢用戶
            cursor.execute(
                """
                SELECT 
                    id, username, email, role, created_at, last_login, is_active 
                FROM 
                    user
                """
            )
            
            for row in cursor.fetchall():
                users[row['id']] = dict(row)
            
            # 關閉連接
            conn.close()
            
            logger.info(f"已載入 {len(users)} 個用戶數據")
            return users
        
        except Exception as e:
            logger.error(f"載入用戶數據失敗: {e}")
            return {}
    
    def get_user_by_id(self, user_id):
        """根據ID獲取用戶
        
        Args:
            user_id: 用戶ID
            
        Returns:
            用戶字典，未找到則返回None
        """
        return self.users.get(user_id)
    
    def get_user_activities(self, user_id, days=30):
        """獲取用戶活動數據
        
        Args:
            user_id: 用戶ID
            days: 最近天數
            
        Returns:
            活動數據字典
        """
        # 檢查緩存
        cache_key = f"activities:{user_id}:{days}"
        if cache_key in self.analytics_cache:
            cache_time, data = self.analytics_cache[cache_key]
            if datetime.now().timestamp() - cache_time < 3600:  # 1小時緩存
                return data
        
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 計算時間範圍
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 查詢用戶活動
            cursor.execute(
                """
                SELECT 
                    activity_type, target_id, created_at, details
                FROM 
                    user_activity
                WHERE 
                    user_id = ? AND created_at >= ?
                ORDER BY 
                    created_at DESC
                """,
                (user_id, cutoff_date)
            )
            
            activities = []
            for row in cursor.fetchall():
                activities.append(dict(row))
            
            # 關閉連接
            conn.close()
            
            # 分類活動
            activity_types = defaultdict(int)
            daily_activities = defaultdict(int)
            
            for activity in activities:
                # 計算活動類型
                activity_type = activity['activity_type']
                activity_types[activity_type] += 1
                
                # 計算每日活動
                date = activity['created_at'].split(' ')[0]
                daily_activities[date] += 1
            
            # 整理每日活動數據
            daily_data = []
            for date, count in sorted(daily_activities.items()):
                daily_data.append({
                    'date': date,
                    'count': count
                })
            
            # 構建結果
            result = {
                'total_activities': len(activities),
                'activity_types': dict(activity_types),
                'daily_activities': daily_data,
                'activities': activities[:100]  # 最近100條活動
            }
            
            # 緩存結果
            self.analytics_cache[cache_key] = (datetime.now().timestamp(), result)
            self.save_cache()
            
            return result
        
        except Exception as e:
            logger.error(f"獲取用戶活動失敗 (用戶ID: {user_id}): {e}")
            return {
                'total_activities': 0,
                'activity_types': {},
                'daily_activities': [],
                'activities': [],
                'error': str(e)
            }
    
    def get_user_engagement(self, user_id, days=30):
        """獲取用戶參與度
        
        Args:
            user_id: 用戶ID
            days: 最近天數
            
        Returns:
            參與度數據字典
        """
        # 檢查緩存
        cache_key = f"engagement:{user_id}:{days}"
        if cache_key in self.analytics_cache:
            cache_time, data = self.analytics_cache[cache_key]
            if datetime.now().timestamp() - cache_time < 3600:  # 1小時緩存
                return data
        
        try:
            # 獲取用戶活動
            activities = self.get_user_activities(user_id, days)
            
            # 提取活動數據
            daily_activities = activities['daily_activities']
            activity_types = activities['activity_types']
            total_activities = activities['total_activities']
            
            # 計算活躍天數
            active_days = len(daily_activities)
            
            # 計算參與度指標
            if days > 0:
                activity_frequency = total_activities / days
                active_rate = active_days / days
            else:
                activity_frequency = 0
                active_rate = 0
            
            # 計算參與度分數 (0-100)
            engagement_score = min(100, (activity_frequency * 10 + active_rate * 50))
            
            # 計算最活躍的時間
            hourly_activities = defaultdict(int)
            for activity in activities['activities']:
                if 'created_at' in activity:
                    try:
                        hour = activity['created_at'].split(' ')[1].split(':')[0]
                        hourly_activities[hour] += 1
                    except:
                        pass
            
            # 找出最活躍的小時
            most_active_hour = max(hourly_activities.items(), key=lambda x: x[1])[0] if hourly_activities else None
            
            # 構建結果
            result = {
                'engagement_score': engagement_score,
                'active_days': active_days,
                'activity_frequency': activity_frequency,
                'active_rate': active_rate,
                'most_active_hour': most_active_hour,
                'hourly_distribution': dict(hourly_activities)
            }
            
            # 緩存結果
            self.analytics_cache[cache_key] = (datetime.now().timestamp(), result)
            self.save_cache()
            
            return result
        
        except Exception as e:
            logger.error(f"獲取用戶參與度失敗 (用戶ID: {user_id}): {e}")
            return {
                'engagement_score': 0,
                'active_days': 0,
                'activity_frequency': 0,
                'active_rate': 0,
                'most_active_hour': None,
                'hourly_distribution': {},
                'error': str(e)
            }
    
    def get_user_content_preferences(self, user_id, days=90):
        """獲取用戶內容偏好
        
        Args:
            user_id: 用戶ID
            days: 最近天數
            
        Returns:
            內容偏好數據字典
        """
        # 檢查緩存
        cache_key = f"preferences:{user_id}:{days}"
        if cache_key in self.analytics_cache:
            cache_time, data = self.analytics_cache[cache_key]
            if datetime.now().timestamp() - cache_time < 3600:  # 1小時緩存
                return data
        
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 計算時間範圍
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 查詢用戶閱讀的新聞
            cursor.execute(
                """
                SELECT 
                    n.id, n.title, n.source, n.category, n.tags,
                    n.importance_score, ua.created_at
                FROM 
                    user_activity ua
                JOIN 
                    news n ON ua.target_id = n.id
                WHERE 
                    ua.user_id = ? AND 
                    ua.activity_type = 'read_news' AND
                    ua.created_at >= ?
                ORDER BY 
                    ua.created_at DESC
                """,
                (user_id, cutoff_date)
            )
            
            read_news = []
            for row in cursor.fetchall():
                read_news.append(dict(row))
            
            # 查詢用戶收藏的新聞
            cursor.execute(
                """
                SELECT 
                    n.id, n.title, n.source, n.category, n.tags,
                    n.importance_score, ua.created_at
                FROM 
                    user_activity ua
                JOIN 
                    news n ON ua.target_id = n.id
                WHERE 
                    ua.user_id = ? AND 
                    ua.activity_type = 'bookmark_news' AND
                    ua.created_at >= ?
                ORDER BY 
                    ua.created_at DESC
                """,
                (user_id, cutoff_date)
            )
            
            bookmarked_news = []
            for row in cursor.fetchall():
                bookmarked_news.append(dict(row))
            
            # 關閉連接
            conn.close()
            
            # 分析偏好
            source_preference = defaultdict(int)
            category_preference = defaultdict(int)
            tags_preference = defaultdict(int)
            importance_distribution = []
            
            # 處理閱讀的新聞
            for news in read_news:
                source_preference[news['source']] += 1
                
                if news['category']:
                    category_preference[news['category']] += 1
                
                if news['tags']:
                    try:
                        tags = json.loads(news['tags'])
                        for tag in tags:
                            tags_preference[tag] += 1
                    except:
                        pass
                
                if news['importance_score']:
                    importance_distribution.append(float(news['importance_score']))
            
            # 處理收藏的新聞 (權重更高)
            for news in bookmarked_news:
                source_preference[news['source']] += 3  # 權重為3
                
                if news['category']:
                    category_preference[news['category']] += 3
                
                if news['tags']:
                    try:
                        tags = json.loads(news['tags'])
                        for tag in tags:
                            tags_preference[tag] += 3
                    except:
                        pass
            
            # 排序偏好
            top_sources = sorted(source_preference.items(), key=lambda x: x[1], reverse=True)[:10]
            top_categories = sorted(category_preference.items(), key=lambda x: x[1], reverse=True)[:10]
            top_tags = sorted(tags_preference.items(), key=lambda x: x[1], reverse=True)[:20]
            
            # 計算平均重要性評分
            avg_importance = np.mean(importance_distribution) if importance_distribution else 0
            
            # 構建結果
            result = {
                'top_sources': top_sources,
                'top_categories': top_categories,
                'top_tags': top_tags,
                'avg_importance': avg_importance,
                'total_read': len(read_news),
                'total_bookmarked': len(bookmarked_news),
                'read_to_bookmark_ratio': len(read_news) / max(1, len(bookmarked_news))
            }
            
            # 緩存結果
            self.analytics_cache[cache_key] = (datetime.now().timestamp(), result)
            self.save_cache()
            
            return result
        
        except Exception as e:
            logger.error(f"獲取用戶內容偏好失敗 (用戶ID: {user_id}): {traceback.format_exc()}")
            return {
                'top_sources': [],
                'top_categories': [],
                'top_tags': [],
                'avg_importance': 0,
                'total_read': 0,
                'total_bookmarked': 0,
                'read_to_bookmark_ratio': 0,
                'error': str(e)
            }
    
    def get_user_performance(self, user_id, days=90):
        """獲取用戶績效數據
        
        Args:
            user_id: 用戶ID
            days: 最近天數
            
        Returns:
            績效數據字典
        """
        # 檢查緩存
        cache_key = f"performance:{user_id}:{days}"
        if cache_key in self.analytics_cache:
            cache_time, data = self.analytics_cache[cache_key]
            if datetime.now().timestamp() - cache_time < 3600:  # 1小時緩存
                return data
        
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 計算時間範圍
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 查詢用戶分享的內容
            cursor.execute(
                """
                SELECT 
                    ua.target_id, ua.details, ua.created_at,
                    n.title, n.importance_score
                FROM 
                    user_activity ua
                LEFT JOIN 
                    news n ON ua.target_id = n.id
                WHERE 
                    ua.user_id = ? AND 
                    ua.activity_type = 'share_news' AND
                    ua.created_at >= ?
                ORDER BY 
                    ua.created_at DESC
                """,
                (user_id, cutoff_date)
            )
            
            shares = []
            for row in cursor.fetchall():
                shares.append(dict(row))
            
            # 查詢用戶收到的回饋
            cursor.execute(
                """
                SELECT 
                    ua.target_id, ua.details, ua.created_at
                FROM 
                    user_activity ua
                WHERE 
                    ua.user_id = ? AND 
                    ua.activity_type = 'receive_feedback' AND
                    ua.created_at >= ?
                ORDER BY 
                    ua.created_at DESC
                """,
                (user_id, cutoff_date)
            )
            
            feedbacks = []
            for row in cursor.fetchall():
                feedbacks.append(dict(row))
            
            # 關閉連接
            conn.close()
            
            # 分析績效
            total_shares = len(shares)
            daily_shares = defaultdict(int)
            shares_by_importance = defaultdict(int)
            
            for share in shares:
                # 計算每日分享
                date = share['created_at'].split(' ')[0]
                daily_shares[date] += 1
                
                # 按重要性分類
                if share['importance_score']:
                    importance_level = round(float(share['importance_score']))
                    shares_by_importance[importance_level] += 1
            
            # 計算平均每日分享
            if days > 0:
                avg_daily_shares = total_shares / days
            else:
                avg_daily_shares = 0
            
            # 計算客戶回饋
            total_feedbacks = len(feedbacks)
            positive_feedbacks = 0
            
            for feedback in feedbacks:
                details = feedback.get('details')
                if details:
                    try:
                        details_dict = json.loads(details)
                        if details_dict.get('sentiment') == 'positive':
                            positive_feedbacks += 1
                    except:
                        pass
            
            # 計算正向反饋比例
            if total_feedbacks > 0:
                positive_ratio = positive_feedbacks / total_feedbacks
            else:
                positive_ratio = 0
            
            # 計算分享轉換率 (假設feedbacks是基於shares)
            if total_shares > 0:
                conversion_rate = total_feedbacks / total_shares
            else:
                conversion_rate = 0
            
            # 計算績效分數 (0-100)
            performance_score = min(100, (avg_daily_shares * 10 + positive_ratio * 50 + conversion_rate * 40))
            
            # 構建結果
            result = {
                'performance_score': performance_score,
                'total_shares': total_shares,
                'avg_daily_shares': avg_daily_shares,
                'total_feedbacks': total_feedbacks,
                'positive_feedbacks': positive_feedbacks,
                'positive_ratio': positive_ratio,
                'conversion_rate': conversion_rate,
                'daily_shares': [{'date': k, 'count': v} for k, v in sorted(daily_shares.items())],
                'shares_by_importance': dict(shares_by_importance)
            }
            
            # 緩存結果
            self.analytics_cache[cache_key] = (datetime.now().timestamp(), result)
            self.save_cache()
            
            return result
        
        except Exception as e:
            logger.error(f"獲取用戶績效數據失敗 (用戶ID: {user_id}): {e}")
            return {
                'performance_score': 0,
                'total_shares': 0,
                'avg_daily_shares': 0,
                'total_feedbacks': 0,
                'positive_feedbacks': 0,
                'positive_ratio': 0,
                'conversion_rate': 0,
                'daily_shares': [],
                'shares_by_importance': {},
                'error': str(e)
            }
    
    def get_comprehensive_analytics(self, user_id):
        """獲取綜合分析數據
        
        Args:
            user_id: 用戶ID
            
        Returns:
            綜合分析數據字典
        """
        try:
            # 獲取各項分析數據
            user = self.get_user_by_id(user_id)
            activities = self.get_user_activities(user_id, days=30)
            engagement = self.get_user_engagement(user_id, days=30)
            preferences = self.get_user_content_preferences(user_id, days=90)
            performance = self.get_user_performance(user_id, days=90)
            
            # 生成圖表
            chart_paths = self.generate_user_charts(user_id, activities, engagement, preferences, performance)
            
            # 構建結果
            result = {
                'user': user,
                'activities': activities,
                'engagement': engagement,
                'preferences': preferences,
                'performance': performance,
                'charts': chart_paths,
                'analysis_time': datetime.now().isoformat()
            }
            
            return result
        
        except Exception as e:
            logger.error(f"獲取綜合分析數據失敗 (用戶ID: {user_id}): {e}")
            return {
                'user': None,
                'error': str(e)
            }
    
    def generate_user_charts(self, user_id, activities, engagement, preferences, performance):
        """生成用戶數據圖表
        
        Args:
            user_id: 用戶ID
            activities: 活動數據
            engagement: 參與度數據
            preferences: 內容偏好數據
            performance: 績效數據
            
        Returns:
            圖表路徑字典
        """
        chart_paths = {}
        
        try:
            # 設置圖表風格
            plt.style.use('seaborn-v0_8')
            
            # 活動趨勢圖
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                daily_data = activities['daily_activities']
                
                if daily_data:
                    dates = [item['date'] for item in daily_data]
                    counts = [item['count'] for item in daily_data]
                    
                    ax.plot(dates, counts, marker='o', linestyle='-', color='#3498db', linewidth=2, markersize=5)
                    ax.set_title('用戶活動趨勢', fontsize=16)
                    ax.set_xlabel('日期', fontsize=12)
                    ax.set_ylabel('活動次數', fontsize=12)
                    ax.grid(True, alpha=0.3)
                    
                    # 設置x軸標籤
                    if len(dates) > 10:
                        plt.xticks(rotation=45, ha='right')
                        # 只顯示部分標籤
                        step = len(dates) // 10 + 1
                        for i, label in enumerate(ax.get_xticklabels()):
                            if i % step != 0:
                                label.set_visible(False)
                    
                    plt.tight_layout()
                    
                    # 儲存圖表
                    chart_path = os.path.join(self.charts_dir, f'activity_trend_{user_id}.png')
                    plt.savefig(chart_path, dpi=100)
                    plt.close(fig)
                    
                    chart_paths['activity_trend'] = chart_path
            except Exception as e:
                logger.error(f"生成活動趨勢圖失敗: {e}")
            
            # 活動類型分佈圖
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                activity_types = activities['activity_types']
                
                if activity_types:
                    labels = list(activity_types.keys())
                    sizes = list(activity_types.values())
                    
                    # 使用自訂色彩
                    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
                    
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops={'width': 0.5})
                    ax.axis('equal')  # 確保圓形
                    ax.set_title('活動類型分佈', fontsize=16)
                    
                    plt.tight_layout()
                    
                    # 儲存圖表
                    chart_path = os.path.join(self.charts_dir, f'activity_types_{user_id}.png')
                    plt.savefig(chart_path, dpi=100)
                    plt.close(fig)
                    
                    chart_paths['activity_types'] = chart_path
            except Exception as e:
                logger.error(f"生成活動類型分佈圖失敗: {e}")
            
            # 時間分佈圖
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                hourly_distribution = engagement['hourly_distribution']
                
                if hourly_distribution:
                    hours = [int(h) for h in hourly_distribution.keys()]
                    counts = list(hourly_distribution.values())
                    
                    # 創建24小時列表
                    full_hours = list(range(24))
                    full_counts = [hourly_distribution.get(str(h), 0) for h in full_hours]
                    
                    # 繪製條形圖
                    bars = ax.bar(full_hours, full_counts, color='#3498db', alpha=0.7)
                    
                    # 標記最活躍時段
                    if engagement['most_active_hour']:
                        most_active = int(engagement['most_active_hour'])
                        bars[most_active].set_color('#e74c3c')
                        bars[most_active].set_alpha(1.0)
                    
                    ax.set_title('活動時間分佈', fontsize=16)
                    ax.set_xlabel('小時', fontsize=12)
                    ax.set_ylabel('活動次數', fontsize=12)
                    ax.set_xticks(full_hours)
                    ax.set_xticklabels([f'{h:02d}:00' for h in full_hours], rotation=45)
                    ax.grid(True, alpha=0.3, axis='y')
                    
                    plt.tight_layout()
                    
                    # 儲存圖表
                    chart_path = os.path.join(self.charts_dir, f'hourly_distribution_{user_id}.png')
                    plt.savefig(chart_path, dpi=100)
                    plt.close(fig)
                    
                    chart_paths['hourly_distribution'] = chart_path
            except Exception as e:
                logger.error(f"生成時間分佈圖失敗: {e}")
            
            # 偏好來源圖
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                top_sources = preferences['top_sources']
                
                if top_sources:
                    sources = [s[0] for s in top_sources]
                    counts = [s[1] for s in top_sources]
                    
                    # 繪製水平條形圖
                    bars = ax.barh(sources, counts, color='#2ecc71', alpha=0.7)
                    
                    ax.set_title('偏好新聞來源', fontsize=16)
                    ax.set_xlabel('活動次數', fontsize=12)
                    ax.set_ylabel('來源', fontsize=12)
                    ax.grid(True, alpha=0.3, axis='x')
                    
                    # 添加數值標籤
                    for i, v in enumerate(counts):
                        ax.text(v + 0.1, i, str(v), color='black', va='center')
                    
                    plt.tight_layout()
                    
                    # 儲存圖表
                    chart_path = os.path.join(self.charts_dir, f'preferred_sources_{user_id}.png')
                    plt.savefig(chart_path, dpi=100)
                    plt.close(fig)
                    
                    chart_paths['preferred_sources'] = chart_path
            except Exception as e:
                logger.error(f"生成偏好來源圖失敗: {e}")
            
            # 分享與回饋圖
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                daily_shares = performance['daily_shares']
                
                if daily_shares:
                    dates = [item['date'] for item in daily_shares]
                    counts = [item['count'] for item in daily_shares]
                    
                    ax.plot(dates, counts, marker='o', linestyle='-', color='#e74c3c', linewidth=2, markersize=5)
                    ax.set_title('分享活動趨勢', fontsize=16)
                    ax.set_xlabel('日期', fontsize=12)
                    ax.set_ylabel('分享次數', fontsize=12)
                    ax.grid(True, alpha=0.3)
                    
                    # 設置x軸標籤
                    if len(dates) > 10:
                        plt.xticks(rotation=45, ha='right')
                        # 只顯示部分標籤
                        step = len(dates) // 10 + 1
                        for i, label in enumerate(ax.get_xticklabels()):
                            if i % step != 0:
                                label.set_visible(False)
                    
                    # 添加平均線
                    if performance['avg_daily_shares'] > 0:
                        ax.axhline(y=performance['avg_daily_shares'], color='#3498db', linestyle='--', alpha=0.7)
                        ax.text(0, performance['avg_daily_shares'], f"平均: {performance['avg_daily_shares']:.2f}", 
                                color='#3498db', va='bottom', ha='left')
                    
                    plt.tight_layout()
                    
                    # 儲存圖表
                    chart_path = os.path.join(self.charts_dir, f'share_trend_{user_id}.png')
                    plt.savefig(chart_path, dpi=100)
                    plt.close(fig)
                    
                    chart_paths['share_trend'] = chart_path
            except Exception as e:
                logger.error(f"生成分享趨勢圖失敗: {e}")
            
            # 績效儀表板
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # 創建儀表板數據
                labels = ['參與度', '活躍率', '分享效率', '客戶回饋']
                values = [
                    engagement['engagement_score'] / 100,
                    engagement['active_rate'],
                    performance['conversion_rate'],
                    performance['positive_ratio']
                ]
                
                # 繪製雷達圖
                angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
                values += values[:1]  # 閉合多邊形
                angles += angles[:1]  # 閉合多邊形
                
                ax.plot(angles, values, 'o-', linewidth=2, color='#3498db')
                ax.fill(angles, values, alpha=0.25, color='#3498db')
                
                # 設置刻度和標籤
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels)
                ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
                ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
                ax.set_ylim(0, 1)
                
                ax.grid(True, alpha=0.3)
                ax.set_title('業績績效指標', fontsize=16)
                
                plt.tight_layout()
                
                # 儲存圖表
                chart_path = os.path.join(self.charts_dir, f'performance_radar_{user_id}.png')
                plt.savefig(chart_path, dpi=100)
                plt.close(fig)
                
                chart_paths['performance_radar'] = chart_path
            except Exception as e:
                logger.error(f"生成績效儀表板失敗: {e}")
            
            # 綜合分數儀表板
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # 創建分數數據
                labels = ['參與度分數', '績效分數']
                values = [
                    engagement['engagement_score'],
                    performance['performance_score']
                ]
                
                # 繪製條形圖
                bars = ax.bar(labels, values, color=['#3498db', '#e74c3c'], alpha=0.7)
                
                # 設置y軸範圍
                ax.set_ylim(0, 100)
                
                # 添加數值標籤
                for i, v in enumerate(values):
                    ax.text(i, v + 1, f'{v:.1f}', ha='center', va='bottom', fontsize=12)
                
                ax.set_ylabel('分數', fontsize=12)
                ax.set_title('業務員綜合評分', fontsize=16)
                ax.grid(True, alpha=0.3, axis='y')
                
                plt.tight_layout()
                
                # 儲存圖表
                chart_path = os.path.join(self.charts_dir, f'overall_scores_{user_id}.png')
                plt.savefig(chart_path, dpi=100)
                plt.close(fig)
                
                chart_paths['overall_scores'] = chart_path
            except Exception as e:
                logger.error(f"生成綜合分數儀表板失敗: {e}")
            
            return chart_paths
        
        except Exception as e:
            logger.error(f"生成用戶數據圖表失敗: {e}")
            return chart_paths
    
    def analyze_all_users(self, days=30):
        """分析所有用戶
        
        Args:
            days: 最近天數
            
        Returns:
            分析結果字典
        """
        results = {}
        
        try:
            # 分析每個用戶
            for user_id, user in self.users.items():
                try:
                    # 僅分析活躍用戶
                    if user.get('is_active'):
                        engagement = self.get_user_engagement(user_id, days=days)
                        performance = self.get_user_performance(user_id, days=days)
                        
                        results[user_id] = {
                            'username': user.get('username'),
                            'engagement_score': engagement.get('engagement_score', 0),
                            'performance_score': performance.get('performance_score', 0),
                            'overall_score': (engagement.get('engagement_score', 0) + 
                                             performance.get('performance_score', 0)) / 2
                        }
                except Exception as e:
                    logger.error(f"分析用戶失敗 (用戶ID: {user_id}): {e}")
                    continue
            
            logger.info(f"已分析 {len(results)} 個用戶")
            return results
        
        except Exception as e:
            logger.error(f"分析所有用戶失敗: {e}")
            return results

def main():
    """主函數"""
    logging.info("啟動業務員數據分析")
    
    # 創建分析器
    analyzer = AgentDataAnalyzer()
    
    # 分析所有用戶
    results = analyzer.analyze_all_users(days=30)
    
    # 返回結果概要
    return {
        'status': 'success',
        'users_analyzed': len(results),
        'sample_results': list(results.values())[:3] if results else []
    }

if __name__ == "__main__":
    import sys
    import matplotlib
    matplotlib.use('Agg')  # 設置後端為Agg
    main()
