"""
高級可視化路由
Advanced Visualization Routes

提供進階數據視覺化功能的API端點
"""

from flask import Blueprint, request, jsonify, render_template, send_file
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path

# 導入服務模組
from app.services.visualization_service import visualization_service

logger = logging.getLogger(__name__)

# 創建可視化藍圖
visualization_bp = Blueprint('visualization', __name__, url_prefix='/visualization')

@visualization_bp.route('/')
@login_required
def dashboard():
    """高級可視化儀表板"""
    return render_template('visualization/dashboard.html')

@visualization_bp.route('/business')
@login_required
def business_dashboard():
    """業務員專用視覺化儀表板"""
    try:
        # 獲取用戶ID
        user_id = current_user.id if hasattr(current_user, 'id') else None
        
        # 獲取時間範圍參數
        days = request.args.get('days', 30, type=int)
        days = min(max(days, 1), 90)  # 限制在1-90天之間
        
        return render_template('visualization/business_dashboard.html',
                             user_id=user_id,
                             days=days)
        
    except Exception as e:
        logger.error(f"載入業務員視覺化儀表板失敗: {e}")
        return render_template('visualization/business_dashboard.html',
                             user_id=None,
                             days=30)

@visualization_bp.route('/reports')
@login_required
def reports():
    """報告視覺化頁面"""
    return render_template('visualization/reports.html')

@visualization_bp.route('/api/generate/business_charts')
@login_required
def generate_business_charts():
    """生成業務員儀表板圖表"""
    try:
        # 獲取參數
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        
        # 限制參數範圍
        days = min(max(days, 1), 90)
        
        # 如果沒有指定用戶ID，使用當前用戶
        if not user_id and hasattr(current_user, 'id'):
            user_id = current_user.id
        
        # 生成圖表
        chart_paths = visualization_service.generate_business_dashboard_charts(
            user_id=user_id, 
            days=days
        )
        
        if not chart_paths:
            return jsonify({
                'status': 'warning',
                'message': '沒有足夠的數據生成圖表',
                'data': {}
            })
        
        # 轉換為相對路徑（用於網頁顯示）
        web_paths = {}
        for chart_name, chart_path in chart_paths.items():
            if chart_path and os.path.exists(chart_path):
                # 轉換為相對於static目錄的路徑
                relative_path = os.path.relpath(chart_path, 
                    start=os.path.join(os.path.dirname(chart_path), '..', '..', '..'))
                web_paths[chart_name] = f'/static/{relative_path.replace(os.sep, "/")}'
        
        return jsonify({
            'status': 'success',
            'message': f'成功生成 {len(web_paths)} 個圖表',
            'data': {
                'charts': web_paths,
                'generated_at': datetime.now().isoformat(),
                'user_id': user_id,
                'days': days
            }
        })
        
    except Exception as e:
        logger.error(f"生成業務員圖表失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'生成圖表失敗: {str(e)}'
        }), 500

@visualization_bp.route('/api/generate/report_charts')
@login_required
def generate_report_charts():
    """生成報告圖表"""
    try:
        # 獲取參數
        report_type = request.args.get('type', 'weekly')
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30}
        days = days_map.get(report_type, 7)
        
        # 生成圖表
        chart_paths = visualization_service.generate_report_charts(
            report_type=report_type,
            days=days
        )
        
        if not chart_paths:
            return jsonify({
                'status': 'warning',
                'message': '沒有足夠的數據生成報告圖表',
                'data': {}
            })
        
        # 轉換為相對路徑
        web_paths = {}
        for chart_name, chart_path in chart_paths.items():
            if chart_path and os.path.exists(chart_path):
                relative_path = os.path.relpath(chart_path, 
                    start=os.path.join(os.path.dirname(chart_path), '..', '..', '..'))
                web_paths[chart_name] = f'/static/{relative_path.replace(os.sep, "/")}'
        
        return jsonify({
            'status': 'success',
            'message': f'成功生成 {report_type} 報告圖表',
            'data': {
                'charts': web_paths,
                'report_type': report_type,
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"生成報告圖表失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'生成報告圖表失敗: {str(e)}'
        }), 500

@visualization_bp.route('/api/chart/<chart_type>')
@login_required
def get_chart(chart_type: str):
    """獲取特定類型的圖表"""
    try:
        # 獲取參數
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        format_type = request.args.get('format', 'png')  # png, jpg, svg, html
        
        # 根據圖表類型生成對應圖表
        if chart_type == 'news_trend':
            # 生成新聞趨勢圖
            chart_paths = visualization_service.generate_business_dashboard_charts(user_id, days)
            chart_path = chart_paths.get('news_trend')
            
        elif chart_type == 'importance_distribution':
            # 生成重要性分佈圖
            chart_paths = visualization_service.generate_business_dashboard_charts(user_id, days)
            chart_path = chart_paths.get('importance_distribution')
            
        elif chart_type == 'interactive_dashboard':
            # 生成交互式儀表板
            chart_paths = visualization_service.generate_business_dashboard_charts(user_id, days)
            chart_path = chart_paths.get('interactive_dashboard')
            
        else:
            return jsonify({
                'status': 'error',
                'message': f'不支援的圖表類型: {chart_type}'
            }), 400
        
        if not chart_path or not os.path.exists(chart_path):
            return jsonify({
                'status': 'error',
                'message': '圖表文件不存在'
            }), 404
        
        # 如果是HTML文件，返回路徑
        if chart_path.endswith('.html'):
            relative_path = os.path.relpath(chart_path, 
                start=os.path.join(os.path.dirname(chart_path), '..', '..', '..'))
            return jsonify({
                'status': 'success',
                'data': {
                    'chart_url': f'/static/{relative_path.replace(os.sep, "/")}',
                    'type': 'html'
                }
            })
        
        # 對於圖片文件，可以直接返回文件或base64編碼
        if format_type == 'base64':
            chart_base64 = visualization_service.get_chart_base64(chart_path)
            return jsonify({
                'status': 'success',
                'data': {
                    'chart_data': chart_base64,
                    'type': 'base64'
                }
            })
        else:
            # 返回文件路徑
            relative_path = os.path.relpath(chart_path, 
                start=os.path.join(os.path.dirname(chart_path), '..', '..', '..'))
            return jsonify({
                'status': 'success',
                'data': {
                    'chart_url': f'/static/{relative_path.replace(os.sep, "/")}',
                    'type': 'image'
                }
            })
        
    except Exception as e:
        logger.error(f"獲取圖表失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'獲取圖表失敗: {str(e)}'
        }), 500

@visualization_bp.route('/api/analytics/summary')
@login_required
def get_analytics_summary():
    """獲取分析摘要數據"""
    try:
        # 獲取參數
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        
        # 這裡應該從數據庫獲取實際的統計數據
        # 暫時返回模擬數據
        summary = {
            'total_news': 150,
            'high_importance_news': 25,
            'avg_importance': 0.65,
            'total_views': 1250,
            'total_shares': 85,
            'active_sources': 8,
            'top_categories': [
                {'name': '市場動態', 'count': 45},
                {'name': '政策法規', 'count': 38},
                {'name': '產品資訊', 'count': 32},
                {'name': '行業分析', 'count': 25}
            ],
            'sentiment_distribution': {
                'positive': 65,
                'neutral': 70,
                'negative': 15
            },
            'daily_trend': [
                {'date': '2024-01-01', 'news_count': 12, 'avg_importance': 0.7},
                {'date': '2024-01-02', 'news_count': 8, 'avg_importance': 0.6},
                {'date': '2024-01-03', 'news_count': 15, 'avg_importance': 0.8}
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': summary,
            'generated_at': datetime.now().isoformat(),
            'user_id': user_id,
            'days': days
        })
        
    except Exception as e:
        logger.error(f"獲取分析摘要失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'獲取分析摘要失敗: {str(e)}'
        }), 500

@visualization_bp.route('/api/export/chart/<chart_type>')
@login_required
def export_chart(chart_type: str):
    """導出圖表文件"""
    try:
        # 獲取參數
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        format_type = request.args.get('format', 'png')
        
        # 生成圖表
        chart_paths = visualization_service.generate_business_dashboard_charts(user_id, days)
        chart_path = chart_paths.get(chart_type)
        
        if not chart_path or not os.path.exists(chart_path):
            return jsonify({
                'status': 'error',
                'message': '圖表文件不存在'
            }), 404
        
        # 返回文件下載
        filename = f"{chart_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
        return send_file(chart_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"導出圖表失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'導出圖表失敗: {str(e)}'
        }), 500

@visualization_bp.route('/api/refresh_charts')
@login_required
def refresh_charts():
    """刷新所有圖表"""
    try:
        # 獲取參數
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        
        # 清除舊圖表文件
        chart_dir = visualization_service.output_dir
        if chart_dir.exists():
            for chart_file in chart_dir.glob('*.png'):
                try:
                    chart_file.unlink()
                except:
                    pass
        
        # 重新生成圖表
        chart_paths = visualization_service.generate_business_dashboard_charts(user_id, days)
        
        # 轉換為網頁路徑
        web_paths = {}
        for chart_name, chart_path in chart_paths.items():
            if chart_path and os.path.exists(chart_path):
                relative_path = os.path.relpath(chart_path, 
                    start=os.path.join(os.path.dirname(chart_path), '..', '..', '..'))
                web_paths[chart_name] = f'/static/{relative_path.replace(os.sep, "/")}'
        
        return jsonify({
            'status': 'success',
            'message': f'已刷新 {len(web_paths)} 個圖表',
            'data': {
                'charts': web_paths,
                'refreshed_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"刷新圖表失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'刷新圖表失敗: {str(e)}'
        }), 500

# 錯誤處理
@visualization_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': '找不到請求的資源'
    }), 404

@visualization_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': '服務器內部錯誤'
    }), 500

# 註冊藍圖的函數
def register_visualization_blueprint(app):
    """註冊可視化藍圖到Flask應用"""
    app.register_blueprint(visualization_bp)
