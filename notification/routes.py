"""
通知系統路由
Notification System Routes

提供通知管理和推送功能的API端點
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json

# 導入服務模組
from .news_pusher import news_pusher
from notification.notification_service import notification_service

logger = logging.getLogger(__name__)

# 創建通知藍圖
notification_bp = Blueprint('notification', __name__, url_prefix='/notification')

@notification_bp.route('/')
@login_required
def dashboard():
    """通知管理儀表板"""
    try:
        # 獲取推送統計
        push_stats = news_pusher.get_push_statistics()
        
        # 獲取通知歷史
        notification_history = notification_service.get_notification_history(limit=20)
        
        # 獲取推送規則
        rules = news_pusher.rules
        
        return render_template('notification/dashboard.html',
                             push_stats=push_stats,
                             notification_history=notification_history,
                             rules=rules)
        
    except Exception as e:
        logger.error(f"載入通知儀表板失敗: {e}")
        flash(f'載入通知儀表板失敗: {str(e)}', 'error')
        return render_template('notification/dashboard.html',
                             push_stats={},
                             notification_history=[],
                             rules=[])

@notification_bp.route('/api/push/manual', methods=['POST'])
@login_required
def manual_push():
    """手動觸發新聞推送"""
    try:
        data = request.get_json()
        rule_name = data.get('rule_name')
        
        if not rule_name:
            return jsonify({
                'status': 'error',
                'message': '請指定推送規則名稱'
            }), 400
        
        # 找到對應的規則
        target_rule = None
        for rule in news_pusher.rules:
            if rule.name == rule_name:
                target_rule = rule
                break
        
        if not target_rule:
            return jsonify({
                'status': 'error',
                'message': f'找不到規則: {rule_name}'
            }), 404
        
        # 執行推送
        news_pusher.check_and_push_news()
        
        return jsonify({
            'status': 'success',
            'message': f'推送規則 "{rule_name}" 執行成功',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"手動推送失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'推送失敗: {str(e)}'
        }), 500

@notification_bp.route('/api/rules', methods=['GET'])
@login_required
def get_rules():
    """獲取推送規則列表"""
    try:
        rules_data = []
        for rule in news_pusher.rules:
            rules_data.append({
                'name': rule.name,
                'condition': rule.condition,
                'target_users': rule.target_users,
                'notification_methods': rule.notification_methods,
                'enabled': rule.enabled,
                'last_run': rule.last_run.isoformat() if rule.last_run else None
            })
        
        return jsonify({
            'status': 'success',
            'data': rules_data
        })
        
    except Exception as e:
        logger.error(f"獲取推送規則失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'獲取推送規則失敗: {str(e)}'
        }), 500

@notification_bp.route('/api/rules/<rule_name>/toggle', methods=['POST'])
@login_required
def toggle_rule(rule_name: str):
    """切換推送規則的啟用狀態"""
    try:
        # 找到規則
        target_rule = None
        for rule in news_pusher.rules:
            if rule.name == rule_name:
                target_rule = rule
                break
        
        if not target_rule:
            return jsonify({
                'status': 'error',
                'message': f'找不到規則: {rule_name}'
            }), 404
        
        # 切換狀態
        target_rule.enabled = not target_rule.enabled
        
        # 保存配置（這裡需要實現保存邏輯）
        
        return jsonify({
            'status': 'success',
            'message': f'規則 "{rule_name}" 已{"啟用" if target_rule.enabled else "停用"}',
            'enabled': target_rule.enabled
        })
        
    except Exception as e:
        logger.error(f"切換規則狀態失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'操作失敗: {str(e)}'
        }), 500

@notification_bp.route('/api/test', methods=['POST'])
@login_required
def test_notifications():
    """測試通知系統"""
    try:
        data = request.get_json()
        test_type = data.get('type', 'all')  # email, line, webhook, all
        
        results = {}
        
        if test_type in ['email', 'all']:
            # 測試郵件
            test_email = current_user.email if hasattr(current_user, 'email') else 'test@example.com'
            results['email'] = notification_service.send_email(
                [test_email],
                '通知系統測試',
                '這是一封測試郵件，確認通知系統正常運行。',
                '<h2>通知系統測試</h2><p>這是一封測試郵件，確認通知系統正常運行。</p>'
            )
        
        if test_type in ['line', 'all']:
            # 測試LINE
            results['line'] = notification_service.send_line_notification(
                '🔔 通知系統測試\n系統運行正常！'
            )
        
        if test_type in ['webhook', 'all']:
            # 測試Webhook
            results['webhook'] = notification_service.send_webhook_notification({
                'type': 'test',
                'message': '通知系統測試',
                'timestamp': datetime.now().isoformat()
            })
        
        # 統計結果
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        return jsonify({
            'status': 'success',
            'message': f'測試完成: {success_count}/{total_count} 成功',
            'results': results,
            'success_rate': success_count / total_count if total_count > 0 else 0
        })
        
    except Exception as e:
        logger.error(f"測試通知系統失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'測試失敗: {str(e)}'
        }), 500

@notification_bp.route('/api/history')
@login_required
def get_notification_history():
    """獲取通知歷史記錄"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = notification_service.get_notification_history(limit=limit)
        
        return jsonify({
            'status': 'success',
            'data': history,
            'total': len(history)
        })
        
    except Exception as e:
        logger.error(f"獲取通知歷史失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'獲取通知歷史失敗: {str(e)}'
        }), 500

@notification_bp.route('/api/stats')
@login_required
def get_notification_stats():
    """獲取通知統計數據"""
    try:
        # 獲取推送統計
        push_stats = news_pusher.get_push_statistics()
        
        # 獲取通知歷史統計
        history = notification_service.get_notification_history(limit=100)
        
        # 計算成功率
        if history:
            success_count = sum(1 for h in history if h.get('success', False))
            success_rate = success_count / len(history)
        else:
            success_rate = 0
        
        # 按類型統計
        type_stats = {}
        for h in history:
            notif_type = h.get('type', 'unknown')
            if notif_type not in type_stats:
                type_stats[notif_type] = {'total': 0, 'success': 0}
            type_stats[notif_type]['total'] += 1
            if h.get('success', False):
                type_stats[notif_type]['success'] += 1
        
        # 計算各類型成功率
        for notif_type in type_stats:
            stats = type_stats[notif_type]
            stats['success_rate'] = stats['success'] / stats['total'] if stats['total'] > 0 else 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'push_stats': push_stats,
                'notification_stats': {
                    'total_notifications': len(history),
                    'success_rate': success_rate,
                    'type_stats': type_stats
                }
            }
        })
        
    except Exception as e:
        logger.error(f"獲取通知統計失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'獲取統計失敗: {str(e)}'
        }), 500

@notification_bp.route('/api/send/custom', methods=['POST'])
@login_required
def send_custom_notification():
    """發送自定義通知"""
    try:
        data = request.get_json()
        
        # 驗證必要參數
        required_fields = ['recipients', 'subject', 'message', 'methods']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要參數: {field}'
                }), 400
        
        recipients = data['recipients']
        subject = data['subject']
        message = data['message']
        methods = data['methods']
        html_message = data.get('html_message')
        
        results = {}
        
        # 發送郵件
        if 'email' in methods:
            results['email'] = notification_service.send_email(
                recipients if isinstance(recipients, list) else [recipients],
                subject,
                message,
                html_message
            )
        
        # 發送LINE
        if 'line' in methods:
            line_text = f"📧 {subject}\n\n{message}"
            results['line'] = notification_service.send_line_notification(line_text)
        
        # 發送Webhook
        if 'webhook' in methods:
            webhook_data = {
                'type': 'custom_notification',
                'subject': subject,
                'message': message,
                'recipients': recipients,
                'timestamp': datetime.now().isoformat()
            }
            results['webhook'] = notification_service.send_webhook_notification(webhook_data)
        
        # 統計結果
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        return jsonify({
            'status': 'success',
            'message': f'通知發送完成: {success_count}/{total_count} 成功',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"發送自定義通知失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'發送失敗: {str(e)}'
        }), 500

@notification_bp.route('/settings')
@login_required
def settings():
    """通知設定頁面"""
    return render_template('notification/settings.html')

@notification_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    """管理通知設定"""
    if request.method == 'GET':
        # 獲取當前設定
        try:
            # 這裡應該從配置文件或數據庫獲取設定
            current_settings = {
                'email_enabled': notification_service.config.email_enabled,
                'email_smtp_server': notification_service.config.email_smtp_server,
                'email_smtp_port': notification_service.config.email_smtp_port,
                'email_from': notification_service.config.email_from,
                'line_enabled': notification_service.config.line_enabled,
                'webhook_enabled': notification_service.config.webhook_enabled
            }
            
            return jsonify({
                'status': 'success',
                'data': current_settings
            })
            
        except Exception as e:
            logger.error(f"獲取通知設定失敗: {e}")
            return jsonify({
                'status': 'error',
                'message': f'獲取設定失敗: {str(e)}'
            }), 500
    
    else:  # POST
        try:
            data = request.get_json()
            
            # 更新設定
            if 'email_enabled' in data:
                notification_service.config.email_enabled = data['email_enabled']
            if 'email_smtp_server' in data:
                notification_service.config.email_smtp_server = data['email_smtp_server']
            if 'email_smtp_port' in data:
                notification_service.config.email_smtp_port = data['email_smtp_port']
            if 'email_from' in data:
                notification_service.config.email_from = data['email_from']
            if 'line_enabled' in data:
                notification_service.config.line_enabled = data['line_enabled']
            if 'webhook_enabled' in data:
                notification_service.config.webhook_enabled = data['webhook_enabled']
            
            # 這裡應該保存設定到配置文件或數據庫
            
            return jsonify({
                'status': 'success',
                'message': '設定已更新'
            })
            
        except Exception as e:
            logger.error(f"更新通知設定失敗: {e}")
            return jsonify({
                'status': 'error',
                'message': f'更新設定失敗: {str(e)}'
            }), 500

# 錯誤處理
@notification_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': '找不到請求的資源'
    }), 404

@notification_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': '服務器內部錯誤'
    }), 500

# 註冊藍圖的函數
def register_notification_blueprint(app):
    """註冊通知藍圖到Flask應用"""
    app.register_blueprint(notification_bp)