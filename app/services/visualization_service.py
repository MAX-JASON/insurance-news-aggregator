"""
進階數據視覺化服務
Advanced Data Visualization Service

為業務員提供豐富的圖表和視覺化報表
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import sqlite3
import base64
from io import BytesIO

# 檢查並導入繪圖庫
PLOTTING_AVAILABLE = False
PANDAS_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError as e:
    print(f"警告: 無法導入pandas/numpy ({e})，將使用基本數據結構")
    # 創建基本的DataFrame替代
    class MockDataFrame:
        def __init__(self, data=None):
            self.data = data or []
        
        def empty(self):
            return len(self.data) == 0
        
        def __len__(self):
            return len(self.data) if self.data else 0
    
    pd = type('MockPandas', (), {
        'DataFrame': MockDataFrame,
        'read_sql_query': lambda *args, **kwargs: MockDataFrame(),
        'date_range': lambda *args, **kwargs: [],
        'to_datetime': lambda x: x
    })()
    np = None

try:
    import matplotlib
    matplotlib.use('Agg')  # 使用非互動式後端
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
    print("✅ 完整繪圖庫可用")
except ImportError as e:
    print(f"警告: matplotlib/seaborn 無法導入 ({e})，將使用簡化功能")
    # 創建替代的plt對象
    class MockPlt:
        @staticmethod
        def subplots(*args, **kwargs):
            return None, None
        
        @staticmethod
        def figure(*args, **kwargs):
            return None
        
        @staticmethod
        def savefig(*args, **kwargs):
            pass
        
        @staticmethod
        def close(*args, **kwargs):
            pass
        
        @staticmethod
        def tight_layout(*args, **kwargs):
            pass
        
        @staticmethod
        def xticks(*args, **kwargs):
            pass
    
    plt = MockPlt()
    sns = None

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
except ImportError as e:
    print(f"警告: plotly 無法導入 ({e})")
    px = None
    go = None
    make_subplots = None
    pyo = None

# 設置中文字體（僅當matplotlib可用時）
if PLOTTING_AVAILABLE:
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class AdvancedVisualization:
    """進階視覺化服務類"""
    
    def __init__(self, db_path: Optional[str] = None, output_dir: Optional[str] = None):
        """
        初始化視覺化服務
        
        Args:
            db_path: 資料庫路徑
            output_dir: 輸出目錄
        """
        self.base_dir = Path(__file__).resolve().parent.parent
        self.db_path = db_path or self.base_dir / 'instance' / 'insurance_news.db'
        self.output_dir = output_dir or self.base_dir / 'web' / 'static' / 'charts' / 'advanced'
        
        # 確保輸出目錄存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 設置樣式
        sns.set_style("whitegrid")
        self.color_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#8E7DBE']
        
    def generate_business_dashboard_charts(self, user_id: Optional[int] = None, days: int = 30) -> Dict[str, str]:
        """
        生成業務員儀表板圖表
        
        Args:
            user_id: 用戶ID，None表示全體統計
            days: 統計天數
            
        Returns:
            圖表文件路徑字典
        """
        chart_paths = {}
        
        if not PLOTTING_AVAILABLE:
            logger.warning("繪圖庫不可用，返回模擬圖表路徑")
            return {
                'news_trend': '/static/charts/advanced/sample_news_trend.png',
                'importance_distribution': '/static/charts/advanced/sample_importance.png',
                'source_stats': '/static/charts/advanced/sample_sources.png',
                'sentiment_analysis': '/static/charts/advanced/sample_sentiment.png'
            }
        
        try:
            # 獲取數據
            news_data = self._get_news_analytics_data(days)
            user_data = self._get_user_analytics_data(user_id, days) if user_id else None
            
            # 1. 新聞趨勢分析圖
            chart_paths['news_trend'] = self._create_news_trend_chart(news_data, days)
            
            # 2. 重要性分佈圓餅圖
            chart_paths['importance_distribution'] = self._create_importance_pie_chart(news_data)
            
            # 3. 來源統計圖
            chart_paths['source_stats'] = self._create_source_stats_chart(news_data)
            
            # 4. 情感分析圖
            chart_paths['sentiment_analysis'] = self._create_sentiment_chart(news_data)
            
            # 5. 關鍵詞雲圖
            chart_paths['keyword_cloud'] = self._create_keyword_wordcloud(news_data)
            
            # 6. 分類熱力圖
            chart_paths['category_heatmap'] = self._create_category_heatmap(news_data, days)
            
            if user_data is not None and not user_data.empty:
                # 7. 個人活動統計
                chart_paths['user_activity'] = self._create_user_activity_chart(user_data)
                
                # 8. 閱讀偏好分析
                chart_paths['reading_preference'] = self._create_reading_preference_chart(user_data)
                
                # 9. 業務績效趨勢
                chart_paths['performance_trend'] = self._create_performance_trend_chart(user_data)
            
            # 10. 交互式綜合儀表板（Plotly）
            chart_paths['interactive_dashboard'] = self._create_interactive_dashboard(news_data, user_data)
            
            logger.info(f"成功生成 {len(chart_paths)} 個圖表")
            return chart_paths
            
        except Exception as e:
            logger.error(f"生成業務員儀表板圖表失敗: {e}")
            return {}
    
    def _get_news_analytics_data(self, days: int) -> Any:
        """獲取新聞分析數據"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT 
                    n.id, n.title, n.content, n.url,
                    n.published_date, n.created_at,
                    n.importance_score, n.sentiment,
                    s.name as source_name,
                    c.name as category_name,
                    n.view_count, n.share_count
                FROM news n
                LEFT JOIN sources s ON n.source_id = s.id
                LEFT JOIN categories c ON n.category_id = c.id
                WHERE n.created_at >= ? AND n.status = 'active'
                ORDER BY n.created_at DESC
            """
            
            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            conn.close()
            
            # 數據預處理
            df['published_date'] = pd.to_datetime(df['published_date'])
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['published_date'].dt.date
            
            # 填充空值
            df['importance_score'] = df['importance_score'].fillna(0.5)
            df['sentiment'] = df['sentiment'].fillna('neutral')
            df['view_count'] = df['view_count'].fillna(0)
            df['share_count'] = df['share_count'].fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"獲取新聞分析數據失敗: {e}")
            return pd.DataFrame()
    
    def _get_user_analytics_data(self, user_id: int, days: int) -> pd.DataFrame:
        """獲取用戶分析數據"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT 
                    ua.id, ua.activity_type, ua.created_at,
                    ua.target_type, ua.target_id,
                    u.username, u.role,
                    n.title as news_title,
                    n.importance_score,
                    s.name as source_name,
                    c.name as category_name
                FROM user_activity ua
                LEFT JOIN users u ON ua.user_id = u.id
                LEFT JOIN news n ON ua.target_type = 'news' AND ua.target_id = n.id
                LEFT JOIN sources s ON n.source_id = s.id
                LEFT JOIN categories c ON n.category_id = c.id
                WHERE ua.user_id = ? AND ua.created_at >= ?
                ORDER BY ua.created_at DESC
            """
            
            df = pd.read_sql_query(query, conn, params=(user_id, cutoff_date))
            conn.close()
            
            # 數據預處理
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
            df['hour'] = df['created_at'].dt.hour
            
            return df
            
        except Exception as e:
            logger.error(f"獲取用戶分析數據失敗: {e}")
            return pd.DataFrame()
    
    def _create_news_trend_chart(self, df: pd.DataFrame, days: int) -> str:
        """創建新聞趨勢分析圖"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 上圖：每日新聞數量趨勢
            daily_counts = df.groupby('date').size()
            daily_counts.plot(kind='line', ax=ax1, color=self.color_palette[0], linewidth=2, marker='o')
            ax1.set_title('每日新聞數量趨勢', fontsize=16, fontweight='bold')
            ax1.set_xlabel('日期', fontsize=12)
            ax1.set_ylabel('新聞數量', fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # 下圖：重要性分佈趨勢
            daily_importance = df.groupby('date')['importance_score'].mean()
            daily_importance.plot(kind='line', ax=ax2, color=self.color_palette[1], linewidth=2, marker='s')
            ax2.set_title('每日平均重要性趨勢', fontsize=16, fontweight='bold')
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('平均重要性分數', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            file_path = self.output_dir / f'news_trend_{days}days.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建新聞趨勢圖失敗: {e}")
            return ""
    
    def _create_importance_pie_chart(self, df: pd.DataFrame) -> str:
        """創建重要性分佈圓餅圖"""
        try:
            # 定義重要性級別
            def importance_level(score):
                if score >= 0.8:
                    return '高重要性 (≥0.8)'
                elif score >= 0.6:
                    return '中重要性 (0.6-0.8)'
                elif score >= 0.4:
                    return '低重要性 (0.4-0.6)'
                else:
                    return '一般 (<0.4)'
            
            df['importance_level'] = df['importance_score'].apply(importance_level)
            importance_counts = df['importance_level'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            wedges, texts, autotexts = ax.pie(
                importance_counts.values, 
                labels=importance_counts.index,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=(0.05, 0.05, 0.05, 0.05)
            )
            
            ax.set_title('新聞重要性分佈', fontsize=16, fontweight='bold')
            
            # 美化文字
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
            
            file_path = self.output_dir / 'importance_distribution.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建重要性分佈圖失敗: {e}")
            return ""
    
    def _create_source_stats_chart(self, df: pd.DataFrame) -> str:
        """創建來源統計圖"""
        try:
            source_stats = df.groupby('source_name').agg({
                'id': 'count',
                'importance_score': 'mean',
                'view_count': 'sum'
            }).round(2)
            
            source_stats.columns = ['新聞數量', '平均重要性', '總瀏覽量']
            source_stats = source_stats.sort_values('新聞數量', ascending=True)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # 左圖：新聞數量
            source_stats['新聞數量'].plot(kind='barh', ax=ax1, color=self.color_palette[0])
            ax1.set_title('各來源新聞數量統計', fontsize=14, fontweight='bold')
            ax1.set_xlabel('新聞數量', fontsize=12)
            
            # 右圖：平均重要性
            source_stats['平均重要性'].plot(kind='barh', ax=ax2, color=self.color_palette[1])
            ax2.set_title('各來源平均重要性', fontsize=14, fontweight='bold')
            ax2.set_xlabel('平均重要性分數', fontsize=12)
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'source_statistics.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建來源統計圖失敗: {e}")
            return ""
    
    def _create_sentiment_chart(self, df: pd.DataFrame) -> str:
        """創建情感分析圖"""
        try:
            sentiment_counts = df['sentiment'].value_counts()
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # 左圖：情感分佈圓餅圖
            colors = ['#28a745', '#6c757d', '#dc3545']  # 綠色正面、灰色中性、紅色負面
            ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, colors=colors,
                   autopct='%1.1f%%', startangle=90)
            ax1.set_title('情感分佈', fontsize=14, fontweight='bold')
            
            # 右圖：每日情感趨勢
            daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
            daily_sentiment.plot(kind='area', stacked=True, ax=ax2, color=colors, alpha=0.7)
            ax2.set_title('每日情感趨勢', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('新聞數量', fontsize=12)
            ax2.legend(title='情感')
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'sentiment_analysis.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建情感分析圖失敗: {e}")
            return ""
    
    def _create_keyword_wordcloud(self, df: pd.DataFrame) -> str:
        """創建關鍵詞雲圖"""
        try:
            # 這裡簡化實現，實際應該使用wordcloud庫
            # 提取標題中的關鍵詞
            from collections import Counter
            import jieba
            
            # 合併所有標題
            all_titles = ' '.join(df['title'].dropna())
            
            # 分詞
            words = jieba.cut(all_titles)
            
            # 過濾停用詞
            stop_words = {'的', '了', '在', '是', '和', '與', '及', '或', '但', '而', '為', '將', '已', '對', '於', '從', '由', '到', '向', '以', '被', '讓', '使', '讓', '把', '給'}
            word_freq = Counter([word for word in words if len(word) > 1 and word not in stop_words])
            
            # 取前20個關鍵詞
            top_words = dict(word_freq.most_common(20))
            
            # 用條形圖代替詞雲（簡化實現）
            fig, ax = plt.subplots(figsize=(12, 8))
            
            words = list(top_words.keys())[:15]  # 只顯示前15個
            frequencies = list(top_words.values())[:15]
            
            bars = ax.barh(words, frequencies, color=self.color_palette[0])
            ax.set_title('熱門關鍵詞統計', fontsize=16, fontweight='bold')
            ax.set_xlabel('出現次數', fontsize=12)
            
            # 添加數值標籤
            for i, (bar, freq) in enumerate(zip(bars, frequencies)):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                       str(freq), ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'keyword_analysis.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建關鍵詞圖失敗: {e}")
            return ""
    
    def _create_category_heatmap(self, df: pd.DataFrame, days: int) -> str:
        """創建分類熱力圖"""
        try:
            # 創建日期-分類的交叉表
            df['weekday'] = df['published_date'].dt.day_name()
            df['hour'] = df['published_date'].dt.hour
            
            # 每小時-每類別的新聞數量
            heatmap_data = df.groupby(['hour', 'category_name']).size().unstack(fill_value=0)
            
            if heatmap_data.empty:
                return ""
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlOrRd', 
                       cbar_kws={'label': '新聞數量'}, ax=ax)
            
            ax.set_title('24小時分類發布熱力圖', fontsize=16, fontweight='bold')
            ax.set_xlabel('新聞分類', fontsize=12)
            ax.set_ylabel('小時', fontsize=12)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            file_path = self.output_dir / 'category_heatmap.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建分類熱力圖失敗: {e}")
            return ""
    
    def _create_user_activity_chart(self, user_df: pd.DataFrame) -> str:
        """創建用戶活動圖"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. 每日活動量
            daily_activity = user_df.groupby('date').size()
            daily_activity.plot(kind='line', ax=ax1, color=self.color_palette[0], marker='o')
            ax1.set_title('每日活動量', fontsize=14, fontweight='bold')
            ax1.set_ylabel('活動次數')
            ax1.grid(True, alpha=0.3)
            
            # 2. 活動類型分佈
            activity_counts = user_df['activity_type'].value_counts()
            ax2.pie(activity_counts.values, labels=activity_counts.index, autopct='%1.1f%%')
            ax2.set_title('活動類型分佈', fontsize=14, fontweight='bold')
            
            # 3. 每小時活動分佈
            hourly_activity = user_df.groupby('hour').size()
            hourly_activity.plot(kind='bar', ax=ax3, color=self.color_palette[1])
            ax3.set_title('每小時活動分佈', fontsize=14, fontweight='bold')
            ax3.set_xlabel('小時')
            ax3.set_ylabel('活動次數')
            
            # 4. 閱讀偏好（新聞來源）
            source_preference = user_df[user_df['activity_type'] == 'view_news']['source_name'].value_counts().head(10)
            source_preference.plot(kind='barh', ax=ax4, color=self.color_palette[2])
            ax4.set_title('偏好新聞來源 (Top 10)', fontsize=14, fontweight='bold')
            ax4.set_xlabel('閱讀次數')
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'user_activity.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建用戶活動圖失敗: {e}")
            return ""
    
    def _create_reading_preference_chart(self, user_df: pd.DataFrame) -> str:
        """創建閱讀偏好分析圖"""
        try:
            # 篩選閱讀活動
            read_activities = user_df[user_df['activity_type'].isin(['view_news', 'read_news'])]
            
            if read_activities.empty:
                return ""
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # 1. 分類偏好
            category_pref = read_activities['category_name'].value_counts().head(8)
            category_pref.plot(kind='pie', ax=ax1, autopct='%1.1f%%', 
                              colors=sns.color_palette("Set3", len(category_pref)))
            ax1.set_title('閱讀分類偏好', fontsize=14, fontweight='bold')
            ax1.set_ylabel('')
            
            # 2. 重要性偏好
            importance_bins = [0, 0.3, 0.6, 0.8, 1.0]
            importance_labels = ['低', '中下', '中上', '高']
            read_activities['importance_level'] = pd.cut(
                read_activities['importance_score'], 
                bins=importance_bins, 
                labels=importance_labels
            )
            importance_pref = read_activities['importance_level'].value_counts()
            importance_pref.plot(kind='bar', ax=ax2, color=self.color_palette[3])
            ax2.set_title('重要性偏好分佈', fontsize=14, fontweight='bold')
            ax2.set_xlabel('重要性級別')
            ax2.set_ylabel('閱讀次數')
            ax2.tick_params(axis='x', rotation=0)
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'reading_preference.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建閱讀偏好圖失敗: {e}")
            return ""
    
    def _create_performance_trend_chart(self, user_df: pd.DataFrame) -> str:
        """創建業務績效趨勢圖"""
        try:
            # 計算每日績效指標
            daily_metrics = user_df.groupby('date').agg({
                'id': 'count',  # 總活動數
                'activity_type': lambda x: (x == 'share_news').sum(),  # 分享數
                'target_id': 'nunique'  # 查看的不同新聞數
            })
            
            daily_metrics.columns = ['總活動數', '分享次數', '閱讀文章數']
            
            # 計算績效分數（簡化算法）
            daily_metrics['績效分數'] = (
                daily_metrics['總活動數'] * 0.3 + 
                daily_metrics['分享次數'] * 0.5 + 
                daily_metrics['閱讀文章數'] * 0.2
            )
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 上圖：活動指標趨勢
            daily_metrics[['總活動數', '分享次數', '閱讀文章數']].plot(
                ax=ax1, marker='o', linewidth=2
            )
            ax1.set_title('每日活動指標趨勢', fontsize=14, fontweight='bold')
            ax1.set_ylabel('次數')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 下圖：績效分數趨勢
            daily_metrics['績效分數'].plot(
                ax=ax2, color=self.color_palette[4], marker='s', linewidth=3
            )
            ax2.set_title('績效分數趨勢', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期')
            ax2.set_ylabel('分數')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'performance_trend.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建績效趨勢圖失敗: {e}")
            return ""
    
    def _create_interactive_dashboard(self, news_df: pd.DataFrame, user_df: Optional[pd.DataFrame] = None) -> str:
        """創建交互式儀表板（Plotly）"""
        try:
            # 創建子圖
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=[
                    '新聞數量趨勢', '重要性分佈',
                    '情感分析', '來源統計',
                    '活動分佈', '績效指標'
                ],
                specs=[
                    [{"secondary_y": False}, {"type": "pie"}],
                    [{"secondary_y": False}, {"secondary_y": False}],
                    [{"type": "pie"}, {"secondary_y": False}]
                ]
            )
            
            # 1. 新聞數量趨勢
            daily_counts = news_df.groupby('date').size()
            fig.add_trace(
                go.Scatter(
                    x=daily_counts.index,
                    y=daily_counts.values,
                    mode='lines+markers',
                    name='新聞數量',
                    line=dict(color='#2E86AB', width=3)
                ),
                row=1, col=1
            )
            
            # 2. 重要性分佈
            importance_counts = news_df.groupby(
                pd.cut(news_df['importance_score'], bins=[0, 0.4, 0.6, 0.8, 1.0], 
                       labels=['低', '中下', '中上', '高'])
            ).size()
            
            fig.add_trace(
                go.Pie(
                    labels=importance_counts.index,
                    values=importance_counts.values,
                    name="重要性分佈"
                ),
                row=1, col=2
            )
            
            # 3. 情感分析
            sentiment_counts = news_df['sentiment'].value_counts()
            fig.add_trace(
                go.Bar(
                    x=sentiment_counts.index,
                    y=sentiment_counts.values,
                    name='情感分析',
                    marker_color=['#28a745', '#6c757d', '#dc3545']
                ),
                row=2, col=1
            )
            
            # 4. 來源統計
            source_counts = news_df['source_name'].value_counts().head(10)
            fig.add_trace(
                go.Bar(
                    x=source_counts.values,
                    y=source_counts.index,
                    orientation='h',
                    name='來源統計'
                ),
                row=2, col=2
            )
            
            if user_df is not None and not user_df.empty:
                # 5. 活動分佈
                activity_counts = user_df['activity_type'].value_counts()
                fig.add_trace(
                    go.Pie(
                        labels=activity_counts.index,
                        values=activity_counts.values,
                        name="活動分佈"
                    ),
                    row=3, col=1
                )
                
                # 6. 每日活動趨勢
                daily_activity = user_df.groupby('date').size()
                fig.add_trace(
                    go.Scatter(
                        x=daily_activity.index,
                        y=daily_activity.values,
                        mode='lines+markers',
                        name='活動數量',
                        line=dict(color='#A23B72', width=3)
                    ),
                    row=3, col=2
                )
            
            # 更新布局
            fig.update_layout(
                height=900,
                showlegend=False,
                title_text="保險新聞聚合器 - 交互式儀表板",
                title_x=0.5,
                title_font_size=20
            )
            
            # 保存為HTML文件
            file_path = self.output_dir / 'interactive_dashboard.html'
            fig.write_html(str(file_path))
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建交互式儀表板失敗: {e}")
            return ""
    
    def generate_report_charts(self, report_type: str = 'weekly', days: int = 7) -> Dict[str, str]:
        """
        生成報告圖表
        
        Args:
            report_type: 報告類型 (daily, weekly, monthly)
            days: 統計天數
            
        Returns:
            圖表文件路徑字典
        """
        chart_paths = {}
        
        try:
            # 獲取數據
            news_data = self._get_news_analytics_data(days)
            
            if news_data.empty:
                logger.warning("沒有找到新聞數據")
                return {}
            
            # 生成報告專用圖表
            chart_paths['summary_stats'] = self._create_summary_stats_chart(news_data, report_type)
            chart_paths['trend_comparison'] = self._create_trend_comparison_chart(news_data, days)
            chart_paths['quality_metrics'] = self._create_quality_metrics_chart(news_data)
            
            logger.info(f"成功生成 {report_type} 報告圖表")
            return chart_paths
            
        except Exception as e:
            logger.error(f"生成報告圖表失敗: {e}")
            return {}
    
    def _create_summary_stats_chart(self, df: pd.DataFrame, report_type: str) -> str:
        """創建摘要統計圖表"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 計算統計數據
            total_news = len(df)
            avg_importance = df['importance_score'].mean()
            high_importance = len(df[df['importance_score'] >= 0.8])
            total_views = df['view_count'].sum()
            
            # 1. 核心指標
            metrics = ['總新聞數', '平均重要性', '高重要性新聞', '總瀏覽量']
            values = [total_news, avg_importance, high_importance, total_views]
            
            bars = ax1.bar(metrics, values, color=self.color_palette[:4])
            ax1.set_title(f'{report_type.title()} 核心指標', fontsize=14, fontweight='bold')
            
            # 添加數值標籤
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.1f}' if isinstance(value, float) else str(value),
                        ha='center', va='bottom', fontweight='bold')
            
            # 2. 每日新聞分佈
            daily_counts = df.groupby('date').size()
            daily_counts.plot(kind='bar', ax=ax2, color=self.color_palette[0])
            ax2.set_title('每日新聞分佈', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期')
            ax2.set_ylabel('新聞數量')
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. 重要性vs瀏覽量散點圖
            ax3.scatter(df['importance_score'], df['view_count'], 
                       alpha=0.6, color=self.color_palette[1])
            ax3.set_xlabel('重要性分數')
            ax3.set_ylabel('瀏覽量')
            ax3.set_title('重要性 vs 瀏覽量關聯', fontsize=14, fontweight='bold')
            
            # 4. 分類統計
            category_stats = df['category_name'].value_counts().head(8)
            category_stats.plot(kind='pie', ax=ax4, autopct='%1.1f%%')
            ax4.set_title('分類分佈', fontsize=14, fontweight='bold')
            ax4.set_ylabel('')
            
            plt.tight_layout()
            
            file_path = self.output_dir / f'summary_stats_{report_type}.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建摘要統計圖失敗: {e}")
            return ""
    
    def _create_trend_comparison_chart(self, df: pd.DataFrame, days: int) -> str:
        """創建趨勢對比圖表"""
        try:
            # 準備對比數據（當前期間 vs 前一期間）
            current_period = df
            
            # 獲取前一期間數據進行對比
            prev_start = datetime.now() - timedelta(days=days*2)
            prev_end = datetime.now() - timedelta(days=days)
            
            # 這裡簡化處理，實際應該查詢前一期間的數據
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # 1. 重要性趨勢對比
            daily_importance = current_period.groupby('date')['importance_score'].mean()
            daily_importance.plot(ax=ax1, label='當前期間', color=self.color_palette[0], linewidth=2)
            
            ax1.set_title('重要性趨勢對比', fontsize=14, fontweight='bold')
            ax1.set_xlabel('日期')
            ax1.set_ylabel('平均重要性')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. 數量趨勢對比
            daily_counts = current_period.groupby('date').size()
            daily_counts.plot(ax=ax2, label='當前期間', color=self.color_palette[1], linewidth=2)
            
            ax2.set_title('新聞數量趨勢對比', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期')
            ax2.set_ylabel('新聞數量')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            file_path = self.output_dir / f'trend_comparison_{days}days.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建趨勢對比圖失敗: {e}")
            return ""
    
    def _create_quality_metrics_chart(self, df: pd.DataFrame) -> str:
        """創建質量指標圖表"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. 重要性分佈直方圖
            ax1.hist(df['importance_score'], bins=20, color=self.color_palette[0], alpha=0.7, edgecolor='black')
            ax1.axvline(df['importance_score'].mean(), color='red', linestyle='--', linewidth=2, label='平均值')
            ax1.set_title('重要性分數分佈', fontsize=14, fontweight='bold')
            ax1.set_xlabel('重要性分數')
            ax1.set_ylabel('新聞數量')
            ax1.legend()
            
            # 2. 瀏覽量分佈
            ax2.hist(df['view_count'], bins=20, color=self.color_palette[1], alpha=0.7, edgecolor='black')
            ax2.axvline(df['view_count'].mean(), color='red', linestyle='--', linewidth=2, label='平均值')
            ax2.set_title('瀏覽量分佈', fontsize=14, fontweight='bold')
            ax2.set_xlabel('瀏覽量')
            ax2.set_ylabel('新聞數量')
            ax2.legend()
            
            # 3. 分享量分佈
            ax3.hist(df['share_count'], bins=20, color=self.color_palette[2], alpha=0.7, edgecolor='black')
            ax3.axvline(df['share_count'].mean(), color='red', linestyle='--', linewidth=2, label='平均值')
            ax3.set_title('分享量分佈', fontsize=14, fontweight='bold')
            ax3.set_xlabel('分享量')
            ax3.set_ylabel('新聞數量')
            ax3.legend()
            
            # 4. 質量評分（綜合指標）
            # 計算質量分數：重要性 * 0.4 + 標準化瀏覽量 * 0.3 + 標準化分享量 * 0.3
            max_views = df['view_count'].max() if df['view_count'].max() > 0 else 1
            max_shares = df['share_count'].max() if df['share_count'].max() > 0 else 1
            
            quality_score = (
                df['importance_score'] * 0.4 + 
                (df['view_count'] / max_views) * 0.3 + 
                (df['share_count'] / max_shares) * 0.3
            )
            
            ax4.hist(quality_score, bins=20, color=self.color_palette[3], alpha=0.7, edgecolor='black')
            ax4.axvline(quality_score.mean(), color='red', linestyle='--', linewidth=2, label='平均值')
            ax4.set_title('綜合質量分數分佈', fontsize=14, fontweight='bold')
            ax4.set_xlabel('質量分數')
            ax4.set_ylabel('新聞數量')
            ax4.legend()
            
            plt.tight_layout()
            
            file_path = self.output_dir / 'quality_metrics.png'
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"創建質量指標圖失敗: {e}")
            return ""
    
    def get_chart_base64(self, chart_path: str) -> str:
        """將圖表轉換為base64編碼（用於網頁顯示）"""
        try:
            with open(chart_path, 'rb') as f:
                chart_data = f.read()
            return base64.b64encode(chart_data).decode()
        except Exception as e:
            logger.error(f"轉換圖表為base64失敗: {e}")
            return ""

# 全域視覺化服務實例
visualization_service = AdvancedVisualization()

if __name__ == "__main__":
    # 測試生成圖表
    charts = visualization_service.generate_business_dashboard_charts(days=30)
    print("生成的圖表:", charts)
