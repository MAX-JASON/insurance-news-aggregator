"""
簡易反饋模塊
Simple Feedback Module

為保險新聞聚合器提供簡易反饋功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
import os
import json
import logging
from datetime import datetime

# 創建日誌
logger = logging.getLogger('feedback_simple')

# 創建藍圖
feedback_simple_bp = Blueprint('feedback_simple', __name__, url_prefix='/feedback-simple')

@feedback_simple_bp.route('/', methods=['GET'])
def index():
    """反饋表單首頁"""
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
    return render_template('feedback/form.html', categories=categories, features=features)

@feedback_simple_bp.route('/submit', methods=['POST'])
def submit():
    """處理反饋表單提交"""
    try:
        category = request.form.get('category')
        rating = request.form.get('rating')
        message = request.form.get('message', '')
        features = request.form.getlist('features[]')
        
        # 記錄反饋
        logger.info(f"收到用戶反饋 - 類別: {category}, 評分: {rating}, 特性: {features}, 訊息: {message}")
        
        # 儲存反饋到檔案
        feedback_data = {
            'category': category,
            'rating': rating,
            'message': message,
            'features': features,
            'timestamp': datetime.now().isoformat()
        }
        
        # 創建反饋資料夾
        feedback_dir = os.path.join(current_app.root_path, '..', 'data', 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # 儲存反饋
        feedback_file = os.path.join(feedback_dir, f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        
        # 回傳成功
        return redirect(url_for('feedback_simple.thanks'))
    
    except Exception as e:
        logger.error(f"處理反饋失敗: {e}")
        return render_template('errors/500.html', error=str(e)), 500

@feedback_simple_bp.route('/thanks', methods=['GET'])
def thanks():
    """感謝頁面"""
    return render_template('feedback/thanks.html')

def register_feedback_simple(app):
    """註冊簡易反饋藍圖"""
    app.register_blueprint(feedback_simple_bp)
    app.logger.info("✅ 簡易反饋藍圖註冊成功")
    
    # 從主頁面重定向到反饋頁面
    @app.route('/feedback')
    def feedback_redirect():
        return redirect(url_for('feedback_simple.index'))
    
    return app
