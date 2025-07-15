from flask import Blueprint, render_template, current_app, jsonify, request
from flask_login import login_required, current_user
import os
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/settings')
@login_required
def settings():
    """用戶個人設置頁面"""
    return render_template('user/settings.html')

@user_bp.route('/api/user/settings', methods=['GET'])
@login_required
def get_user_settings():
    """獲取用戶設置"""
    try:
        # 檢查是否有用戶特定的設置文件
        settings_dir = os.path.join(current_app.instance_path, 'user_settings')
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_file = os.path.join(settings_dir, f'user_{current_user.id}.json')
        
        # 如果文件存在則讀取
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return jsonify({'status': 'success', 'data': settings})
        else:
            # 返回默認設置
            default_settings = {
                'theme': 'light',
                'fontSize': 16,
                'dashboardLayout': 'grid',
                'notificationsEnabled': True,
                'autoRefresh': False,
                'refreshInterval': 5,
                'compactView': False
            }
            return jsonify({'status': 'success', 'data': default_settings})
    
    except Exception as e:
        current_app.logger.error(f"獲取用戶設置時出錯: {str(e)}")
        return jsonify({'status': 'error', 'message': '無法獲取設置信息'}), 500

@user_bp.route('/api/user/settings', methods=['POST'])
@login_required
def save_user_settings():
    """保存用戶設置"""
    try:
        # 獲取請求中的設置數據
        settings_data = request.json
        
        if not settings_data:
            return jsonify({'status': 'error', 'message': '未提供設置數據'}), 400
        
        # 創建用戶設置目錄
        settings_dir = os.path.join(current_app.instance_path, 'user_settings')
        os.makedirs(settings_dir, exist_ok=True)
        
        # 保存設置到文件
        settings_file = os.path.join(settings_dir, f'user_{current_user.id}.json')
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'status': 'success', 'message': '設置已成功保存'})
    
    except Exception as e:
        current_app.logger.error(f"保存用戶設置時出錯: {str(e)}")
        return jsonify({'status': 'error', 'message': '無法保存設置'}), 500

@user_bp.route('/api/user/settings/reset', methods=['POST'])
@login_required
def reset_user_settings():
    """重置用戶設置為默認值"""
    try:
        # 設置文件路徑
        settings_dir = os.path.join(current_app.instance_path, 'user_settings')
        settings_file = os.path.join(settings_dir, f'user_{current_user.id}.json')
        
        # 如果文件存在則刪除
        if os.path.exists(settings_file):
            os.remove(settings_file)
        
        return jsonify({'status': 'success', 'message': '設置已重置為默認值'})
    
    except Exception as e:
        current_app.logger.error(f"重置用戶設置時出錯: {str(e)}")
        return jsonify({'status': 'error', 'message': '無法重置設置'}), 500
