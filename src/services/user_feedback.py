"""
實時用戶反饋收集系統
Realtime User Feedback Collection System

用於收集和分析用戶對系統的反饋
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加路徑到系統路徑
sys.path.insert(0, str(BASE_DIR))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'feedback.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('feedback')

# 導入資料庫模型
from database.models import db, Feedback, User

# 創建藍圖
feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

class FeedbackManager:
    """用戶反饋管理類"""
    
    def __init__(self, db_session=None):
        """初始化反饋管理器
        
        Args:
            db_session: 資料庫會話
        """
        self.db = db_session or db.session
        self.feedback_path = os.path.join(BASE_DIR, 'data', 'feedback')
        os.makedirs(self.feedback_path, exist_ok=True)
        
        # 創建圖表輸出目錄
        self.charts_path = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'web', 'static', 'charts', 'feedback')
        os.makedirs(self.charts_path, exist_ok=True)
    
    def add_feedback(self, user_id, category, rating, message, features=None, source=None, metadata=None):
        """添加新的用戶反饋
        
        Args:
            user_id: 用戶ID
            category: 反饋類別
            rating: 評分 (1-5)
            message: 反饋消息
            features: 相關功能列表
            source: 反饋來源
            metadata: 附加元數據
            
        Returns:
            新建的反饋對象
        """
        try:
            # 驗證參數
            if not user_id or not category:
                logger.error("添加反饋失敗：缺少必要參數")
                return None
                
            if rating not in range(1, 6):
                logger.error(f"添加反饋失敗：無效的評分 {rating}")
                return None
            
            # 創建反饋對象
            feedback = Feedback(
                user_id=user_id,
                category=category,
                rating=rating,
                message=message or '',
                features=json.dumps(features or []),
                source=source or 'web',
                metadata=json.dumps(metadata or {}),
                timestamp=datetime.datetime.now()
            )
            
            # 保存到資料庫
            self.db.add(feedback)
            self.db.commit()
            
            logger.info(f"成功添加用戶 {user_id} 的反饋，ID: {feedback.id}")
            return feedback
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加反饋失敗: {e}")
            return None
    
    def get_feedback(self, feedback_id):
        """根據ID獲取反饋
        
        Args:
            feedback_id: 反饋ID
            
        Returns:
            反饋對象
        """
        try:
            return Feedback.query.get(feedback_id)
        except Exception as e:
            logger.error(f"獲取反饋失敗: {e}")
            return None
    
    def get_user_feedback(self, user_id, limit=10, offset=0):
        """獲取用戶的反饋列表
        
        Args:
            user_id: 用戶ID
            limit: 限制數量
            offset: 偏移量
            
        Returns:
            反饋對象列表
        """
        try:
            return Feedback.query.filter_by(user_id=user_id) \
                .order_by(Feedback.timestamp.desc()) \
                .limit(limit) \
                .offset(offset) \
                .all()
        except Exception as e:
            logger.error(f"獲取用戶反饋失敗: {e}")
            return []
    
    def get_feedback_by_category(self, category, limit=50, offset=0):
        """根據類別獲取反饋
        
        Args:
            category: 反饋類別
            limit: 限制數量
            offset: 偏移量
            
        Returns:
            反饋對象列表
        """
        try:
            return Feedback.query.filter_by(category=category) \
                .order_by(Feedback.timestamp.desc()) \
                .limit(limit) \
                .offset(offset) \
                .all()
        except Exception as e:
            logger.error(f"獲取類別反饋失敗: {e}")
            return []
    
    def get_feedback_stats(self):
        """獲取反饋統計信息
        
        Returns:
            統計信息字典
        """
        try:
            # 獲取總反饋數
            total_count = Feedback.query.count()
            
            # 按類別統計
            category_stats = db.session.query(
                Feedback.category, db.func.count(Feedback.id), db.func.avg(Feedback.rating)
            ).group_by(Feedback.category).all()
            
            # 按評分統計
            rating_stats = db.session.query(
                Feedback.rating, db.func.count(Feedback.id)
            ).group_by(Feedback.rating).all()
            
            # 計算平均評分
            avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar() or 0
            
            # 生成統計數據
            stats = {
                'total_count': total_count,
                'avg_rating': float(avg_rating),
                'categories': {cat: {'count': count, 'avg_rating': float(avg)} for cat, count, avg in category_stats},
                'ratings': {rating: count for rating, count in rating_stats}
            }
            
            logger.info("成功生成反饋統計信息")
            return stats
            
        except Exception as e:
            logger.error(f"獲取反饋統計信息失敗: {e}")
            return {
                'total_count': 0,
                'avg_rating': 0,
                'categories': {},
                'ratings': {}
            }
    
    def export_feedback_data(self, format='json'):
        """導出反饋數據
        
        Args:
            format: 導出格式 (json, csv)
            
        Returns:
            導出文件路徑
        """
        try:
            # 獲取所有反饋
            feedbacks = Feedback.query.all()
            
            # 轉換為字典列表
            data = []
            for fb in feedbacks:
                try:
                    features = json.loads(fb.features) if fb.features else []
                    metadata = json.loads(fb.metadata) if fb.metadata else {}
                except:
                    features = []
                    metadata = {}
                
                data.append({
                    'id': fb.id,
                    'user_id': fb.user_id,
                    'category': fb.category,
                    'rating': fb.rating,
                    'message': fb.message,
                    'features': features,
                    'source': fb.source,
                    'metadata': metadata,
                    'timestamp': fb.timestamp.isoformat() if fb.timestamp else None
                })
            
            # 導出文件路徑
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format.lower() == 'json':
                # 導出為JSON
                filepath = os.path.join(self.feedback_path, f'feedback_export_{timestamp}.json')
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
            elif format.lower() == 'csv':
                # 導出為CSV
                filepath = os.path.join(self.feedback_path, f'feedback_export_{timestamp}.csv')
                
                # 展平列表和字典字段
                flat_data = []
                for item in data:
                    flat_item = item.copy()
                    flat_item['features'] = ', '.join(item['features'])
                    flat_item['metadata'] = str(item['metadata'])
                    flat_data.append(flat_item)
                
                df = pd.DataFrame(flat_data)
                df.to_csv(filepath, index=False, encoding='utf-8')
            
            else:
                logger.error(f"不支持的導出格式: {format}")
                return None
            
            logger.info(f"成功導出反饋數據至: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"導出反饋數據失敗: {e}")
            return None
    
    def generate_feedback_charts(self):
        """生成反饋數據圖表
        
        Returns:
            生成的圖表文件路徑列表
        """
        try:
            # 獲取所有反饋
            feedbacks = Feedback.query.all()
            
            if not feedbacks:
                logger.warning("沒有反饋數據，無法生成圖表")
                return []
            
            # 轉換為DataFrame
            data = []
            for fb in feedbacks:
                try:
                    features = json.loads(fb.features) if fb.features else []
                    metadata = json.loads(fb.metadata) if fb.metadata else {}
                except:
                    features = []
                    metadata = {}
                
                data.append({
                    'id': fb.id,
                    'user_id': fb.user_id,
                    'category': fb.category,
                    'rating': fb.rating,
                    'message': fb.message,
                    'features': features,
                    'source': fb.source,
                    'timestamp': fb.timestamp
                })
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning("反饋數據為空，無法生成圖表")
                return []
            
            chart_files = []
            
            # 設置圖表風格
            plt.style.use('seaborn-v0_8')
            
            # 生成評分分佈圖
            chart_file = self._generate_rating_distribution_chart(df)
            if chart_file:
                chart_files.append(chart_file)
            
            # 生成類別評分對比圖
            chart_file = self._generate_category_rating_chart(df)
            if chart_file:
                chart_files.append(chart_file)
            
            # 生成反饋時間趨勢圖
            chart_file = self._generate_feedback_trend_chart(df)
            if chart_file:
                chart_files.append(chart_file)
            
            # 生成詞雲
            chart_file = self._generate_feedback_wordcloud(df)
            if chart_file:
                chart_files.append(chart_file)
            
            logger.info(f"成功生成 {len(chart_files)} 個反饋圖表")
            return chart_files
            
        except Exception as e:
            logger.error(f"生成反饋圖表失敗: {e}")
            return []
    
    def _generate_rating_distribution_chart(self, df):
        """生成評分分佈圖
        
        Args:
            df: 反饋數據DataFrame
            
        Returns:
            圖表文件路徑
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 統計各評分數量
            rating_counts = df['rating'].value_counts().sort_index()
            
            # 設置顏色映射
            colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60']
            color_map = {i+1: color for i, color in enumerate(colors)}
            
            # 繪製柱狀圖
            sns.barplot(x=rating_counts.index, y=rating_counts.values, 
                       palette=[color_map[x] for x in rating_counts.index], ax=ax)
            
            # 添加數據標籤
            for i, v in enumerate(rating_counts.values):
                ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
            
            # 設置圖表標題和標籤
            ax.set_title('用戶評分分佈', fontsize=16)
            ax.set_xlabel('評分', fontsize=14)
            ax.set_ylabel('數量', fontsize=14)
            ax.set_xticks(range(5))
            ax.set_xticklabels(['1星', '2星', '3星', '4星', '5星'])
            
            # 添加平均分標註
            avg_rating = df['rating'].mean()
            ax.axvline(avg_rating - 1, color='#3498db', linestyle='--', linewidth=2)
            ax.text(avg_rating - 1, ax.get_ylim()[1] * 0.9, f'平均分: {avg_rating:.2f}', 
                   color='#3498db', fontweight='bold', ha='center', backgroundcolor='white',
                   bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
            
            plt.tight_layout()
            
            # 保存圖表
            output_file = os.path.join(self.charts_path, 'rating_distribution.png')
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"成功生成評分分佈圖: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"生成評分分佈圖失敗: {e}")
            return None
    
    def _generate_category_rating_chart(self, df):
        """生成類別評分對比圖
        
        Args:
            df: 反饋數據DataFrame
            
        Returns:
            圖表文件路徑
        """
        try:
            # 確保有足夠的類別數據
            if df['category'].nunique() < 2:
                logger.warning("類別數據不足，無法生成類別評分對比圖")
                return None
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 計算每個類別的評分統計
            category_stats = df.groupby('category')['rating'].agg(['mean', 'count', 'std']).reset_index()
            category_stats = category_stats.sort_values('mean', ascending=False)
            
            # 設置顏色
            cmap = plt.cm.get_cmap('viridis', len(category_stats))
            colors = [cmap(i) for i in range(len(category_stats))]
            
            # 繪製類別平均評分柱狀圖
            bars = ax.bar(category_stats['category'], category_stats['mean'], 
                         yerr=category_stats['std'], 
                         capsize=10, color=colors, alpha=0.7)
            
            # 添加數據標籤
            for i, bar in enumerate(bars):
                height = bar.get_height()
                count = category_stats.iloc[i]['count']
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height:.2f}\n(n={count})', ha='center', va='bottom', fontweight='bold')
            
            # 設置圖表標題和標籤
            ax.set_title('各類別反饋評分對比', fontsize=16)
            ax.set_xlabel('反饋類別', fontsize=14)
            ax.set_ylabel('平均評分', fontsize=14)
            ax.set_ylim(0, 5.5)  # 評分範圍為1-5
            
            # 旋轉X軸標籤
            plt.xticks(rotation=45, ha='right')
            
            # 添加水平參考線
            ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            
            # 保存圖表
            output_file = os.path.join(self.charts_path, 'category_rating.png')
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"成功生成類別評分對比圖: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"生成類別評分對比圖失敗: {e}")
            return None
    
    def _generate_feedback_trend_chart(self, df):
        """生成反饋時間趨勢圖
        
        Args:
            df: 反饋數據DataFrame
            
        Returns:
            圖表文件路徑
        """
        try:
            # 確保時間戳列存在
            if 'timestamp' not in df.columns or df['timestamp'].isna().all():
                logger.warning("時間戳數據不足，無法生成反饋時間趨勢圖")
                return None
            
            # 創建日期列
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            
            # 按日期分組計算每日反饋數量和平均評分
            daily_stats = df.groupby('date').agg({
                'id': 'count',
                'rating': 'mean'
            }).reset_index()
            
            daily_stats.columns = ['date', 'count', 'avg_rating']
            daily_stats['date'] = pd.to_datetime(daily_stats['date'])
            
            # 確保有足夠的日期數據
            if len(daily_stats) < 2:
                logger.warning("日期數據不足，無法生成反饋時間趨勢圖")
                return None
            
            # 創建子圖
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
            
            # 繪製每日反饋數量折線圖
            ax1.plot(daily_stats['date'], daily_stats['count'], marker='o', color='#3498db', linewidth=2, markersize=8)
            ax1.set_title('每日反饋數量趨勢', fontsize=16)
            ax1.set_ylabel('反饋數量', fontsize=14)
            ax1.grid(True, alpha=0.3)
            
            # 添加數據點標籤
            for i, row in daily_stats.iterrows():
                ax1.text(row['date'], row['count'] + 0.3, str(row['count']), 
                        ha='center', va='bottom', fontweight='bold')
            
            # 繪製每日平均評分折線圖
            ax2.plot(daily_stats['date'], daily_stats['avg_rating'], marker='s', color='#e67e22', linewidth=2, markersize=8)
            ax2.set_title('每日平均評分趨勢', fontsize=16)
            ax2.set_ylabel('平均評分', fontsize=14)
            ax2.set_xlabel('日期', fontsize=14)
            ax2.set_ylim(0, 5.5)  # 評分範圍為1-5
            ax2.grid(True, alpha=0.3)
            
            # 添加平均評分參考線
            overall_avg = df['rating'].mean()
            ax2.axhline(y=overall_avg, color='#e74c3c', linestyle='--', alpha=0.7)
            ax2.text(daily_stats['date'].iloc[-1], overall_avg + 0.1, 
                    f'總體平均: {overall_avg:.2f}', color='#e74c3c', fontweight='bold',
                    ha='right', va='bottom')
            
            # 添加數據點標籤
            for i, row in daily_stats.iterrows():
                ax2.text(row['date'], row['avg_rating'] + 0.1, f'{row["avg_rating"]:.2f}', 
                        ha='center', va='bottom', fontweight='bold')
            
            # 格式化X軸日期
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            # 保存圖表
            output_file = os.path.join(self.charts_path, 'feedback_trend.png')
            plt.savefig(output_file, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"成功生成反饋時間趨勢圖: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"生成反饋時間趨勢圖失敗: {e}")
            return None
    
    def _generate_feedback_wordcloud(self, df):
        """生成反饋詞雲
        
        Args:
            df: 反饋數據DataFrame
            
        Returns:
            圖表文件路徑
        """
        try:
            # 確保消息列存在且不為空
            if 'message' not in df.columns or df['message'].isna().all() or df['message'].str.strip().eq('').all():
                logger.warning("消息數據不足，無法生成反饋詞雲")
                return None
            
            # 合併所有反饋消息
            all_text = ' '.join(df['message'].dropna().astype(str).tolist())
            
            if not all_text.strip():
                logger.warning("反饋文本為空，無法生成詞雲")
                return None
            
            # 創建詞雲
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=200,
                contour_width=3,
                contour_color='steelblue',
                font_path='simsun.ttc' if os.path.exists('/usr/share/fonts/truetype/arphic/uming.ttc') else None,
                collocations=False
            ).generate(all_text)
            
            # 繪製詞雲
            fig, ax = plt.subplots(figsize=(16, 8))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('用戶反饋關鍵詞雲', fontsize=20)
            
            plt.tight_layout()
            
            # 保存圖表
            output_file = os.path.join(self.charts_path, 'feedback_wordcloud.png')
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"成功生成反饋詞雲: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"生成反饋詞雲失敗: {e}")
            return None

# 定義路由

@feedback_bp.route('/thank-you', methods=['GET'])
def thank_you():
    """感謝頁面"""
    return render_template('feedback/thank_you.html')

@feedback_bp.route('/submit', methods=['POST'])
def submit_feedback():
    """提交反饋"""
    try:
        # 獲取請求數據
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        if not data:
            return jsonify({'success': False, 'message': '未提供有效數據'}), 400
        
        # 檢查必填字段
        required_fields = ['category', 'rating']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': '缺少必填字段'}), 400
        
        # 獲取用戶ID
        user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else data.get('user_id')
        
        if not user_id:
            user_id = 0  # 匿名用戶
        
        # 處理特徵列表
        features = data.get('features', [])
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except:
                features = [features]
        
        # 處理元數據
        metadata = data.get('metadata', {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {'raw': metadata}
        
        # 創建反饋管理器
        feedback_manager = FeedbackManager()
        
        # 添加反饋
        feedback = feedback_manager.add_feedback(
            user_id=user_id,
            category=data.get('category'),
            rating=int(data.get('rating')),
            message=data.get('message', ''),
            features=features,
            source=data.get('source', 'web'),
            metadata=metadata
        )
        
        if feedback:
            # 如果是AJAX請求，返回JSON響應
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': '反饋提交成功',
                    'id': feedback.id
                }), 201
            else:
                # 否則重定向到感謝頁面
                return redirect(url_for('feedback.thank_you'))
        else:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '反饋提交失敗'}), 500
            else:
                return render_template('errors/500.html'), 500
            
    except Exception as e:
        logger.error(f"提交反饋失敗: {e}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': f'處理請求時出錯: {str(e)}'}), 500
        else:
            return render_template('errors/500.html'), 500

@feedback_bp.route('/list', methods=['GET'])
@login_required
def list_feedback():
    """列出反饋"""
    try:
        # 檢查用戶是否有權限查看
        if not current_user.is_admin:
            return render_template('errors/403.html', message='權限不足'), 403
        
        # 獲取分頁和篩選參數
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        rating = request.args.get('rating', '')
        timeframe = request.args.get('timeframe', '')
        feature = request.args.get('feature', '')
        search = request.args.get('search', '')
        
        # 每頁顯示數量
        per_page = 20
        
        # 創建查詢
        query = Feedback.query
        
        # 應用篩選
        if category:
            query = query.filter(Feedback.category == category)
            
        if rating:
            query = query.filter(Feedback.rating >= int(rating))
            
        if timeframe:
            today = datetime.datetime.now().date()
            if timeframe == 'today':
                query = query.filter(func.date(Feedback.timestamp) == today)
            elif timeframe == 'week':
                week_ago = today - datetime.timedelta(days=7)
                query = query.filter(func.date(Feedback.timestamp) >= week_ago)
            elif timeframe == 'month':
                month_ago = today - datetime.timedelta(days=30)
                query = query.filter(func.date(Feedback.timestamp) >= month_ago)
        
        if feature:
            # 這裡需要使用LIKE查詢，因為features是JSON字串
            query = query.filter(Feedback.features.like(f'%{feature}%'))
            
        if search:
            query = query.filter(Feedback.message.like(f'%{search}%'))
        
        # 排序 - 最新的優先
        query = query.order_by(Feedback.timestamp.desc())
        
        # 分頁
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 準備顯示數據
        feedbacks = []
        for fb in pagination.items:
            try:
                features = json.loads(fb.features) if fb.features else []
            except:
                features = []
            
            # 查詢用戶名稱
            user = User.query.get(fb.user_id)
            username = user.username if user else f'匿名用戶_{fb.user_id}'
            
            feedbacks.append({
                'id': fb.id,
                'username': username,
                'category': fb.category,
                'rating': fb.rating,
                'message': fb.message,
                'features': features,
                'source': fb.source,
                'timestamp': fb.timestamp.strftime('%Y-%m-%d %H:%M:%S') if fb.timestamp else ''
            })
        
        # 獲取類別和功能選項
        categories = [
            {'id': 'ui', 'name': '用戶界面'},
            {'id': 'crawler', 'name': '爬蟲功能'},
            {'id': 'analyzer', 'name': '分析功能'},
            {'id': 'recommendation', 'name': '推薦功能'},
            {'id': 'optimization', 'name': '系統效能'},
            {'id': 'other', 'name': '其他'}
        ]
        
        features = [
            {'id': 'news_list', 'name': '新聞列表'},
            {'id': 'news_detail', 'name': '新聞詳情'},
            {'id': 'search', 'name': '搜索功能'},
            {'id': 'filter', 'name': '篩選功能'},
            {'id': 'analytics', 'name': '分析圖表'},
            {'id': 'recommendation', 'name': '推薦系統'},
            {'id': 'notification', 'name': '通知功能'},
            {'id': 'export', 'name': '導出功能'},
            {'id': 'user_profile', 'name': '用戶資料'},
            {'id': 'performance', 'name': '系統效能'}
        ]
        
        # 當前篩選條件
        current_filters = {
            'category': category,
            'rating': rating,
            'timeframe': timeframe,
            'feature': feature,
            'search': search
        }
        
        return render_template(
            'feedback/list.html',
            feedbacks=feedbacks,
            pagination=pagination,
            categories=categories,
            features=features,
            current_filters=current_filters
        )
            
    except Exception as e:
        logger.error(f"列出反饋失敗: {e}")
        return render_template('errors/500.html'), 500

@feedback_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """獲取反饋統計信息"""
    try:
        # 檢查用戶是否有權限查看
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '權限不足'}), 403
        
        # 創建反饋管理器
        feedback_manager = FeedbackManager()
        
        # 獲取統計信息
        stats = feedback_manager.get_feedback_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
            
    except Exception as e:
        logger.error(f"獲取統計信息失敗: {e}")
        return jsonify({'success': False, 'message': f'處理請求時出錯: {str(e)}'}), 500

@feedback_bp.route('/export', methods=['GET'])
@login_required
def export_feedback():
    """導出反饋數據"""
    try:
        # 檢查用戶是否有權限導出
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '權限不足'}), 403
        
        # 獲取導出格式
        format = request.args.get('format', 'json')
        
        # 創建反饋管理器
        feedback_manager = FeedbackManager()
        
        # 導出數據
        filepath = feedback_manager.export_feedback_data(format)
        
        if filepath:
            return jsonify({
                'success': True,
                'message': '數據導出成功',
                'filepath': filepath
            }), 200
        else:
            return jsonify({'success': False, 'message': '數據導出失敗'}), 500
            
    except Exception as e:
        logger.error(f"導出反饋數據失敗: {e}")
        return jsonify({'success': False, 'message': f'處理請求時出錯: {str(e)}'}), 500

@feedback_bp.route('/charts', methods=['GET'])
@login_required
def generate_charts():
    """生成反饋圖表"""
    try:
        # 檢查用戶是否有權限生成圖表
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '權限不足'}), 403
        
        # 創建反饋管理器
        feedback_manager = FeedbackManager()
        
        # 生成圖表
        chart_files = feedback_manager.generate_feedback_charts()
        
        if chart_files:
            return jsonify({
                'success': True,
                'message': '圖表生成成功',
                'charts': chart_files
            }), 200
        else:
            return jsonify({'success': False, 'message': '圖表生成失敗，可能是數據不足'}), 500
            
    except Exception as e:
        logger.error(f"生成反饋圖表失敗: {e}")
        return jsonify({'success': False, 'message': f'處理請求時出錯: {str(e)}'}), 500

@feedback_bp.route('/form', methods=['GET'])
def feedback_form():
    """反饋表單頁面"""
    return render_template(
        'feedback/form.html',
        categories=[
            {'id': 'ui', 'name': '用戶界面'},
            {'id': 'crawler', 'name': '爬蟲功能'},
            {'id': 'analyzer', 'name': '分析功能'},
            {'id': 'recommendation', 'name': '推薦功能'},
            {'id': 'optimization', 'name': '系統效能'},
            {'id': 'other', 'name': '其他'}
        ],
        features=[
            {'id': 'news_list', 'name': '新聞列表'},
            {'id': 'news_detail', 'name': '新聞詳情'},
            {'id': 'search', 'name': '搜索功能'},
            {'id': 'filter', 'name': '篩選功能'},
            {'id': 'analytics', 'name': '分析圖表'},
            {'id': 'recommendation', 'name': '推薦系統'},
            {'id': 'notification', 'name': '通知功能'},
            {'id': 'export', 'name': '導出功能'},
            {'id': 'user_profile', 'name': '用戶資料'},
            {'id': 'performance', 'name': '系統效能'}
        ]
    )

@feedback_bp.route('/dashboard', methods=['GET'])
@login_required
def feedback_dashboard():
    """反饋儀表板頁面"""
    # 檢查用戶是否有權限查看
    if not current_user.is_admin:
        return render_template('errors/403.html', message='權限不足'), 403
    
    # 創建反饋管理器
    feedback_manager = FeedbackManager()
    
    # 獲取統計信息
    stats = feedback_manager.get_feedback_stats()
    
    # 生成圖表
    feedback_manager.generate_feedback_charts()
    
    # 獲取最新反饋
    latest_feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).limit(10).all()
    
    # 格式化最新反饋
    latest_feedback_data = []
    for fb in latest_feedbacks:
        user = User.query.get(fb.user_id)
        username = user.username if user else f'匿名用戶_{fb.user_id}'
        
        latest_feedback_data.append({
            'id': fb.id,
            'username': username,
            'category': fb.category,
            'rating': fb.rating,
            'message': fb.message,
            'timestamp': fb.timestamp.strftime('%Y-%m-%d %H:%M:%S') if fb.timestamp else ''
        })
    
    # 添加今日和低評分統計
    # 計算今日反饋數量
    today = datetime.now().date()
    stats['today_count'] = Feedback.query.filter(
        func.date(Feedback.timestamp) == today
    ).count()
    
    # 計算低評分反饋數量 (評分<=2)
    stats['low_rating_count'] = Feedback.query.filter(
        Feedback.rating <= 2
    ).count()
    
    # 渲染模板
    return render_template(
        'feedback/dashboard.html',
        stats=stats,
        latest_feedbacks=latest_feedback_data,
        charts={
            'rating_distribution': '/static/charts/feedback/rating_distribution.png',
            'category_rating': '/static/charts/feedback/category_rating.png',
            'feedback_trend': '/static/charts/feedback/feedback_trend.png',
            'feedback_wordcloud': '/static/charts/feedback/feedback_wordcloud.png'
        }
    )

# 修改資料庫模型
def init_feedback_model():
    """確保反饋模型存在於資料庫中"""
    # 該函數在應用啟動時由app/__init__.py調用
    try:
        # 如果模型尚未在資料庫中定義，則會自動創建
        db.create_all()
        logger.info("反饋模型初始化完成")
    except Exception as e:
        logger.error(f"初始化反饋模型失敗: {e}")

# 註冊藍圖
def register_feedback_blueprint(app):
    """向Flask應用註冊反饋藍圖"""
    app.register_blueprint(feedback_bp)
    logger.info("反饋藍圖已註冊")
    
    # 初始化模型
    with app.app_context():
        init_feedback_model()
        
    return app
