"""
API V1 修復路由模組
API V1 Routes Fix Module

提供與前端兼容的 API v1 端點
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
import logging
import threading
import time

# 創建API V1藍圖
api_v1_bp = Blueprint('api_v1', __name__)
logger = logging.getLogger(__name__)

# 初始化爬蟲狀態數據
crawler_data = {
    'sources': [
        {'name': '工商時報保險版', 'count': 145},
        {'name': '經濟日報保險', 'count': 128},
        {'name': '金管會公告', 'count': 87},
        {'name': '保險業動態', 'count': 76}
    ],
    'recent_activities': []
}

# 模擬初始化一些最近活動數據
now = datetime.now(timezone.utc)
for i in range(5):
    crawler_data['recent_activities'].append({
        'id': i + 1,
        'source': crawler_data['sources'][i % len(crawler_data['sources'])]['name'],
        'success': i % 3 != 0,  # 大部分成功
        'news_found': 10 - i,
        'news_new': 5 - (i // 2),
        'duration': round(30 + i * 2.5, 1),
        'start_time': (now - timedelta(minutes=i * 30)).isoformat(),
        'error_message': None if i % 3 != 0 else "連接超時"
    })

@api_v1_bp.route('/health')
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '2.1.0'
    })

@api_v1_bp.route('/stats')
def get_stats():
    """獲取系統統計數據（與前端兼容的格式）"""
    global crawler_data
    try:
        # 增加統計計算
        total_news = sum(source['count'] for source in crawler_data['sources'])
        today_news = sum(activity['news_new'] for activity in crawler_data['recent_activities'] if activity['success'])
        
        return jsonify({
            'status': 'success',
            'data': {
                'totalNews': total_news,
                'totalSources': len(crawler_data['sources']),
                'totalCategories': 8,
                'todayNews': today_news,
                'weekNews': today_news * 7,
                'sourceStats': crawler_data['sources'],
                'categoryStats': [
                    {'name': '產業新聞', 'count': round(total_news * 0.4)},
                    {'name': '政策法規', 'count': round(total_news * 0.2)},
                    {'name': '市場分析', 'count': round(total_news * 0.15)},
                    {'name': '商品資訊', 'count': round(total_news * 0.15)},
                    {'name': '人事異動', 'count': round(total_news * 0.1)}
                ],
                'lastUpdated': datetime.now(timezone.utc).isoformat(),
                # 前端額外期望的格式
                'source_totals': crawler_data['sources'],
                'recent_runs': crawler_data['recent_activities']
            }
        })
        
    except Exception as e:
        logger.error(f"獲取統計數據失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': '無法獲取統計數據',
            'error': str(e)
        }), 500

@api_v1_bp.route('/crawler/status')
def get_crawler_status():
    """獲取爬蟲狀態（與前端兼容的格式）"""
    global crawler_data
    try:
        # 計算今日爬取數據
        successful = sum(1 for a in crawler_data['recent_activities'] if a['success'])
        failed = len(crawler_data['recent_activities']) - successful
        
        return jsonify({
            'status': 'success',
            'data': {
                'sources': {
                    'total': len(crawler_data['sources']),
                    'active': len(crawler_data['sources']) - 1,
                    'inactive': 1
                },
                'crawls_today': {
                    'total': len(crawler_data['recent_activities']),
                    'successful': successful,
                    'failed': failed,
                    'success_rate': round(successful / max(len(crawler_data['recent_activities']), 1) * 100, 1)
                },
                'news': {
                    'total': sum(s['count'] for s in crawler_data['sources']),
                    'today': sum(a['news_new'] for a in crawler_data['recent_activities'] if a['success'])
                },
                'recent_activities': crawler_data['recent_activities'],
                # 前端額外期望的格式
                'source_totals': crawler_data['sources'],
                'recent_runs': crawler_data['recent_activities']
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲狀態失敗'
        }), 500

@api_v1_bp.route('/crawler/sources')
def get_crawler_sources():
    """獲取爬蟲來源列表（與前端兼容的格式）"""
    global crawler_data
    try:
        now = datetime.now(timezone.utc)
        sources_data = []
        
        for i, source in enumerate(crawler_data['sources']):
            sources_data.append({
                'id': i + 1,
                'name': source['name'],
                'url': f'https://example.com/{source["name"]}',
                'status': 'active' if i % 4 != 2 else 'warning',
                'total_news': source['count'],
                'successful_crawls': round(source['count'] * 0.9),
                'failed_crawls': round(source['count'] * 0.1),
                'success_rate': 90.0,
                'reliability_score': 0.95 - (i * 0.05),
                'last_crawl': (now - timedelta(minutes=i * 15)).isoformat(),
                'last_crawl_success': i % 4 != 2
            })
        
        return jsonify({
            'status': 'success',
            'data': sources_data
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲來源失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲來源失敗'
        }), 500

@api_v1_bp.route('/crawler/start', methods=['POST'])
def start_crawler():
    """手動啟動爬蟲（與前端兼容的格式）"""
    global crawler_data
    try:
        # 獲取請求參數
        data = request.get_json() or {}
        use_mock = data.get('use_mock', True)
        sources = data.get('sources', [])
        
        logger.info(f"手動啟動爬蟲 - 模擬模式: {use_mock}, 來源: {sources}")
        
        # 模擬爬蟲執行
        def mock_crawl():
            time.sleep(2)  # 模擬執行時間
            
            # 添加新的爬蟲活動記錄
            now = datetime.now(timezone.utc)
            new_activity = {
                'id': len(crawler_data['recent_activities']) + 1,
                'source': '模擬爬蟲',
                'success': True,
                'news_found': 15,
                'news_new': 8,
                'duration': 3.5,
                'start_time': now.isoformat(),
                'error_message': None
            }
            
            crawler_data['recent_activities'].insert(0, new_activity)
            # 限制活動記錄數量
            crawler_data['recent_activities'] = crawler_data['recent_activities'][:10]
            
            logger.info(f"模擬爬蟲執行完成，添加新活動記錄: {new_activity}")
        
        # 在後台執行
        threading.Thread(target=mock_crawl, daemon=True).start()
        
        return jsonify({
            'status': 'success',
            'message': '爬蟲任務已啟動，正在背景執行',
            'data': {
                'task_id': f'crawler_{int(datetime.now().timestamp())}',
                'total': 15,  # 模擬處理的新聞總數
                'new': 8,     # 模擬新增的新聞數 
                'updated': 3,  # 模擬更新的新聞數
                'duration': 3.5,  # 模擬執行時間
                'sources_processed': sources if sources else ['模擬爬蟲'],
                'message': '爬蟲執行成功'
            }
        })
        
    except Exception as e:
        logger.error(f"啟動爬蟲失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'啟動爬蟲失敗: {str(e)}'
        }), 500
