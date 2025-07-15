"""
簡單API路由模組
Simple API Routes Module

提供基本的API端點，不依賴分析引擎
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import logging

# 創建簡單API藍圖
simple_api_bp = Blueprint('simple_api', __name__)
logger = logging.getLogger(__name__)

@simple_api_bp.route('/health')
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '2.0.0-simple'
    })

@simple_api_bp.route('/v1/stats')
def get_stats():
    """獲取系統統計數據"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'totalNews': 542,
                'totalSources': 12,
                'totalCategories': 8,
                'todayNews': 23,
                'weekNews': 146,
                'sourceStats': [
                    {'name': '工商時報', 'count': 145},
                    {'name': '經濟日報', 'count': 128},
                    {'name': '金管會公告', 'count': 87},
                    {'name': '保險業動態', 'count': 76}
                ],
                'categoryStats': [
                    {'name': '產業新聞', 'count': 213},
                    {'name': '政策法規', 'count': 112},
                    {'name': '市場分析', 'count': 95},
                    {'name': '商品資訊', 'count': 78}
                ],
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"獲取統計數據失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': '無法獲取統計數據',
            'error': str(e)
        }), 500

@simple_api_bp.route('/v1/crawler/status')
def get_crawler_status():
    """獲取爬蟲狀態"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'sources': {
                    'total': 12,
                    'active': 10,
                    'inactive': 2
                },
                'crawls_today': {
                    'total': 24,
                    'successful': 23,
                    'failed': 1,
                    'success_rate': 95.8
                },
                'news': {
                    'total': 542,
                    'today': 23
                },
                'recent_activities': [
                    {
                        'id': 1,
                        'source': '工商時報',
                        'success': True,
                        'news_found': 12,
                        'news_new': 8,
                        'duration': 45.2,
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'error_message': None
                    }
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲狀態失敗'
        }), 500

@simple_api_bp.route('/v1/crawler/sources')
def get_crawler_sources():
    """獲取爬蟲來源統計"""
    try:
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': 1,
                    'name': '工商時報',
                    'url': 'https://ctee.com.tw/category/finance/insurance',
                    'status': 'active',
                    'total_news': 145,
                    'successful_crawls': 120,
                    'failed_crawls': 5,
                    'success_rate': 96.0,
                    'reliability_score': 0.98,
                    'last_crawl': datetime.now(timezone.utc).isoformat(),
                    'last_crawl_success': True
                }
            ]
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲來源失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲來源失敗'
        }), 500

# 業務員分類新聞API
@simple_api_bp.route('/business/api/category-news')
def get_business_category_news():
    """獲取業務員分類新聞"""
    try:
        group = request.args.get('group', '')
        category = request.args.get('category', '')
        
        # 模擬數據
        news_data = [
            {
                'id': 101,
                'title': f'{category}相關新聞：保險業最新動態',
                'summary': f'這是關於{category}的重要新聞，對業務員工作具有指導意義。',
                'importance_score': 0.8,
                'published_date': datetime.now(timezone.utc).isoformat(),
                'source_name': '保險業動態'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'news': news_data
        })
        
    except Exception as e:
        logger.error(f"獲取業務分類新聞失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': '獲取分類新聞失敗'
        }), 500

# 監控API端點
@simple_api_bp.route('/monitor/api/crawler/status')
def get_monitor_crawler_status():
    """監控頁面的爬蟲狀態"""
    return get_crawler_status()

@simple_api_bp.route('/monitor/api/news/stats')
def get_monitor_news_stats():
    """監控頁面的新聞統計"""
    return get_stats()
