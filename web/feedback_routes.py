"""
簡易反饋頁面路由
Simple Feedback Routes

為了測試反饋系統而設計的簡單路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
import os
import json
from datetime import datetime

feedback_test_bp = Blueprint('feedback_test', __name__, url_prefix='/feedback-test')

@feedback_test_bp.route('/', methods=['GET'])
def index():
    """反饋系統首頁"""
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

@feedback_test_bp.route('/submit', methods=['POST'])
def submit():
    """提交反饋（簡單存檔版本）"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '未提供有效數據'}), 400
        
        # 簡單記錄反饋到文件
        feedback_dir = os.path.join(current_app.root_path, '..', 'data', 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # 添加時間戳
        data['timestamp'] = datetime.now().isoformat()
        
        # 存儲到JSON文件
        feedback_file = os.path.join(feedback_dir, f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '反饋提交成功'}), 201
    
    except Exception as e:
        current_app.logger.error(f"提交反饋失敗: {e}")
        return jsonify({'success': False, 'message': f'處理請求時出錯: {str(e)}'}), 500

@feedback_test_bp.route('/thanks', methods=['GET'])
def thanks():
    """感謝頁面"""
    return render_template('feedback/thanks.html')

def register_feedback_test_routes(app):
    """註冊反饋測試藍圖"""
    app.register_blueprint(feedback_test_bp)
    app.logger.info("✅ 反饋測試藍圖註冊成功")
    return app
