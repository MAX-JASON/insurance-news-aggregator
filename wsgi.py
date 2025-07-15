#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
雲端部署啟動器 - 簡化版
Cloud Deployment Launcher - Simplified
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
import threading
import time

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 設置基本日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('cloud_app')

# 全局資料庫對象
db = SQLAlchemy()

def create_app():
    """創建簡化的雲端應用"""
    # 設置模板和靜態文件目錄
    template_dir = os.path.join(current_dir, 'templates')  # 簡化模板路徑
    static_dir = os.path.join(current_dir, 'web', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # 基本配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-insurance-news')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # 資料庫配置
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # 使用 SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance_news.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化資料庫
    db.init_app(app)
    
    # 定義基本的資料庫模型
    class News(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(500), nullable=False)
        content = db.Column(db.Text)
        url = db.Column(db.String(1000))
        source = db.Column(db.String(200))
        category = db.Column(db.String(100))
        published_date = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        importance_score = db.Column(db.Float, default=0.0)
        
        def to_dict(self):
            return {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'url': self.url,
                'source': self.source,
                'category': self.category,
                'published_date': self.published_date.isoformat() if self.published_date else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'importance_score': self.importance_score
            }
    
    # 註冊路由
    register_routes(app, News)
    
    # 創建資料庫表
    with app.app_context():
        db.create_all()
        # 如果沒有數據，創建一些示例數據
        if News.query.count() == 0:
            create_sample_data(News)
    
    return app

def create_sample_data(News):
    """創建示例數據"""
    sample_news = [
        {
            'title': '金管會發布保險業數位轉型指導方針',
            'content': '金融監督管理委員會今日發布保險業數位轉型指導方針，鼓勵保險公司積極投入數位化服務...',
            'source': '金管會官網',
            'category': '政策法規',
            'importance_score': 8.5,
            'published_date': datetime.now() - timedelta(hours=2)
        },
        {
            'title': '台灣人壽推出新型態投資型保險商品',
            'content': '台灣人壽宣布推出結合ESG投資概念的新型態投資型保險商品，預計將吸引重視永續投資的客戶...',
            'source': '經濟日報',
            'category': '商品資訊',
            'importance_score': 7.2,
            'published_date': datetime.now() - timedelta(hours=5)
        },
        {
            'title': '保險業去年獲利創新高 總資產突破30兆',
            'content': '根據金管會統計，國內保險業去年總獲利達到歷史新高，總資產規模首次突破30兆元大關...',
            'source': '工商時報',
            'category': '市場分析',
            'importance_score': 9.1,
            'published_date': datetime.now() - timedelta(days=1)
        },
        {
            'title': '疫情後保險需求轉變 健康險成長顯著',
            'content': '新冠疫情改變民眾對保險的認知，健康險、醫療險需求大幅增加，成為保險市場新的成長動能...',
            'source': '聯合報',
            'category': '市場分析',
            'importance_score': 8.0,
            'published_date': datetime.now() - timedelta(days=2)
        }
    ]
    
    for news_data in sample_news:
        news = News(**news_data)
        db.session.add(news)
    
    db.session.commit()
    logger.info("✅ 示例數據創建完成")

def register_routes(app, News):
    """註冊路由"""
    
    @app.route('/')
    def index():
        """首頁"""
        return render_template('simple_index.html')
    
    @app.route('/business')
    def business_dashboard():
        """業務員儀表板"""
        return render_template('simple_index.html')
    
    @app.route('/analysis')
    def analysis_dashboard():
        """分析儀表板"""
        return render_template('simple_index.html')
    
    @app.route('/api/health')
    def api_health():
        """健康檢查"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/news')
    def api_news():
        """獲取新聞列表"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        
        query = News.query.order_by(News.created_at.desc())
        
        if category:
            query = query.filter(News.category == category)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'news': [news.to_dict() for news in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    
    @app.route('/api/news/<int:news_id>')
    def api_news_detail(news_id):
        """獲取新聞詳情"""
        news = News.query.get_or_404(news_id)
        return jsonify({
            'status': 'success',
            'data': news.to_dict()
        })
    
    @app.route('/api/stats')
    def api_stats():
        """獲取統計信息"""
        total_news = News.query.count()
        today = datetime.now().date()
        today_news = News.query.filter(
            db.func.date(News.created_at) == today
        ).count()
        
        # 分類統計
        categories = db.session.query(
            News.category, 
            db.func.count(News.id).label('count')
        ).group_by(News.category).all()
        
        # 來源統計
        sources = db.session.query(
            News.source, 
            db.func.count(News.id).label('count')
        ).group_by(News.source).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_news': total_news,
                'today_news': today_news,
                'categories': [{'name': cat, 'count': count} for cat, count in categories],
                'sources': [{'name': source, 'count': count} for source, count in sources]
            }
        })
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

# 創建應用實例（供 WSGI 伺服器使用）
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
